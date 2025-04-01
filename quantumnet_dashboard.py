
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="QuantumNet Dashboard", layout="wide")

st.title("📊 QuantumNet Market Snapshot")

# Load latest snapshot
def load_latest_snapshot():
    log_folder = "quantumnet_logs"
    strategy_path = os.path.join(log_folder, "strategy_log.json")
    if not os.path.exists(strategy_path):
        st.warning("No strategy log found.")
        return []
    with open(strategy_path, "r") as f:
        return json.load(f)

data = load_latest_snapshot()

if data:
    latest = data[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("BTC Price", f"${latest['btc_price']}")
    col2.metric("ETH Price", f"${latest['eth_price']}")
    col3.metric("Fear & Greed Index", latest['fear_greed_index'])

    st.markdown(f"**Trend:** `{latest['trend'].upper()}`")
    st.markdown(f"**Summary:** {latest['summary']}")
    st.markdown(f"**Action Suggestion:** *{latest['action_suggestion']}*")

    st.divider()
    st.subheader("📜 Strategy Log")
    df = pd.DataFrame(data)
    st.dataframe(df[::-1], use_container_width=True)
else:
    st.info("No data available yet.")
