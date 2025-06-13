import os
import pandas as pd
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import subprocess

# Setup logging
logging.basicConfig(
    filename="logs/data_pull.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

API_URL = "https://api.kraken.com/0/public/OHLC"
PAIR = "XMRUSD"
INTERVAL = 1440  # Daily candles

def fetch_daily_data():
    logging.info("Starting daily data pull...")
    try:
        params = {"pair": PAIR, "interval": INTERVAL}
        response = requests.get(API_URL, params=params)
        data = response.json()

        if "error" in data and data["error"]:
            raise Exception(data["error"])

        result_key = list(data["result"].keys())[0]
        records = data["result"][result_key]
        columns = ["time", "open", "high", "low", "close", "vwap", "volume", "count"]
        df = pd.DataFrame(records, columns=columns)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        out_file = "data/daily_ohlc.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(out_file, index=False)
        logging.info(f"Saved daily OHLC to {out_file}")
        
        # Run the full pipeline after successful data pull
        logging.info("Running full pipeline...")
        subprocess.run(["python", "scripts/run_pipeline.py"], check=True)
        logging.info("Pipeline completed.")
        
    except Exception as e:
        logging.error(f"Data pull failed or pipeline failed: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_daily_data, "cron", hour=6, minute=0)  # 6:00 AM daily
    logging.info("Scheduler started.")
    scheduler.start()
