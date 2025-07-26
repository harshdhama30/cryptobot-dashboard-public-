# modules/profit_tracker.py

import os
import csv
import pandas as pd
from datetime import datetime

# Where your trades get logged
LOG_PATH = os.path.expanduser("~/Downloads/crypto_bot_complete/logs/profits.csv")

def log_profits(orders):
    """
    Append each order in `orders` (list of dicts) to a CSV at LOG_PATH,
    with columns: timestamp, symbol, action, qty, price, quoteQty
    """
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    is_new = not os.path.exists(LOG_PATH)

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp","symbol","action","qty","price","quoteQty"])
        for o in orders:
            ts    = datetime.now().isoformat()
            sym   = o.get("symbol", "")
            act   = o.get("side", o.get("action", ""))
            qty   = o.get("executedQty", "")
            price = o.get("fills", [{}])[0].get("price", "")
            quote = o.get("cummulativeQuoteQty", "")
            writer.writerow([ts, sym, act, qty, price, quote])

    print(f"Logged {len(orders)} trades to {LOG_PATH}")

def load_profits() -> pd.DataFrame:
    """
    Load the CSV at LOG_PATH into a DataFrame with columns:
    timestamp, symbol, action, qty, price, quoteQty.
    If the file doesn’t exist yet, returns an empty DataFrame.
    """
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        # ensure timestamp is string (will parse later in dashboard)
        return df
    # Return empty with the exact columns we expect
    return pd.DataFrame(columns=["timestamp","symbol","action","qty","price","quoteQty"])