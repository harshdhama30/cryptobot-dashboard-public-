#!/usr/bin/env python3
import os

from modules.data_collector   import collect_historical_data
from modules.forecaster       import predict_prices      # ← import your forecaster
from modules.trading_logic    import evaluate_trades
from modules.binance_api      import execute_trades
from modules.profit_tracker   import log_profits
from modules.coin_list        import get_top_pairs

def main():
    # 1) Choose which symbols to trade (e.g. top 10 by volume)
    top_n = int(os.getenv("TOP_N", "10"))
    symbols = get_top_pairs(n=top_n)

    # 2) Collect historical data
    print("📊 Collecting data…")
    hist_data = collect_historical_data(symbols)

    # 3) Predict 7-day ahead prices
    print("📈 Predicting 7-day forecasts…")
    forecasts = predict_prices(hist_data)

    # 4) Extract the Day+7 prediction for each coin
    day7_preds = {coin: prices[6] for coin, prices in forecasts.items()}

    # 5) Decide buy/sell/hold
    trade_decisions = evaluate_trades(day7_preds)

    # 6) Send orders to Binance (simulated or real)
    orders = execute_trades(trade_decisions)

    # 7) Log your trades
    log_profits(orders)

if __name__ == "__main__":
    main()