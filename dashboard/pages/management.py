import streamlit as st
import pandas as pd

from components import db
from components.charts import bar_chart
from components.metric_cards import metric_card
from components.tables import attention_table, data_table
from utils.helpers import first_value, to_float, safe_rerun


@st.cache_data(ttl=600)
def load_supplier_delay():
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
def load_unreliable_supply():
    df = pd.DataFrame(db.products_relying_on_least_reliable_suppliers(), columns=["product_name", "supplier_name"])
    return df


@st.cache_data(ttl=600)
def load_dead_stock():
    df = pd.DataFrame(db.warehouse_most_dead_stock(), columns=["warehouse", "stock_level", "sales", "ratio"])
    if not df.empty:
        df["stock_level"] = df["stock_level"].astype(float)
        df["sales"] = df["sales"].astype(float)
        df["ratio"] = df["ratio"].astype(float)
    return df


@st.cache_data(ttl=600)
def load_oos_products():
    df = pd.DataFrame(db.out_of_stock_products(), columns=["product_name", "warehouse", "stock_level"])
    if not df.empty:
        df["stock_level"] = df["stock_level"].astype(int)
    return df


@st.cache_data(ttl=600)
def load_overstocked():
    df = pd.DataFrame(db.overstocked_products(), columns=["product_name", "total_stock", "recent_sales"])
    if not df.empty:
        df["total_stock"] = df["total_stock"].astype(int)
        df["recent_sales"] = df["recent_sales"].astype(float)
    return df


def management_page():
    st.title("Management")
    st.markdown("##### Operational view for supplier, warehouse, and inventory action priorities.")

    nav_cols = st.columns([1, 1, 1, 1])
    with nav_cols[0]:
        st.button("Home", on_click=lambda: st.session_state.update({"sidebar_nav": "Home"}) or safe_rerun(), use_container_width=True)
    with nav_cols[1]:
        st.button("Analysis", on_click=lambda: st.session_state.update({"sidebar_nav": "Analysis"}) or safe_rerun(), use_container_width=True)
    with nav_cols[2]:
        st.button("Predictive", on_click=lambda: st.session_state.update({"sidebar_nav": "Predictive"}) or safe_rerun(), use_container_width=True)
    with nav_cols[3]:
        st.button("Suppliers", on_click=lambda: st.session_state.update({"sidebar_nav": "Suppliers"}) or safe_rerun(), use_container_width=True)

    delay_df = load_supplier_delay()
    delayed_df = load_most_delayed()
    unreliable_df = load_unreliable_supply()
    dead_stock_df = load_dead_stock()
    oos_df = load_oos_products()
    overstock_df = load_overstocked()

    section = st.radio(
        "Management focus",
        ["Supplier reliability", "Warehouse stock", "Inventory alerts"],
        horizontal=True,
        index=0,
        key="management_section",
    )

    best_supplier = first_value(delay_df.sort_values("avg_delay_days"), 0, "N/A") if not delay_df.empty else "N/A"
    worst_supplier = first_value(delay_df.sort_values("avg_delay_days", ascending=False), 0, "N/A") if not delay_df.empty else "N/A"
    total_oos = len(oos_df)
    total_unreliable = len(unreliable_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Fastest supplier", best_supplier)
    with c2:
        metric_card("Slowest supplier", worst_supplier, delta_positive=False)
    with c3:
        metric_card("Out-of-stock items", f"{total_oos}", delta_positive=False)
    with c4:
        metric_card("Unreliable products", f"{total_unreliable}", delta_positive=False)

    st.divider()

    if section == "Supplier reliability":
        left, right = st.columns(2)
        with left:
            st.subheader("Suppliers with most delay events")
            if not delayed_df.empty:
                fig = bar_chart(
                    delayed_df.sort_values("delays", ascending=False).head(10),
                    x="supplier",
                    y="delays",
                    title="Most delayed supplier restock deliveries",
                    height=420,
                    labels={"supplier": "Supplier", "delays": "Delay events"},
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No supplier delay data available.")

        with right:
            st.subheader("Products tied to unreliable suppliers")
            if not unreliable_df.empty:
                data_table(unreliable_df)
            else:
                st.info("No products are currently tied to the least reliable supplier.")

    elif section == "Warehouse stock":
        st.subheader("Warehouses with dead stock")
        if not dead_stock_df.empty:
            data_table(dead_stock_df.head(10))
        else:
            st.info("No dead stock data available.")

        st.divider()
        st.subheader("Overstock signals")
        if not overstock_df.empty:
            data_table(overstock_df.head(10))
        else:
            st.info("No overstock risk data available.")

    else:
        st.subheader("Immediate operational attention")
        attention_table(
            oos_df,
            title="Out-of-stock products",
            message="These products are out of stock and need replenishment or sales reprioritization.",
            height=320,
        )

        with st.expander("Potential overstock opportunities"):
            if not overstock_df.empty:
                data_table(overstock_df.head(10))
            else:
                st.info("No overstock risk data available.")

    st.divider()
    st.markdown(
        "##### Management insight"
    )
    st.write(
        "Use these operational views to prioritize supplier follow-up, clear dead stock, and keep inventory availability aligned with demand." 
    )
