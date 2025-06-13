import requests
import pandas as pd
import time
from datetime import datetime
import plotly.io as pio
import os
import sys
from pathlib import Path
import logging

sys.path.append(os.path.abspath("."))
from utils.plotting import plot_signals_plotly

# configuration
API_URL = "https://api.kraken.com/0/public/OHLC"
PAIR = "XMRUSD"
INTERVAL = 5  # in minutes
LOG_PATH = "logs/signals.csv"
CHECK_INTERVAL = 120  # seconds
pio.renderers.default = "svg"

# logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/live_monitor.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

def fetch_ohlc(pair=PAIR, interval=INTERVAL):
    params = {"pair": pair, "interval": interval}
    response = requests.get(API_URL, params=params)
    data = response.json()

    if "error" in data and data["error"]:
        print("Kraken API error:", data["error"])
        return pd.DataFrame()

    result = data.get("result")
    if not result:
        print("No result returned from Kraken.")
        return pd.DataFrame()

    key = list(result.keys())[0]
    ohlc = result[key]

    df = pd.DataFrame(ohlc, columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df["close"] = df["close"].astype(float)
    return df

def compute_rsi(df, window=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    df["rsi_14"] = 100 - (100 / (1 + rs))
    return df

def generate_signal(df):
    df["signal"] = 0
    df.loc[df["rsi_14"] < 30, "signal"] = 1
    df.loc[df["rsi_14"] > 70, "signal"] = -1
    return df

def log_signal(row):
    from pathlib import Path
    row.to_frame().T.to_csv(LOG_PATH, mode="a", index=False, header=not Path(LOG_PATH).exists())


def monitor_loop():
    print("Starting XMR signal monitor...")
    last_timestamp = None

    while True:
        try:
            df = fetch_ohlc()
            if df.empty:
                print("No data received.")
            else:
                current_timestamp = df.iloc[-1]["time"]

                if last_timestamp is None or current_timestamp != last_timestamp:
                    last_timestamp = current_timestamp
                    df = compute_rsi(df)
                    df = generate_signal(df)
                    latest = df.iloc[-1]
                    ts = latest["time"]
                    price = latest["close"]
                    signal = latest["signal"]
                    action = {1: "BUY", -1: "SELL"}.get(signal, "HOLD")

                    logging.info(f"{ts} | ${price:.2f} | Signal: {action}")
                    log_signal(latest[["time", "close", "rsi_14", "signal"]])

                    fig = plot_signals_plotly(df.tail(50))
                    if fig is not None:
                        fig.write_image("logs/latest_signal_plot.png")
                    else:
                        logging.warning("plot_signals_plotly returned None, skipping image save.")

        except Exception as e:
            logging.error(f"Runtime error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_loop()
