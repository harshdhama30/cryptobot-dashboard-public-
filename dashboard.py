"""
📱⚡️ Mobile-Friendly CryptoBot Dashboard
"""

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, date, timedelta

from modules.data_collector import collect_historical_data
from modules.forecaster     import predict_prices
from modules.profit_tracker import load_profits
from modules.coin_list      import get_top_pairs

# ─── Page configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoBot Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    top_n    = st.slider("Top N by volume", 5, 30, 10)
    coins    = get_top_pairs(top_n)
    selected = st.multiselect("Select coins", coins, default=coins[:3])

    # Load existing profit logs
    df_logs = load_profits()

    # Defensive defaults if logs are empty
    if df_logs.empty:
        max_d = date.today()
        min_d = max_d - timedelta(days=7)
    else:
        df_logs["date"] = pd.to_datetime(df_logs["timestamp"]).dt.date
        min_d = df_logs["date"].min()
        max_d = df_logs["date"].max()

    drange = st.date_input(
        "P&L date range",
        value=[min_d, max_d],
        min_value=min_d,
        max_value=max_d,
    )

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

# Filter logs by selected date range
if not df_logs.empty:
    df_filtered = df_logs[
        (df_logs["date"] >= drange[0]) & (df_logs["date"] <= drange[1])
    ]
else:
    df_filtered = pd.DataFrame(columns=df_logs.columns)

total_trades = len(df_filtered)
invested     = df_filtered[df_filtered["action"]=="buy"]["quoteQty"].sum()
realized     = df_filtered[df_filtered["action"]=="sell"]["quoteQty"].sum()
pnl          = realized - invested
roi          = (pnl / invested * 100) if invested else 0.0

col1.metric("Trades", total_trades)
col2.metric("Invested", f"${invested:,.2f}")
col3.metric("P&L", f"${pnl:,.2f}")
col4.metric("ROI", f"{roi:.2f}%")

# ─── Daily P&L chart ─────────────────────────────────────────────────────────
with st.expander("📈 Daily P&L", expanded=True):
    if not df_filtered.empty:
        sell_pnl = df_filtered[df_filtered["action"]=="sell"].groupby("date")["quoteQty"].sum()
        buy_pnl  = df_filtered[df_filtered["action"]=="buy"].groupby("date")["quoteQty"].sum()
        # fill missing dates
        idx = pd.date_range(min_d, max_d)
        daily = (
            sell_pnl.reindex(idx, fill_value=0)
            - buy_pnl.reindex(idx, fill_value=0)
        ).reset_index(name="pnl").rename(columns={"index":"date"})
    else:
        daily = pd.DataFrame({"date":[min_d, max_d], "pnl":[0, 0]})

    chart = (
        alt.Chart(daily)
        .mark_line(point=True)
        .encode(
            x="date:T", y="pnl:Q",
            tooltip=[alt.Tooltip("date:T"), alt.Tooltip("pnl:Q", format=",.2f")],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

# ─── Forecast comparison ────────────────────────────────────────────────────
with st.expander("🔮 7-Day Forecasts", expanded=False):
    rows = []
    for coin in selected:
        # try real forecasts
        preds = forecasts.get(coin) or []
        # if none, dummy linear +1% per day
        if not preds and hist_data.get(coin) is not None:
            last = hist_data[coin]["close"].iloc[-1]
            preds = [last * (1 + 0.01*i) for i in range(1,8)]
        for i, price in enumerate(preds, start=1):
            rows.append({"coin": coin, "day": i, "price": price})
    df_fc = pd.DataFrame(rows)

    if df_fc.empty:
        st.write("No forecast data available.")
    else:
        fc_chart = (
            alt.Chart(df_fc)
            .mark_line(point=True)
            .encode(
                x="day:O", y="price:Q",
                color="coin:N",
                tooltip=["coin","day","price"],
            )
            .properties(height=300)
        )
        st.altair_chart(fc_chart, use_container_width=True)

# ─── Recent trades table ─────────────────────────────────────────────────────
with st.expander("📝 Recent Trades", expanded=False):
    if not df_logs.empty:
        recent = df_logs.sort_values("timestamp", ascending=False)
        st.dataframe(recent[["timestamp","symbol","action","quoteQty"]], use_container_width=True)
    else:
        st.warning("No trades logged yet. Run your trading bot locally to generate logs.")