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

    # Initialize group index
    group_index = 0

    # Input for number of machines
    n_rows = st.number_input(f"Enter number of machines for group {group_index+1}", min_value=1, key=f"n_rows_{group_index}")

    # Initialize the input array for machine names and sizes
    input_array = []
                
    # Generate the grid: left column for text, right column for numbers
    for j in range(int(n_rows)):
        col1, col2 = st.columns(2)  # Create two columns
        with col1:
            text_input = st.text_input(f"Machine input {j+1} for group {group_index+1}", key=f"machine_text_{group_index}_{j}")
        with col2:
            num_input = st.number_input(f"Size input {j+1} for group {group_index+1}", key=f"machine_num_{group_index}_{j}")
                    
        # Store the inputs as a tuple in the array
        input_array.append((text_input, num_input))
                
    # Create a DataFrame for the machine inputs
    machine_df = pd.DataFrame(input_array, columns=['Machine', 'Size'])
                
    # Display the DataFrame of machines and sizes
    st.write("Machine DataFrame:")
    st.dataframe(machine_df)
    
    # Allow users to select machine columns
    machine_columns = st.multiselect("Select machine columns", df.columns)

    # Initialize a list to store DataFrames for groups of four
    dataframes = []

    if machine_columns:
        # Group selected columns into sets of four
        for group_index, i in enumerate(range(0, len(machine_columns), 4)):
            group = machine_columns[i:i + 4]  # Get the current group of columns
            
            # Create a DataFrame for this group
            if all(col in df.columns for col in group):  # Check if all columns exist in df
                group_df = df[group]
                dataframes.append(group_df)
                
                # Display the DataFrame for the current group
                st.write(f"DataFrame for columns: {group}")
                st.dataframe(group_df)
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")
    
    # Multiselect widget to choose DataFrames to concatenate
    selected_dfs = st.multiselect("Select DataFrames to concatenate", [f"Group {i+1}" for i in range(len(dataframes))])

    if selected_dfs:
        # Concatenate the selected DataFrames
        dfs_to_concat = [dataframes[int(i.split()[1])-1] for i in selected_dfs]
        concatenated_df = pd.concat(dfs_to_concat, axis=1)
        
        # Display the concatenated DataFrame
        st.write("Concatenated DataFrame:")
        st.dataframe(concatenated_df)
