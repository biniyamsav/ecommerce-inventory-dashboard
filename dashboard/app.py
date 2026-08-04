import streamlit as st

from utils.styles import inject_custom_css
from components.sidebar import render_sidebar

from app_pages.home import home_page
from app_pages.analysis import analysis_page
from app_pages.sales import sales_page
from app_pages.products import products_page
from app_pages.customers import customers_page
from app_pages.inventory import inventory_page
from app_pages.warehouse import warehouse_page
from app_pages.suppliers import suppliers_page
from app_pages.predictive import predictive_page
from app_pages.management import management_page

st.set_page_config(
    page_title="E-commerce Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

PAGES = {
    "Home": home_page,
    "Analysis": analysis_page,
    "Sales": sales_page,
    "Products": products_page,
    "Customers": customers_page,
    "Inventory": inventory_page,
    "Warehouse": warehouse_page,
    "Suppliers": suppliers_page,
    "Predictive": predictive_page,
    "Management": management_page,
}

if "sidebar_nav" not in st.session_state:
    st.session_state.sidebar_nav = "Home"

render_sidebar(PAGES)

# call the selected page
selection = st.session_state.get("sidebar_nav", "Home")
PAGES[selection]()

