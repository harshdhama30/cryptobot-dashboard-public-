"""
📱⚡️ Mobile-Friendly CryptoBot Dashboard with Enhanced Metrics
"""

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import streamlit as st
import altair as alt
import requests
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

    # Load & clean profit logs
    df_logs = load_profits()
    if not df_logs.empty:
        df_logs["quoteQty"] = pd.to_numeric(df_logs["quoteQty"], errors="coerce").fillna(0.0)
        df_logs["action"]   = df_logs["action"].str.lower()
        df_logs["date"]     = pd.to_datetime(df_logs["timestamp"]).dt.date
        min_d = df_logs["date"].min()
        max_d = df_logs["date"].max()
    else:
        # Default last week
        max_d = date.today()
        min_d = max_d - timedelta(days=7)

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

# ─── Live Prices Ticker ──────────────────────────────────────────────────────
st.markdown("## 💱 Live Prices")
price_cols = st.columns(len(selected))
for idx, coin in enumerate(selected):
    try:
        resp = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT", timeout=5)
        price = float(resp.json().get("price", 0))
        price_cols[idx].metric(f"{coin}", f"${price:,.2f}")
    except Exception:
        price_cols[idx].metric(f"{coin}", "N/A")

# ─── Summary metrics ─────────────────────────────────────────────────────────
st.markdown("## 📊 Summary Metrics")
c1, c2, c3, c4 = st.columns(4)

if not df_logs.empty:
    df_filtered = df_logs[
        (df_logs["date"] >= drange[0]) & (df_logs["date"] <= drange[1])
    ]
else:
    df_filtered = pd.DataFrame(columns=df_logs.columns)

trades_count = len(df_filtered)
invested     = df_filtered[df_filtered["action"]=="buy"]["quoteQty"].sum()
realized     = df_filtered[df_filtered["action"]=="sell"]["quoteQty"].sum()
pnl          = realized - invested
roi          = (pnl / invested * 100) if invested else 0.0

c1.metric("Trades", trades_count)
c2.metric("Invested", f"${invested:,.2f}")
c3.metric("P&L", f"${pnl:,.2f}")
c4.metric("ROI", f"{roi:.2f}%")

# ─── Daily P&L chart & Cumulative ─────────────────────────────────────────────
with st.expander("📈 Daily P&L", expanded=True):
    if not df_filtered.empty:
        sell_tot = df_filtered[df_filtered["action"]=="sell"].groupby("date")["quoteQty"].sum()
        buy_tot  = df_filtered[df_filtered["action"]=="buy"].groupby("date")["quoteQty"].sum()
        idx      = pd.date_range(min_d, max_d)
        daily    = (
            sell_tot.reindex(idx, fill_value=0)
           -buy_tot .reindex(idx, fill_value=0)
        ).reset_index(name="pnl").rename(columns={"index":"date"})
    else:
        daily = pd.DataFrame({"date":[min_d, max_d], "pnl":[0, 0]})

    line_chart = (
        alt.Chart(daily)
        .mark_line(point=True)
        .encode(
            x="date:T", y="pnl:Q",
            tooltip=[alt.Tooltip("date:T"), alt.Tooltip("pnl:Q", format=",.2f")],
        )
        .properties(height=250, title="Daily P&L")
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Cumulative P&L
    daily["cum_pnl"] = daily["pnl"].cumsum()
    cum_chart = (
        alt.Chart(daily)
        .mark_line(point=True, color="purple")
        .encode(
            x="date:T", y="cum_pnl:Q",
            tooltip=[alt.Tooltip("date:T"), alt.Tooltip("cum_pnl:Q", format=",.2f")],
        )
        .properties(height=200, title="Cumulative P&L")
    )
    st.altair_chart(cum_chart, use_container_width=True)

# ─── Portfolio Allocation Pie Chart ───────────────────────────────────────────
st.markdown("## 🥧 Portfolio Allocation")
if not df_filtered.empty:
    buy_by_sym  = df_filtered[df_filtered["action"]=="buy"].groupby("symbol")["quoteQty"].sum()
    sell_by_sym = df_filtered[df_filtered["action"]=="sell"].groupby("symbol")["quoteQty"].sum()
    net_alloc   = (buy_by_sym.subtract(sell_by_sym, fill_value=0)).clip(lower=0)
    df_alloc    = net_alloc.reset_index().rename(columns={0:"netQuote",'quoteQty':'netQuote'})

    pie = (
        alt.Chart(df_alloc)
        .mark_arc()
        .encode(
            theta=alt.Theta("netQuote:Q"),
            color=alt.Color("symbol:N"),
            tooltip=[alt.Tooltip("symbol:N"), alt.Tooltip("netQuote:Q", format=",.2f")],
        )
        .properties(height=300, title="Net Investment by Symbol")
    )
    st.altair_chart(pie, use_container_width=True)
else:
    st.write("No portfolio allocation to display.")

# ─── 7-Day Forecasts ─────────────────────────────────────────────────────────
with st.expander("🔮 7-Day Forecasts", expanded=False):
    rows = []
    for coin in selected:
        preds = forecasts.get(coin) or []
        if not preds:
            try:
                resp = requests.get(
                    f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT",
                    timeout=5
                )
                base = float(resp.json().get("price", 0))
            except:
                base = hist_data.get(coin)["close"].iloc[-1] if coin in hist_data else 0
            preds = [base * (1 + 0.01 * i) for i in range(1,8)]
        for day, price in enumerate(preds, start=1):
            rows.append({"coin": coin, "day": day, "price": price})
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
            .properties(height=300, title="7-Day Forecasts")
        )
        st.altair_chart(fc_chart, use_container_width=True)

# ─── Recent Trades ───────────────────────────────────────────────────────────
with st.expander("📝 Recent Trades", expanded=False):
    if not df_logs.empty:
        recent = df_logs.sort_values("timestamp", ascending=False)
        st.dataframe(
            recent[["timestamp","symbol","action","quoteQty"]],
            use_container_width=True
        )
    else:
        st.warning("No trades logged yet. Run your bot locally to generate logs.")