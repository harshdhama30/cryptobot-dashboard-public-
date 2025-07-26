import os
import csv
from collections import defaultdict

# Same log path your profit_tracker uses
LOG_PATH = os.path.expanduser("~/Downloads/crypto_bot_complete/logs/profits.csv")

def summarize_performance():
    """
    Reads profits.csv and prints daily P&L:
    P&L = total sells – total buys
    """
    if not os.path.exists(LOG_PATH):
        print("ℹ️ No profit log found yet.")
        return

    daily = defaultdict(lambda: {"buys": 0.0, "sells": 0.0})
    with open(LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["timestamp"][:10]  # YYYY-MM-DD
            action = row["action"].lower()
            quote = float(row.get("quoteQty") or 0)
            if action == "buy":
                daily[date]["buys"] += quote
            elif action == "sell":
                daily[date]["sells"] += quote

    print("🏷️ Daily Performance Summary:")
    for date in sorted(daily):
        b = daily[date]["buys"]
        s = daily[date]["sells"]
        pnl = s - b
        print(f"  {date}: P&L = ${pnl:.2f} (buys ${b:.2f}, sells ${s:.2f})")

