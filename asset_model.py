import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale to be")
st.sidebar.title("Functions")

# File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# Step 1: Handle the uploaded file
if file_to_analyze is not None:
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

# Step 2: Handle user input for TC and ELCO
st.sidebar.write("Enter TC and ELCO Data:")

# Input for number of machines
n_rows = st.number_input("Enter number of TC", min_value=1)
ELCO_rows = st.number_input("Enter number of ELCO", min_value=1)

# Initialize input arrays for machine names and sizes
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

# Step 4: Handle selection of columns from the uploaded file (df)
if file_to_analyze is not None:
    machine_columns = st.multiselect("Select machine columns", df.columns)

    dataframes = []
    
    if machine_columns:
        for i in range(0, len(machine_columns), 4):
            group = machine_columns[i:i + 4]  # Get the current group of up to 4 columns
            
            if all(col in df.columns for col in group):  # Check if all columns exist in df
                group_df = df[group].copy()  # Copy the DataFrame to avoid SettingWithCopyWarning
                dataframes.append(group_df)

                # Rename columns based on user input
                renamed_columns = []
                for col in group:
                    new_col_name = st.text_input(f"Enter a new name for column {col}:", value=col)
                    renamed_columns.append(new_col_name)
                
                group_df.columns = renamed_columns  # Assign new column names
                
                # Display the DataFrame for the current group with renamed columns
                st.write(f"DataFrame for renamed columns: {renamed_columns}")
                st.dataframe(group_df)
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")

# Step 5: Input for the number of merged DataFrames to create
if dataframes:
    num_merged_dfs = st.number_input("How many merged databases do you want to create?", min_value=1, max_value=len(dataframes))

    # Loop to allow users to select which dataframes to merge for each merged dataset
    merged_dataframes = []
    for merge_idx in range(int(num_merged_dfs)):
        st.write(f"### Merged Database {merge_idx + 1}")
        selected_dfs = st.multiselect(f"Select DataFrames to merge for Merged Database {merge_idx + 1}", options=range(len(dataframes)), format_func=lambda x: f"Group {x + 1}")
        
        if selected_dfs:
            dfs_to_merge = [dataframes[i] for i in selected_dfs]
            merged_df = pd.concat(dfs_to_merge, ignore_index=True)
            
            # Display the merged DataFrame
            st.write(f"Merged DataFrame {merge_idx + 1}:")
            st.dataframe(merged_df)
            
            merged_dataframes.append(merged_df)
            merged_dataframes["Rapporto potenza assorbita/pot tot"]=merge_dataframes[1]/merge_dataframes[2]
            st.dataframe(merged_dataframes)

    # Option to download each merged DataFrame
    for idx, merged_df in enumerate(merged_dataframes):
        csv = merged_df.to_csv(index=False)
        st.download_button(label=f"Download Merged CSV {idx + 1}", data=csv, file_name=f'merged_data_{idx + 1}.csv', mime='text/csv')
