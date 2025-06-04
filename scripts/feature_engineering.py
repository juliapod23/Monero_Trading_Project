import pandas as pd
import numpy as np
import os
import ta_py as ta
from ta.momentum import RSIIndicator
from scipy.stats import zscore, entropy
from ta.trend import SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

INPUT_CSV = "data/raw/kraken_xmr_ohlcv.csv"
OUTPUT_CSV = "data/processed/xmr_features.csv"

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# load data
df = pd.read_csv(INPUT_CSV, parse_dates=["time"])
df.sort_values("time", inplace=True)

# moving averages
sma_window = 20
ema_window = 20
df["sma_20"] = SMAIndicator(close=df["close"], window=sma_window).sma_indicator()
df["ema_20"] = EMAIndicator(close=df["close"], window=ema_window).ema_indicator()

# rsi (momentum)
df["rsi_14"] = RSIIndicator(close=df["close"], window=14).rsi()

# bollinger bands (volatility)
bb = BollingerBands(close=df["close"], window=20, window_dev=2)
df["bb_bbm"] = bb.bollinger_mavg()
df["bb_bbh"] = bb.bollinger_hband()
df["bb_bbl"] = bb.bollinger_lband()
df["bb_width"] = df["bb_bbh"] - df["bb_bbl"]

# log returns
df["log_return"] = np.log(df["close"] / df["close"].shift(1))

# rolling volatility (2 week std of log returns)
df["volatility_14"] = df["log_return"].rolling(window=14).std()

# RSI (2 week)
rsi = RSIIndicator(df["close"], window=14)
df["rsi_14"] = rsi.rsi()

# rolling z-score of price
df["zscore_14"] = (df["close"] - df["close"].rolling(window=14).mean()) / df["close"].rolling(14).std()

def calc_entropy(series, bins=10):
    hist, _ = np.histogram(series, bins=bins, density=True)
    return entropy(hist + 1e-9)  # add epsilon to avoid log(0)

df["entropy_14"] = df["log_return"].rolling(window=14).apply(calc_entropy, raw=False)    

df.dropna(inplace=True)

# save output
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved {len(df)} rows with features to {OUTPUT_CSV}")
