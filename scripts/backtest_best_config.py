import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
from utils.best_config_loader import load_best_config, generate_signals_with_config
import matplotlib.pyplot as plt

df = pd.read_csv("logs/signals.csv")
df["time"] = pd.to_datetime(df["time"])

# Load best config
config = load_best_config()
forward_window = config.get("future_window", 5)

# Generate signals
df = generate_signals_with_config(df, config)

# Compute strategy returns
df["future_return"] = df["close"].shift(-forward_window) / df["close"] - 1
df["strategy_return"] = df["filtered_signal"] * df["future_return"]
df["cumulative"] = (1 + df["strategy_return"]).cumprod()

# Plot performance
plt.figure(figsize=(10, 5))
plt.plot(df["time"], df["cumulative"], label="Strategy")
plt.title("Cumulative Returns Using Best Config")
plt.xlabel("Time")
plt.ylabel("Equity Curve")
plt.legend()
plt.tight_layout()
plt.show()
