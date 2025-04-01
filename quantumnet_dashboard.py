import streamlit as st
import os
import json
import base64

# Load and decode the base64 GCP key from Streamlit secrets
gcp_key_b64 = st.secrets["GCP_KEY_BASE64"]
gcp_key_json = base64.b64decode(gcp_key_b64).decode("utf-8")

# Write the key to a temporary file
gcp_key_path = "/tmp/gcp_key.json"
with open(gcp_key_path, "w") as f:
    f.write(gcp_key_json)

# Set environment variable so GCP libraries can find it
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_key_path
import streamlit as st
import pandas as pd
import json
from google.cloud import storage
from io import StringIO

# === CONFIG ===
BUCKET_NAME = "quantumnet-core-bucket"
LOG_FOLDER = "logs"

st.set_page_config(page_title="QuantumNet Market Snapshot", page_icon="📊")

st.title("📊 QuantumNet Market Snapshot")

# === Load from GCS ===
@st.cache_data
def load_json_from_gcs(filename):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{LOG_FOLDER}/{filename}")
    data = blob.download_as_text()
    return json.loads(data)

@st.cache_data
def load_csv_from_gcs(filename):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{LOG_FOLDER}/{filename}")
    data = blob.download_as_text()
    return pd.read_csv(StringIO(data))

# === Load Strategy Log ===
try:
    strategy_data = load_json_from_gcs("strategy_log.json")
    st.subheader("📈 Strategy Log")
    for entry in reversed(strategy_data[-5:]):  # Last 5 entries
        st.markdown(f"""
        - **Time:** `{entry['timestamp']}`
        - **Trend:** `{entry['trend'].upper()}`
        - **BTC:** `${entry['btc_price']}` | **ETH:** `${entry['eth_price']}`
        - **FGI:** `{entry['fear_greed_index']}` | **Whale:** `{entry['whale_activity']}`
        - **Signal:** *{entry['signal']}*
        - **Summary:** {entry['summary']}
        ---
        """)
except Exception as e:
    st.warning("⚠️ No strategy log found.")
    st.caption(f"Debug: {e}")

# === Load Training Data Table ===
try:
    df = load_csv_from_gcs("training_data.csv")
    st.subheader("📊 Training Dataset Snapshot")
    st.dataframe(df.tail(10), use_container_width=True)
except Exception as e:
    st.info("ℹ️ No data available yet.")
    st.caption(f"Debug: {e}")
