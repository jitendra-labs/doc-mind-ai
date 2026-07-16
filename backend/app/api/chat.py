from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LlmService

router = APIRouter(prefix="/chats", tags=["Chat"])


@router.get("/debug-retrieve")
async def debug_retrieval(query: str, top_k: int = 3, db: AsyncSession = Depends(get_db_session)):
    """
    Bare diagnostic endpoint to analyze chunking accuracy, table boundaries, 
    and vector extraction qualities independently.
    """
    retrieval_service = RetrievalService()
    chunks = await retrieval_service.retrieve_chunks(db=db, query=query, top_k=top_k)
    prompt_preview = retrieval_service.build_prompt(query, chunks)
    
    return {
        "retrieved_chunks_count": len(chunks),
        "matches": chunks,
        "constructed_prompt_preview": prompt_preview
    }

@router.post("/ask")
def ask(
    query: str = Query(..., description="Your question about the uploaded documents"),
    top_k: int = Query(4),
    db: Session = Depends(get_db_session),
):
    # chunks = retrieve_chunks(db, query, top_k=top_k)
    # prompt = build_prompt(query, chunks)
    # answer = generate(prompt, system=SYSTEM_PROMPT)

    # return {
    #     "query": query,
    #     "answer": answer,
    #     "sources": [
    #         {
    #             "filename": c["filename"],
    #             "page": c["page_number"],
    #             "similarity": round(c["similarity"], 4),
    #         }
    #         for c in chunks
    #     ],
    # }
    return 'Chat Ask api'

@router.post("/ask/stream")
async def ask_question_stream(
    query: str = Query(..., description="Your question about the uploaded documents"),
    top_k: int = Query(4),
    db: AsyncSession = Depends(get_db_session)
):
    retrieval_service = RetrievalService()
    llm_service = LlmService()

    chunks = await retrieval_service.retrieve_chunks(db=db, query=query, top_k=top_k)
    
    # Inject context into the baseline prompt structure
    prompt = retrieval_service.build_prompt(query=query, chunks=chunks)
    
    # Stream tokens immediately back to your browser frontend
    return StreamingResponse(
        llm_service.generate_stream(system_prompt=retrieval_service.SYSTEM_PROMPT, user_prompt=prompt),
        media_type="text/event-stream"
    )