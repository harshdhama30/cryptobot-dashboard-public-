# modules/data_collector.py

"""
Fetch daily historical OHLCV data for given symbols using Binance public REST API,
avoiding authenticated client instantiation at import time.
"""
import pandas as pd
import requests
from datetime import datetime, timedelta

# Binance public klines endpoint
KLINES_URL = "https://api.binance.com/api/v3/klines"


def collect_historical_data(symbols: list[str], years: int = 5) -> dict[str, pd.DataFrame]:
    """
    For each base symbol, fetch daily klines for the last `years` years
    from Binance public API. Returns a dict mapping symbol -> DataFrame.
    """
    data: dict[str, pd.DataFrame] = {}
    now = datetime.utcnow()
    start_time = int((now - timedelta(days=365 * years)).timestamp() * 1000)
    end_time = int(now.timestamp() * 1000)

    for base in symbols:
        pair = f"{base}USDT"
        all_klines: list = []
        next_start = start_time

        while True:
            params = {
                "symbol": pair,
                "interval": "1d",
                "startTime": next_start,
                "endTime": end_time,
                "limit": 1000
            }
            try:
                resp = requests.get(KLINES_URL, params=params, timeout=10)
                resp.raise_for_status()
                klines = resp.json()
            except Exception as e:
                print(f"⚠️ Error fetching {pair} klines: {e}")
                break

            if not klines:
                break

            all_klines.extend(klines)
            if len(klines) < 1000:
                break

            # prepare next window
            next_start = klines[-1][0] + 1

        if not all_klines:
            print(f"⚠️ No data for {pair}, skipping.")
            continue

        # Build DataFrame
        df = pd.DataFrame(
            all_klines,
            columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "num_trades",
                "taker_buy_base", "taker_buy_quote", "ignore"
            ]
        )
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        for col in ["open", "high", "low", "close", "volume", "quote_asset_volume", "taker_buy_base", "taker_buy_quote"]:
            df[col] = df[col].astype(float)

        data[base] = df
        print(f"Fetched {len(df)} days for {pair}")

    return data