#!/bin/bash

set -euo pipefail

echo "Setting up pharmasummarizer-mvp..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

echo "Setup complete."
echo "Run the app with:"
echo "  streamlit run app.py"
