import pandas as pd

def apply_signal_filters(df):
    # Example: suppress signals when volatility too high
    if "volatility_zscore" in df.columns:
        df.loc[df["volatility_zscore"] > 2, "filtered_signal"] = 0
    return df
