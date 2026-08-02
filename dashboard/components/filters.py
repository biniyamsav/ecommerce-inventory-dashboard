import streamlit as st


def date_filter(label, start_date, end_date):
    return st.date_input(label, [start_date, end_date])
