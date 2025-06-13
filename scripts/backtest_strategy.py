import pandas as pd

def backtest_strategy(df: pd.DataFrame, forward_window: int = 5) -> pd.DataFrame:
    df = df.copy()
    df["future_return"] = df["close"].shift(-forward_window) / df["close"] - 1
    df["strategy_return"] = df["filtered_signal"] * df["future_return"]
    df["cumulative_return"] = (1 + df["strategy_return"]).cumprod()
    df["actual_direction"] = df["future_return"].apply(lambda r: 1 if r > 0 else -1)
    df["predicted_direction"] = df["filtered_signal"]
    return df

if __name__ == "__main__":
    INPUT_PATH = "logs/filtered_signals.csv"
    OUTPUT_PATH = "logs/backtest_results.csv"

    df = pd.read_csv(INPUT_PATH)
    df["time"] = pd.to_datetime(df["time"])

    result = backtest_strategy(df)
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"Backtest results saved to {OUTPUT_PATH}")
