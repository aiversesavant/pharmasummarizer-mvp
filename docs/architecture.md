# Architecture

## Purpose

PharmaSummarizer MVP is a lightweight deterministic pharmaceutical and regulatory PDF summarization prototype.

It does not use an LLM.

The application demonstrates a rule-based document-processing pipeline built around local PDF extraction, domain-oriented filtering, extractive sentence selection, and keyword-guided highlights.

## Processing Architecture

```text
Uploaded PDF
     ↓
PyMuPDF
     ↓
Raw Document Text
     ↓
Preview Cleanup
     ↓
Noise / Revision-History Filtering
     ↓
Title Detection
     ↓
Body Sentence Selection
     ↓
Extractive Summary
     ↓
Keyword-Guided Highlights
     ↓
Streamlit UI
