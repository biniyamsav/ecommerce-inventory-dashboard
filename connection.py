import psycopg2
import streamlit as st
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="your_db_name",
        user="your_user",
        password="your_password",
        port=5432
    )
# .\.venv\Scripts\activate.bat