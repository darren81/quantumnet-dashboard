import streamlit as st
import json
import requests
from google.cloud import storage
from datetime import datetime

st.set_page_config(page_title="QuantumNet Market Snapshot", layout="centered")

# --- HEADER ---
st.markdown("""
### 📊 **QuantumNet Market Snapshot**
""")

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


def update_strategy_log_history(bucket_name, new_entry):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    history_blob = bucket.blob("logs/strategy_log_history.json")

    history = []
    if history_blob.exists():
        history_data = history_blob.download_as_text()
        history = json.loads(history_data)

    history.append(new_entry)
    history_blob.upload_from_string(json.dumps(history, indent=4))


# --- HANDLE FILE UPLOAD ---
if uploaded_file is not None:
    try:
        content = json.load(uploaded_file)
        uploaded_file.seek(0)

        if upload_type == "Strategy Log":
            file_name = "logs/strategy_log.json"
            update_strategy_log_history("quantumnet-core-bucket", content)
        else:
            file_name = "logs/market_data.json"

        upload_to_gcs("quantumnet-core-bucket", file_name, uploaded_file)
        st.sidebar.success("✅ Upload successful! Refreshing...")
        st.experimental_rerun()

    except json.JSONDecodeError:
        st.sidebar.error("❌ Invalid JSON file")


# --- LOAD SNAPSHOTS ---
def fetch_gcs_json(bucket_name, file_path):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        if blob.exists():
            data = blob.download_as_text()
            return json.loads(data)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None


strategy_log = fetch_gcs_json("quantumnet-core-bucket", "logs/strategy_log.json")
market_data = fetch_gcs_json("quantumnet-core-bucket", "logs/market_data.json")
strategy_log_history = fetch_gcs_json("quantumnet-core-bucket", "logs/strategy_log_history.json")


# --- DISPLAY STRATEGY LOG ---
if strategy_log:
    st.markdown("""
    ### 🧠 Strategy Log History
    """)
    st.json(strategy_log)

# --- DISPLAY MARKET DATA ---
if market_data:
    st.markdown("""
    ### 📊 Market Data Snapshot
    """)
    st.json(market_data)

# --- DISPLAY STRATEGY LOG TABLE ---
if strategy_log_history:
    st.markdown("""
    ### 📜 Strategy Log Upload History
    """)
    st.dataframe(strategy_log_history, use_container_width=True)

# --- LIVE MARKET PRICES ---
def get_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url)
        data = res.json()
        return data[symbol]["usd"]
    except:
        return "N/A"

btc_price = get_price("bitcoin")
eth_price = get_price("ethereum")

st.markdown("""
### ⚡ Live Market Prices
""")
col1, col2 = st.columns(2)

with col1:
    st.caption("Bitcoin (BTC)")
    st.subheader(f"${btc_price:,}")

with col2:
    st.caption("Ethereum (ETH)")
    st.subheader(f"${eth_price:,}")
