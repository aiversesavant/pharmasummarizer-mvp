#!/bin/bash

set -euo pipefail

echo "Running PharmaSummarizer MVP smoke checks..."

test -f app.py
test -f summarizer.py
test -f README.md
test -f requirements.txt
test -f requirements-dev.txt
test -f pytest.ini
test -f tests/test_summarizer.py
test -f docs/architecture.md
test -f docs/runbook.md

python -c "import summarizer; print('summarizer import OK')"
python -m compileall -q app.py summarizer.py tests

echo "Smoke checks passed."
