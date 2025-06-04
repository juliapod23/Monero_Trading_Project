import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import ace_tools_open as tools

sys.path.append(os.path.abspath("."))
from utils.plotting import plot_signals_plotly

# paths
input_csv = "data/processed/xmr_signals.csv"
output_csv = "data/processed/xmr_backtest_results.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# parameters
transaction_fee = 0.001  # 0.1% fee per trade
stop_loss = -0.03   # -3% stop
take_profit = 0.05  # +5% take
long_only = True
short_only = False

# load data
df = pd.read_csv(input_csv, parse_dates=["time"])
df.sort_values("time", inplace=True)

# backtest logic
df["next_close"] = df["close"].shift(-1)
df["position"] = df["signal"].replace(0, method="ffill") # create a persistent position based on signal 
df["strategy_return"] = df["position"] * (df["next_close"] - df["close"]) / df["close"] # calculate daily returns based on position
df["cumulative_return"] = (1 + df["strategy_return"]).cumprod()
df["buy_and_hold"] = df["close"] / df["close"].iloc[0]
df["raw_return"] = (df["next_close"] - df["close"]) / df["close"]

if long_only:
    df["position"] = df["position"].apply(lambda x: x if x > 0 else 0)
elif short_only:
    df["position"] = df["position"].apply(lambda x: x if x < 0 else 0)
 
# apply capped returns   
df["strategy_return_capped"] = np.where(
    df["raw_return"] < stop_loss, stop_loss,
    np.where(df["raw_return"] > take_profit, take_profit, df["raw_return"])
)
df["strategy_return_capped"] *= df["position"]

# if return breaches limits, cancel the trade
df["strategy_return_capped"] = np.where(
    df["raw_return"] < stop_loss, stop_loss,
    np.where(df["raw_return"] > take_profit, take_profit, df["raw_return"])
)

# track when the position changes (i.e., a new signal is executed) and apply transaction fees
df["position_change"] = df["position"] != df["position"].shift(1)
df["fee"] = df["position_change"].astype(float) * transaction_fee
df["strategy_return_net"] = df["strategy_return"] - df["fee"]
df["cumulative_return_net"] = (1 + df["strategy_return_net"]).cumprod()
df["buy_and_hold"] = df["close"] / df["close"].iloc[0]

# save backtest results
df.to_csv(output_csv, index=False)

# performance metrics
def sharpe_ratio(returns, risk_free_rate=0.0):
    excess = returns - risk_free_rate
    return (excess.mean() / excess.std()) * np.sqrt(252)

def max_drawdown(series):
    cumulative = series.cummax()
    drawdown = series / cumulative - 1
    return drawdown.min()

# display metrics
metrics = {
    "Total Return (%)": (df["cumulative_return_net"].iloc[-1] - 1) * 100,
    "Sharpe Ratio": sharpe_ratio(df["strategy_return_net"].dropna()),
    "Max Drawdown": max_drawdown(df["cumulative_return_net"])
}

summary_df = pd.DataFrame([metrics])
tools.display_dataframe_to_user(name="Backtest Performance Summary", dataframe=summary_df)

# plotly
plot_signals_plotly(df, signal_col="signal", title="XMR Strategy Signals")

# plot performance
plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["buy_and_hold"], label="Buy & Hold")
plt.plot(df["time"], df["cumulative_return"], label="Strategy")
plt.title("Strategy vs Buy-and-Hold Performance")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
