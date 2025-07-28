import streamlit as st
import pandas as pd
import altair as alt
from modules.data_collector import collect_historical_data
from modules.forecaster import predict_prices
from modules.profit_tracker import load_profits

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")

# -- Live Prices Section --
st.header("💱 Live Prices")
# User selects base symbols (e.g., BTC, ETH)
selected = st.multiselect(
    "Select base symbols (e.g., BTC, ETH)",
    options=["BTC", "ETH", "XRP", "BNB", "SOL"],
    default=["BTC", "ETH"],
)

if selected:
    price_cols = st.columns(len(selected))
    # Fetch and display current price for each selected symbol
    for col, sym in zip(price_cols, selected):
        with col:
            st.subheader(sym)
            pair = f"{sym}USDT"  # append USDT for trading pair
            data = collect_historical_data([pair])
            if pair in data:
                price = data[pair]["close"].iloc[-1]
                st.metric(label="Price", value=f"${price:,.2f}")
            else:
                st.error(f"Data for {pair} not available.")
else:
    st.info("No symbols selected for live prices.")

# -- Summary Metrics --
# ... rest of dashboard follows unchanged ...
