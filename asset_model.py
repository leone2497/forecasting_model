for merge_idx in range(int(num_merged_dfs)):
    st.write(f"### Merged Database {merge_idx + 1}")
    selected_dfs = st.multiselect(f"Select DataFrames to merge for Merged Database {merge_idx + 1}", options=range(len(dataframes)), format_func=lambda x: f"Group {x + 1}")
    
    if selected_dfs:
        # Get the DataFrames to merge
        dfs_to_merge = [dataframes[i] for i in selected_dfs]
        merged_df = pd.concat(dfs_to_merge, ignore_index=True)
        
        # Display the merged DataFrame
        st.write(f"Merged DataFrame {merge_idx + 1}:")
        st.dataframe(merged_df)
        
        # Assuming the 2nd and 3rd columns in the merged DataFrame contain the necessary data
        # Adjust the column indices/names based on your DataFrame structure
        if merged_df.shape[1] >= 3:  # Ensure there are at least 3 columns in the merged DF
            merged_df["Rapporto potenza assorbita/pot tot"] = merged_df.iloc[:, 1] / merged_df.iloc[:, 2]
        
        st.write(f"DataFrame {merge_idx + 1} with 'Rapporto potenza assorbita/pot tot' column:")
        st.dataframe(merged_df)
        
        # Append the merged DataFrame to the list
        merged_dataframes.append(merged_df)
