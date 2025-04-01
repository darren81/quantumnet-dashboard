import streamlit as st
import os
import json
import base64
import pandas as pd
from google.cloud import storage
from io import StringIO

# === Load and decode the base64 GCP key from Streamlit secrets ===
gcp_key_b64 = st.secrets["GCP_KEY_BASE64"]
gcp_key_json = base64.b64decode(gcp_key_b64).decode("utf-8")

# === Write the key to a temporary file ===
gcp_key_path = "/tmp/gcp_key.json"
with open(gcp_key_path, "w") as f:
    f.write(gcp_key_json)

# === Set environment variable so GCP libraries can find it ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_key_path

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

# === Main App ===
try:
    strategy_log = load_json_from_gcs("strategy_log.json")
    market_data = load_json_from_gcs("market_data.json")

    st.subheader("Latest Strategy Log")
    st.json(strategy_log)

    st.subheader("Market Data")
    st.json(market_data)

except Exception as e:
    st.error("⚠️ Failed to load data from GCS:")
    st.code(str(e))
