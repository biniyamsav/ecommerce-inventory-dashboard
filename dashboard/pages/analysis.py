import streamlit as st

from components import db
from components.metric_cards import metric_card
from utils.helpers import first_value, to_float, safe_rerun


@st.cache_data(ttl=600)
def load_analysis_metrics():
    total_revenue = db.revenue_per_month_last_12_months()
    top_category = db.top_revenue_category()
    top_region = db.top_revenue_region()
    avg_order_value = db.average_order_value()

    revenue = 0.0
    if total_revenue:
        revenue = sum(float(row[1]) for row in total_revenue if row[1] is not None)

    return {
        "revenue": revenue,
        "avg_order_value": to_float(first_value(avg_order_value, 0, 0)),
        "top_category": str(first_value(top_category, 0, "N/A")).strip(),
        "top_region": str(first_value(top_region, 0, "N/A")).strip(),
    }


def _navigate(target: str):
    st.session_state.sidebar_nav = target
    safe_rerun()


def analysis_page():
    st.title("Analysis")
    st.markdown(
        "##### Focused analytics for sales, product performance, customer behavior, inventory health, warehouse operations, and supplier reliability."
    )

    nav_cols = st.columns([1, 1, 1, 1])
    with nav_cols[0]:
        st.button("Home", on_click=_navigate, args=("Home",), use_container_width=True)
    with nav_cols[1]:
        st.button("Sales", on_click=_navigate, args=("Sales",), use_container_width=True)
    with nav_cols[2]:
        st.button("Products", on_click=_navigate, args=("Products",), use_container_width=True)
    with nav_cols[3]:
        st.button("Customers", on_click=_navigate, args=("Customers",), use_container_width=True)

    metrics = load_analysis_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("12-mo revenue", f"${metrics['revenue']:,.0f}")
    with c2:
        metric_card("Avg order value", f"${metrics['avg_order_value']:,.2f}")
    with c3:
        metric_card("Top category", metrics["top_category"])
    with c4:
        metric_card("Top region", metrics["top_region"])

    st.divider()
    st.markdown("### Select an analysis dashboard")

    cols = st.columns(3)
    buttons = [
        ("Sales", "Core sales performance and revenue trends."),
        ("Products", "Product margin and SKU performance insights."),
        ("Customers", "Customer spend and retention behavior."),
        ("Inventory", "Stock health and turnover visibility."),
        ("Warehouse", "Fulfillment and warehouse operations metrics."),
        ("Suppliers", "Supplier reliability and delivery performance."),
    ]

    for idx, (label, description) in enumerate(buttons):
        col = cols[idx % 3]
        with col:
            st.markdown(
                f"""
                <div class='nav-card'>
                    <h3>{label}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(f"Open {label}", on_click=_navigate, args=(label,), use_container_width=True)

    st.divider()
    st.markdown(
        """
        #### Why this matters
        The analysis section provides direct access to the dashboards that drive daily business decisions. Use it to monitor revenue momentum, product portfolio health, customer lifetime value, inventory risk, and supplier performance.
        """
    )
