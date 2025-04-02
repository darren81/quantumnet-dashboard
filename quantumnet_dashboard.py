import streamlit as st
import json
import requests
from google.cloud import storage

st.set_page_config(page_title="QuantumNet Market Snapshot", page_icon="📊")

st.title("📊 QuantumNet Market Snapshot")

# --- GCS STRATEGY LOG LOADER ---
def load_logs(bucket_name, file_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    data = blob.download_as_text()
    return json.loads(data)

# --- LIVE PRICE FETCHER ---
def get_live_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"]
        }
    except Exception as e:
        return {"BTC": "N/A", "ETH": "N/A", "Error": str(e)}

# --- CONFIG ---
BUCKET_NAME = "quantumnet-core-bucket"
LOG_FILE = "logs/strategy_log.json"
MARKET_FILE = "logs/market_data.json"

# --- LOAD DATA ---
try:
    strategy_logs = load_logs(BUCKET_NAME, LOG_FILE)
    if isinstance(strategy_logs, dict):
        strategy_logs = [strategy_logs]  # Convert to list if only one entry
except Exception as e:
    strategy_logs = [{"error": f"Failed to load strategy log: {str(e)}"}]

try:
    market_data = load_logs(BUCKET_NAME, MARKET_FILE)
except Exception as e:
    market_data = {"error": f"Failed to load market data: {str(e)}"}

live_prices = get_live_prices()

# --- LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📘 Strategy Log History")
    if strategy_logs:
        for log in reversed(strategy_logs[-5:]):
            st.json(log)
    else:
        st.warning("No logs found.")

with col2:
    st.subheader("📊 Market Data Snapshot")
    st.json(market_data)

    st.subheader("⚡ Live Market Prices")
    st.write(live_prices)
