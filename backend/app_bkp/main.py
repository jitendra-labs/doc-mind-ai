import os
import shutil
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app_bkp.db import Base, engine, get_db
from app_bkp.models import Document, Chunk  # noqa: F401 -- needed for Base.metadata
from app_bkp.ingest import ingest_document
from app_bkp.retrieval import retrieve_chunks, build_prompt, SYSTEM_PROMPT
from app_bkp.llm import generate

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Document Intelligence Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; tighten for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Tables are also created via init.sql, but this is a safety net for local dev
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Query("fixed", enum=["fixed", "recursive"]),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    document = ingest_document(db, file_path, file.filename, chunk_strategy=chunk_strategy)

    return {
        "id": document.id,
        "filename": document.filename,
        "page_count": document.page_count,
        "chunk_strategy": document.chunk_strategy,
        "chunks_created": len(document.chunks),
    }


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "page_count": d.page_count,
            "chunk_strategy": d.chunk_strategy,
            "chunks": len(d.chunks),
            "uploaded_at": d.uploaded_at,
        }
        for d in docs
    ]


@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)  # cascade deletes chunks too
    db.commit()
    return {"deleted": document_id}


@app.get("/retrieve")
def retrieve_only(query: str, top_k: int = 4, db: Session = Depends(get_db)):
    """
    Debug endpoint: retrieval WITHOUT generation.
    Useful for sanity-checking retrieval quality in isolation (Phase 2 milestone).
    """
    chunks = retrieve_chunks(db, query, top_k=top_k)
    return {"query": query, "results": chunks}


@app.post("/ask")
def ask(
    query: str = Query(..., description="Your question about the uploaded documents"),
    top_k: int = Query(4),
    db: Session = Depends(get_db),
):
    chunks = retrieve_chunks(db, query, top_k=top_k)
    prompt = build_prompt(query, chunks)
    answer = generate(prompt, system=SYSTEM_PROMPT)

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "filename": c["filename"],
                "page": c["page_number"],
                "similarity": round(c["similarity"], 4),
            }
            for c in chunks
        ],
    }
