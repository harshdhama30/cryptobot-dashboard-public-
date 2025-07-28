import streamlit as st
import pandas as pd
import altair as alt
from modules.data_collector import collect_historical_data
from modules.forecaster import predict_prices
from modules.profit_tracker import load_profits

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")

# -- Live Prices Section --
st.header("💱 Live Prices")
# Assume `selected` is defined earlier, e.g., top N symbols
selected = st.multiselect("Select symbols", options=["BTC", "ETH", "XRP"], default=["BTC", "ETH"])

if selected:
    # Create one column per symbol
    price_cols = st.columns(len(selected))
    for col, sym in zip(price_cols, selected):
        with col:
            st.subheader(sym)
            price = collect_historical_data([sym])[sym]["close"].iloc[-1]
            st.metric(label="Price", value=f"${price:,.2f}")
else:
    st.info("No symbols selected for live prices.")

# -- Summary Metrics --
# ... rest of dashboard follows unchanged ...