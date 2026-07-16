from sqlalchemy.orm import Session
from app_bkp.ocr import extract_pages
from app_bkp.chunking import chunk_text
from app_bkp.embeddings import embed_texts
from app_bkp.models import Document, Chunk


def ingest_document(db: Session, file_path: str, filename: str, chunk_strategy: str = "fixed") -> Document:
    pages = extract_pages(file_path)
    full_text_chars = sum(len(p["text"]) for p in pages)

    document = Document(
        filename=filename,
        page_count=len(pages),
        raw_text_chars=full_text_chars,
        chunk_strategy=chunk_strategy,
    )
    db.add(document)
    db.flush()  # get document.id without committing yet

    # Chunk per-page so we retain accurate page_number attribution for citations.
    all_chunks = []  # list of (content, page_number)
    for page in pages:
        page_chunks = chunk_text(page["text"], strategy=chunk_strategy)
        for c in page_chunks:
            all_chunks.append((c, page["page_number"]))

    if not all_chunks:
        db.commit()
        return document

    contents = [c[0] for c in all_chunks]
    embeddings = embed_texts(contents)

    for idx, ((content, page_number), embedding) in enumerate(zip(all_chunks, embeddings)):
        chunk = Chunk(
            document_id=document.id,
            chunk_index=idx,
            content=content,
            page_number=page_number,
            embedding=embedding,
        )
        db.add(chunk)

    db.commit()
    db.refresh(document)
    return document
