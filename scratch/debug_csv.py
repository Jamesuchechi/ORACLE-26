import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
file_path = PROCESSED_DIR / "conflux_wc2026.csv"
print(f"Reading {file_path}")
df = pd.read_csv(file_path)
print(f"Columns: {df.columns.tolist()}")
print(f"Groups: {df['group'].unique()}")
