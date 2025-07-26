def evaluate_trades(predictions):
    sorted_coins = sorted(predictions.items(), key=lambda item: item[1], reverse=True)
    top_coins = [coin for coin, _ in sorted_coins[:30]]

    decisions = {}
    for coin in predictions:
        if coin in top_coins:
            decisions[coin] = "buy"
        else:
            decisions[coin] = "hold"

    print(f"  Top {len(top_coins)} coins to buy: {top_coins}")
    return decisions
