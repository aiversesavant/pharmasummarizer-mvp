#!/bin/bash
set -e

echo "Running smoke checks..."

test -f app.py
test -f extractor.py
test -d app
test -d data/output/flagged
test -f requirements.txt
test -f README.md
test -f .env.example

echo "Smoke checks passed."
