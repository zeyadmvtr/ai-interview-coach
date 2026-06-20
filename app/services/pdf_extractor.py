"""
Thin wrapper around PyMuPDF for pulling raw text out of an uploaded resume PDF.
Kept separate from ResumeProcessor so the parsing logic isn't coupled to
"how do I get text out of a PDF".
"""
import fitz  # PyMuPDF

from app.core.exceptions import InvalidFileError
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF's bytes, page by page, in order."""
    if not file_bytes:
        raise InvalidFileError("Uploaded file is empty.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises its own RuntimeError/ValueError variants
        raise InvalidFileError(f"Could not open file as PDF: {exc}") from exc

    try:
        if doc.page_count == 0:
            raise InvalidFileError("PDF has no pages.")

        page_count = doc.page_count
        pages_text = [page.get_text("text") for page in doc]
        full_text = "\n".join(pages_text)
    finally:
        doc.close()

    if not full_text.strip():
        raise InvalidFileError(
            "No extractable text found in PDF. The file may be a scanned image "
            "without an OCR text layer."
        )

    logger.info("Extracted %d characters from %d-page PDF", len(full_text), page_count)
    return full_text
