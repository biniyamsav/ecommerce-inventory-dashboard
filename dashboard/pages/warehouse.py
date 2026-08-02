import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart
from components.metric_cards import metric_card
from components.tables import data_table
from utils.helpers import first_value, to_float


@st.cache_data(ttl=600)
def load_orders_fulfilled():
    df = pd.DataFrame(db.orders_fulfilled_per_warehouse(), columns=["warehouse", "number_of_orders"])
    if not df.empty:
        df["number_of_orders"] = df["number_of_orders"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_revenue_fulfilled():
    df = pd.DataFrame(db.revenue_fulfilled_per_warehouse(), columns=["warehouse", "total_revenue"])
    if not df.empty:
        df["total_revenue"] = df["total_revenue"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_stockout_frequency():
    df = pd.DataFrame(db.warehouse_highest_stockout_frequency(), columns=["warehouse", "stockout_frequency"])
    if not df.empty:
        df["stockout_frequency"] = df["stockout_frequency"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_fastest_fulfillment():
    df = pd.DataFrame(db.warehouse_fastest_fulfillment(), columns=["warehouse", "avg_restock_delay"])
    if not df.empty:
        df["avg_restock_delay"] = df["avg_restock_delay"].astype(float)
    return df


def warehouse_page():
    st.title("Warehouse")

    orders_df = load_orders_fulfilled()
    revenue_df = load_revenue_fulfilled()
    stockout_df = load_stockout_frequency()
    fastest_df = load_fastest_fulfillment()

    best_order_warehouse = first_value(orders_df.values.tolist(), 0, "N/A") if not orders_df.empty else "N/A"
    best_revenue_warehouse = first_value(revenue_df.values.tolist(), 0, "N/A") if not revenue_df.empty else "N/A"
    fastest_warehouse = fastest_df["warehouse"].iloc[0] if not fastest_df.empty else "N/A"
    average_delay = fastest_df["avg_restock_delay"].iloc[0] if not fastest_df.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Top orders warehouse", best_order_warehouse)
    with c2:
        metric_card("Top revenue warehouse", best_revenue_warehouse)
    with c3:
        metric_card("Stockout hotspots", f"{len(stockout_df):,}", delta_positive=False)
    with c4:
        metric_card("Fastest fulfillment", f"{fastest_warehouse}", delta=f"{average_delay:.1f} days")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue fulfilled per warehouse")
        if not revenue_df.empty:
            fig = bar_chart(
                revenue_df,
                x="warehouse",
                y="total_revenue",
                title="Revenue fulfilled per warehouse",
                height=420,
                labels={"warehouse": "Warehouse", "total_revenue": "Revenue ($)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No warehouse revenue data available.")

    with right:
        st.subheader("Orders fulfilled per warehouse")
        if not orders_df.empty:
            fig = bar_chart(
                orders_df,
                x="warehouse",
                y="number_of_orders",
                title="Orders fulfilled per warehouse",
                height=420,
                labels={"warehouse": "Warehouse", "number_of_orders": "Orders"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No warehouse order volume data available.")

    st.divider()

    st.subheader("Stockout frequency")
    if not stockout_df.empty:
        fig = bar_chart(
            stockout_df,
            x="warehouse",
            y="stockout_frequency",
            title="Warehouse stockout frequency",
            height=380,
            labels={"warehouse": "Warehouse", "stockout_frequency": "Stockout events"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No warehouse stockout data available.")

    st.divider()

    st.subheader("Fulfillment performance")
    if not fastest_df.empty:
        data_table(fastest_df)
    else:
        st.info("No warehouse fulfillment timing data available.")

    with st.expander("Raw warehouse data"):
        merged = pd.merge(
            orders_df,
            revenue_df,
            on="warehouse",
            how="outer",
        )
        st.dataframe(merged, use_container_width=True)

