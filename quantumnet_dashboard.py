import streamlit as st
import json
import requests
from google.cloud import storage
from datetime import datetime

st.set_page_config(page_title="QuantumNet Dashboard", layout="wide")

# === Load JSON files from GCS ===
def load_json_from_gcs(bucket_name, file_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    data = blob.download_as_text()
    return json.loads(data)

# === Fetch live crypto prices ===
def fetch_live_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,ethereum',
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "BTC": data['bitcoin']['usd'],
            "ETH": data['ethereum']['usd'],
            "Error": None
        }
    except Exception as e:
        return {
            "BTC": "N/A",
            "ETH": "N/A",
            "Error": str(e)
        }

# === Load from GCS ===
bucket_name = "quantumnet-core-bucket"
strategy_log = load_json_from_gcs(bucket_name, "logs/strategy_log.json")
market_data = load_json_from_gcs(bucket_name, "logs/market_data.json")
live_prices = fetch_live_prices()

# === Title ===
st.title("📊 QuantumNet Market Snapshot")

# === Strategy Log History ===
st.subheader("📘 Strategy Log History")
st.json(strategy_log)

# === Market Data Snapshot ===
st.subheader("📊 Market Data Snapshot")
st.json(market_data)

# === Live Market Prices ===
st.subheader("⚡ Live Market Prices")
if live_prices["Error"]:
    st.error(f"⚠️ Error fetching prices: {live_prices['Error']}")
else:
    col1, col2 = st.columns(2)
    col1.metric("Bitcoin (BTC)", f"${live_prices['BTC']:,}")
    col2.metric("Ethereum (ETH)", f"${live_prices['ETH']:,}")
