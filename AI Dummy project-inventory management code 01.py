# streamlit_app.py

import streamlit as st
import pandas as pd
import altair as alt

st.title("Agentic AI: Inventory Signal Dashboard")

# Sample CSVs as byte arrays for downloads
sample_demand_csv = """
SKU001,SKU002,SKU003,SKU004
100,50,80,130
110,60,85,120
140,40,90,125
130,55,80,135
"""

sample_inventory_csv = """
SKU,Current Stock
SKU001,200
SKU002,150
SKU003,90
SKU004,300
"""

demand_bytes = sample_demand_csv.encode('utf-8')
inventory_bytes = sample_inventory_csv.encode('utf-8')

# Sidebar with inputs and instructions
with st.sidebar:
    st.header("Upload & Settings")

    demand_file = st.file_uploader("Upload Historic Demand Data (CSV)", type="csv")
    inventory_file = st.file_uploader("Upload Current Inventory Data (CSV)", type="csv")

    lead_time = st.number_input("Enter Standard Lead Time (days)", min_value=1, value=3)

    st.markdown("---")

    with st.expander("How to Use This Dashboard", expanded=True):
        st.markdown("""
        1. Upload **Historic Demand Data** CSV with SKUs as columns and daily demand as rows.
        2. Upload **Current Inventory Data** CSV with
