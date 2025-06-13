import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
from utils.best_config_loader import load_best_config, generate_signals_with_config
from scripts.backtest_strategy import backtest_strategy

def run_pipeline():
    df = pd.read_csv("logs/signals.csv")
    df["time"] = pd.to_datetime(df["time"])

    config = load_best_config()
    df = generate_signals_with_config(df, config)
    df = backtest_strategy(df, forward_window=int(config.get("future_window", 5)))

    df.to_csv("logs/backtest_results.csv", index=False)
    print("Full pipeline completed and saved to logs/backtest_results.csv")

if __name__ == "__main__":
    run_pipeline()
