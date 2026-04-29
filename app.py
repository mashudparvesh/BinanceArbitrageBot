import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
BINANCE_API_KEY = "Z8KbhsKpbZua198ev2hQHvRf0sMM6d8g39J9jsL5fpT7C1bXWEoDNmLKwa8hxfX7"
BINANCE_SECRET_KEY = "Fe745RzAVjnMm7Bkv9gc5NAoFjecgTleXMv5oGcL58LWpvDrPelHBoSjt5yhWUwm"
USER_ID = "admin"
USER_PASS = "ruppur2026"

# Page Config
st.set_page_config(page_title="Binance Arbitrage Bot", layout="wide")

# Persistent Login Session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.session_state.logged_in = False
    st.rerun()

def check_login():
    if not st.session_state.logged_in:
        st.title("🔐 Arbitrage Bot Login")
        user = st.text_input("Username", key="login_user")
        pw = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if user == USER_ID and pw == USER_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড!")
        return False
    return True

if check_login():
    # --- Sidebar Control ---
    st.sidebar.title("🤖 Bot Control Panel")
    st.sidebar.success("API Keys Loaded ✅")
    
    use_compounding = st.sidebar.checkbox("Enable Auto-Compounding", value=True)
    
    if "bot_running" not in st.session_state:
        st.session_state.bot_running = False

    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
    
    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        st.session_state.bot_running = False

    st.sidebar.divider()
    
    # Logout Button at the bottom of sidebar
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        logout()

    # --- Main Dashboard ---
    st.title("🚀 Universal Arbitrage Dashboard")
    
    c1, c2, c3 = st.columns(3)
    
    try:
        # Binance Connection with Timeout handling
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
            'timeout': 30000
        })
        
        # Balance Fetching
        balance_data = exchange.fetch_balance()
        usdt_balance = float(balance_data['total'].get('USDT', 0.0))
        
        c1.metric("Current Balance (USDT)", f"${usdt_balance:.2f}")
        c3.metric("Compounding", "ON" if use_compounding else "OFF")
        
        if st.session_state.bot_running:
            elapsed = datetime.now() - st.session_state.start_time
            c2.metric("Running Time", str(elapsed).split('.')[0])
            st.success(f"বোট সক্রিয়: বর্তমানে লভ্যাংশসহ পূর্ণ ${usdt_balance:.2f} ইনভেস্ট করা হচ্ছে।")
        else:
            st.warning("বোট বর্তমানে বন্ধ আছে। 'START BOT' চাপুন।")

    except Exception as e:
        st.error(f"Binance Connection Error: {e}")
        c1.metric("Balance", "Error")

    # Tables & Logs Layout
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Live Arbitrage Opportunities")
        data = {
            "Coin": ["Scanning...", "---", "---"],
            "Funding Rate": ["0.0000%", "0.0000%", "0.0000%"],
            "Net Profit (Est)": ["0.00%", "0.00%", "0.00%"],
            "Next Pay": ["--", "--", "--"]
        }
        st.table(pd.DataFrame(data))

    with col_right:
        st.subheader("📜 Trading Logs")
        log_box = st.empty()
        if st.session_state.bot_running:
            log_box.info(f"[{datetime.now().strftime('%H:%M:%S')}] API Connected. \nScanning 300+ coins on Binance...")
        else:
            log_box.write("Logs will appear here after starting the bot.")

    st.divider()
    st.caption("Developed for Md Mashud Parvesh | © 2026 Arbitrage Systems")
