import pandas as pd
import streamlit as st
import itertools

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
        col1, col2, col3 = st.columns(3)
        with col1:
            tc_name = st.text_input(f"TC {i + 1} Name")
        with col2:
            tc_size = st.number_input(f"TC {i + 1} Size", min_value=0)
        with col3:
            tc_carico_minimo_tecnico= st.number_input(f"TC {i + 1} Carico minimo tecnico", min_value=0)
        if tc_name and tc_size:
            tc_data.append((tc_name, tc_size, tc_carico_minimo_tecnico))

    TC_df = pd.DataFrame(tc_data, columns=['Machine', 'Size','Carico minimo tecnico'])
    st.write("TC DataFrame:")
    st.dataframe(TC_df)

    # ELCO Data entry
    elco_data = []
    for i in range(int(n_elco)):
        col1, col2, col3 = st.columns(3)
        with col1:
            elco_name = st.text_input(f"ELCO {i + 1} Name")
        with col2:
            elco_size = st.number_input(f"ELCO {i + 1} Size", min_value=0)
        with col3:
            elco_carico_minimo_tecnico=st.number_input(f"ELCO {i + 1} Carico minimo tecnico", min_value=0)
        if elco_name and elco_size:
            elco_data.append((elco_name, elco_size, elco_carico_minimo_tecnico))

    ELCO_df = pd.DataFrame(elco_data, columns=['Machine', 'Size', 'Carico minimo tecnico'])
    st.write("ELCO DataFrame:")
    st.dataframe(ELCO_df)

    # Step 3: Function to generate specific combinations of ELCO and TC machines
    def generate_combinations(tc_data, elco_data):
        """Generate specific combinations of ELCO and TC machines."""
        assets = []

        # ELCO alone (single and multiple ELCOs)
        for r in range(1, len(elco_data) + 1):
            for combo in itertools.combinations(elco_data, r):
                assets.append(combo)

        # ELCO + TC combinations
        for elco_r in range(1, len(elco_data) + 1):
            for elco_combo in itertools.combinations(elco_data, elco_r):
                for tc_r in range(1, len(tc_data) + 1):
                    for tc_combo in itertools.combinations(tc_data, tc_r):
                        assets.append(elco_combo + tc_combo)

        return assets

    # Step 4: Generate asset combinations when the button is clicked
    if st.button("Generate Asset Combinations"):
        if not elco_data:
            st.error("Please enter ELCO data.")
        elif not tc_data:
            st.error("Please enter TC data.")
        else:
            assets = generate_combinations(tc_data, elco_data)

            # Step 5: Display asset combinations
            st.write(f"Total asset combinations generated: {len(assets)}")
            
            asset_list = []
            for idx, asset in enumerate(assets):
                asset_list.append({
                    'Combination': f"Asset Combination {idx + 1}",
                    'Machines': ' + '.join([f"{machine[0]} ({machine[1]} kW)" for machine in asset]),
                    'Total Power': sum([machine[1] for machine in asset])
                })
            
            asset_df = pd.DataFrame(asset_list)
            st.dataframe(asset_df)

            # Step 6: Option to download the asset combinations as CSV
            asset_csv = asset_df.to_csv(index=False)
            st.download_button(label="Download Asset Combinations CSV",
                               data=asset_csv,
                               file_name='asset_combinations.csv',
                               mime='text/csv')
