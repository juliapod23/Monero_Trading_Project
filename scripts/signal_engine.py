import pandas as pd
import numpy as np
from utils.indicators import compute_indicators
from utils.filters import apply_signal_filters

INPUT_PATH = "logs/signals.csv"
OUTPUT_PATH = "logs/filtered_signals.csv"
VERSION = "v1.0.0"  # tag your logic version

# Load raw signal data
df = pd.read_csv(INPUT_PATH)
df["time"] = pd.to_datetime(df["time"])

# === Compute Features (example placeholders) ===
df = compute_indicators(df)

# === Signal Logic (placeholder) ===
df["filtered_signal"] = 0
df.loc[df["rsi_14"] < 30, "filtered_signal"] = 1
df.loc[df["rsi_14"] > 70, "filtered_signal"] = -1

# === Filter logic (optional advanced logic)
df = apply_signal_filters(df)

# === Compute actual outcome
N_FORWARD = 5
df["future_return"] = df["close"].shift(-N_FORWARD) / df["close"] - 1
df["actual_direction"] = df["future_return"].apply(lambda r: 1 if r > 0 else -1)
df["predicted_direction"] = df["filtered_signal"]
df["version"] = VERSION

# === Save to CSV
df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved filtered signals with actual/predicted labels and version to {OUTPUT_PATH}")
