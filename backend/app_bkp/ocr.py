"""
Text extraction from PDFs, page by page.

For CLEAN/digitally-generated PDFs (your synthetic medical docs), pdfplumber's
extract_text() works directly on the embedded text layer — no actual OCR needed.

If/when you move to SCANNED PDFs (real-world messy documents), swap this out for:
    from pdf2image import convert_from_path
    import pytesseract
    images = convert_from_path(path)
    text = pytesseract.image_to_string(images[i])
This is the natural extension point to revisit your earlier OCR project.
"""
import pdfplumber


def extract_pages(file_path: str) -> list[dict]:
    """
    Returns a list of {"page_number": int, "text": str} for each page in the PDF.
    """
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page_number": i, "text": text})
    return pages
