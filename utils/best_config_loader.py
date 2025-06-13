import json
import pandas as pd
from utils.indicators import compute_indicators
from utils.filters import apply_signal_filters

CONFIG_PATH = "params/best_strategy_config.json"

def load_best_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def generate_signals_with_config(df, config):
    df = compute_indicators(df)
    df["filtered_signal"] = 0
    df.loc[(df["rsi_14"] < config["rsi_low"]) & (df["volatility_zscore"] < config["vol_z_cap"]), "filtered_signal"] = 1
    df.loc[(df["rsi_14"] > config["rsi_high"]) & (df["volatility_zscore"] < config["vol_z_cap"]), "filtered_signal"] = -1
    df = apply_signal_filters(df)
    return df
