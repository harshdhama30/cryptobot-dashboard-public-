# modules/profit_tracker.py

"""
Handle logging and loading of trade history (profits) relative to the project.
"""
import os
import csv
import pandas as pd
from datetime import datetime

# Use a relative logs directory in the project root
LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_PATH = os.path.join(LOG_DIR, "profits.csv")

# Ensure the directory exists when logging

def log_profits(orders):
    os.makedirs(LOG_DIR, exist_ok=True)
    is_new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow([
                "timestamp",
                "symbol",
                "action",
                "qty",
                "price",
                "quoteQty"
            ])
        for o in orders:
            ts = datetime.now().isoformat()
            sym = o.get("symbol")
            act = o.get("side", o.get("action"))
            qty = o.get("executedQty", "")
            price = o.get("fills", [{}])[0].get("price", "")
            quote = o.get("cummulativeQuoteQty", "")
            writer.writerow([ts, sym, act, qty, price, quote])
    print(f"Logged {len(orders)} trades to {LOG_PATH}")


def load_profits() -> pd.DataFrame:
    """
    Read the profits.csv into a DataFrame. If missing, return an empty DataFrame
    with the correct columns.
    """
    if not os.path.exists(LOG_PATH):
        # Return empty DF with headers
        return pd.DataFrame(
            columns=["timestamp","symbol","action","qty","price","quoteQty"]
        )
    return pd.read_csv(LOG_PATH)
