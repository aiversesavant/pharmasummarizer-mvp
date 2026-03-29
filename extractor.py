import fitz


def extract_summary(file_path: str) -> str:
    doc = fitz.open(file_path)

    text_parts = []
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text_parts.append(page_text)

    text = "\n".join(text_parts).strip()

    if not text:
        return "No readable text found in the uploaded PDF."

    return text[:1500]