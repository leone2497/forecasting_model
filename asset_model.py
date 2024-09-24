import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import easyocr
import numpy as np
from glob import glob 
from PIL import Image

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale to be")
st.sidebar.title("Functions")

# File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

if file_to_analyze is not None:
    # Read the file based on its extension
    if file_to_analyze.name.endswith('.csv'):
        df = pd.read_csv(file_to_analyze)
    else:
        df = pd.read_excel(file_to_analyze, engine="openpyxl")
    
    # Display columns and DataFrame
    st.write("Available columns:", df.columns.tolist())
    st.write(df)

    # Sidebar selections for power and date-time columns
    hours_data = st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    time_column = st.sidebar.selectbox("Indicate the date time column", df.columns.tolist())
    
    # Allow users to select machine columns
    machine_columns = st.multiselect("Select machine columns", df.columns)

    # Initialize dictionary to store DataFrames
    machine_dfs = {}

    if machine_columns:
        for machine_col in machine_columns:
            # Create a power column name based on the selected machine column
            power_col = f"{machine_col}_power" if f"{machine_col}_power" in df.columns else None
            
            # Create DataFrame for the machine and its power column (if exists)
            if power_col:
                machine_dfs[machine_col] = df[[machine_col, power_col]]
                st.write(f"Data for machine: {machine_col} and power: {power_col}")
            else:
                machine_dfs[machine_col] = df[[machine_col]]
                st.write(f"Data for machine: {machine_col} (no power column found)")

            # Display the created DataFrame
            st.dataframe(machine_dfs[machine_col])
