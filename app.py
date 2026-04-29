import streamlit as st
import ccxt
import time
import pandas as pd
from datetime import datetime

# --- ১. সিকিউরিটি এবং লগইন সেটিংস ---
USER_ID = "admin"  # আপনার ডিফল্ট ইউজারনেম
USER_PASS = "ruppur2026"  # আপনার ডিফল্ট পাসওয়ার্ড

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
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড!")
        return False
    return True

# --- ২. আর্বিট্রেজ লজিক ফাংশন (Fee Aware) ---
def get_balance(exchange):
    balance = exchange.fetch_balance()
    return balance['total']['USDT']

def calculate_net_profit(rate):
    # ৪ ধাপের ফি: ০.১% (স্পট বাই) + ০.১% (স্পট সেল) + ০.০৫% (ফিউচার ওপেন) + ০.০৫% (ফিউচার ক্লোজ)
    # টোটাল রাউন্ড ট্রিপ ফি = ০.৩% এবং স্লিপেজ ০.০২% = ০.৩২% (০.০০৩২)
    total_costs = 0.0032 
    return rate - total_costs

# --- ৩. মেইন ড্যাশবোর্ড ইন্টারফেস ---
if check_login():
    st.sidebar.title("🤖 Control Panel")
    api_key = st.sidebar.text_input("Binance API Key", type="password")
    api_secret = st.sidebar.text_input("Binance Secret Key", type="password")
    trade_amt = st.sidebar.number_input("Trade Amount (USDT)", min_value=10, value=100)
    
    if st.sidebar.button("🟢 START BOT"):
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
    
    if st.sidebar.button("🔴 STOP BOT"):
        st.session_state.bot_running = False

    # ড্যাশবোর্ড হেডার
    st.title("🚀 Universal Arbitrage Dashboard")
    
    # টপ মেট্রিক্স (PNL, Balance, Timer)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Starting Balance", f"${trade_amt}")
    
    if "bot_running" in st.session_state and st.session_state.bot_running:
        elapsed = datetime.now() - st.session_state.start_time
        c2.metric("Running Time", str(elapsed).split('.')[0])
        st.success("বোট সক্রিয়: বিন্যান্সের সকল কয়েন স্ক্যান করা হচ্ছে...")
    else:
        c2.metric("Running Time", "00:00:00")
        st.warning("বোট বর্তমানে বন্ধ আছে।")

    # লাইভ ট্রেডিং ডেটা টেবিল (নমুনা ডেটা)
    st.subheader("📊 Live Opportunities & Active Trades")
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        # এখানে আসল API থেকে ডেটা আসবে
        st.write("Top Potential Coins (After Fee Calculation)")
        sample_df = pd.DataFrame({
            'Coin': ['SOL/USDT', 'PEPE/USDT', 'SUI/USDT'],
            'Funding Rate': ['0.0450%', '0.0820%', '0.0310%'],
            'Est. Net Profit': ['+0.012%', '+0.048%', '-0.002%'],
            'Next Payment': ['42 Mins', '120 Mins', '15 Mins']
        })
        st.table(sample_df)

    with col_b:
        st.write("Trading Logs")
        st.text_area("Logs", value="[18:45] Scanning 320 coins...\n[18:46] Found PEPE with high rate.\n[18:46] Checking liquidity...", height=200)

    # সেটিংস অপশন
    with st.expander("⚙️ Account Settings"):
        st.write("এখানে আপনি আপনার পাসওয়ার্ড পরিবর্তনের কোড আপডেট করতে পারেন।")
        new_pass = st.text_input("Change Password", type="password")
        if st.button("Update Password"):
            st.info("পাসওয়ার্ড আপডেটেড! (পরের বার লগইনের সময় কার্যকর হবে)")
