import re
from typing import List

import fitz
import streamlit as st


NOISE_PATTERNS = [
    "www.",
    "email:",
    "phone:",
    "fax:",
    "additional copies are available",
    "office of communications",
    "division of drug information",
    "new hampshire ave",
    "silver spring",
    "reproduction is authorised",
    "see websites for contact details",
    "heads of medicines agencies",
    "an agency of the european union",
    "committee for human medicinal products",
    "page ",
    "table of contents",
    "document history",
    "regulatory history",
    "draft revision",
    "date for coming into effect",
    "final adoption",
    "start of public consultation",
    "end of consultation",
    "adopted by chmp",
    "agreed by the eu network",
    "revision 2 contains the following",
    "changes are integrated directly",
    "current e6(r2) addendum",
    "approval by the cpmp",
    "step 5 corrected version",
    "codification",
    "history date",
    "public consultation",
    "for release for consultation",
    "effective date",
]

TITLE_KEYWORDS = [
    "guideline",
    "best practices",
    "pharmacovigilance",
    "clinical practice",
    "module",
    "drug safety",
]

BODY_START_HINTS = [
    "introduction",
    "objectives",
    "scope",
    "background",
    "purpose",
    "risk-based approach",
    "pharmacovigilance system",
    "clinical practice",
    "the principles of ich gcp",
    "structures and processes",
    "this guideline",
    "this document",
    "information to be contained",
    "executive summary",
    "summary of the applicant",
    "objectives of this guideline",
]


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF uploaded in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts: List[str] = []

    for page in doc:
        page_text = page.get_text()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def clean_preview_text(text: str) -> str:
    """Clean preview text while keeping readable line breaks."""
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned_lines = []

    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def get_clean_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def is_noise_line(line: str) -> bool:
    lowered = line.lower().strip()
    if not lowered:
        return True
    return any(pattern in lowered for pattern in NOISE_PATTERNS)


def normalize_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip()
    sentence = re.sub(r"^\d+\s+", "", sentence)
    sentence = re.sub(r"^[•\-]+\s*", "", sentence)
    return sentence


def split_sentences(text: str) -> List[str]:
    text = text.replace("\n", " ")
    raw = [s.strip() for s in text.split(".") if s.strip()]
    normalized = [normalize_sentence(s) for s in raw]
    return [s for s in normalized if s]


def is_revision_sentence(sentence: str) -> bool:
    lowered = sentence.lower()

    revision_patterns = [
        "revision",
        "draft revision",
        "date for coming into effect",
        "final adoption",
        "agreed by",
        "adopted by",
        "public consultation",
        "start of public consultation",
        "end of consultation",
        "this revision of the module",
        "revision 2 contains the following",
        "changes are integrated directly",
        "document history",
        "regulatory members",
        "current e6(r2) addendum",
        "approval by the cpmp",
        "step 5 corrected version",
        "codification",
    ]

    return any(pattern in lowered for pattern in revision_patterns)


def extract_title(text: str) -> str:
    """Extract a best-effort title from the PDF text."""
    lines = get_clean_lines(text)

    for i, line in enumerate(lines[:80]):
        lowered = line.lower()

        if is_noise_line(line):
            continue

        if any(keyword in lowered for keyword in TITLE_KEYWORDS):
            title_parts = [line]

            for j in range(1, 4):
                if i + j < len(lines):
                    next_line = lines[i + j].strip()
                    next_lower = next_line.lower()

                    if is_noise_line(next_line):
                        continue
                    if len(next_line) > 100:
                        continue
                    if any(x in next_lower for x in [
                        "date",
                        "page",
                        "table of contents",
                        "document history",
                        "draft revision",
                        "adopted by",
                        "public consultation",
                        "committee for human medicinal products",
                        "an agency of the european union",
                        "drug safety",
                    ]):
                        continue

                    title_parts.append(next_line)

            title = " ".join(title_parts).strip()
            title = re.sub(r"\s+", " ", title)

            if title.endswith("Human Drug"):
                title += " and Biological Products"

            return title

    for line in lines:
        if not is_noise_line(line) and len(line) > 10:
            return line

    return "Untitled Document"


def find_body_sentences(text: str) -> List[str]:
    """Find the most meaningful content sentences from the document body."""
    sentences = split_sentences(text)

    meaningful = []
    started = False

    for sentence in sentences:
        lowered = sentence.lower()

        if any(pattern in lowered for pattern in NOISE_PATTERNS):
            continue

        if is_revision_sentence(sentence):
            continue

        if len(sentence) < 50:
            continue

        if not started:
            if any(hint in lowered for hint in BODY_START_HINTS):
                started = True

        if started:
            meaningful.append(sentence)

    if not meaningful:
        for sentence in sentences:
            lowered = sentence.lower()

            if any(pattern in lowered for pattern in NOISE_PATTERNS):
                continue
            if is_revision_sentence(sentence):
                continue
            if len(sentence) < 50:
                continue

            meaningful.append(sentence)

    if not meaningful:
        for sentence in sentences:
            if len(sentence) >= 50:
                meaningful.append(sentence)

    return meaningful


def summarize_text(text: str) -> str:
    """Create a short summary from meaningful body sentences."""
    sentences = find_body_sentences(text)

    if not sentences:
        return "No meaningful summary could be generated from the PDF."

    selected = []
    for sentence in sentences:
        if is_revision_sentence(sentence):
            continue

        selected.append(sentence)

        if len(selected) >= 3:
            break

    if not selected:
        selected = sentences[:3]

    summary = ". ".join(selected).strip()
    if summary and not summary.endswith("."):
        summary += "."

    return summary


def extract_key_highlights(text: str, max_points: int = 5) -> List[str]:
    """Extract important highlights using simple keyword-guided selection."""
    sentences = find_body_sentences(text)

    keywords = [
        "must",
        "should",
        "required",
        "recommended",
        "safety",
        "risk",
        "surveillance",
        "pharmacovigilance",
        "reporting",
        "monitoring",
        "rights",
        "well-being",
        "system",
        "master file",
        "guideline",
        "clinical trial",
        "regulatory authorities",
    ]

    highlights = []
    for sentence in sentences:
        lowered = sentence.lower()

        if is_revision_sentence(sentence):
            continue

        if any(keyword in lowered for keyword in keywords):
            highlights.append(sentence)

        if len(highlights) >= max_points:
            break

    if not highlights:
        for sentence in sentences[:max_points]:
            if not is_revision_sentence(sentence):
                highlights.append(sentence)

    return highlights[:max_points]


st.set_page_config(page_title="PharmaSummarizer MVP", page_icon="💊", layout="wide")

st.title("💊 PharmaSummarizer MVP")
st.write("Upload a pharmaceutical or regulatory PDF and generate a structured summary.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()

    with st.spinner("Extracting and summarizing document..."):
        extracted_text = extract_text_from_pdf(pdf_bytes)
        title = extract_title(extracted_text)
        summary = summarize_text(extracted_text)
        highlights = extract_key_highlights(extracted_text)
        preview_text = clean_preview_text(extracted_text)

    st.subheader("Document Title")
    st.write(title)

    st.subheader("Short Summary")
    st.write(summary)

    st.subheader("Key Highlights")
    if highlights:
        for i, point in enumerate(highlights, start=1):
            st.markdown(f"{i}. {point}")
    else:
        st.write("No key highlights identified.")

    with st.expander("Extracted Text Preview"):
        st.text(preview_text[:4000] if preview_text else "No text extracted.")
else:
    st.info("Please upload a PDF file to begin.")