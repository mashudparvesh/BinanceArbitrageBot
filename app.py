import streamlit as st
import ccxt
import pandas as pd
import os

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
    # --- Sidebar Controls ---
    st.sidebar.title("🤖 Bot Control Panel")
    
    # Start/Stop Logic using a local file
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("running")
        st.sidebar.success("বোটকে চলার নির্দেশ দেওয়া হয়েছে।")

    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("stopped")
        st.sidebar.warning("বোটকে থামার নির্দেশ দেওয়া হয়েছে।")

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- Main Dashboard ---
    st.title("📈 Live Efficiency Monitor")
    
    # Check current status
    current_status = "Unknown"
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f: current_status = f.read()

    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY})
        b = ex.fetch_balance()
        total = b['total'].get('USDT', 0.0) + ex.fetch_balance({'type': 'future'})['total'].get('USDT', 0.0)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Balance", f"${total:.2f}")
        c2.success(f"Worker Status: {current_status.upper()}")
        c3.info("Strategy: Time-Weighted")

        st.subheader("⏱️ Live Opportunities")
        st.table(pd.DataFrame({"Coin": ["Scanning..."], "Efficiency": ["Calculating..."]}))

    except Exception as e:
        st.error(f"Sync Error: {e}")
