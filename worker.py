import streamlit as st
import ccxt
import pandas as pd
import os
from datetime import datetime

# API Config
API_KEY = "6YRwMwD6u8zGZ4QV5iHnKxy8ThzCKGB7XfeQqL9f7Ld5Qp56gDQCFXVK1XeXH67w"
SECRET_KEY = "1NzFKZtOZ6peDLCJONegPjkjTYAgp70fAZKh381gmdhIeR5gt8bA7Bb6yhb3fYhV"
STATUS_FILE = "bot_status.txt"

st.set_page_config(page_title="Arbitrage Controller", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Login")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Login"):
        if u == "admin" and p == "ruppur2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    # Sidebar
    st.sidebar.title("🤖 Control Panel")
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("running")
        st.success("Bot started!")

    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("stopped")
        st.warning("Bot stopped!")

    # Dashboard Metrics
    st.title("📈 Live Efficiency Monitor")
    
    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY})
        # Fetch Live Balance directly for confirmation
        bal = ex.fetch_balance()
        usdt_total = bal['total'].get('USDT', 0.0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Live USDT Balance", f"${usdt_total:.2f}")
        c2.success("API Status: Connected ✅")
        c3.info("Region: Singapore")

        # Opportunity Table
        st.subheader("⏱️ Live Market Scan")
        # Real logic to show data from exchange
        rates = ex.fetch_funding_rates()
        df = pd.DataFrame([{'Coin': k, 'Rate %': v['fundingRate']*100} for k, v in rates.items() if '/USDT' in k])
        st.dataframe(df.sort_values(by='Rate %', ascending=False).head(10), use_container_width=True)

    except Exception as e:
        st.error(f"Sync Error: {e}")

    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
