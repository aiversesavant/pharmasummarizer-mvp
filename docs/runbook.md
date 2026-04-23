# Runbook

## Local Setup
1. Activate the local virtual environment if present
2. Install dependencies from `requirements.txt`
3. Start the application from the project root

## Operational Checks
- `app.py` exists
- `extractor.py` exists
- `app/` exists
- `requirements.txt` exists

## Recovery Notes
- if flagged outputs are needed, ensure `data/output/flagged/` exists
- never commit runtime data or secrets
