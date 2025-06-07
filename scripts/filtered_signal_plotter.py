import pandas as pd
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.plotting import plot_signals_plotly

# configuration
INPUT_PATH = "logs/filtered_signals.csv"
PLOT_PATH = "logs/filtered_signal_plot.png"

# load data
df = pd.read_csv(INPUT_PATH, parse_dates=["time"])
df = df.sort_values("time")

# use filtered signals
df["signal"] = df["filtered_signal"]

# plot and save
fig = plot_signals_plotly(df.tail(100))

os.makedirs("logs", exist_ok=True)
try:
    fig.write_image(PLOT_PATH, format="png", engine="kaleido")
    print(f"Filtered signal plot saved to {PLOT_PATH}")
except Exception as e:
    print(f"Failed to write plot image: {e}")
