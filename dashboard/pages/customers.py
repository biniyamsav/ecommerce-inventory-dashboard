import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart
from components.metric_cards import metric_card
from components.tables import attention_table, data_table
from utils.helpers import first_value, to_float


@st.cache_data(ttl=600)
def load_top_customers():
    df = pd.DataFrame(
        db.top_20_customers_by_spend(),
        columns=["customer_id", "customer_name", "total_spend"],
    )
    if not df.empty:
        df["total_spend"] = df["total_spend"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_region_avg_order_value():
    df = pd.DataFrame(
        db.region_highest_avg_order_value(),
        columns=["region", "avg_order_value"],
    )
    if not df.empty:
        df["avg_order_value"] = df["avg_order_value"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_one_time_customers():
    df = pd.DataFrame(
        db.one_time_customers(),
        columns=["customer_id", "customer_name", "order_count"],
    )
    if not df.empty:
        df["order_count"] = df["order_count"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_order_frequency_distribution():
    df = pd.DataFrame(
        db.order_frequency_distribution(),
        columns=["frequency_bucket", "customer_count"],
    )
    if not df.empty:
        df["customer_count"] = df["customer_count"].astype(int)
    return df


def customers_page():
    st.title("Customers")

    top_customers_df = load_top_customers()
    region_avg_df = load_region_avg_order_value()
    one_time_df = load_one_time_customers()
    freq_df = load_order_frequency_distribution()

    new_customers = int(first_value(db.new_customers_last_month(), 0, 0))
    one_time_count = len(one_time_df)
    top_customer_name = top_customers_df["customer_name"].iloc[0] if not top_customers_df.empty else "N/A"
    top_customer_spend = top_customers_df["total_spend"].iloc[0] if not top_customers_df.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("New customers", f"{new_customers}")
    with c2:
        metric_card("One-time customers", f"{one_time_count}", delta_positive=False)
    with c3:
        metric_card("Top customer", top_customer_name, delta=f"${top_customer_spend:,.2f}")
    with c4:
        region_label = region_avg_df["region"].iloc[0] if not region_avg_df.empty else "N/A"
        region_value = region_avg_df["avg_order_value"].iloc[0] if not region_avg_df.empty else 0.0
        metric_card("Top region AOV", region_label, delta=f"${region_value:,.2f}")

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Top 20 customers by spend")
        if not top_customers_df.empty:
            formatted = top_customers_df.copy()
            formatted["total_spend"] = formatted["total_spend"].map("${:,.2f}".format)
            data_table(formatted)
        else:
            st.info("No customer spend data available.")

    with right:
        st.subheader("Churn risk: one-time customers")
        attention_table(
            one_time_df,
            title="One-time customers",
            message="Customers with only a single purchase are higher churn risk and should receive targeted retention outreach.",
            height=380,
        )

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Average order value by region")
        if not region_avg_df.empty:
            fig = bar_chart(
                region_avg_df,
                x="region",
                y="avg_order_value",
                title="Region average order value",
                height=380,
                labels={"region": "Region", "avg_order_value": "Avg order value ($)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No region order value data available.")

    with right:
        st.subheader("Order frequency distribution")
        if not freq_df.empty:
            fig = bar_chart(
                freq_df,
                x="frequency_bucket",
                y="customer_count",
                title="Customer order frequency",
                height=380,
                labels={"frequency_bucket": "Order frequency", "customer_count": "Customer count"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order frequency data available.")
