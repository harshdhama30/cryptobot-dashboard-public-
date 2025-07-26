# modules/coin_list.py

"""
Helper to fetch top N coin symbols by 24h USDT volume using Binance public REST API.
Lazy-loading without requiring an authenticated Binance client at import time.
"""
from typing import List
import requests

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr"


def get_top_pairs(n: int = 10) -> List[str]:
    """
    Return the top `n` base symbols (e.g. 'BTC','ETH',…) 
    sorted by 24h USDT trading volume using Binance public API.
    """
    try:
        resp = requests.get(BINANCE_API_URL, timeout=10)
        resp.raise_for_status()
        tickers = resp.json()
    except Exception as e:
        print(f"⚠️ Error fetching tickers from public API: {e}")
        return []

    # Filter for USDT-quoted markets
    usdt_pairs = [t for t in tickers if t.get("symbol", "").endswith("USDT")]
    # Sort by quoteVolume descending
    sorted_pairs = sorted(
        usdt_pairs,
        key=lambda t: float(t.get("quoteVolume", 0)),
        reverse=True
    )
    # Strip "USDT" to get base symbols
    base_symbols = [t["symbol"][:-4] for t in sorted_pairs]
    return base_symbols[:n]
