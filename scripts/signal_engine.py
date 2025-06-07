import pandas as pd
import numpy as np
from scipy.stats import zscore
import os

# configuration
INPUT_PATH = "logs/signals.csv"
OUTPUT_PATH = "logs/filtered_signals.csv"
RSI_BUY = 30
RSI_SELL = 70
VOLATILITY_WINDOW = 20
VOLATILITY_ZSCORE_THRESHOLD = 1.5

# load and prepare data
df = pd.read_csv(INPUT_PATH, parse_dates=["time"])
df = df.sort_values("time")
df.reset_index(drop=True, inplace=True)

# compute volatility
df["returns"] = df["close"].pct_change()
df["volatility"] = df["returns"].rolling(VOLATILITY_WINDOW).std()
df["volatility_zscore"] = zscore(df["volatility"].fillna(0))

# signal logic
def determine_signal(row):
    if pd.isna(row["rsi_14"]) or pd.isna(row["volatility_zscore"]):
        return 0, "insufficient data"  # hold

    if row["rsi_14"] < RSI_BUY and row["volatility_zscore"] < VOLATILITY_ZSCORE_THRESHOLD:
        return 1, "rsi_oversold + low_volatility"  # buy

    if row["rsi_14"] > RSI_SELL and row["volatility_zscore"] < VOLATILITY_ZSCORE_THRESHOLD:
        return -1, "rsi_overbought + low_volatility"  # sell

    return 0, "neutral or high_volatility" # hold

signals = df.apply(determine_signal, axis=1)
df["filtered_signal"] = signals.apply(lambda x: x[0])
df["signal_reason"] = signals.apply(lambda x: x[1])

# save to file
os.makedirs("logs", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

# print summary
print(f"Filtered signals saved to {OUTPUT_PATH}")
print(df[["time", "close", "rsi_14", "volatility", "filtered_signal"]].tail())
