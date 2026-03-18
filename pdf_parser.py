import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from an uploaded PDF file."""
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"
