import streamlit as st
import ccxt
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "Z8KbhsKpbZua198ev2hQHvRf0sMM6d8g39J9jsL5fpT7C1bXWEoDNmLKwa8hxfX7"
SECRET_KEY = "Fe745RzAVjnMm7Bkv9gc5NAoFjecgTleXMv5oGcL58LWpvDrPelHBoSjt5yhWUwm"
STATUS_FILE = "bot_status.txt"

# Fees (BNB Discount included)
SPOT_FEE = 0.00075
FUT_FEE = 0.00018
TOTAL_FEE = (SPOT_FEE * 2) + (FUT_FEE * 2)

st.set_page_config(page_title="Arbitrage Master Controller", layout="wide")

# --- AUTHENTICATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Bot Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "ruppur2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials!")
else:
    # --- SIDEBAR CONTROLS ---
    st.sidebar.title("🤖 Bot Control Panel")
    
    if st.sidebar.button("🟢 START BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("running")
        st.sidebar.success("বোট চলার নির্দেশ পেয়েছে।")

    if st.sidebar.button("🔴 STOP BOT", use_container_width=True):
        with open(STATUS_FILE, "w") as f: f.write("stopped")
        st.sidebar.warning("বোট থামার নির্দেশ পেয়েছে।")

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- MAIN DASHBOARD ---
    st.title("🚀 Universal Arbitrage Dashboard")
    
    try:
        # Binance Connection (Spot & Future Sync)
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})
        
        # ১. লাইভ ব্যালেন্স চেক (Spot + Futures)
        bal = ex.fetch_balance()
        spot_usdt = bal['total'].get('USDT', 0.0)
        fut_bal = ex.fetch_balance({'type': 'future'})
        fut_usdt = fut_bal['total'].get('USDT', 0.0)
        total_balance = spot_usdt + fut_usdt

        # ২. স্ট্যাটাস চেক
        bot_status = "STOPPED"
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f: bot_status = f.read().upper()

        # ৩. মেট্রিক্স ডিসপ্লে
        c1, c2, c3 = st.columns(3)
        c1.metric("Live Total Balance", f"${total_balance:.2f}")
        c2.metric("Bot Status", bot_status)
        c3.info("Strategy: Time-Weighted + Auto-Compounding")

        # ৪. লাইভ মার্কেট স্ক্যান (সব অপশনসহ)
        st.subheader("⏱️ Live Profit Opportunities (After Fees)")
        
        funding_rates = ex.fetch_funding_rates()
        profitable_list = []
        
        for symbol, data in funding_rates.items():
            if '/USDT' in symbol:
                f_rate = data['fundingRate']
                next_pay = data['nextFundingTimestamp']
                
                # টাইম ক্যালকুলেশন (টাইম-সেনসিটিভ লজিক)
                time_to_wait = (next_pay - (datetime.now().timestamp() * 1000)) / (1000 * 3600)
                if time_to_wait <= 0: time_to_wait = 8
                
                # নিট লাভ = ফান্ডিং রেট - ৪ ধাপের মোট ফি
                net_profit = f_rate - TOTAL_FEE
                
                # এফিসিয়েন্সি স্কোর (আপনার ১ঘণ্টা বনাম ৪ঘণ্টা লজিক)
                efficiency_score = net_profit / time_to_wait

                if net_profit > 0:
                    profitable_list.append({
                        "Coin": symbol,
                        "Funding Rate (%)": f"{f_rate * 100:.4f}%",
                        "Net Profit (%)": f"{net_profit * 100:.4f}%",
                        "Next Pay In": f"{time_to_wait:.2f}h",
                        "Efficiency Score": round(efficiency_score * 100, 6)
                    })

        if profitable_list:
            df = pd.DataFrame(profitable_list).sort_values(by="Efficiency Score", ascending=False)
            st.table(df.head(10))
        else:
            st.warning("বর্তমানে ফি বাদ দেওয়ার পর কোনো লাভজনক কয়েন পাওয়া যায়নি। স্ক্যানিং চলছে...")

    except Exception as e:
        st.error(f"Connection Error: {e}")

    st.divider()
    st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Region: Singapore ✅")
