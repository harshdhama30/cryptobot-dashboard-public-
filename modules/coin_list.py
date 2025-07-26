# modules/coin_list.py

from binance.client import Client

# ─── Your Binance Credentials ─────────────────────────────────────────────
API_KEY    = "W5rhVJF0G4KZflh7mtuTFdQ0SbEweXgqlF825WwkVIKbzCK1m8GDGO5eKKcu5KHw"
API_SECRET = "BL9Ath1uiNOu6LZKP0vNWQkoVHhVEd2DCPL4Tyke908uHv9wCDit9sfi5gJKYapq"

# Set to True if you want to hit the TESTNET instead of live
TESTNET    = False

def get_top_pairs(n: int = 10) -> list[str]:
    """
    Connect to Binance and return the top `n` base symbols (e.g. 'BTC','ETH',…)
    ranked by their 24-hour USDT volume.
    """
    # 1) Initialize the client
    client = Client(API_KEY, API_SECRET, testnet=TESTNET)

    # 2) Fetch 24h ticker data for all symbols
    #    NOTE: the correct method is get_ticker(), not get_ticker_24hr()
    tickers = client.get_ticker()

    # 3) Filter for USDT-quoted pairs
    usdt_pairs = [t for t in tickers if t["symbol"].endswith("USDT")]

    # 4) Sort descending by quoteVolume (the USD volume)
    sorted_pairs = sorted(
        usdt_pairs,
        key=lambda t: float(t.get("quoteVolume", 0)),
        reverse=True
    )

    # 5) Strip off the “USDT” suffix to get base symbols
    base_symbols = [t["symbol"][:-4] for t in sorted_pairs]

    # 6) Return only the top N
    return base_symbols[:n]
