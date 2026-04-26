import pandas as pd
import os

file_path = '/home/jamesuchechi/Projects/ORACLE-26/data/processed/conflux_wc2026.csv'

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
else:
    df = pd.read_csv(file_path)
    df['alpha'] = df['sports'] - df['markets']
    df['abs_alpha'] = df['alpha'].abs()

    high_div = df[df['abs_alpha'] > 0.10].sort_values('alpha', ascending=False)
    print("Top 10 Divergences (Alpha > 0.10):")
    print(high_div[['subject','sports','markets','alpha','conflux_score']].head(10))

