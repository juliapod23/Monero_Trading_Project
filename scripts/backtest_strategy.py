import pandas as pd

# configuration
DATA_PATH = "logs/filtered_signals.csv"
INITIAL_BALANCE = 1000.0

# load data
df = pd.read_csv(DATA_PATH, parse_dates=["time"])
df = df.sort_values("time")
df["future_return"] = df["close"].pct_change().shift(-1)
df["strategy_return"] = df["future_return"] * df["filtered_signal"].shift(1)

# backtest logic
df["balance"] = INITIAL_BALANCE * (1 + df["strategy_return"].fillna(0)).cumprod()

# results
total_return = df["balance"].iloc[-1] / INITIAL_BALANCE - 1
print(f"Final Balance: ${df['balance'].iloc[-1]:.2f}")
print(f"Strategy Return: {total_return * 100:.2f}%")

# save results
df.to_csv("logs/backtest_results.csv", index=False)
