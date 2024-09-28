import pandas as pd
import streamlit as st

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale to be")
st.sidebar.title("Functions")

# Step 1: File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

df = None
if file_to_analyze is not None:
    try:
        # Read the uploaded file into a DataFrame
        if file_to_analyze.name.endswith('.csv'):
            df = pd.read_csv(file_to_analyze)
        else:
            df = pd.read_excel(file_to_analyze, engine="openpyxl")
        
        # Display available columns and the DataFrame
        st.write("Available columns:", df.columns.tolist())
        st.write("Preview of DataFrame:")
        st.dataframe(df.head())
    
    except Exception as e:
        st.error(f"Error reading the file: {e}")

# Check if a DataFrame has been uploaded before proceeding
if df is not None:
    # Sidebar selections for power and date-time columns
    hours_data = st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    time_column = st.sidebar.selectbox("Indicate the date time column", df.columns.tolist())

    # Step 2: Handle user input for TC and ELCO data entry
    st.sidebar.write("Enter TC and ELCO Data:")

    # Input for number of machines (TC and ELCO)
    n_tc = st.number_input("Enter number of TC", min_value=1)
    n_elco = st.number_input("Enter number of ELCO", min_value=1)

    # TC Data entry
    tc_data = []
    for i in range(int(n_tc)):
        col1, col2 = st.columns(2)
        with col1:
            tc_name = st.text_input(f"TC {i + 1} Name")
        with col2:
            tc_size = st.number_input(f"TC {i + 1} Size", min_value=0)
        if tc_name and tc_size:
            tc_data.append((tc_name, tc_size))

    TC_df = pd.DataFrame(tc_data, columns=['Machine', 'Size'])
    st.write("TC DataFrame:")
    st.dataframe(TC_df)

    # ELCO Data entry
    elco_data = []
    for i in range(int(n_elco)):
        col1, col2 = st.columns(2)
        with col1:
            elco_name = st.text_input(f"ELCO {i + 1} Name")
        with col2:
            elco_size = st.number_input(f"ELCO {i + 1} Size", min_value=0)
        if elco_name and elco_size:
            elco_data.append((elco_name, elco_size))

    ELCO_df = pd.DataFrame(elco_data, columns=['Machine', 'Size'])
    st.write("ELCO DataFrame:")
    st.dataframe(ELCO_df)

    # Step 3: Define the asset generation logic
    def create_assets(required_power, tc_data, elco_data):
        """Function to create assets based on required power using ELCO and TC."""
        total_elco_power = sum([elco[1] for elco in elco_data])  # Sum of ELCO sizes
        
        # Start by using ELCOs
        assets = []
        current_power = 0
        
        # Add ELCOs first
        for elco in elco_data:
            if current_power + elco[1] <= required_power:
                assets.append(elco)
                current_power += elco[1]
        
        # If power is not sufficient, add TCs
        if current_power < required_power:
            for tc in tc_data:
                if current_power + tc[1] <= required_power:
                    assets.append(tc)
                    current_power += tc[1]
                if current_power >= required_power:
                    break
        
        return assets, current_power
    
    # Step 4: Input for required power and generate asset combinations
    required_power = st.number_input("Enter required power", min_value=1)
    
    if st.button("Generate Asset Combinations"):
        assets, final_power = create_assets(required_power, tc_data, elco_data)
        
        st.write(f"Asset combination to meet the required power ({required_power}):")
        asset_df = pd.DataFrame(assets, columns=['Machine', 'Size'])
        st.dataframe(asset_df)
        
        st.write(f"Total generated power: {final_power}")

    # Step 5: Option to download the asset combination
    if assets:
        asset_csv = asset_df.to_csv(index=False)
        st.download_button(label="Download Asset CSV",
                           data=asset_csv,
                           file_name='asset_combination.csv',
                           mime='text/csv')
