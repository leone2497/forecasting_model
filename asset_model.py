import pandas as pd
import streamlit as st
import itertools

# Set up the Streamlit app
st.title("Modello forecast degli assetti di centrale to be")
st.sidebar.title("Functions")

# Step 1: File uploader for CSV or Excel files
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# Function to assign machine based on power requirement
def assign_machine(power_hour, machines):
    # Check which machines can satisfy the power requirement
    suitable_machine = machines[machines['power_capacity'] >= power_hour]
    if not suitable_machine.empty:
        # Return the first suitable machine (smallest one that can handle the power)
        return suitable_machine.iloc[0]['machine']
    return 'No suitable machine'

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
    hours_data_column = st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
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

    # Combine ELCO and TC machines into a single DataFrame
    asset_df = pd.concat([TC_df[['Machine', 'Size (kW)']], ELCO_df[['Machine', 'Size (kW)']]])
    asset_df.rename(columns={'Size (kW)': 'power_capacity'}, inplace=True)

    # Step 3: Generate asset combinations (already handled in your code)

    # Step 4: Assign machine based on power requirements
    if hours_data_column:
        df['assigned_machine'] = df[hours_data_column].apply(lambda x: assign_machine(x, asset_df))

        st.write("Updated DataFrame with Assigned Machines:")
        st.dataframe(df)

        # Step 5: Option to download the updated DataFrame with machine assignments
        csv_output = df.to_csv(index=False)
        st.download_button(label="Download Updated Data with Machines",
                           data=csv_output,
                           file_name='updated_data_with_machines.csv',
                           mime='text/csv')
