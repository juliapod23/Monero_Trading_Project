import plotly.graph_objs as go

def plot_signals_plotly(df, signal_col="signal", title="Price Chart with Signals"):
    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["close"],
        mode="lines", name="Price", line=dict(color="blue")
    ))

    # Buy signals
    buys = df[df[signal_col] == 1]
    fig.add_trace(go.Scatter(
        x=buys["time"], y=buys["close"],
        mode="markers", name="Buy", marker=dict(color="green", symbol="triangle-up", size=10)
    ))

    # Sell signals
    sells = df[df[signal_col] == -1]
    fig.add_trace(go.Scatter(
        x=sells["time"], y=sells["close"],
        mode="markers", name="Sell", marker=dict(color="red", symbol="triangle-down", size=10)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        legend_title="Legend",
        template="plotly_white",
        height=600
    )

    fig.show()
