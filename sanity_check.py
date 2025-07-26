from modules.data_collector import collect_historical_data
from modules.forecaster     import predict_prices

symbols = ["BTC", "ETH"]
print("=== Fetching historical data ===")
hist = collect_historical_data(symbols)
for coin, df in hist.items():
    print(f"{coin}: {len(df)} days of data -> columns: {list(df.columns)}")

print("\n=== Generating 7-day forecasts ===")
preds = predict_prices(hist)
for coin, forecast in preds.items():
    print(f"{coin}: {len(forecast)} points -> {forecast}")
