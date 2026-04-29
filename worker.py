import ccxt
import time
import pandas as pd

# --- CONFIGURATION ---
API_KEY = "Z8KbhsKpbZua198ev2hQHvRf0sMM6d8g39J9jsL5fpT7C1bXWEoDNmLKwa8hxfX7"
SECRET_KEY = "Fe745RzAVjnMm7Bkv9gc5NAoFjecgTleXMv5oGcL58LWpvDrPelHBoSjt5yhWUwm"

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# Fees (BNB Discount included)
SPOT_FEE = 0.00075
FUT_FEE = 0.00018
TOTAL_FEE = (SPOT_FEE * 2) + (FUT_FEE * 2)

def run_arbitrage_worker():
    print(f"[{time.strftime('%H:%M:%S')}] Time-Optimized Worker Started...")
    
    while True:
        try:
            # Current Balance for Compounding
            bal = exchange.fetch_balance()
            total_usdt = float(bal['total'].get('USDT', 0.0))
            
            # Fetch Funding Rates
            funding_rates = exchange.fetch_funding_rates()
            
            opportunities = []
            for symbol, data in funding_rates.items():
                if '/USDT' in symbol:
                    # Funding logic (Binance 1h, 4h, or 8h)
                    raw_rate = data['fundingRate']
                    
                    # Next funding porjonto koto ghonta baki (Time Factor)
                    next_funding_time = data['nextFundingTimestamp']
                    time_to_wait_hrs = (next_funding_time - (time.time() * 1000)) / (1000 * 3600)
                    
                    if time_to_wait_hrs <= 0: time_to_wait_hrs = 8 # Default safety
                    
                    # Calculation: Hourly Profitability
                    # Net Profit = (Funding - Fees) divided by wait time
                    hourly_net = (raw_rate - TOTAL_FEE) / time_to_wait_hrs
                    
                    if hourly_net > 0:
                        opportunities.append({
                            'symbol': symbol,
                            'rate': raw_rate * 100,
                            'wait': round(time_to_wait_hrs, 2),
                            'hourly_net': hourly_net
                        })
            
            if opportunities:
                # Time-Efficiency-r bhitite shera coin-ti pick korbe
                best = max(opportunities, key=lambda x: x['hourly_net'])
                print(f"Best: {best['symbol']} | Rate: {best['rate']:.4f}% | Wait: {best['wait']}h")
                # Auto-trade execution logic here...
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Scanning... No efficient deals found after fees.")

            time.sleep(300) # Scan every 5 mins

        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_arbitrage_worker()
