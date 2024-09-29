import pandas as pd
import streamlit as st
import itertools

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale")
st.sidebar.title("Functions")

# Step 1: File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# Function to assign machines based on power demand
def assign_machine(power_hour, machines):
    suitable_machine = machines[machines['Size (kW)'] >= power_hour]
    if not suitable_machine.empty:
        return suitable_machine.iloc[0]['Machine']
    return 'No suitable machine'

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
            tc_size = st.number_input(f"TC {i + 1} Size (kW)", min_value=0)
        with col3:
            tc_carico_minimo_tecnico = st.number_input(f"TC {i + 1} Carico minimo tecnico (%)", min_value=0, max_value=100)
        if tc_name and tc_size:
            tc_data.append((tc_name, tc_size, tc_carico_minimo_tecnico))

    TC_df = pd.DataFrame(tc_data, columns=['Machine', 'Size (kW)', 'Carico minimo tecnico (%)'])
    st.write("TC DataFrame:")
    st.dataframe(TC_df)

    # ELCO Data entry
    elco_data = []
    for i in range(int(n_elco)):
        col1, col2, col3 = st.columns(3)
        with col1:
            elco_name = st.text_input(f"ELCO {i + 1} Name")
        with col2:
            elco_size = st.number_input(f"ELCO {i + 1} Size (kW)", min_value=0)
        with col3:
            elco_carico_minimo_tecnico = st.number_input(f"ELCO {i + 1} Carico minimo tecnico (%)", min_value=0, max_value=100)
        if elco_name and elco_size:
            elco_data.append((elco_name, elco_size, elco_carico_minimo_tecnico))

    ELCO_df = pd.DataFrame(elco_data, columns=['Machine', 'Size (kW)', 'Carico minimo tecnico (%)'])
    st.write("ELCO DataFrame:")
    st.dataframe(ELCO_df)

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
        if not elco_data:
            st.error("Please enter ELCO data.")
        elif not tc_data:
            st.error("Please enter TC data.")
        else:
            assets = generate_combinations(tc_data, elco_data)

            st.write(f"Total asset combinations generated: {len(assets)}")
            asset_list = []
            for idx, asset in enumerate(assets):
                asset_list.append({
                    'Combination': f"Asset Combination {idx + 1}",
                    'Machines': ' + '.join([f"{machine[0]} ({machine[1]} kW)" for machine in asset]),
                    'Total Power (kW)': sum([machine[1] for machine in asset])
                })
            
            asset_df = pd.DataFrame(asset_list)
            st.dataframe(asset_df)

            # Option to download the asset combinations as CSV
            asset_csv = asset_df.to_csv(index=False)
            st.download_button(label="Download Asset Combinations CSV",
                               data=asset_csv,
                               file_name='asset_combinations.csv',
                               mime='text/csv')

# The following part (machine columns selection and merging) should be separate from the asset generation logic:
if file_to_analyze is not None and df is not None:
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

                st.write(f"DataFrame for renamed columns: {renamed_columns}")
                st.dataframe(group_df)
            else:
                st.warning(f"Some columns in the group {group} do not exist in the DataFrame.")

# Step 5: Input for number of merged DataFrames to create
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
            st.write("Summary DataFrame:")
            st.dataframe(summary_df)
