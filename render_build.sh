#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the CONFLUX Intelligence Pipeline (Quick Mode)
# This generates the CSV files needed by the API without hanging
echo "◈ Starting CONFLUX Intelligence Pipeline (Quick Mode)..."
python wc2026_pipeline.py --all --quick

echo "◈ Build Complete."
