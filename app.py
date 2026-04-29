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

def logout():
    st.session_state.logged_in = False
    st.rerun()

if not st.session_state.logged_in:
    st.title("🔐 Arbitrage Bot Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
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
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    st.title("🚀 Universal Arbitrage Dashboard")
    
    try:
        # Improved Connection Logic
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True 
            }
        })
        
        # ব্যালেন্স চেক করার আগে টাইম সিঙ্ক করা (রেন্ডার সার্ভারের জন্য জরুরি)
        exchange.load_markets()
        
        balance_data = exchange.fetch_balance()
        usdt_balance = float(balance_data['total'].get('USDT', 0.0))
        
        c1, c2 = st.columns(2)
        c1.metric("Current Balance (USDT)", f"${usdt_balance:.2f}")
        c2.info("সার্ভার সফলভাবে বিন্যান্সের সাথে কানেক্ট হয়েছে।")

    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.info("পরামর্শ: যদি আবার 'Restricted Location' দেখায়, তবে বিন্যান্স এপিআই সেটিংসে গিয়ে আইপি রেস্ট্রিকশন 'Unrestricted' আছে কি না চেক করুন।")

    # Placeholder for trades
    st.subheader("📊 Live Opportunities")
    st.write("বোট স্ক্যান করার জন্য প্রস্তুত। 'START' বাটনটি আপনার আগের কোড অনুযায়ী কাজ করবে।")
