def detect_trend(snapshot):
    fg = snapshot.get("fear_greed_index", 50)
    whale = snapshot.get("whale_activity", {}).get("btc_whale_alert", False)

    if fg >= 70 and whale:
        return "bullish"
    elif fg <= 30 and not whale:
        return "bearish"
    else:
        return "neutral"

def get_signal_details(trend):
    if trend == "bullish":
        return {
            "signal": "BTC Whale + Greed > 70",
            "confidence": 0.85,
            "suggestion": "Monitor for breakout confirmation"
        }
    elif trend == "bearish":
        return {
            "signal": "Fear < 30 and no BTC whales",
            "confidence": 0.8,
            "suggestion": "Consider risk-off strategy"
        }
    else:
        return {
            "signal": "Mixed signals",
            "confidence": 0.5,
            "suggestion": "Stay cautious"
        }
