---
title: PharmaSummarizer MVP
emoji: 💊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.44.1"
app_file: app.py
pinned: false
---

# PharmaSummarizer MVP

PharmaSummarizer MVP is a lightweight Streamlit app for pharmaceutical and regulatory PDF summarization.

## Features
- Upload a PDF
- Extract raw text
- Generate a document title
- Generate a short summary
- Extract key highlights
- Show an extracted text preview

## Tech Stack
- Python
- Streamlit
- PyMuPDF

## How to Use
1. Upload a pharmaceutical or regulatory PDF
2. Wait for extraction and summary generation
3. Review the document title, summary, highlights, and preview text

## Project Purpose
This project is the summarization module in the broader PharmaAI platform.

## Notes
- This MVP is designed for lightweight document summarization
- It is separate from:
  - **PharmaRAG** → grounded pharma/regulatory Q&A
  - **CompliBot** → compliance/SOP/process-oriented Q&A