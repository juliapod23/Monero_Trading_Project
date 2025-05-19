import pandas as pd
import numpy as np
import os

input_path = "data/processed/xmr_features.csv"
output_path = "data/processed/xmr_signals.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

df = pd.read_csv(input_path, parse_dates=["time"])
df.sort_values("time", inplace=True)

# signal logic (rsi-based mean reversion)
df["signal"] = 0
df.loc[df["rsi_14"] < 30, "signal"] = 1   # Buy
df.loc[df["rsi_14"] > 70, "signal"] = -1  # Sell

# save only relevant columns
df[["time", "close", "signal"]].to_csv(output_path, index=False)
print(f"Signals saved to {output_path}")
