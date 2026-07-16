
import pdfplumber

class OcrService:

    """
    Service responsible for performing OCR 
    on uploaded documents while preserving page structures.
    """

    def __init__(self):
        pass

    async def extract_pages(self, file_path: str) -> list[dict]:
        """
        Returns a list of {"page_number": int, "text": str} for each page in the PDF.
        """
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append({"page_number": i, "text": text})
        return pages