import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
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
    try:
        if file_to_analyze.name.endswith('.csv'):
            df = pd.read_csv(file_to_analyze)
        else:
            df = pd.read_excel(file_to_analyze, engine="openpyxl")
        
        # Display columns and DataFrame
        st.write("Available columns:", df.columns.tolist())
        st.write("Preview of DataFrame:")
        st.dataframe(df.head())
    
    except Exception as e:
        st.error(f"Error reading the file: {e}")

    # Sidebar selections for power and date-time columns
    hours_data = st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    time_column = st.sidebar.selectbox("Indicate the date time column", df.columns.tolist())

    # Input for number of machines
    n_rows = st.number_input("Enter number of TC", min_value=1)
    ELCO_rows = st.number_input("Enter number of ELCO", min_value=1)

    # Initialize the input arrays for machine names and sizes
    input_array = []
    elco_array = []
    
    # Generate the grid for TC inputs
    for j in range(int(n_rows)):
        col1, col2 = st.columns(2)  # Create two columns
        with col1:
            text_input = st.text_input(f"TC {j + 1} Name")
        with col2:
            num_input = st.number_input(f"TC {j + 1} Size", min_value=0)

        if text_input and num_input:  # Check for valid input
            input_array.append((text_input, num_input))
                
    # Create a DataFrame for the TC inputs
    TC_df = pd.DataFrame(input_array, columns=['Machine', 'Size'])
    st.write("TC DataFrame:")
    st.dataframe(TC_df)

    # Generate the grid for ELCO inputs
    for j in range(int(ELCO_rows)):
        col1, col2 = st.columns(2)  # Create two columns
        with col1:
            ELCO_text_input = st.text_input(f"ELCO {j + 1} Name")
        with col2:
            ELCO_num_input = st.number_input(f"ELCO {j + 1} Size", min_value=0)

        if ELCO_text_input and ELCO_num_input:  # Check for valid input
            elco_array.append((ELCO_text_input, ELCO_num_input))
                
    # Create a DataFrame for the ELCO inputs
    ELCO_df = pd.DataFrame(elco_array, columns=['Machine', 'Size'])
    st.write("ELCO DataFrame:")
    st.dataframe(ELCO_df)
    
    # Store the DataFrames in a dictionary
    dataframes_dict = {
        "TC": TC_df,
        "ELCO": ELCO_df,
    }

    # Allow users to select DataFrames to merge
    selected_dfs = st.multiselect("Select DataFrames to merge", list(dataframes_dict.keys()))

    if selected_dfs:
        # Concatenate the selected DataFrames
        dfs_to_concat = [dataframes_dict[df] for df in selected_dfs]
        merged_df = pd.concat(dfs_to_concat, ignore_index=True)
        
        # Display the merged DataFrame
        st.write("Merged DataFrame:")
        st.dataframe(merged_df)

        # Optionally, provide a download button for the merged DataFrame
        csv = merged_df.to_csv(index=False)
        st.download_button(label="Download Merged CSV", data=csv, file_name='merged_data.csv', mime='text/csv')
