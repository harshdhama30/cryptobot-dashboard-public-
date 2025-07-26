"""
📱⚡️ Mobile-Friendly CryptoBot Dashboard
"""

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

from modules.data_collector import collect_historical_data
from modules.forecaster     import predict_prices
from modules.profit_tracker import load_profits
from modules.coin_list      import get_top_pairs

# Page configuration
st.set_page_config(
    page_title="CryptoBot Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    top_n = st.slider("Top N by volume", 5, 30, 10)
    coins = get_top_pairs(top_n)
    selected = st.multiselect("Select coins", coins, default=coins[:3])

    df_logs = load_profits()
    df_logs['date'] = pd.to_datetime(df_logs['timestamp']).dt.date
    min_d, max_d = df_logs['date'].min(), df_logs['date'].max()
    drange = st.date_input("P&L date range", [min_d, max_d])

    st.markdown("---")
    st.caption("Built with Streamlit • Altair • Mobile-friendly")

# ─── Data fetching & caching ─────────────────────────────────────────────────
@st.cache_data
def load_data(sym_list):
    hist = collect_historical_data(sym_list)
    fc   = predict_prices(hist)
    return hist, fc

hist_data, forecasts = load_data(selected)

# ─── Summary metrics ─────────────────────────────────────────────────────────
st.markdown("## 📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
df_filt = df_logs[(df_logs.date >= drange[0]) & (df_logs.date <= drange[1])]

total_trades = len(df_filt)
invested     = df_filt[df_filt.action=="buy"].quoteQty.sum()
realized     = df_filt[df_filt.action=="sell"].quoteQty.sum()
pnl          = realized - invested
roi          = (pnl/invested*100) if invested else 0.0

col1.metric("Trades", total_trades)
col2.metric("Invested", f"${invested:,.2f}")
col3.metric("P&L",      f"${pnl:,.2f}")
col4.metric("ROI",      f"{roi:.2f}%")

# ─── Daily P&L chart ─────────────────────────────────────────────────────────
with st.expander("📈 Daily P&L", expanded=True):
    daily = df_filt.groupby('date').apply(
        lambda d: d[d.action=="sell"].quoteQty.sum() - d[d.action=="buy"].quoteQty.sum()
    ).reset_index(name="pnl")

    chart = alt.Chart(daily).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("pnl:Q",  title="P&L ($)"),
        tooltip=[alt.Tooltip("date:T"), alt.Tooltip("pnl:Q", format=",.2f")]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

# ─── Forecast comparison ────────────────────────────────────────────────────
with st.expander("🔮 7-Day Forecasts", expanded=False):
    rows = []
    for coin in selected:
        for i, price in enumerate(forecasts[coin], start=1):
            rows.append({"coin":coin, "day":i, "price":price})
    df_fc = pd.DataFrame(rows)

    fc_chart = alt.Chart(df_fc).mark_line(point=True).encode(
        x=alt.X("day:O", title="Day +"),
        y=alt.Y("price:Q", title="Price ($)"),
        color=alt.Color("coin:N"),
        tooltip=["coin","day","price"]
    ).properties(height=300)
    st.altair_chart(fc_chart, use_container_width=True)

# ─── Recent trades table ─────────────────────────────────────────────────────
with st.expander("📝 Recent Trades", expanded=False):
    recent = df_logs.sort_values("timestamp", ascending=False)
    st.dataframe(recent[["timestamp","symbol","action","quoteQty"]], use_container_width=True)
