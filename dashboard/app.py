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

# cd dashboard
# streamlit run app.py
# Tier 1 — straightforward, strong portfolio value, do these first

# Demand forecasting per product — predict next 7/30 days of sales per product using historical order data. Feeds directly off your rolling_7_30_day_sales_per_product data.
# Stockout risk classification — predict which products will run out of stock in the next N days, using current stock level + sales velocity + restock lead time. Natural extension of days_until_stockout.
# Reorder point / reorder quantity prediction — given sales velocity and supplier delay patterns, predict when and how much to reorder. Ties stock_turnover_rate_per_product + average_delay_days_per_supplier together.

# Tier 2 — customer-focused, needs the customers table

# Customer churn prediction — classify customers likely to stop ordering, based on recency/frequency of past orders (order_frequency_distribution is your starting point).
# Customer lifetime value (CLV) prediction — predict future spend per customer based on early order behavior.
# Next purchase category prediction — given a customer's order history, predict what category they're likely to buy next (useful for recommendations).

# Tier 3 — supplier/ops focused

# Supplier delay prediction — predict probability a given restock order will arrive late, based on that supplier's historical on-time rate and current order size/season.
# Warehouse demand allocation — predict which warehouse will see the highest order volume next month, to optimize stock distribution.

# Tier 4 — more advanced / stretch goals if you want to go further

# Price elasticity / optimal pricing signal — model how revenue responds to unit_price changes per product (needs price variation in your data, may not be available if prices are static in your dataset).
# Anomaly detection on order patterns — flag unusual spikes/drops in orders per product/day that might indicate fraud, data entry errors, or viral demand.