import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart
from components.metric_cards import metric_card
from components.tables import attention_table
from utils.helpers import first_value, to_float


@st.cache_data(ttl=600)
def load_profit_margin_per_product():
    df = pd.DataFrame(db.profit_margin_per_product(), columns=["product_id", "product_name", "profit_margin"])
    if not df.empty:
        df["profit_margin"] = df["profit_margin"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_category_margin_highlight():
    rows = db.category_highest_avg_profit_margin()
    if not rows:
        return "N/A", 0.0
    return str(rows[0][0]).strip() if rows[0][0] is not None else "N/A", to_float(rows[0][1])


@st.cache_data(ttl=600)
def load_products_never_ordered():
    df = pd.DataFrame(db.products_never_ordered(), columns=["product_id", "product_name"])
    return df


@st.cache_data(ttl=600)
def load_revenue_rank_by_category():
    df = pd.DataFrame(
        db.product_rank_by_revenue_within_category(),
        columns=["product_id", "product_name", "category", "total_revenue", "revenue_rank"],
    )
    if not df.empty:
        df["total_revenue"] = df["total_revenue"].astype(float)
        df["revenue_rank"] = df["revenue_rank"].astype(int)
    return df


def products_page():
    st.title("Products")

    profit_df = load_profit_margin_per_product()
    top_category, category_avg_margin = load_category_margin_highlight()
    never_ordered_df = load_products_never_ordered()
    rank_df = load_revenue_rank_by_category()

    top_margin_name = profit_df["product_name"].iloc[0] if not profit_df.empty else "N/A"
    top_margin_value = profit_df["profit_margin"].iloc[0] if not profit_df.empty else 0.0
    never_ordered_count = len(never_ordered_df)
    category_options = sorted(rank_df["category"].dropna().unique().tolist())
    selected_category = category_options[0] if category_options else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Top profit margin", top_margin_name, delta=f"${top_margin_value:,.2f}")
    with c2:
        metric_card("Best margin category", top_category, delta=f"${category_avg_margin:,.2f}")
    with c3:
        metric_card("Never ordered", f"{never_ordered_count}", delta_positive=False)
    with c4:
        metric_card("Products tracked", f"{len(profit_df):,}")

    st.divider()

    st.subheader("Profit margin ranking")
    if not profit_df.empty:
        sorted_profit = profit_df.sort_values("profit_margin")
        fig = bar_chart(
            sorted_profit,
            x="profit_margin",
            y="product_name",
            title="Profit margin by product",
            orientation="h",
            height=460,
            labels={"profit_margin": "Profit margin ($)", "product_name": "Product"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No profit margin data available.")

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Revenue rank within category")
        if selected_category and not rank_df.empty:
            category_df = rank_df[rank_df["category"] == selected_category]
            if not category_df.empty:
                fig = bar_chart(
                    category_df.sort_values("revenue_rank", ascending=False),
                    x="total_revenue",
                    y="product_name",
                    title=f"Revenue rank for {selected_category}",
                    orientation="h",
                    height=420,
                    labels={"total_revenue": "Revenue ($)", "product_name": "Product"},
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ranked revenue data available for the selected category.")
        else:
            st.info("No category revenue ranking data available.")

    with right:
        st.subheader("Category profit margin highlight")
        st.markdown(
            f"""
            <div style='border-left: 4px solid #4F46E5; background: rgba(79, 70, 229, 0.08); padding: 16px; border-radius: 10px;'>
                <strong style='font-size: 1rem;'>Highest average margin category</strong><br>
                <div style='margin-top: 8px; font-size: 0.95rem;'>
                    <strong>{top_category}</strong><br>
                    Average profit margin of <strong>${category_avg_margin:,.2f}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        attention_table(
            never_ordered_df,
            title="Products never ordered",
            message="These products have no recorded order history. Investigate pricing, catalog visibility, or fulfillment readiness.",
            height=320,
        )
