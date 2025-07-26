# modules/forecaster.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_prices(hist_data: dict[str, pd.DataFrame]) -> dict[str, list[float]]:
    """
    For each symbol, fit a simple linear model on daily closing price
    and extrapolate 7 future points.
    """
    forecasts = {}
    for symbol, df in hist_data.items():
        # assume df has columns ['timestamp','open','high','low','close','volume']
        prices = df["close"].values.reshape(-1, 1)
        days   = np.arange(len(prices)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(days, prices)

        future_days = np.arange(len(prices), len(prices) + 7).reshape(-1, 1)
        pred_prices = model.predict(future_days).flatten().tolist()

        forecasts[symbol] = pred_prices
    return forecasts