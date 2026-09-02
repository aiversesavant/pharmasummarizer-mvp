import re
from typing import List

import fitz


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

REVISION_HISTORY_PATTERNS = [
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
    "regulatory history",
    "regulatory members",
    "current e6(r2) addendum",
    "approval by the cpmp",
    "step 5 corrected version",
    "codification",
    "history date",
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

HIGHLIGHT_KEYWORDS = [
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


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from an in-memory PDF."""

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        text_parts = []

        for page in document:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def clean_preview_text(text: str) -> str:
    """Collapse repeated blank lines while preserving readable structure."""

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
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def is_noise_line(line: str) -> bool:
    lowered = line.lower().strip()

    if not lowered:
        return True

    return any(
        pattern in lowered
        for pattern in NOISE_PATTERNS
    )


def normalize_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip()
    sentence = re.sub(r"^\d+\s+", "", sentence)
    sentence = re.sub(r"^[•\-]+\s*", "", sentence)

    return sentence


def split_sentences(text: str) -> List[str]:
    """Split text using the lightweight rule retained by this MVP."""

    text = text.replace("\n", " ")

    raw = [
        sentence.strip()
        for sentence in text.split(".")
        if sentence.strip()
    ]

    normalized = [
        normalize_sentence(sentence)
        for sentence in raw
    ]

    return [
        sentence
        for sentence in normalized
        if sentence
    ]


def is_revision_sentence(sentence: str) -> bool:
    """Identify regulatory revision/history metadata sentences."""

    lowered = sentence.lower()

    return any(
        pattern in lowered
        for pattern in REVISION_HISTORY_PATTERNS
    )


def extract_title(text: str) -> str:
    """Extract a best-effort title from document text."""

    lines = get_clean_lines(text)

    for index, line in enumerate(lines[:80]):
        lowered = line.lower()

        if is_noise_line(line):
            continue

        if any(
            keyword in lowered
            for keyword in TITLE_KEYWORDS
        ):
            title_parts = [line]

            for offset in range(1, 4):
                if index + offset >= len(lines):
                    continue

                next_line = lines[index + offset].strip()
                next_lower = next_line.lower()

                if is_noise_line(next_line):
                    continue

                if len(next_line) > 100:
                    continue

                excluded_title_fragments = [
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
                ]

                if any(
                    fragment in next_lower
                    for fragment in excluded_title_fragments
                ):
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


def _is_meaningful_sentence(sentence: str) -> bool:
    lowered = sentence.lower()

    if any(
        pattern in lowered
        for pattern in NOISE_PATTERNS
    ):
        return False

    if is_revision_sentence(sentence):
        return False

    return len(sentence) >= 50


def find_body_sentences(text: str) -> List[str]:
    """Find meaningful non-history sentences from the document body."""

    sentences = split_sentences(text)

    meaningful = []
    started = False

    for sentence in sentences:
        lowered = sentence.lower()

        if not _is_meaningful_sentence(sentence):
            continue

        if not started and any(
            hint in lowered
            for hint in BODY_START_HINTS
        ):
            started = True

        if started:
            meaningful.append(sentence)

    if meaningful:
        return meaningful

    meaningful = [
        sentence
        for sentence in sentences
        if _is_meaningful_sentence(sentence)
    ]

    return meaningful


def summarize_text(text: str) -> str:
    """Create a short extractive summary from meaningful body sentences."""

    sentences = find_body_sentences(text)

    if not sentences:
        return "No meaningful summary could be generated from the PDF."

    selected = sentences[:3]

    summary = ". ".join(selected).strip()

    if summary and not summary.endswith("."):
        summary += "."

    return summary


def extract_key_highlights(
    text: str,
    max_points: int = 5,
) -> List[str]:
    """Select important sentences using domain-oriented keywords."""

    sentences = find_body_sentences(text)

    highlights = []

    for sentence in sentences:
        lowered = sentence.lower()

        if any(
            keyword in lowered
            for keyword in HIGHLIGHT_KEYWORDS
        ):
            highlights.append(sentence)

        if len(highlights) >= max_points:
            break

    if not highlights:
        highlights = sentences[:max_points]

    return highlights[:max_points]
