import optuna
import pandas as pd
import matplotlib.pyplot as plt

# Create a new in-memory study (no persistent storage)
study = optuna.create_study(study_name="no_name")

# Plot performance vs. trial
fig = optuna.visualization.matplotlib.plot_optimization_history(study)
fig.imshow()

# Optional: Save performance data
df_trials = study.trials_dataframe()
df_trials.to_csv("logs/optuna_trials.csv", index=False)
