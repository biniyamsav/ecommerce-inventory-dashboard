import streamlit as st
from utils.helpers import safe_rerun


def _nav_button(label, display_name, current):
    """Render one nav button; highlight if active."""
    is_active = current == label
    if st.sidebar.button(
        display_name,
        key=f"sb_{label}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.sidebar_nav = label
        safe_rerun()


def render_sidebar(pages):
    """Render a three-zone sidebar: Analysis, Management, Predictive — plus Home."""
    current = st.session_state.get("sidebar_nav", "Home")

    st.sidebar.markdown("### E-commerce Analytics")

    _nav_button("Home", "Home", current)

    st.sidebar.markdown("---")

    st.sidebar.markdown("**Analysis**")
    for label in ["Sales", "Products", "Customers"]:
        if label in pages:
            _nav_button(label, label, current)

    st.sidebar.markdown("---")

    st.sidebar.markdown("**Management**")
    for label in ["Inventory", "Warehouse", "Suppliers"]:
        if label in pages:
            _nav_button(label, label, current)

    st.sidebar.markdown("---")

    st.sidebar.markdown("**Predictive**")
    if "Predictive" in pages:
        _nav_button("Predictive", "Predictive", current)