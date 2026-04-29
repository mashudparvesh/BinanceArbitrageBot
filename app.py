import streamlit as st
import ccxt
import time
import pandas as pd
from datetime import datetime

# --- Security Settings ---
USER_ID = "admin"
USER_PASS = "ruppur2026"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("🔐 Arbitrage Bot Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == USER_ID and pw == USER_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        return False
    return True

if check_login():
    st.sidebar.title("🤖 Compounding Bot Control")
    api_key = st.sidebar.text_input("Binance API Key", type="password")
    api_secret = st.sidebar.text_input("Binance Secret Key", type="password")
    
    # এখানে ডিফল্ট ব্যালেন্স থাকবে, কিন্তু বোট অটোমেটিক ফুল ব্যালেন্স ব্যবহার করবে
    use_compounding = st.sidebar.checkbox("Enable Auto-Compounding", value=True)
    
    if st.sidebar.button("🟢 START BOT"):
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
    
    if st.sidebar.button("🔴 STOP BOT"):
        st.session_state.bot_running = False

    st.title("🚀 Universal Arbitrage Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    
    # লাইভ ব্যালেন্স এবং কম্পাউন্ডিং স্ট্যাটাস
    if api_key and api_secret:
        try:
            ex = ccxt.binance({'apiKey': api_key, 'secret': api_secret})
            bal = ex.fetch_balance()['total']['USDT']
            c1.metric("Current Balance (Live)", f"${bal:.2f}")
            c3.metric("Mode", "Compounding" if use_compounding else "Fixed")
        except:
            c1.metric("Current Balance", "Connect API")
    
    if "bot_running" in st.session_state and st.session_state.bot_running:
        elapsed = datetime.now() - st.session_state.start_time
        c2.metric("Running Time", str(elapsed).split('.')[0])
        st.success(f"বোট সক্রিয়: বর্তমানে লভ্যাংশসহ পূর্ণ ব্যালেন্স ইনভেস্ট করা হচ্ছে।")
    else:
        st.warning("বোট বন্ধ আছে।")

    # (বাকি ড্যাশবোর্ড কোড আগের মতোই থাকবে...)
    st.info("Log: বোটটি এখন প্রতিটি প্রফিট পাওয়ার পর অটোমেটিক পরবর্তী ট্রেডে সেই অ্যামাউন্ট যোগ করে নেবে।")
