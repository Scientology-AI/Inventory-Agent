# streamlit_app.py

import streamlit as st
import pandas as pd

st.title("Agentic AI: Inventory Signal Dashboard")

# Upload files
demand_file = st.file_uploader("Upload Historic Demand Data (CSV)", type="csv")
inventory_file = st.file_uploader("Upload Current Inventory Data (CSV)", type="csv")

# Input lead time
lead_time = st.number_input("Enter Standard Lead Time (days)", min_value=1, value=3)

if demand_file and inventory_file:
    # Read data
    demand_df = pd.read_csv(demand_file)
    inventory_df = pd.read_csv(inventory_file)

    # Calculate buffer stock
    buffer_stock = {}
for sku in demand_df.columns:
    consumption = demand_df[sku].dropna().tolist()
    if len(consumption) >= lead_time:
        rolling_max = max([sum(consumption[i:i+lead_time]) for i in range(len(consumption) - lead_time + 1)])
    else:
        rolling_max = sum(consumption)
    buffer_stock[sku] = rolling_max


    # Signal logic
    def get_signal(current, buffer):
        if current > buffer:
            return 'No Action'
        elif current <= buffer and current > (2/3) * buffer:
            return 'Green'
        elif current <= (2/3) * buffer and current > (1/3) * buffer:
            return 'Yellow'
        elif current <= (1/3) * buffer and current > 0.05 * buffer:
            return 'Red'
        else:
            return 'Black'

    # Generate output
    output = []
    for _, row in inventory_df.iterrows():
        sku = row['SKU']
        current = row['Current Stock']
        buffer = buffer_stock.get(sku, 0)
        signal = get_signal(current, buffer)
        output.append({'SKU': sku, 'Current Stock': current, 'Buffer Stock': buffer, 'Signal': signal})

    output_df = pd.DataFrame(output)
    st.subheader("Inventory Signal Report")
    st.dataframe(output_df)

    # Optional: Download report
    csv = output_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "inventory_signal_report.csv", "text/csv")
    

