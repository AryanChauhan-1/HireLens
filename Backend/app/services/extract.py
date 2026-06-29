import pdfplumber
import re
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from uploaded PDF file
    """

    text = ""

    try:
        # Convert bytes into file-like object
        pdf_stream = BytesIO(file_bytes)

        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        # Clean extracted text
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)

        return text.strip()

    except Exception as e:
        print("PDF Extraction Error:", e)
        return ""
