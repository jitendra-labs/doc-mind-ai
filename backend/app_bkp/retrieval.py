"""
Retrieval (vector search) and prompt construction (context injection).
Kept as separate functions so you can test/inspect each stage independently —
e.g. call retrieve_chunks() alone to sanity-check retrieval quality before
ever involving the LLM (this is exactly what Phase 2's bare /ask endpoint did).
"""
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from app_bkp.embeddings import embed_query
from app_bkp.config import settings


def retrieve_chunks(db: Session, query: str, top_k: int = None) -> list[dict]:
    top_k = top_k or settings.top_k
    query_embedding = embed_query(query)

    # pgvector cosine distance operator: <=>  (0 = identical, 2 = opposite)
    # We convert to a similarity score (1 - distance) for readability in the response.
    result = db.execute(
        sql_text("""
            SELECT
                c.id,
                c.content,
                c.page_number,
                c.document_id,
                d.filename,
                1 - (c.embedding <=> CAST(:query_embedding AS vector)) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
            ORDER BY c.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
        """),
        {"query_embedding": str(query_embedding), "top_k": top_k},
    )

    rows = result.fetchall()
    return [
        {
            "chunk_id": row.id,
            "content": row.content,
            "page_number": row.page_number,
            "document_id": row.document_id,
            "filename": row.filename,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]


SYSTEM_PROMPT = (
    "You are a careful assistant answering questions about uploaded documents. "
    "Only use information from the provided context to answer. "
    "If the answer is not present in the context, say clearly that the documents "
    "do not contain that information — do not guess or make up an answer. "
    "When you answer, mention which source (filename/page) the information came from."
)


def build_prompt(query: str, chunks: list[dict]) -> str:
    if not chunks:
        context_block = "(No relevant context was retrieved.)"
    else:
        context_block = "\n\n".join(
            f"[Source: {c['filename']}, page {c['page_number']}]\n{c['content']}"
            for c in chunks
        )

    return (
        f"CONTEXT:\n{context_block}\n\n"
        f"QUESTION:\n{query}\n\n"
        f"Answer the question using only the context above. Cite the source filename/page."
    )
