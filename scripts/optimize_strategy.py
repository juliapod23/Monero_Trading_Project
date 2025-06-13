import optuna
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.signal_engine import generate_signals
from scripts.backtest_strategy import backtest_strategy
from utils.indicators import compute_indicators
from utils.filters import apply_signal_filters

INPUT_PATH = "logs/signals.csv"
CONFIG_OUT = "params/best_strategy_config.json"
N_TRIALS = 30

def objective(trial):
    # Suggest parameters
    rsi_low = trial.suggest_int("rsi_low", 20, 35)
    rsi_high = trial.suggest_int("rsi_high", 65, 80)
    vol_z_cap = trial.suggest_float("vol_z_cap", 1.0, 2.5)
    forward_window = trial.suggest_int("future_window", 3, 10)

    # Load raw data
    df = pd.read_csv(INPUT_PATH)
    df["time"] = pd.to_datetime(df["time"])
    df = compute_indicators(df)

    # Apply signal logic
    df["filtered_signal"] = 0
    df.loc[(df["rsi_14"] < rsi_low) & (df["volatility_zscore"] < vol_z_cap), "filtered_signal"] = 1
    df.loc[(df["rsi_14"] > rsi_high) & (df["volatility_zscore"] < vol_z_cap), "filtered_signal"] = -1

    # Apply post-filters
    df = apply_signal_filters(df)

    # Evaluate with backtest
    df["future_return"] = df["close"].shift(-forward_window) / df["close"] - 1
    df["strategy_return"] = df["filtered_signal"] * df["future_return"]

    sharpe = df["strategy_return"].mean() / (df["strategy_return"].std() + 1e-8)
    return sharpe

# Run study
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=N_TRIALS)

# Save best params
best_params = study.best_params
Path("params").mkdir(parents=True, exist_ok=True)
pd.Series(best_params).to_json(CONFIG_OUT)
print(f"Best parameters saved to {CONFIG_OUT}")
print(best_params)
