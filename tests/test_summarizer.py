import fitz

from summarizer import (
    clean_preview_text,
    extract_key_highlights,
    extract_text_from_pdf,
    extract_title,
    find_body_sentences,
    summarize_text,
)


REGULATORY_TEXT = """
Pharmacovigilance Guideline

This guideline describes pharmacovigilance requirements for monitoring
medicinal products and reporting safety information to regulatory authorities.

Revision 2 contains the following changes to this pharmacovigilance guideline
and its implementation schedule for regulated organizations.

Adopted by CHMP following review of the revised implementation timeline and
supporting regulatory documentation.

Sponsors should maintain appropriate safety monitoring and reporting procedures
throughout the medicinal product lifecycle.
"""


REVISION_ONLY_TEXT = """
Revision 2 contains the following changes to the implementation schedule for
regulated organizations and associated supporting documentation.

Adopted by CHMP following review of the revised implementation timeline and
supporting regulatory documentation.
"""


LEGITIMATE_REVISION_CONTROL_TEXT = """
This guideline describes document control expectations for regulated quality
systems and associated operating procedures.

Revision control is required to ensure approved procedures remain current,
traceable, and appropriately documented throughout their lifecycle.
"""


def create_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_extract_text_from_pdf_reads_in_memory_pdf():
    pdf_bytes = create_pdf_bytes(
        "Pharmacovigilance monitoring requirements."
    )

    extracted = extract_text_from_pdf(pdf_bytes)

    assert "Pharmacovigilance monitoring requirements" in extracted


def test_clean_preview_collapses_repeated_blank_lines():
    text = "First line\n\n\n\nSecond line"

    cleaned = clean_preview_text(text)

    assert cleaned == "First line\n\nSecond line"


def test_extract_title_prefers_domain_title():
    title = extract_title(REGULATORY_TEXT)

    assert title.startswith("Pharmacovigilance Guideline")


def test_revision_history_is_excluded_from_body_summary_and_highlights():
    body = " ".join(find_body_sentences(REGULATORY_TEXT)).lower()
    summary = summarize_text(REGULATORY_TEXT).lower()
    highlights = " ".join(
        extract_key_highlights(REGULATORY_TEXT)
    ).lower()

    for output in (body, summary, highlights):
        assert "revision 2 contains" not in output
        assert "adopted by chmp" not in output

    assert "pharmacovigilance requirements" in body
    assert "safety monitoring and reporting procedures" in body


def test_revision_only_document_does_not_reenter_fallback():
    sentences = find_body_sentences(REVISION_ONLY_TEXT)

    assert sentences == []

    assert summarize_text(
        REVISION_ONLY_TEXT
    ) == "No meaningful summary could be generated from the PDF."


def test_legitimate_revision_control_content_is_preserved():
    body = " ".join(
        find_body_sentences(LEGITIMATE_REVISION_CONTROL_TEXT)
    ).lower()

    assert "revision control is required" in body


def test_highlight_limit_is_respected():
    highlights = extract_key_highlights(
        REGULATORY_TEXT,
        max_points=1,
    )

    assert len(highlights) <= 1
