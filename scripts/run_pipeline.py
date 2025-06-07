import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import subprocess
import time
import os
import subprocess

def run_step(description, command):
    print(f"\n{description}...")
    start = time.time()
    result = subprocess.run(command, shell=True)
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"{description} completed in {elapsed:.2f}s")
    else:
        print(f"{description} failed with exit code {result.returncode}")
        exit(1)

# run full pipeline
run_step("1. Run signal engine", "python scripts/signal_engine.py")
run_step("2. Generate filtered signal plot", "python scripts/filtered_signal_plotter.py")
run_step("3. Run backtest", "python scripts/backtest_strategy.py")

print("\n Pipeline completed successfully.")

Path("scripts").mkdir(parents=True, exist_ok=True)