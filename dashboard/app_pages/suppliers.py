import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart, line_chart
from components.metric_cards import metric_card
from components.tables import attention_table, data_table
from utils.helpers import first_value, to_float


@st.cache_data(ttl=600)
def load_on_time_rate():
    df = pd.DataFrame(db.on_time_delivery_rate_per_supplier(), columns=["supplier", "on_time_rate"])
    if not df.empty:
        df["on_time_rate"] = df["on_time_rate"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_worst_on_time_rate():
    df = pd.DataFrame(db.worst_on_time_delivery_rate_per_supplier(), columns=["supplier", "on_time_rate"])
    if not df.empty:
        df["on_time_rate"] = df["on_time_rate"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_avg_delay():
    df = pd.DataFrame(db.average_delay_days_per_supplier(), columns=["supplier", "avg_delay_days"])
    if not df.empty:
        df["avg_delay_days"] = df["avg_delay_days"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_most_delayed():
    df = pd.DataFrame(db.supplier_most_delayed_deliveries(), columns=["supplier", "delays"])
    if not df.empty:
        df["delays"] = df["delays"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_trend():
    df = pd.DataFrame(
        db.supplier_on_time_rate_trend_last_6_months(),
        columns=["supplier", "month", "total_orders", "on_time_orders", "on_time_rate"],
    )
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"])
        df["on_time_rate"] = df["on_time_rate"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_products_at_risk():
    df = pd.DataFrame(db.products_relying_on_least_reliable_suppliers(), columns=["product_name", "supplier_name"])
    return df


@st.cache_data(ttl=600)
def load_not_restocked():
    df = pd.DataFrame(db.not_restocked_in_last_30_days(), columns=["product_name"])
    return df


def suppliers_page():
    st.title("Suppliers")

    on_time_df = load_on_time_rate()
    worst_df = load_worst_on_time_rate()
    delay_df = load_avg_delay()
    delayed_df = load_most_delayed()
    trend_df = load_trend()
    risk_products_df = load_products_at_risk()
    stale_products_df = load_not_restocked()

    best_supplier = on_time_df["supplier"].iloc[0] if not on_time_df.empty else "N/A"
    best_rate = on_time_df["on_time_rate"].iloc[0] if not on_time_df.empty else 0.0
    worst_supplier = worst_df["supplier"].iloc[0] if not worst_df.empty else "N/A"
    worst_rate = worst_df["on_time_rate"].iloc[0] if not worst_df.empty else 0.0
    avg_delay = delay_df["avg_delay_days"].mean() if not delay_df.empty else 0.0
    delayed_count = delayed_df["supplier"].nunique() if not delayed_df.empty else 0
    stale_count = len(stale_products_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Best on-time supplier", best_supplier, delta=f"{best_rate:.1f}%")
    with c2:
        metric_card("Worst on-time supplier", worst_supplier, delta=f"{worst_rate:.1f}%", delta_positive=False)
    with c3:
        metric_card("Avg restock delay", f"{avg_delay:.1f} days")
    with c4:
        metric_card("Products at risk", f"{delayed_count}", delta=f"{stale_count} stale products", delta_positive=False)

    st.divider()

    st.subheader("Supplier on-time delivery rates")
    if not on_time_df.empty:
        fig = bar_chart(
            on_time_df,
            x="supplier",
            y="on_time_rate",
            title="Supplier on-time delivery rate",
            height=420,
            labels={"supplier": "Supplier", "on_time_rate": "On-time rate (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No supplier on-time rate data available.")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("On-time delivery trend")
        if not trend_df.empty:
            fig = line_chart(
                trend_df,
                x="month",
                y="on_time_rate",
                color="supplier",
                title="Supplier on-time rate trend (last 6 months)",
                height=420,
                labels={"month": "Month", "on_time_rate": "On-time rate (%)", "supplier": "Supplier"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No supplier trend data available.")

    with right:
        st.subheader("Most delayed deliveries")
        if not delayed_df.empty:
            fig = bar_chart(
                delayed_df.sort_values("delays", ascending=False),
                x="supplier",
                y="delays",
                title="Suppliers with most delayed restock deliveries",
                height=420,
                labels={"supplier": "Supplier", "delays": "Delayed deliveries"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No delayed delivery data available.")

    st.divider()

    st.subheader("Reliability risks and stale products")
    attention_table(
        risk_products_df,
        title="Products relying on least reliable suppliers",
        message="These products are tied to the lowest on-time supplier and need sourcing or fulfillment attention.",
        height=320,
    )

    with st.expander("Products not restocked in last 30 days"):
        if not stale_products_df.empty:
            data_table(stale_products_df)
        else:
            st.info("All products have restock activity in the last 30 days.")

    with st.expander("Supplier delay details"):
        st.dataframe(delay_df, use_container_width=True)
