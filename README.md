# PharmaSummarizer MVP

PharmaSummarizer MVP is a lightweight pharmacovigilance extraction demo.

## Features

- adverse event narrative input
- extraction of:
  - drug name
  - adverse event
  - severity
  - outcome
  - seriousness
  - patient age
  - patient sex
- structured JSON output
- Gradio UI

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py