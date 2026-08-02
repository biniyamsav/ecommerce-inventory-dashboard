import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart, grouped_bar_chart
from components.metric_cards import metric_card
from components.tables import data_table, attention_table
from utils.helpers import to_float


@st.cache_data(ttl=600)
def load_stock_levels():
    df = pd.DataFrame(
        db.stock_level_per_product_per_warehouse(),
        columns=["product_name", "warehouse_name", "stock_level"],
    )
    if not df.empty:
        df["stock_level"] = df["stock_level"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_out_of_stock():
    df = pd.DataFrame(db.out_of_stock_products(), columns=["product_name", "warehouse", "stock_level"])
    if not df.empty:
        df["stock_level"] = df["stock_level"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_low_stock(threshold=50):
    df = pd.DataFrame(db.low_stock_products(threshold), columns=["product_name", "warehouse", "stock_level"])
    if not df.empty:
        df["stock_level"] = df["stock_level"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_turnover():
    df = pd.DataFrame(db.stock_turnover_rate_per_product(), columns=["product_name", "quantity_sold", "avg_stock", "turnover_rate"])
    if not df.empty:
        df["quantity_sold"] = df["quantity_sold"].astype(float)
        df["avg_stock"] = df["avg_stock"].astype(float)
        df["turnover_rate"] = df["turnover_rate"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_days_until_stockout():
    df = pd.DataFrame(db.days_until_stockout(), columns=["product_name", "current_stock", "days_remaining"])
    if not df.empty:
        df["current_stock"] = df["current_stock"].astype(float)
        df["days_remaining"] = df["days_remaining"].astype(float)
    return df


def inventory_page():
    st.title("Inventory")

    stock_df = load_stock_levels()
    out_df = load_out_of_stock()
    low_df = load_low_stock()
    turnover_df = load_turnover()
    days_df = load_days_until_stockout()

    out_count = len(out_df)
    low_count = len(low_df)
    products_tracked = stock_df["product_name"].nunique() if not stock_df.empty else 0
    avg_turnover = turnover_df["turnover_rate"].mean() if not turnover_df.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Products tracked", f"{products_tracked}")
    with c2:
        metric_card("Out of stock", f"{out_count}", delta_positive=False)
    with c3:
        metric_card("Low stock", f"{low_count}", delta_positive=False)
    with c4:
        metric_card("Avg turnover rate", f"{avg_turnover:.2f}")

    st.divider()

    st.subheader("Stock level comparison")
    if not stock_df.empty:
        # let user choose top N products by total stock
        product_totals = stock_df.groupby("product_name")["stock_level"].sum().reset_index().sort_values("stock_level", ascending=False)
        top_n = st.selectbox("Show top N products", options=[5, 10, 20], index=1)
        top_products = product_totals.head(top_n)["product_name"].tolist()
        plot_df = stock_df[stock_df["product_name"].isin(top_products)]
        fig = grouped_bar_chart(
            plot_df,
            x="product_name",
            y="stock_level",
            color="warehouse_name",
            title="Stock level by warehouse (top products)",
            height=420,
            facet_col=None,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No stock level data available.")

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Stock turnover rate")
        if not turnover_df.empty:
            fig = bar_chart(
                turnover_df.sort_values("turnover_rate"),
                x="turnover_rate",
                y="product_name",
                title="Stock turnover rate by product",
                orientation="h",
                height=420,
                labels={"turnover_rate": "Turnover rate", "product_name": "Product"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No turnover data available.")

    with right:
        st.subheader("Days until stockout")
        if not days_df.empty:
            data_table(days_df.sort_values("days_remaining"))
        else:
            st.info("No stockout projection data available.")

    st.divider()

    st.subheader("Products requiring attention")
    attention_table(
        out_df,
        title="Out of stock products",
        message="Products with zero stock require immediate restock or reprioritization.",
        height=360,
    )

    with st.expander("Raw stock level data"):
        st.dataframe(stock_df, use_container_width=True)

