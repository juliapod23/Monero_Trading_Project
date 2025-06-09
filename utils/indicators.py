import pandas as pd
import numpy as np

def compute_indicators(df):
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(20).std()
    df["volatility_zscore"] = (df["volatility"] - df["volatility"].mean()) / df["volatility"].std()
    df["rsi_14"] = compute_rsi(df["close"], 14)
    return df

def compute_rsi(series, period):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
