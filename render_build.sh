#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

echo "◈ Build Complete (Using pre-committed data)."
