import ccxt
import time
import os

API_KEY = "6YRwMwD6u8zGZ4QV5iHnKxy8ThzCKGB7XfeQqL9f7Ld5Qp56gDQCFXVK1XeXH67w"
SECRET_KEY = "1NzFKZtOZ6peDLCJONegPjkjTYAgp70fAZKh381gmdhIeR5gt8bA7Bb6yhb3fYhV"
STATUS_FILE = "bot_status.txt"

exchange = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY, 'options': {'defaultType': 'future'}})

def run_worker():
    print("Worker is checking for signals...")
    while True:
        try:
            # Check if bot should run
            status = "stopped"
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f: status = f.read()

            if status == "running":
                # --- Core Arbitrage Logic ---
                bal = exchange.fetch_balance()
                # (আপনার আগের সব ক্যালকুলেশন এখানে চলবে)
                print(f"[{time.strftime('%H:%M:%S')}] Working... Balance: {bal['total'].get('USDT')}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Bot is STOPPED. Waiting for Start signal...")

            time.sleep(30) # ৩০ সেকেন্ড পর পর চেক করবে
        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_worker()
