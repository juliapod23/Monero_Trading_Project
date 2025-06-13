import pandas as pd
from utils.indicators import compute_indicators
from utils.filters import apply_signal_filters

def generate_signals(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = compute_indicators(df)

    df["filtered_signal"] = 0
    df.loc[(df["rsi_14"] < config["rsi_low"]) & (df["volatility_zscore"] < config["vol_z_cap"]), "filtered_signal"] = 1
    df.loc[(df["rsi_14"] > config["rsi_high"]) & (df["volatility_zscore"] < config["vol_z_cap"]), "filtered_signal"] = -1

    df = apply_signal_filters(df)
    return df

if __name__ == "__main__":
    import json

    CONFIG_PATH = "params/best_strategy_config.json"
    INPUT_PATH = "logs/signals.csv"
    OUTPUT_PATH = "logs/filtered_signals.csv"

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    df = pd.read_csv(INPUT_PATH)
    df["time"] = pd.to_datetime(df["time"])

    df = generate_signals(df, config)

    # Compute future returns and save
    forward_window = config.get("future_window", 5)
    df["future_return"] = df["close"].shift(-forward_window) / df["close"] - 1
    df["predicted_direction"] = df["filtered_signal"]
    df["actual_direction"] = df["future_return"].apply(lambda r: 1 if r > 0 else -1)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Signals saved to {OUTPUT_PATH}")
