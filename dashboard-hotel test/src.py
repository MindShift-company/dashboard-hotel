# scr.py

# All library imports
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import timedelta
import os

def run_streamlit_main():
    """
    If you want to auto-run Streamlit from this file, you can call this function.
    It uses 'os.system' to run 'main.py' (or mindshift.py). Adjust as needed.
    """
    os.system("streamlit run mindshift.py --server.address localhost")

def login():
    """Simple Streamlit login form."""
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        # Replace with secure authentication in production
        if username == "hamza" and password == "dream123":
            st.session_state["logged_in"] = True
        else:
            st.sidebar.error("Invalid username or password")

def add_contact_message():
    """Displays your contact message in the sidebar."""
    st.sidebar.write("For inquiries, contact us at htssociete@hotmail.com.")
