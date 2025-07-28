# modules/binance_api.py
"""
Binance API client setup with hard-coded credentials as requested.
"""
import nest_asyncio
from binance.client import Client

nest_asyncio.apply()

# 🔒 Hard-coded Binance credentials (updated)
API_KEY = "W5rhVJF0G4KZflh7mtuTFdQ0SbEweXgqlF825WwkVIKbzCK1m8GDGO5eKKcu5KHw"
API_SECRET = "BL9Ath1uiNOu6LZKP0vNWQkoVHhVEd2DCPL4Tyke908uHv9wCDit9sfi5gJKYapq"
TESTNET = False  # Set to True if using Binance testnet

# Initialize client
_client = Client(API_KEY, API_SECRET, testnet=TESTNET)

# Public functions

def get_client():
    """Return the singleton Binance client instance."""
    return _client

# Example wrapper for order execution

def execute_trade(symbol: str, side: str, quantity: float):
    """
    Place a market order.
    side: 'BUY' or 'SELL'
    quantity: amount of base asset
    """
    client = get_client()
    if side.upper() == 'BUY':
        return client.order_market_buy(symbol=symbol, quantity=quantity)
    else:
        return client.order_market_sell(symbol=symbol, quantity=quantity)
