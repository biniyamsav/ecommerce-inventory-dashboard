import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart, line_chart
from components.metric_cards import metric_card
from utils.helpers import first_value, to_float
from utils.styles import CHART_COLORS


@st.cache_data(ttl=600)
def load_revenue_trend():
    df = pd.DataFrame(db.revenue_per_month_last_12_months(), columns=["month", "revenue"])
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"])
        df["revenue"] = df["revenue"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_top_products():
    df = pd.DataFrame(db.top_10_products_by_revenue(), columns=["product", "revenue"])
    if not df.empty:
        df["revenue"] = df["revenue"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_order_status():
    df = pd.DataFrame(db.pct_cancelled_vs_delivered(), columns=["status", "percentage"])
    if not df.empty:
        df["status"] = df["status"].astype(str).str.strip()
        df["percentage"] = df["percentage"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_weekday_volume():
    df = pd.DataFrame(db.highest_order_volume_day_of_week(), columns=["day", "order_volume"])
    if not df.empty:
        df["day"] = df["day"].astype(str).str.strip()
        df["order_volume"] = df["order_volume"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_rolling_sales():
    df = pd.DataFrame(
        db.rolling_7_30_day_sales_per_product(),
        columns=["product", "order_date", "daily_sales", "rolling_7_day", "rolling_30_day"],
    )
    if not df.empty:
        df["order_date"] = pd.to_datetime(df["order_date"])
        for col in ["daily_sales", "rolling_7_day", "rolling_30_day"]:
            df[col] = df[col].astype(float)
    return df


@st.cache_data(ttl=600)
def load_monthly_top_product():
    df = pd.DataFrame(
        db.top_selling_product_per_month_last_12_months(),
        columns=["product", "month", "quantity_sold"],
    )
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"])
        df["month_label"] = df["month"].dt.strftime("%b %Y")
        df["quantity_sold"] = df["quantity_sold"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_top_category():
    rows = db.top_revenue_category()
    if not rows:
        return "N/A", 0.0
    category = str(rows[0][0]).strip() if rows[0][0] is not None else "N/A"
    return category, to_float(rows[0][1])


@st.cache_data(ttl=600)
def load_top_region():
    rows = db.top_revenue_region()
    if not rows:
        return "N/A", 0.0
    region = str(rows[0][0]).strip() if rows[0][0] is not None else "N/A"
    return region, to_float(rows[0][1])


def sales_page():
    st.title("Sales")

    revenue_df = load_revenue_trend()
    top_products_df = load_top_products()
    status_df = load_order_status()
    weekday_df = load_weekday_volume()
    rolling_df = load_rolling_sales()
    monthly_product_df = load_monthly_top_product()
    top_category, top_category_revenue = load_top_category()
    top_region, top_region_revenue = load_top_region()

    avg_order_value = to_float(first_value(db.average_order_value(), 0, 0))

    delivered_pct = 0.0
    cancelled_pct = 0.0
    if not status_df.empty:
        delivered_pct = float(status_df.loc[status_df["status"] == "delivered", "percentage"].squeeze()) if "delivered" in status_df["status"].values else 0.0
        cancelled_pct = float(status_df.loc[status_df["status"] == "cancelled", "percentage"].squeeze()) if "cancelled" in status_df["status"].values else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Avg order value", f"${avg_order_value:,.2f}")
    with c2:
        metric_card("Top category", top_category, delta=f"${top_category_revenue:,.0f}")
    with c3:
        metric_card("Top region", top_region, delta=f"${top_region_revenue:,.0f}")
    with c4:
        metric_card(
            "Delivered rate",
            f"{delivered_pct:.1f}%",
            delta=f"{cancelled_pct:.1f}% cancelled",
            delta_positive=False,
        )

    st.divider()

    st.subheader("Revenue trend")
    if not revenue_df.empty:
        fig = line_chart(
            revenue_df,
            x="month",
            y="revenue",
            title="Revenue trend over the last 12 months",
            height=420,
            labels={"month": "Month", "revenue": "Revenue ($)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No revenue data available for the last 12 months.")

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Top 10 products by revenue")
        if not top_products_df.empty:
            fig = bar_chart(
                top_products_df.sort_values("revenue"),
                x="revenue",
                y="product",
                title="Top product revenue",
                orientation="h",
                height=420,
                labels={"revenue": "Revenue ($)", "product": "Product"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product revenue data available.")

    with right:
        st.subheader("Order status")
        if not status_df.empty:
            fig = bar_chart(
                status_df,
                x="status",
                y="percentage",
                title="Delivered vs cancelled",
                height=420,
                color="status",
                labels={"status": "Order status", "percentage": "Share (%)"},
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order status data available.")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Top-selling product per month")
        if not monthly_product_df.empty:
            fig = bar_chart(
                monthly_product_df,
                x="month_label",
                y="quantity_sold",
                color="product",
                title="Monthly top-selling product",
                height=380,
                labels={"month_label": "Month", "quantity_sold": "Quantity sold", "product": "Product"},
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly top product data available.")

    with right:
        st.subheader("Orders by day of week")
        if not weekday_df.empty:
            fig = bar_chart(
                weekday_df,
                x="day",
                y="order_volume",
                title="Order volume by weekday",
                height=380,
                labels={"day": "Day", "order_volume": "Order volume"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No weekday order volume data available.")

    st.divider()

    st.subheader("Rolling sales by product")
    if not rolling_df.empty:
        selected_product = st.selectbox("Select product", sorted(rolling_df["product"].unique()))
        product_sales = rolling_df[rolling_df["product"] == selected_product]
        fig = line_chart(
            product_sales,
            x="order_date",
            y=["rolling_7_day", "rolling_30_day"],
            title=f"Rolling 7 / 30 day sales for {selected_product}",
            height=420,
            labels={"order_date": "Order date", "rolling_7_day": "7-day sales", "rolling_30_day": "30-day sales"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rolling sales data available.")

    # =====================================================
    # Raw Data
    # =====================================================

    with st.expander("Top products data"):
        st.dataframe(top_products_df, use_container_width=True)

    with st.expander("Monthly top-selling products"):
        st.dataframe(monthly_product_df, use_container_width=True)

    with st.expander("Rolling sales data"):
        st.dataframe(rolling_df, use_container_width=True)
