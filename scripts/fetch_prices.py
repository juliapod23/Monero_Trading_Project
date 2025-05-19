import requests
import time
import logging
import pandas as pd
from datetime import datetime

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# constants
API_URL = "https://api.kraken.com/0/public/OHLC"
PAIR = "XMRUSD"
INTERVAL = 1440 # 1 day candles
OUTPUT_CSV = "data/raw/kraken_xmr_ohlcv.csv"

def fetch_ohlcv(pair=PAIR, interval=INTERVAL):
    logging.info(f"Requesting OHLCV data for {pair} at {interval}-minute intervals...")
    
    params = {
        'pair': pair,
        'interval': interval,
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # extract correct key
        key = next(iter(data["result"]))
        raw_ohlc = data["result"][key]
        
        df = pd.DataFrame(raw_ohlc, columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"])
        df["time"] = pd.to_datetime(df["time"], unit='s')
        df = df[["time", "open", "high", "low", "close", "vwap", "volume"]].astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        })
        
        df.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"Saved {len(df)} rows to {OUTPUT_CSV}")
        
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
    
if __name__ == "__main__":
    fetch_ohlcv()
        
        
