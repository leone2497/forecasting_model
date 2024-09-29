import pandas as pd
import streamlit as st
import itertools

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale")
st.sidebar.title("Functions")

# Function to handle machine input for TC and ELCO
def handle_machine_input(machine_type, n):
    """Handles input for TC or ELCO machines."""
    data = []
    for i in range(n):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"{machine_type} {i + 1} Name")
        with col2:
            size = st.number_input(f"{machine_type} {i + 1} Size (kW)", min_value=0)
        with col3:
            min_load = st.number_input(f"{machine_type} {i + 1} Min Technical Load (%)", min_value=0, max_value=100)
            min_load = min_load / 100  # Convert to a decimal
        if name and size:
            data.append((name, size, min_load))
    return pd.DataFrame(data, columns=['Machine', 'Size (kW)', 'Min Technical Load (%)'])

# Function to display a DataFrame
def display_data_frame(df, title):
    """Display a DataFrame with a title."""
    st.write(title)
    st.dataframe(df)

# Step 1: File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# Function to assign machines based on power demand and asset combinations
# Function to assign machines based on power demand and asset combinations
def assign_machine(power_hour, elco_df, tc_df=None):
    try:
        # Step 1: Attempt to meet power demand with only ELCO machines
        suitable_elco = elco_df[elco_df['Size (kW)'] >= power_hour]
        if not suitable_elco.empty:
            # Return the ELCO machine(s) that meet the power demand
            return ' + '.join(suitable_elco['Machine'].tolist())
        
        # Step 2: If no ELCO machine(s) can meet the demand, try ELCO + TC combinations
        for tc_idx, tc_row in tc_df.iterrows():
            for elco_idx, elco_row in elco_df.iterrows():
                total_power = elco_row['Size (kW)'] + tc_row['Size (kW)']
                if total_power >= power_hour:
                    return f"{elco_row['Machine']} + {tc_row['Machine']}"

        return "No suitable machine"  # If no combination is found
    except Exception as e:
        st.error(f"Error in assign_machine: {e}")
        return None


# File handling and initial DataFrame setup
df = None
if file_to_analyze is not None:
    try:
        if file_to_analyze.name.endswith('.csv'):
            df = pd.read_csv(file_to_analyze)
        else:
            df = pd.read_excel(file_to_analyze, engine="openpyxl")
        
        st.write("Available columns:", df.columns.tolist())
        st.write("Preview of DataFrame:")
        st.dataframe(df.head())
    
    except Exception as e:
        st.error(f"Error reading the file: {e}")

# Proceed only if a DataFrame has been uploaded
if df is not None:
    hours_data_column = st.sidebar.selectbox("Select the power column", df.columns.tolist())
    time_column = st.sidebar.selectbox("Select the date-time column", df.columns.tolist())

    # Step 2: Handle user input for TC and ELCO data entry
    st.sidebar.write("Enter TC and ELCO Data:")
    n_tc = st.number_input("Enter number of TC", min_value=1, value=1)
    n_elco = st.number_input("Enter number of ELCO", min_value=1, value=1)

    TC_df = handle_machine_input("TC", n_tc)
    ELCO_df = handle_machine_input("ELCO", n_elco)

    # Display the input DataFrames
    display_data_frame(TC_df, "TC DataFrame:")
    display_data_frame(ELCO_df, "ELCO DataFrame:")

    # Step 3: Generate asset combinations (ELCO and TC)
    def generate_combinations(tc_data, elco_data):
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
        if ELCO_df.empty:
            st.error("Please enter ELCO data.")
        elif TC_df.empty:
            st.error("Please enter TC data.")
        else:
            assets = generate_combinations(TC_df.values, ELCO_df.values)

            st.write(f"Total asset combinations generated: {len(assets)}")
            asset_list = []
            for idx, asset in enumerate(assets):
                asset_list.append({
                    'Combination': f"Asset Combination {idx + 1}",
                    'Machines': ' + '.join([f"{machine[0]} ({machine[1]} kW)" for machine in asset]),
                    'Total Power (kW)': sum([machine[1] for machine in asset])
                })
            
            asset_df = pd.DataFrame(asset_list)
            display_data_frame(asset_df, "Asset Combinations")

            # Option to download the asset combinations as CSV
            asset_csv = asset_df.to_csv(index=False)
            st.download_button(label="Download Asset Combinations CSV",
                               data=asset_csv,
                               file_name='asset_combinations.csv',
                               mime='text/csv')

    # Step 5: Assign machines based on power data
    if hours_data_column in df.columns:
        assets = generate_combinations(TC_df.values, ELCO_df.values)
        assigned_machines = df[hours_data_column].apply(lambda x: assign_machine(x, assets, ELCO_df, TC_df))
        df['assigned_machine'] = assigned_machines
        display_data_frame(df, "Assigned Machine DataFrame")

        # Option to download the DataFrame with assigned machines
        assigned_machine_csv = df.to_csv(index=False)
        st.download_button(label="Download Assigned Machine DataFrame CSV",
                           data=assigned_machine_csv,
                           file_name='assigned_machine_data.csv',
                           mime='text/csv')
