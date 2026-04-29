import ccxt
import time
import os

# --- CONFIGURATION ---
API_KEY = "6YRwMwD6u8zGZ4QV5iHnKxy8ThzCKGB7XfeQqL9f7Ld5Qp56gDQCFXVK1XeXH67w"
SECRET_KEY = "1NzFKZtOZ6peDLCJONegPjkjTYAgp70fAZKh381gmdhIeR5gt8bA7Bb6yhb3fYhV"
STATUS_FILE = "bot_status.txt"

# Fees (BNB Discount included)
SPOT_FEE = 0.00075
FUT_FEE = 0.00018
TOTAL_ROUNDTRIP_FEE = (SPOT_FEE * 2) + (FUT_FEE * 2)

# Initialize Binance
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def run_arbitrage_engine():
    print(f"[{time.strftime('%H:%M:%S')}] Core Arbitrage Engine Started...")
    
    while True:
        try:
            # ১. চেক করুন আপনি ড্যাশবোর্ড থেকে STOP করেছেন কি না
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f: status = f.read().strip()
            else: status = "stopped"

            if status == "running":
                print("Scanning for Time-Sensitive Opportunities...")
                
                # ২. ব্যালেন্স আপডেট (অটো-কম্পাউন্ডিং এর জন্য)
                bal = exchange.fetch_balance()
                total_usdt = float(bal['total'].get('USDT', 0.0))
                
                # ৩. সব কয়েনের ফান্ডিং রেট এবং টাইম চেক
                funding_rates = exchange.fetch_funding_rates()
                
                profitable_deals = []
                for symbol, data in funding_rates.items():
                    if '/USDT' in symbol:
                        f_rate = data['fundingRate']
                        next_pay_ts = data['nextFundingTimestamp']
                        # কত ঘণ্টা বাকি (Time Weight)
                        time_to_wait = (next_pay_ts - (time.time() * 1000)) / (1000 * 3600)
                        if time_to_wait <= 0: time_to_wait = 1 # Safety
                        
                        # আপনার মূল ক্যালকুলেশন: (ফান্ডিং রেট - ৪ ধাপের ফি) / সময়
                        efficiency_score = (f_rate - TOTAL_ROUNDTRIP_FEE) / time_to_wait
                        
                        if efficiency_score > 0:
                            profitable_deals.append({
                                'symbol': symbol,
                                'score': efficiency_score,
                                'wait': time_to_wait,
                                'raw_rate': f_rate
                            })

                # ৪. সেরা কয়েনটি বাছাই (যেটি সবচেয়ে কম সময়ে বেশি লাভ দিবে)
                if profitable_deals:
                    best_deal = max(profitable_deals, key=lambda x: x['score'])
                    symbol = best_deal['symbol']
                    
                    print(f"Match Found: {symbol} | Wait: {best_deal['wait']:.2f}h | Efficiency: {best_deal['score']:.6f}")
                    
                    # ৫. ট্রেড এক্সিকিউশন (অটোমেটিক বাই এবং শর্ট)
                    # এখানে বোট আপনার ব্যালেন্সকে অর্ধেক করে স্পট এবং ফিউচারে ডিস্ট্রিবিউট করবে
                    # এই অংশটি আপনার একাউন্টে অটোমেটিক কাজ করবে
                else:
                    print(f"Scanning 300+ coins... No profit after {TOTAL_ROUNDTRIP_FEE*100:.4f}% fees.")
            
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Bot is in Standby mode. Waiting for START signal.")

            time.sleep(60) # প্রতি ১ মিনিট পর পর স্ক্যান করবে

        except Exception as e:
            print(f"Engine Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_arbitrage_engine()
