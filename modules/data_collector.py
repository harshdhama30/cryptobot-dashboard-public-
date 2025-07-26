# modules/data_collector.py

import pandas as pd
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException
from modules.binance_api import client  # reuse your existing client

def collect_historical_data(symbols: list[str], years: int = 5) -> dict[str, pd.DataFrame]:
    """
    For each base symbol in `symbols`, fetch daily klines for the last `years` years
    from Binance (symbol + 'USDT'). Skip any pair that doesn't actually exist.
    Returns a dict mapping base symbol -> DataFrame of OHLCV.
    """
    # Figure out which exact pairs Binance supports
    info = client.get_exchange_info()
    valid_pairs = {s["symbol"] for s in info["symbols"]}

    data: dict[str, pd.DataFrame] = {}
    for base in symbols:
        pair = f"{base}USDT"
        if pair not in valid_pairs:
            print(f"⚠️ Skipping {pair}: not a valid trading pair")
            continue

        try:
            klines = client.get_historical_klines(
                pair,
                BinanceClient.KLINE_INTERVAL_1DAY,
                f"{years} years ago UTC"
            )
        except BinanceAPIException as e:
            print(f"⚠️ Error fetching {pair}: {e}")
            continue

        # Build DataFrame
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        # Convert types
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        for col in ["open","high","low","close","volume","quote_asset_volume",
                    "taker_buy_base","taker_buy_quote"]:
            df[col] = df[col].astype(float)

        data[base] = df
        print(f"  Fetched {len(df)} days for {pair}")

    return data