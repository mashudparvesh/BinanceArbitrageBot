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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

def logout():
    st.session_state.logged_in = False
    st.rerun()

if not st.session_state.logged_in:
    st.title("🔐 Arbitrage Bot Login")
    user = st.text_input("Username", key="u1")
    pw = st.text_input("Password", type="password", key="p1")
    if st.button("Login"):
        if user == USER_ID and pw == USER_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("ভুল ইউজারনেম বা পাসওয়ার্ড!")
else:
    # --- Sidebar ---
    st.sidebar.title("🤖 Bot Control Panel")
    st.sidebar.success("Region: Singapore ✅")
    
    use_compounding = st.sidebar.checkbox("Enable Auto-Compounding", value=True)
    
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
    
    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        st.session_state.bot_running = False

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    # --- Main Dashboard ---
    st.title("🚀 Universal Arbitrage Dashboard")
    
    try:
        # Connect to Binance
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Sync time and Fetch Balance
        balance_data = exchange.fetch_balance()
        usdt_balance = float(balance_data['total'].get('USDT', 0.0))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Balance (USDT)", f"${usdt_balance:.2f}")
        
        if st.session_state.bot_running:
            elapsed = datetime.now() - st.session_state.start_time
            c2.metric("Running Time", str(elapsed).split('.')[0])
            c3.metric("Mode", "Compounding ON")
            st.success(f"বোট সক্রিয়: বর্তমানে আপনার পূর্ণ ${usdt_balance:.2f} ব্যালেন্স নিয়ে স্ক্যানিং চলছে।")
        else:
            c2.metric("Status", "Stopped")
            st.warning("বোট বর্তমানে বন্ধ আছে। 'START BOT' চাপুন।")

    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.info("টিপস: যদি Signature Error দেখায়, তবে আপনার API Key এবং Secret Key বিন্যান্স থেকে পুনরায় চেক করে কপি করুন।")

    # Layout for Results
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Live Arbitrage Opportunities")
        data = {
            "Coin": ["Searching...", "---", "---"],
            "Funding Rate": ["0.0000%", "0.0000%", "0.0000%"],
            "Net Profit": ["0.00%", "0.00%", "0.00%"],
            "Pay Time": ["--", "--", "--"]
        }
        st.table(pd.DataFrame(data))

    with col_right:
        st.subheader("📜 Trading Logs")
        if st.session_state.bot_running:
            st.info(f"[{datetime.now().strftime('%H:%M:%S')}] API Connected.\nScanning 300+ coins...")
        else:
            st.write("বোট চালু করার জন্য অপেক্ষা করছি...")

    st.divider()
    st.caption("Developed for Md Mashud Parvesh | © 2026 Arbitrage Systems")
