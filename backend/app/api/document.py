import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status

from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.db.repositories.document_repo import DocumentRepository

from app.services.ingest_service import IngestService

router = APIRouter(prefix="/documents", tags=["Document"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post('/upload')
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Query("fixed", enum=["fixed", "recursive"]),
    session: Session = Depends(get_db_session),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ingest = IngestService()
    document, chunks_count = await ingest.ingest_document(session, file_path, file.filename, chunk_strategy)
    
    return {
        "id": document.id,
        "filename": document.filename,
        "page_count": document.page_count,
        "chunk_strategy": document.chunk_strategy,
        "chunks_created": chunks_count,
    }

@router.get("/")
async def list_documents(session: Session = Depends(get_db_session)):
    document_repository = DocumentRepository()
    docs_with_counts = await document_repository.list_documents_with_chunk_counts(db=session)
    
    return {
        'success': True,
        'data': [
            {
                "id": doc.id,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "chunk_strategy": doc.chunk_strategy,
                "chunks": chunk_count,  # Safe primitive integer, no relational traversal!
                "created_at": doc.created_at,
            }
            for doc, chunk_count in docs_with_counts
        ]
    }


@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: int, db: Session = Depends(get_db_session)):
    document_repository = DocumentRepository()
    
    # Check existence and fetch first using our stateless repository pattern
    doc = await document_repository.get_by_id(db, id=document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Document with ID {document_id} not found"
        )
        
    # Execute delete via repository abstraction
    await document_repository.delete(db, id=document_id)
    
    # Commit the transaction safely to trigger the database cascade
    await db.commit()
    
    return {
        "success": True,
        "message": f"Successfully deleted document and all associated text chunks.",
        "deleted_document_id": document_id
    }