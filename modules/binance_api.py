# modules/binance_api.py

from binance.client import Client, BinanceAPIException

# ─── YOUR BINANCE CREDENTIALS ────────────────────────────────────────────
API_KEY    = "W5rhVJF0G4KZflh7mtuTFdQ0SbEweXgqlF825WwkVIKbzCK1m8GDGO5eKKcu5KHw"
API_SECRET = "BL9Ath1uiNOu6LZKP0vNWQkoVHhVEd2DCPL4Tyke908uHv9wCDit9sfi5gJKYapq"

# ─── MODE FLAGS ───────────────────────────────────────────────────────────
TESTNET         = False    # if you ever want to switch to Binance testnet
SIMULATE_TRADES = True     # <— set to True to avoid real order calls  

# ─── INITIALIZE CLIENT ────────────────────────────────────────────────────
client = Client(API_KEY, API_SECRET, testnet=TESTNET)

# ─── HELPER: CALCULATE QUANTITY ────────────────────────────────────────────
def _calc_quantity(symbol: str, usd_allocation: float) -> float:
    ticker = client.get_symbol_ticker(symbol=symbol)
    price  = float(ticker["price"])
    qty    = usd_allocation / price
    return round(qty, 6)

# ─── MAIN: EXECUTE TRADES ──────────────────────────────────────────────────
def execute_trades(trade_decisions: dict[str, str]) -> list[dict]:
    """
    For each base-coin decision ("buy"/"sell"), simulate or place a market order.
    Returns a list of order-like dicts for logging.
    """
    USD_ALLOCATION = 100.0
    orders = []

    for base, action in trade_decisions.items():
        symbol = base + "USDT"
        qty    = _calc_quantity(symbol, USD_ALLOCATION)

        if SIMULATE_TRADES:
            # Build a fake order-response dict
            fake = {
                "symbol": symbol,
                "side": action.upper(),
                "executedQty": str(qty),
                "fills": [{"price": "0.00"}],
                "cummulativeQuoteQty": "0.00",
                "status": "SIMULATED"
            }
            print(f"🔧 Simulated {action.upper()} for {symbol}, qty={qty}")
            orders.append(fake)
            continue

        # Real trading path
        try:
            if action.lower() == "buy":
                order = client.order_market_buy(symbol=symbol, quantity=qty)
            elif action.lower() == "sell":
                order = client.order_market_sell(symbol=symbol, quantity=qty)
            else:
                continue
            print(f"✔️ {action.upper()} {symbol} → {order['status']}")
            orders.append(order)
        except BinanceAPIException as e:
            print(f"⚠️ Error executing {action} on {symbol}: {e}")

    return orders