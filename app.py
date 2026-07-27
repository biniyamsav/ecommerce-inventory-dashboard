import streamlit as st 
import plotly.express as px


def home_page():
    st.header("E-commerce inventory and performance dashboard")
    Analysis=st.button("Analysis")
    if Analysis:
            st.session_state.page = "Analysis"
            st.rerun()
    Management=st.button("Management")
    if Management:
        st.session_state.page = "Management"
        st.rerun()
    Predictive=st.button("Predictive")
    if Predictive:
        st.session_state.page = "Predictive"
        st.rerun()

def Analysis_page():
    st.header("Analysis page")
    page = st.sidebar.selectbox(
    "Select Page",
    ["Dashboard", "Sales", "Inventory", "Customers"]
    )

    if page == "Dashboard":
        st.title("Dashboard")

    elif page == "Sales":
        st.title("Sales Analytics")

    elif page == "Inventory":
        st.title("Inventory Analytics")

    elif page == "Customers":
        st.title("Customer Analytics")

    Home=st.button("Home")
    if Home:
        st.session_state.page = "Home"
        st.rerun()

def management_page():
    st.header("Management Page")
    Home=st.button("Home")
    if Home:
        st.session_state.page = "Home"
        st.rerun()

def Predictive_page():
    st.header("Predictive page")
    Home=st.button("Home")
    if Home:
        st.session_state.page = "Home"
        st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Management":
    management_page()
elif st.session_state.page=="Analysis":
    Analysis_page()
elif st.session_state.page=="Predictive":
    Predictive_page()


