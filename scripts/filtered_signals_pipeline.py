import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, hilbert
import os
import plotly.graph_objects as go

# configuration
INPUT_PATH = "logs/signals.csv"
OUTPUT_PATH = "logs/filtered_signals.csv"
CUTOFF_FREQ = 0.05  # Butterworth cutoff
RSI_WINDOW = 14

# load data
df = pd.read_csv(INPUT_PATH, parse_dates=["time"])
df = df.sort_values("time")

# butterworth low-pass filter
def butter_lowpass_filter(data, cutoff=0.05, fs=1, order=3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data)

df["filtered_close"] = butter_lowpass_filter(df["close"], cutoff=CUTOFF_FREQ)

# hilbert envelope
analytic_signal = hilbert(df["filtered_close"])
df["envelope"] = np.abs(analytic_signal)

# compute rsi on filtered close
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df["filtered_rsi"] = compute_rsi(df["filtered_close"], window=RSI_WINDOW)

# generate signals
df["signal"] = 0
df.loc[df["filtered_rsi"] < 30, "signal"] = 1
df.loc[df["filtered_rsi"] > 70, "signal"] = -1

# visualization
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=df["close"], name="Raw Close"))
fig.add_trace(go.Scatter(x=df["time"], y=df["filtered_close"], name="Filtered Close"))
fig.add_trace(go.Scatter(x=df["time"], y=df["envelope"], name="Hilbert Envelope"))
fig.show()

# export results
os.makedirs("logs", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"Filtered signal pipeline complete. Output saved to {OUTPUT_PATH}")
