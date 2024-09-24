import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import easyocr
import numpy as np
from glob import glob 
from PIL import Image

st.title("Modello forecast degli assetti di centrale to be")
st.sidebar.title("Functions")
file_to_analyze = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

if file_to_analyze is not None:
  if file_to_analyze.name.endswith('.csv'):
    df = pd.read_csv(file_to_analyze)
  else:
    df = pd.read_excel(file_to_analyze, engine="openpyxl")
    st.write(df.columns.tolist())
    st.write(df)
    hours_data= st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    time_column= st.sidebar.selectbox("Indicate the date time column", df.columns.tolist())
    machine_columns = st.sidebar.multiselect("Select machine columns", df.columns)
    if machine_columns:
      for machine_col in machine_columns:
        power_col = f"{machine_col}_power" if f"{machine_col}_power" in df.columns else None
        if power_col:
                machine_dfs[machine_col] = df[[machine_col, power_col]]
                st.write(f"Data for machine: {machine_col} and power: {power_col}")
            else:
                machine_dfs[machine_col] = df[[machine_col]]
                st.write(f"Data for machine: {machine_col} (no power column found)")
                st.dataframe(machine_dfs[machine_col])
    
      

