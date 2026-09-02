import streamlit as st

from summarizer import (
    clean_preview_text,
    extract_key_highlights,
    extract_text_from_pdf,
    extract_title,
    summarize_text,
)


st.set_page_config(
    page_title="PharmaSummarizer MVP",
    page_icon="💊",
    layout="wide",
)

st.title("💊 PharmaSummarizer MVP")

st.write(
    "Upload a pharmaceutical or regulatory PDF and generate "
    "a deterministic extractive summary."
)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
)

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
        for index, point in enumerate(highlights, start=1):
            st.markdown(f"{index}. {point}")
    else:
        st.write("No key highlights identified.")

    with st.expander("Extracted Text Preview"):
        st.text(
            preview_text[:4000]
            if preview_text
            else "No text extracted."
        )
else:
    st.info("Please upload a PDF file to begin.")
