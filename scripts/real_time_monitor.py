import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from utils.best_config_loader import load_best_config, generate_signals_with_config
from scripts.backtest_strategy import backtest_strategy
from utils.notifier import send_telegram_message

# Setup logging
logging.basicConfig(
    filename="logs/real_time_monitor.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

API_URL = "https://api.kraken.com/0/public/OHLC"
PAIR = "XMRUSD"
INTERVAL = 15  # 15-minute candles
DATA_FILE = "data/real_time_ohlc.csv"
RESULT_FILE = "logs/real_time_signals.csv"

def fetch_recent_data():
    try:
        response = requests.get(API_URL, params={"pair": PAIR, "interval": INTERVAL})
        data = response.json()
        result_key = list(data["result"].keys())[0]
        records = data["result"][result_key]
        columns = ["time", "open", "high", "low", "close", "vwap", "volume", "count"]
        df = pd.DataFrame(records, columns=columns)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.drop_duplicates(subset="time").sort_values("time")
        os.makedirs("data", exist_ok=True)
        df.to_csv(DATA_FILE, index=False)
        return df
    except Exception as e:
        logging.error(f"Data fetch failed: {e}")
        return None

def process_signals():
    logging.info("Fetching latest data...")
    df = fetch_recent_data()
    if df is None or df.empty:
        return

    try:
        config = load_best_config()
        df = generate_signals_with_config(df, config)
        df["future_return"] = df["close"].shift(-config.get("future_window", 4)) / df["close"] - 1
        df["predicted_direction"] = df["filtered_signal"]
        df["actual_direction"] = df["future_return"].apply(lambda r: 1 if r > 0 else -1)

        latest_signal = df.iloc[-1][["time", "close", "filtered_signal", "predicted_direction"]]
        logging.info(f"Latest signal: {latest_signal.to_dict()}")

        # Send Telegram alert if signal is high confidence
        if abs(latest_signal["filtered_signal"]) > 0.8:
            msg = (
                f"🚨 *High Confidence Signal* 🚨\n"
                f"*Time:* {latest_signal['time']}\n"
                f"*Price:* ${float(latest_signal['close']):.2f}\n"
                f"*Signal:* {float(latest_signal['filtered_signal']):.2f}\n"
                f"*Direction:* {'📈 Long' if latest_signal['predicted_direction'] > 0 else '📉 Short'}"
            )
            send_telegram_message(msg)

        df.to_csv(RESULT_FILE, index=False)
    except Exception as e:
        logging.error(f"Signal processing failed: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(process_signals, "interval", minutes=15)
    logging.info("Real-time monitor started.")
    process_signals()  # Run immediately on launch
    scheduler.start()
