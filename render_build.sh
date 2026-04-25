#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the CONFLUX Intelligence Pipeline
# This generates the CSV files needed by the API
echo "◈ Starting CONFLUX Intelligence Pipeline..."
python wc2026_pipeline.py --all

echo "◈ Build Complete."
