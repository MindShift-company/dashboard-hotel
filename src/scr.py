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
    It uses 'os.system' to run 'mindshift.py'. Adjust as needed.
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


def display_dashboard_analytics():
    st.title("Intelligent Dashboard Analytics")
    st.sidebar.title("MindShift")
    st.sidebar.write("Explore different analysis")

    # Corrected image path
    image_path = "/Applications/XAMPP/xamppfiles/htdocs/mywebsite/project/hotels/dashboard-hotel/src/mindshift.jpg"

    # Check if the image file exists before displaying it
    if os.path.exists(image_path):
        st.image(image_path, width=200)
    else:
        st.error(f"Error: Image file '{image_path}' not found. Please check the file path.")

    # File Upload
    uploaded_file = st.file_uploader("Upload your file (csv, txt, xlsx, xls)", type=["csv", "txt", "xlsx", "xls"])
    
    if uploaded_file:
        # Load data based on file type
        if uploaded_file.name.endswith(".csv") or uploaded_file.name.endswith(".txt"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        return data  # Corrected indentation issue
    else:
        st.warning("Please upload a file to proceed.")
        return None
