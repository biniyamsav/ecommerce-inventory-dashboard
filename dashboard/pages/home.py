import streamlit as st
import pandas as pd

from components import db
from components.charts import line_chart
from components.metric_cards import metric_card
from utils.helpers import first_value, to_float, safe_rerun


@st.cache_data(ttl=600)
def load_summary_metrics():
    revenue_rows = db.revenue_per_month_last_12_months()
    category_rows = db.top_revenue_category()
    avg_order_rows = db.average_order_value()
    new_customer_rows = db.new_customers_last_month()

    revenue_df = pd.DataFrame(revenue_rows, columns=["month", "revenue"])
    if not revenue_df.empty:
        revenue_df["month"] = pd.to_datetime(revenue_df["month"])
        revenue_df["revenue"] = revenue_df["revenue"].astype(float)

    return {
        "revenue_df": revenue_df,
        "avg_order_value": to_float(first_value(avg_order_rows, 0, 0)),
        "top_category": str(first_value(category_rows, 0, "N/A")).strip(),
        "top_category_revenue": to_float(first_value(category_rows, 1, 0)),
        "new_customers": int(first_value(new_customer_rows, 0, 0)),
    }


def _navigate(target: str):
    st.session_state.sidebar_nav = target
    safe_rerun()


def home_page():
    st.markdown(
        """
        <div class='hero-panel'>
            <div class='hero-copy'>
                <div class='hero-eyebrow'>E-commerce analytics</div>
                <div class='hero-title'>Inventory, performance, and supplier intelligence in one modern dashboard.</div>
                <div class='hero-text'>Navigate revenue momentum, inventory risk, stockout forecasts, and supplier reliability with a clean analytics home page designed for operational leaders.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = load_summary_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "12-mo revenue",
            f"${metrics['revenue_df']['revenue'].sum():,.0f}" if not metrics["revenue_df"].empty else "$0",
        )
    with c2:
        metric_card("Avg order value", f"${metrics['avg_order_value']:,.2f}")
    with c3:
        metric_card("New customers", f"{metrics['new_customers']}")
    with c4:
        metric_card(
            "Top revenue category",
            metrics["top_category"],
            delta=f"${metrics['top_category_revenue']:,.0f}",
        )

    st.divider()
    st.markdown("### Start smart")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class='nav-card'>
                <h3>Analysis</h3>
                <p>Open the full analytics hub for sales, product, customer, inventory, warehouse, and supplier performance.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Explore analysis", on_click=_navigate, args=("Analysis",), use_container_width=True)

    with col2:
        st.markdown(
            """
            <div class='nav-card'>
                <h3>Predictive</h3>
                <p>See forecasted stockouts, supplier trend signals, and inventory pressure before the next buying cycle.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Explore predictive", on_click=_navigate, args=("Predictive",), use_container_width=True)

    with col3:
        st.markdown(
            """
            <div class='nav-card'>
                <h3>Management</h3>
                <p>Track operational action items from supplier delays to out-of-stock and overstock attention.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Explore management", on_click=_navigate, args=("Management",), use_container_width=True)

    st.divider()
    st.subheader("Revenue trend")
    if not metrics["revenue_df"].empty:
        fig = line_chart(
            metrics["revenue_df"],
            x="month",
            y="revenue",
            title="Revenue trend over the last 12 months",
            height=420,
            labels={"month": "Month", "revenue": "Revenue ($)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Revenue data is not available yet.")

    st.divider()
    highlight_cols = st.columns(3)
    with highlight_cols[0]:
        st.markdown("**Customer growth**")
        st.write("Track adoption with new customer volume and retention signals.")
    with highlight_cols[1]:
        st.markdown("**Operational readiness**")
        st.write("Monitor inventory and stockout risk before it impacts demand.")
    with highlight_cols[2]:
        st.markdown("**Revenue pulse**")
        st.write("See the high-level financial momentum driving decision-making.")
