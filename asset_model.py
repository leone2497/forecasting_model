import pandas as pd
import streamlit as st
import seaborn as sns
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
    df = pd.read_excel(file_to_analyze)
    st.write(df.columns.tolist())
    st.write(df)
    hours_data= st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    time_column= st.sidebar.selectbox("Indicate the power column", df.columns.tolist())
    for column in df.columns.tolist():
      

