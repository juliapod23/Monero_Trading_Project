import pandas as pd
import numpy as np
import os
import ta_py as ta
from ta.momentum import RSIIndicator
from scipy.stats import zscore

INPUT_CSV = "data/raw/kraken_xmr_ohlcv.csv"
OUTPUT_CSV = "data/processed/xmr_features.csv"

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# load data
df = pd.read_csv(INPUT_CSV, parse_dates=["time"])
df.sort_values("time", inplace=True)

# log returns
df["log_return"] = np.log(df["close"] / df["close"].shift(1))

# rolling volatility (2 week std of log returns)
df["volatility_14"] = df["log_return"].rolling(window=14).std()

# RSI (2 week)
rsi = RSIIndicator(df["close"], window=14)
df["rsi_14"] = rsi.rsi()

# rolling z-score of price
df["zscore_14"] = (df["close"] - df["close"].rolling(window=14).mean()) / df["close"].rolling(14).std()

df.dropna(inplace=True)

# save output
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved {len(df)} rows with features to {OUTPUT_CSV}")
