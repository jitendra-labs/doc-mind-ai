"""
Two chunking strategies, intentionally kept simple and readable so you can
reason about exactly what they do (Phase 4: compare strategies on real docs).

1. fixed_size_chunk   — splits raw text by character count with overlap.
                         Simple, fast, but can cut mid-sentence or mid-table-row.

2. recursive_chunk    — tries to split on natural boundaries first (double
                         newlines / paragraphs), falling back to fixed-size
                         only when a paragraph itself is too long. Generally
                         produces more semantically coherent chunks.
"""
from app_bkp.config import settings


def fixed_size_chunk(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap  # move forward, leaving overlap
    return [c for c in chunks if c]


def recursive_chunk(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    text = text.strip()
    if not text:
        return []

    # Split on paragraph boundaries first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    buffer = ""
    for para in paragraphs:
        # If a single paragraph itself exceeds chunk_size, fall back to fixed-size split on it
        if len(para) > chunk_size:
            if buffer:
                chunks.append(buffer.strip())
                buffer = ""
            chunks.extend(fixed_size_chunk(para, chunk_size, overlap))
            continue

        if len(buffer) + len(para) + 2 <= chunk_size:
            buffer = f"{buffer}\n\n{para}" if buffer else para
        else:
            if buffer:
                chunks.append(buffer.strip())
            buffer = para

    if buffer:
        chunks.append(buffer.strip())

    return chunks


def chunk_text(text: str, strategy: str = "fixed") -> list[str]:
    if strategy == "recursive":
        return recursive_chunk(text)
    return fixed_size_chunk(text)
