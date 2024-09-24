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
        # Group selected columns into sets of three
        for i in range(0, len(machine_columns), 3):
            group = machine_columns[i:i + 3]  # Get the current group of three columns
            
            # Create a DataFrame for this group
            if all(col in df.columns for col in group):  # Check if all columns exist in df
                group_df = df[group]
                dataframes.append(group_df)
                
                # Display the DataFrame for the current group
                st.write(f"DataFrame for columns: {group}")
                st.dataframe(group_df)
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")
            # Display the created DataFrame
            st.dataframe(machine_dfs[machine_col])
