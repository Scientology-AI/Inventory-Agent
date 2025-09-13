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
    try:
        # Read data
        demand_df = pd.read_csv(demand_file)
        demand_df.columns = demand_df.columns.str.strip()

        inventory_df = pd.read_csv(inventory_file)
        inventory_df.columns = inventory_df.columns.str.strip()

        # Convert demand data to numeric, coercing errors to NaN
        for col in demand_df.columns:
            demand_df[col] = pd.to_numeric(demand_df[col], errors='coerce')

        if demand_df.empty or not isinstance(demand_df, pd.DataFrame):
            st.error("Uploaded demand data is not valid or empty.")
        else:
            # Calculate buffer stock with warning if lead_time > data length
            buffer_stock = {}
            for sku in demand_df.columns:
                consumption = demand_df[sku].dropna().tolist()
                if len(consumption) < lead_time:
                    st.warning(
                        f"Lead time ({lead_time}) is greater than demand data length ({len(consumption)}) for SKU: {sku}. "
                        "Buffer stock calculation skipped and set to 0."
                    )
                    buffer_stock[sku] = 0
                else:
                    rolling_sums = [sum(consumption[i:i+lead_time]) for i in range(len(consumption) - lead_time + 1)]
                    rolling_max = max(rolling_sums)
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

            # Color coding signals in DataFrame display
            def color_signal(val):
                color_map = {
                    'No Action': 'white',
                    'Green': '#2ecc71',
                    'Yellow': '#f1c40f',
                    'Red': '#e74c3c',
                    'Black': '#000000',
                }
                color = color_map.get(val, 'white')
                text_color = 'white' if val == 'Black' else 'black'
                return f'background-color: {color}; color: {text_color}'

            st.subheader("Inventory Signal Report")
            st.dataframe(output_df.style.applymap(color_signal, subset=['Signal']))

            # Optional: Download report
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Report", csv, "inventory_signal_report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error processing files: {e}")
else:
    st.info("Please upload both historic demand and current inventory CSV files to proceed.")
