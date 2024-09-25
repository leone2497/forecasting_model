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
            text_input = st.text_input(f"TC{j + 1}")
        with col2:
            num_input = st.number_input(f"TC{j + 1} Size", min_value=0)

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
            ELCO_text_input = st.text_input(f"ELCO {j + 1}")
        with col2:
            ELCO_num_input = st.number_input(f"ELCO {j + 1} Size", min_value=0)

        if ELCO_text_input and ELCO_num_input:  # Check for valid input
            elco_array.append((ELCO_text_input, ELCO_num_input))
                
    # Create a DataFrame for the ELCO inputs
    ELCO_df = pd.DataFrame(elco_array, columns=['Machine', 'Size'])
    st.write("ELCO DataFrame:")
    st.dataframe(ELCO_df)
    
    # Allow users to select machine columns
    machine_columns = st.multiselect("Select machine columns", df.columns)

    # Initialize a list to store DataFrames for groups of four
    dataframes = []

    if machine_columns:
        # Group selected columns into sets of four
        for group_index, i in enumerate(range(0, len(machine_columns), 4)):
            group = machine_columns[i:i + 4]  # Get the current group
            
            # Create a DataFrame for this group
            if all(col in df.columns for col in group):  # Check if all columns exist in df
                group_df = df[group]
                dataframes.append(group_df)
                
                # Display the DataFrame for the current group
                st.write(f"DataFrame for columns: {group}")
                st.dataframe(group_df)
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")
    
    # Input widget to specify the number of times to perform the concatenation
    num_concat_times = st.number_input("Enter the number of times to concatenate", min_value=1, value=1)

    # Multiselect widget to choose DataFrames to concatenate
    selected_dfs = st.multiselect("Select DataFrames to concatenate", [f"Group {i + 1}" for i in range(len(dataframes))])

    if selected_dfs:
        # Concatenate the selected DataFrames vertically the specified number of times
        dfs_to_concat = [dataframes[int(i.split()[1]) - 1] for i in selected_dfs]
        concatenated_df = pd.concat(dfs_to_concat, axis=0)
        
        # Repeat the concatenation the specified number of times
        for _ in range(num_concat_times - 1):
            concatenated_df = pd.concat([concatenated_df] + dfs_to_concat, axis=0)
        
        # Display the concatenated DataFrame
        st.write("Concatenated DataFrame:")
        st.dataframe(concatenated_df)

        # Visualization of the concatenated DataFrame
        st.subheader("Visualization of Concatenated DataFrame")
        if concatenated_df.shape[1] > 1:  # Ensure there is data to plot
            plot_column = st.selectbox("Select a column to plot", concatenated_df.columns)
            plt.figure(figsize=(10, 6))
            plt.plot(concatenated_df.index, concatenated_df[plot_column], marker='o')
            plt.title(f"Plot of {plot_column}")
            plt.xlabel("Index")
            plt.ylabel(plot_column)
            st.pyplot(plt)

        # Download button for the concatenated DataFrame
        csv = concatenated_df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name='concatenated_data.csv', mime='text/csv')
