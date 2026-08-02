import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart, line_chart
from components.metric_cards import metric_card
from components.tables import attention_table, data_table
from utils.helpers import to_float


@st.cache_data(ttl=600)
def load_stockout_forecast():
    df = pd.DataFrame(db.days_until_stockout(), columns=["product_name", "current_stock", "days_remaining"])
    if not df.empty:
        df["current_stock"] = df["current_stock"].astype(float)
        df["days_remaining"] = df["days_remaining"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_overstocked():
    df = pd.DataFrame(db.overstocked_products(), columns=["product_name", "total_stock", "recent_sales"])
    if not df.empty:
        df["total_stock"] = df["total_stock"].astype(int)
        df["recent_sales"] = df["recent_sales"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_stale_products():
    df = pd.DataFrame(db.not_restocked_in_last_30_days(), columns=["product_name"])
    return df


@st.cache_data(ttl=600)
def load_supplier_trend():
    df = pd.DataFrame(
        db.supplier_on_time_rate_trend_last_6_months(),
        columns=["supplier", "month", "total_orders", "on_time_orders", "on_time_rate"],
    )
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"])
        df["on_time_rate"] = df["on_time_rate"].astype(float)
    return df


def predictive_page():
    st.title("Predictive")
    st.markdown("##### Forecasted risks and supply chain signals for the next business cycle.")

    forecast_df = load_stockout_forecast()
    overstock_df = load_overstocked()
    stale_df = load_stale_products()
    supplier_df = load_supplier_trend()

    top_at_risk = forecast_df.sort_values("days_remaining").head(1)["product_name"].iloc[0] if not forecast_df.empty else "N/A"
    avg_days = forecast_df["days_remaining"].mean() if not forecast_df.empty else 0.0
    stale_count = len(stale_df)
    low_fulfillment = overstock_df["product_name"].iloc[0] if not overstock_df.empty else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Product most at risk", top_at_risk)
    with c2:
        metric_card("Avg stockout horizon", f"{avg_days:.1f} days")
    with c3:
        metric_card("Stale catalog items", f"{stale_count}", delta_positive=False)
    with c4:
        metric_card("Potential overstock", low_fulfillment, delta_positive=False)

    st.divider()
    section = st.radio(
        "Explore predictive insights",
        ["Stockout forecast", "Supplier reliability", "Inventory signals"],
        horizontal=True,
        index=0,
        key="predictive_section",
    )

    if section == "Stockout forecast":
        st.subheader("Stockout forecast")
        if not forecast_df.empty:
            fig = bar_chart(
                forecast_df.sort_values("days_remaining"),
                x="product_name",
                y="days_remaining",
                title="Days until stockout by product",
                orientation="h",
                height=420,
                labels={"product_name": "Product", "days_remaining": "Days remaining"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No stockout forecast data available.")

        attention_table(
            forecast_df.sort_values("days_remaining").head(10)[["product_name", "days_remaining"]].rename(
                columns={"product_name": "Product", "days_remaining": "Days remaining"}
            ),
            title="Immediate stockout risks",
            message="These products are forecasted to run out soon and need restock prioritization.",
            height=320,
        )

    elif section == "Supplier reliability":
        st.subheader("Supplier reliability")
        if not supplier_df.empty:
            fig = line_chart(
                supplier_df,
                x="month",
                y="on_time_rate",
                color="supplier",
                title="Supplier on-time rate trend",
                height=420,
                labels={"month": "Month", "on_time_rate": "On-time rate (%)", "supplier": "Supplier"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No supplier trend data available.")

        st.markdown(
            "##### What matters now"
        )
        st.write(
            "Monitor supplier punctuality over time and flag partners whose on-time rate is dropping before it impacts inventory reliability."
        )

    else:
        st.subheader("Inventory signals")
        if not overstock_df.empty:
            fig = bar_chart(
                overstock_df.sort_values("total_stock", ascending=False).head(10),
                x="product_name",
                y="total_stock",
                title="Potential overstocked products",
                orientation="h",
                height=420,
                labels={"product_name": "Product", "total_stock": "Total stock"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No overstock signal data available.")

        with st.expander("Stale products not restocked in 30 days"):
            if not stale_df.empty:
                data_table(stale_df)
            else:
                st.info("All products have recent restock activity.")

    st.divider()
    st.markdown(
        "##### Signal summary"
    )
    st.write(
        "Use these predictive views to prioritize stock replenishment, align supplier follow-up, and reduce the chance of inventory stress in the next cycle."
    )
