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

PharmaSummarizer MVP is an early deterministic prototype for summarizing pharmaceutical and regulatory PDF documents.

It uses local PDF extraction and rule-based document heuristics rather than an LLM.

## What It Demonstrates

- in-memory PDF text extraction with PyMuPDF
- pharmaceutical and regulatory document cleanup
- noise and revision-history filtering
- heuristic title detection
- deterministic extractive summarization
- keyword-guided highlight selection
- Streamlit document-review UI
- regression testing for document-filtering behavior

## Processing Flow

```text
PDF Upload
    ↓
PyMuPDF Text Extraction
    ↓
Noise / Revision Filtering
    ↓
Title Detection
    ↓
Body Sentence Selection
    ↓
Extractive Summary
    ↓
Keyword-Guided Highlights
    ↓
Streamlit Review
