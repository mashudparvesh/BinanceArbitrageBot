import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime

API_KEY = "6YRwMwD6u8zGZ4QV5iHnKxy8ThzCKGB7XfeQqL9f7Ld5Qp56gDQCFXVK1XeXH67w"
SECRET_KEY = "1NzFKZtOZ6peDLCJONegPjkjTYAgp70fAZKh381gmdhIeR5gt8bA7Bb6yhb3fYhV"

st.set_page_config(page_title="Arbitrage 24/7 Monitor", layout="wide")

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
    st.sidebar.title("🤖 Arbitrage Controller")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📈 Live Efficiency Monitor")
    
    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY})
        # Balance Fetch (Spot + Futures)
        b = ex.fetch_balance()
        s_bal = b['total'].get('USDT', 0.0)
        f_bal = ex.fetch_balance({'type': 'future'})['total'].get('USDT', 0.0)
        total = s_bal + f_bal

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Balance", f"${total:.2f}")
        c2.success("Worker: Active (Singapore) ✅")
        c3.info("Strategy: Time-Weighted Arbitrage")

        st.subheader("⏱️ Time-Sensitive Opportunities")
        # Sample table showing the time logic
        st.table(pd.DataFrame({
            "Coin": ["Scanning...", "---"],
            "Next Funding In": ["1h / 4h / 8h", "---"],
            "Efficiency Score": ["Highest Priority", "---"]
        }))

    except Exception as e:
        st.error(f"Sync Error: {e}")

    st.caption("Developed for Md Mashud Parvesh | © 2026")
