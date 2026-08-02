import streamlit as st
import pandas as pd
import plotly.express as px
from components import db

from components import db
from components.metric_cards import metric_card
from utils.helpers import first_value, to_float
from utils.styles import CHART_COLORS


def overview_page():
    st.title("Overview")

    # =====================================================
    # Load Data
    # =====================================================

    revenue_df = pd.DataFrame(
        db.revenue_per_month_last_12_months(),
        columns=["month", "revenue"],
    )
    if not revenue_df.empty:
        revenue_df["revenue"] = revenue_df["revenue"].astype(float)

    avg_order = to_float(first_value(db.average_order_value(), 0, 0))

    category_row = db.top_revenue_category()
    category_name = first_value(category_row, 0, "N/A")
    category_revenue = to_float(first_value(category_row, 1, 0))

    region_row = db.top_revenue_region()
    region_name = first_value(region_row, 0, "N/A")
    region_revenue = to_float(first_value(region_row, 1, 0))

    quarter_row = db.highest_revenue_quarter()
    quarter_num = first_value(quarter_row, 1, "N/A")
    quarter_revenue = to_float(first_value(quarter_row, 2, 0))

    new_customers = first_value(db.new_customers_last_month(), 0, 0)

    low_stock_count = db.count_low_stock_products()
    out_of_stock_count = db.count_out_of_stock_products()

    top_product_row = db.top_10_products_by_revenue()
    top_product_name = first_value(top_product_row, 0, "N/A")
    top_product_revenue = to_float(first_value(top_product_row, 1, 0))

    total_revenue = revenue_df["revenue"].sum() if not revenue_df.empty else 0

    # =====================================================
    # Executive KPI Row
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Revenue (12mo)", f"${total_revenue:,.0f}")

    with c2:
        metric_card("Avg Order Value", f"${avg_order:,.2f}")

    with c3:
        metric_card(
            "New Customers",
            f"{int(new_customers)}",
            delta="last 30 days",
            delta_positive=True,
        )

    with c4:
        metric_card(
            "Stock Alerts",
            f"{low_stock_count + out_of_stock_count}",
            delta=f"{out_of_stock_count} out of stock",
            delta_positive=False,
        )

    st.divider()

    # =====================================================
    # Revenue Trend
    # =====================================================

    st.subheader("Revenue Trend")

    if not revenue_df.empty:
        fig = px.line(
            revenue_df,
            x="month",
            y="revenue",
            markers=True,
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(height=380, xaxis_title="Month", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No revenue data available for the last 12 months.")

    st.divider()

    # =====================================================
    # Inventory Health + Recent Highlights
    # =====================================================

    left, right = st.columns(2)

    with left:
        st.subheader("Inventory Health")

        health_df = pd.DataFrame({
            "status": ["Low Stock", "Out of Stock"],
            "count": [low_stock_count, out_of_stock_count],
        })

        fig = px.bar(
            health_df,
            x="status",
            y="count",
            text="count",
            color="status",
            color_discrete_sequence=[CHART_COLORS[2], CHART_COLORS[3]],
        )
        fig.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Low Stock Products"):
            low_stock_df = pd.DataFrame(
                db.low_stock_products(),
                columns=["product", "warehouse", "stock_level"],
            )
            st.dataframe(low_stock_df, use_container_width=True)

    with right:
        st.subheader("Recent Highlights")

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Recent Highlights</div>
                <div style="margin-top: 10px; line-height: 1.9; font-size: 14px; color: #111827;">
                    <strong>Top category:</strong> {category_name} — ${category_revenue:,.0f}<br>
                    <strong>Top region:</strong> {region_name} — ${region_revenue:,.0f}<br>
                    <strong>Top product:</strong> {top_product_name} — ${top_product_revenue:,.0f}<br>
                    <strong>Best quarter:</strong> Q{quarter_num} — ${quarter_revenue:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    with st.expander("Raw Revenue Data"):
        st.dataframe(revenue_df, use_container_width=True)