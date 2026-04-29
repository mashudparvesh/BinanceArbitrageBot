import streamlit as st
import ccxt
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "6YRwMwD6u8zGZ4QV5iHnKxy8ThzCKGB7XfeQqL9f7Ld5Qp56gDQCFXVK1XeXH67w"
SECRET_KEY = "1NzFKZtOZ6peDLCJONegPjkjTYAgp70fAZKh381gmdhIeR5gt8bA7Bb6yhb3fYhV"
STATUS_FILE = "bot_status.txt"

# Fees (BNB Discount included)
SPOT_FEE = 0.00075
FUT_FEE = 0.00018
TOTAL_FEE = (SPOT_FEE * 2) + (FUT_FEE * 2)

st.set_page_config(page_title="Arbitrage Final Control", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "ruppur2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    # Sidebar
    st.sidebar.title("🤖 Bot Control")
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("running")
    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("stopped")

    st.title("🚀 Universal Arbitrage Dashboard")
    
    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})
        
        # ১. ব্যালেন্স লোড (Spot + Future)
        bal = ex.fetch_balance()
        fut_bal = ex.fetch_balance({'type': 'future'})
        total_balance = (bal['total'].get('USDT', 0) or 0) + (fut_bal['total'].get('USDT', 0) or 0)

        # ২. স্ট্যাটাস
        bot_status = "STOPPED"
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f: bot_status = f.read().upper()

        c1, c2, c3 = st.columns(3)
        c1.metric("Live Total Balance", f"${total_balance:.2f}")
        c2.metric("Bot Status", bot_status)
        c3.info("Strategy: Time-Weighted + Compounding")

        # ৩. ডাটা স্ক্যান ও এরর ফিক্স
        st.subheader("⏱️ Live Profit Opportunities (After Fees)")
        rates = ex.fetch_funding_rates()
        profitable_list = []
        
        now = datetime.now().timestamp() * 1000

        for symbol, data in rates.items():
            if '/USDT' in symbol:
                f_rate = data.get('fundingRate')
                next_pay = data.get('nextFundingTimestamp')
                
                # নিশ্চিত করা যে ডাটা None নয়
                if f_rate is not None and next_pay is not None:
                    time_to_wait = (next_pay - now) / (1000 * 3600)
                    if time_to_wait <= 0: time_to_wait = 1
                    
                    net_profit = float(f_rate) - TOTAL_FEE
                    efficiency = net_profit / time_to_wait

                    if net_profit > 0:
                        profitable_list.append({
                            "Coin": symbol,
                            "Funding (%)": f"{f_rate * 100:.4f}%",
                            "Net Profit (%)": f"{net_profit * 100:.4f}%",
                            "Wait": f"{time_to_wait:.2f}h",
                            "Score": round(efficiency * 100, 6)
                        })

        if profitable_list:
            df = pd.DataFrame(profitable_list).sort_values(by="Score", ascending=False)
            st.table(df.head(10))
        else:
            st.warning("বর্তমানে ফি বাদ দিয়ে কোনো লাভজনক সুযোগ নেই।")

    except Exception as e:
        st.error(f"System logic updated: {e}")

    st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} | Singapore ✅")
