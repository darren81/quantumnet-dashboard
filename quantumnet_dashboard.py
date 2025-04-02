import streamlit as st
import json
import requests
from google.cloud import storage
from datetime import datetime

st.set_page_config(page_title="QuantumNet Market Snapshot", layout="centered")

# --- HEADER ---
st.markdown("### 📊 **QuantumNet Market Snapshot**")

# --- UPLOAD SECTION (SIDEBAR) ---
st.sidebar.header("📤 Upload New Log")
upload_type = st.sidebar.radio("Choose file type", ["Strategy Log", "Market Data"])
uploaded_file = st.sidebar.file_uploader("Upload a .json file")

def upload_to_gcs(bucket_name, destination_blob_name, file):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)
    return True

if uploaded_file is not None:
    try:
        content = json.load(uploaded_file)
        uploaded_file.seek(0)  # Reset file pointer
        blob_name = "logs/strategy_log.json" if upload_type == "Strategy Log" else "logs/market_data.json"
        upload_to_gcs("quantumnet-core-bucket", blob_name, uploaded_file)
        st.sidebar.success("✅ Upload successful! Refreshing...")
        st.experimental_rerun()
    except json.JSONDecodeError:
        st.sidebar.error("❌ Invalid JSON file")

# --- LOAD STRATEGY LOG ---
def fetch_gcs_json(bucket_name, file_path):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(file_path)
        data = blob.download_as_text()
        return json.loads(data)
    except Exception as e:
        return {"Error": str(e)}

strategy_log = fetch_gcs_json("quantumnet-core-bucket", "logs/strategy_log.json")
market_data = fetch_gcs_json("quantumnet-core-bucket", "logs/market_data.json")

# --- STRATEGY LOG DISPLAY ---
st.markdown("### 🧠 Strategy Log History")
st.json(strategy_log)

# --- MARKET SNAPSHOT DISPLAY ---
st.markdown("### 📊 Market Data Snapshot")
st.json(market_data)

# --- LIVE MARKET PRICES ---
st.markdown("### ⚡ Live Market Prices")

def get_price(symbol):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd")
        return r.json()[symbol]["usd"]
    except:
        return "N/A"

btc_price = get_price("bitcoin")
eth_price = get_price("ethereum")

col1, col2 = st.columns(2)
with col1:
    st.caption("Bitcoin (BTC)")
    st.markdown(f"**${btc_price:,}**")
with col2:
    st.caption("Ethereum (ETH)")
    st.markdown(f"**${eth_price:,}**")
