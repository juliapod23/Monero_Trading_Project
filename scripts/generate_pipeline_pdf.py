import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os

# load data
signals_path = "logs/filtered_signals.csv"
backtest_path = "logs/backtest_results.csv"
plot_path = "logs/filtered_signal_plot.png"
pdf_output_path = "logs/pipeline_summary.pdf"

# load csvs
signals_df = pd.read_csv(signals_path, parse_dates=["time"])
backtest_df = pd.read_csv(backtest_path, parse_dates=["time"])

# summary stats
summary_text = f"""
Filtered Signals Summary
------------------------
Total Records: {len(signals_df)}
Buy Signals: {(signals_df['filtered_signal'] == 1).sum()}
Sell Signals: {(signals_df['filtered_signal'] == -1).sum()}
Hold Signals: {(signals_df['filtered_signal'] == 0).sum()}
Final Balance: ${backtest_df['balance'].iloc[-1]:.2f}
Strategy Return: {(backtest_df['balance'].iloc[-1] / 1000 - 1) * 100:.2f}%
"""

# create pdf figure
fig = go.Figure()

# Add image trace
with open(plot_path, "rb") as f:
    image_bytes = f.read()

fig.add_layout_image(
    dict(
        source="data:image/png;base64," + image_bytes.encode("base64").decode(),
        x=0, y=1, xref="paper", yref="paper",
        sizex=1, sizey=1, xanchor="left", yanchor="top", layer="below"
    )
)

fig.add_annotation(
    text=summary_text,
    x=0.01, y=0.95,
    xref="paper", yref="paper",
    showarrow=False,
    align="left",
    font=dict(size=14),
    bordercolor="#000",
    borderwidth=1
)

fig.update_layout(width=800, height=1000, margin=dict(t=40, b=40))

# save pdf
pio.write_image(fig, pdf_output_path, format="pdf", engine="kaleido")
print(f"Pipeline summary saved to {pdf_output_path}")
