import pandas as pd
import streamlit as st
import itertools

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale")
st.sidebar.title("Functions")
# Function to handle machine input for TC carico fisso
import pandas as pd
import streamlit as st

def handle_machine_input_with_carico_fisso(n_tc):
    """Handles input for TC machines with fixed load."""
    tc_carico_fisso = []  # List to store TC machines with fixed load

    for i in range(n_tc):
        col1, col2 = st.columns(2)
        
        with col1:
            # Input for TC machine name
            tc_name = st.text_input(f"TC {i + 1} Name")
        
        with col2:
            # Input for TC machine size
            size = st.number_input(f"TC {i + 1} Size (kW)", min_value=0)
            # Input for minimum technical load
            min_load = st.number_input(f"TC {i + 1} Min Technical Load (%)", min_value=0, max_value=100)
            # Calculate fixed load based on the input
            fixed_load = size * (min_load / 100) if size > 0 else 0
        
        if tc_name and size:
            # Append the machine name and fixed load to the list
            tc_carico_fisso.append((tc_name, fixed_load))
    
    # Create and return a DataFrame from the collected data
    return pd.DataFrame(tc_carico_fisso, columns=['Machine', 'Size (kW) Carico Fisso'])



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
            min_load = min_load / 100
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


def assign_machine(power_hour, asset_combinations, elco_df, tc_df):
    """Assigns all possible machine combinations based on power demand."""
    
    assigned_combinations = []

    # Step 1: Check all combinations of ELCO machines
    elco_combinations = []
    for r in range(1, len(elco_df) + 1):
        for combo in itertools.combinations(elco_df.values, r):
            total_elco_power = sum(machine[1] for machine in combo)
            if total_elco_power >= power_hour:
                elco_combinations.append(combo)
    
    # Add ELCO combinations to assigned_combinations
    if elco_combinations:
        for combo in elco_combinations:
            assigned_combinations.append(' + '.join([machine[0] for machine in combo]))

    # Step 2: Check all combinations of ELCO + TC machines
    for asset in asset_combinations:
        total_power = sum(machine[1] for machine in asset)  # Calculate total power of the asset
        if total_power >= power_hour:
            assigned_combinations.append(' + '.join([machine[0] for machine in asset]))
    
    # Return all possible combinations that meet or exceed the power demand
    if assigned_combinations:
        return assigned_combinations

    return ['No suitable machine']  # Return if no combinations are found
 # If no suitable combination is found


# File handling and initial dataframe setup
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

    # Step 5: Input for number of merged DataFrames to create
    machine_columns = st.multiselect("Select machine columns", df.columns)
    dataframes = []

    # Group columns into sets of up to 4 and allow renaming
    if machine_columns:
        for i in range(0, len(machine_columns), 4):
            group = machine_columns[i:i + 4]
            if all(col in df.columns for col in group):
                group_df = df[group].copy()
                renamed_columns = [st.text_input(f"Rename column {col}:", value=col) for col in group]
                group_df.columns = renamed_columns
                dataframes.append(group_df)

                display_data_frame(group_df, f"DataFrame for renamed columns: {renamed_columns}")
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")

    if dataframes:
        num_merged_dfs = st.number_input("How many merged databases do you want to create?", min_value=1, max_value=len(dataframes))
        merged_dataframes = []
        
        # Loop through user input to merge DataFrames
        for merge_idx in range(int(num_merged_dfs)):
            st.write(f"### Merged Database {merge_idx + 1}")
            selected_dfs = st.multiselect(f"Select DataFrames to merge for Merged Database {merge_idx + 1}",
                                          options=range(len(dataframes)),
                                          format_func=lambda x: f"Group {x + 1}")

            if selected_dfs:
                dfs_to_merge = [dataframes[i] for i in selected_dfs]
                merged_df = pd.concat(dfs_to_merge, ignore_index=True)

                # Calculate 'Rapporto potenza assorbita/pot tot' if applicable
                if merged_df.shape[1] >= 3:
                    merged_df["Rapporto potenza assorbita/pot tot"] = merged_df.iloc[:, 1] / merged_df.iloc[:, 2]
                    merged_df["Fuel/Rapporto potenza assorbita"] = (merged_df.iloc[:, 3] * 1000) / merged_df.iloc[:, 1]

                    # Create classes for 'Rapporto potenza assorbita/pot tot'
                    merged_df['Class'] = pd.cut(
                        merged_df["Rapporto potenza assorbita/pot tot"] * 100,  # Convert to percentage
                        bins=[0, 30, 50, 70, 100],  # Define the ranges
                        labels=['0-30%', '30-50%', '50-70%', '70-100%'],  # Labels for the ranges
                        include_lowest=True
                    )

                # Group by 'Class' and calculate the mean for each class
                summary_df = merged_df.groupby('Class').agg(
                    Lim_inf=('Rapporto potenza assorbita/pot tot', lambda x: x.min() * 100),  # Lower limit of the class
                    Lim_sup=('Rapporto potenza assorbita/pot tot', lambda x: x.max() * 100),  # Upper limit of the class
                    Rapporto_fuel=('Fuel/Rapporto potenza assorbita', 'mean')  # Mean fuel ratio
                ).reset_index()  # Reset index for better display

                # Display summary DataFrame
                display_data_frame(summary_df, "Summary DataFrame")

    # Step 6: Assign machines based on power data
    if hours_data_column in df.columns:
        # Generate asset combinations again for assigning machines
        assets = generate_combinations(TC_df.values, ELCO_df.values)
        assigned_machines = df[hours_data_column].apply(lambda x: assign_machine(x, assets, ELCO_df, TC_df))
        df['assigned_machine'] = assigned_machines
        display_data_frame(df, "Assigned Machine DataFrame")

        # Option to download the DataFrame with assigned machines
        assigned_machine_csv = df.to_csv(index=False)
        st.download_button(label="Download Assigned Machine Data CSV",
                           data=assigned_machine_csv,
                           file_name='assigned_machines.csv',
                           mime='text/csv')
