import requests
import pandas as pd
import time
from datetime import datetime
import os
import sys
import plotly.io as pio
pio.renderers.default = 'browser'

sys.path.append(os.path.abspath("."))

from utils.plotting import plot_signals_plotly

# configuration 
API_URL = "https://api.kraken.com/0/public/OHLC"
PAIR = "XMRUSD"
INTERVAL = 5  
LOOKBACK_CANDLES = 100

def fetch_ohlc(pair=PAIR, interval=INTERVAL):
    params = {
        "pair": pair,
        "interval": interval
    }
    response = requests.get(API_URL, params=params)
    result = response.json()["result"]
    key = list(result.keys())[0]  # dynamic pair key
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

def monitor():
    print("Fetching latest XMR data from Kraken...")
    df = fetch_ohlc()
    df = compute_rsi(df)
    df = generate_signal(df)

    latest_row = df.iloc[-1]
    ts = latest_row["time"]
    price = latest_row["close"]
    signal = latest_row["signal"]

    if signal == 1:
        action = "BUY"
    elif signal == -1:
        action = "SELL"
    else:
        action = "HOLD"

    print(f"[{ts}] Price: ${price:.2f} | Signal: {action}")

    plot_signals_plotly(df.tail(50))

if __name__ == "__main__":
    monitor()
