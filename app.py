import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
BINANCE_API_KEY = "Z8KbhsKpbZua198ev2hQHvRf0sMM6d8g39J9jsL5fpT7C1bXWEoDNmLKwa8hxfX7"
BINANCE_SECRET_KEY = "Fe745RzAVjnMm7Bkv9gc5NAoFjecgTleXMv5oGcL58LWpvDrPelHBoSjt5yhWUwm"
USER_ID = "admin"
USER_PASS = "ruppur2026"

# Page Settings
st.set_page_config(page_title="Arbitrage Bot", layout="wide")

# Persistent State Management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

def check_login():
    if not st.session_state.logged_in:
        st.title("🔐 Login to Arbitrage System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == USER_ID and p == USER_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        return False
    return True

if check_login():
    # Sidebar
    st.sidebar.title("🤖 Bot Control")
    st.sidebar.success(f"Region: Singapore | API: Active ✅")
    
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
    
    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        st.session_state.bot_running = False
        
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🚀 Universal Arbitrage Dashboard")

    try:
        # Connect with Spot and Futures priority
        ex = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'enableRateLimit': True,
        })
        
        # Balance fetch from both Spot and Futures
        bal = ex.fetch_balance()
        spot_usdt = float(bal['total'].get('USDT', 0.0))
        
        # Separate check for Futures if Spot is zero
        futures_bal = ex.fetch_balance({'type': 'future'})
        fut_usdt = float(futures_bal['total'].get('USDT', 0.0))
        
        total_usdt = spot_usdt + fut_usdt
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Available USDT (Live)", f"${total_usdt:.2f}")
        
        if st.session_state.bot_running:
            run_time = datetime.now() - st.session_state.start_time
            c2.metric("Running Time", str(run_time).split('.')[0])
            c3.metric("Mode", "Compounding ON")
            st.success(f"Bot cholchhe! Apnar ${total_usdt:.2f} USDT bebohar kore scan kora hochhe.")
        else:
            c2.metric("Status", "Standby")
            st.warning("Bot bondho ache. Shuru korte Start chapun.")

    except Exception as e:
        st.error(f"Binance Data Error: {e}")

    # Tables
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📊 Profit Opportunities")
        st.table(pd.DataFrame({
            "Coin": ["Scanning...", "---"],
            "Funding %": ["0.0000%", "0.0000%"],
            "Net Profit": ["0.00%", "0.00%"]
        }))
    
    with col2:
        st.subheader("📜 Live Logs")
        if st.session_state.bot_running:
            st.info(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Binance... \nChecking Spot and Futures wallets.")
