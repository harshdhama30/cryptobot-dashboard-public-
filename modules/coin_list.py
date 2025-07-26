# modules/coin_list.py

"""
Lazy-loaded helper to fetch top N coin symbols by 24h USDT volume.
"""
from typing import List
from modules.binance_api import _get_client


def get_top_pairs(n: int = 10) -> List[str]:
    """
    Return the top `n` base symbols (e.g. 'BTC','ETH',…) 
    sorted by 24h USDT trading volume, using a lazy-loaded Binance client.
    """
    client = _get_client()
    try:
        tickers = client.get_ticker()  # fetch 24h stats for all symbols
    except Exception as e:
        print(f"⚠️ Error fetching tickers: {e}")
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
