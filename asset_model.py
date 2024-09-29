import pandas as pd
import streamlit as st

# Assuming TC_df and ELCO_df are defined earlier in your code
asset_df = pd.concat([TC_df, ELCO_df])

# Step 6: Assign machines based on power data
if hours_data_column in df.columns:
    try:
        # Assign machines based on hours data
        df['assigned_machine'] = df[hours_data_column].apply(lambda x: assign_machine(x, asset_df))
        
        # Display the DataFrame with assigned machines
        st.write("Assigned Machine DataFrame:")
        st.dataframe(df)
        
        # Check if any machines were assigned
        if df['assigned_machine'].isnull().all():
            st.warning("No machines were assigned based on the provided data.")
        
        # Option to download the DataFrame with assigned machines
        assigned_machine_csv = df.to_csv(index=False)
        st.download_button(
            label="Download Data with Assigned Machines",
            data=assigned_machine_csv,
            file_name='assigned_machines.csv',
            mime='text/csv'
        )
    except Exception as e:
        st.error(f"An error occurred while assigning machines: {e}")
else:
    st.warning(f"The column '{hours_data_column}' does not exist in the DataFrame.")
