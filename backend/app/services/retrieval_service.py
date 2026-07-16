from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.document_chunk_repo import DocumentChunkRepository
from app.services.embedding_service import EmbeddingService
from app.core.logging_config import logger


class RetrievalService:

    def __init__(self):
        # Local SentenceTransformer async service
        self.embedding_service = EmbeddingService()
        # Stateless pgvector chunk repository
        self.chunk_repo = DocumentChunkRepository()

    async def retrieve_chunks(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = 4,
        MIN_SIMILARITY: float = 0.50,
        doc_type_filter: Optional[str] = None,
        document_id_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Pure semantic retrieval stage. This can be called completely isolated 
        from the LLM endpoint to check vector matching accuracy and similarity dimensions.
        """
        logger.info(f"Retrieving vector matches for query: '{query[:50]}...'")

        # 1. Transform raw text query to float embedding array
        query_embedding = await self.embedding_service.embed_query(query)

        # 2. Query pgvector store via the repository layer
        matched_records = await self.chunk_repo.vector_similarity_search(
            session=db,
            query_embedding=query_embedding,
            top_k=top_k,
            doc_type_filter=doc_type_filter,
            document_id_filter=document_id_filter
        )

        # 3. Construct clean serialization structures
        structured_chunks = []
        for chunk, distance in matched_records:
            # Convert cosine distance to cosine similarity score for readability (1 = identical)
            similarity_score = round(1.0 - distance, 4)

            # if similarity_score < MIN_SIMILARITY:
            #     continue

            structured_chunks.append({
                "chunk_id": chunk.id,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "document_id": chunk.document_id,
                # Safe checking handles attribute evaluation safely if join isn't eagerly loaded
                "filename": chunk.document.filename if hasattr(chunk, "document") else "Unknown Document",
                "similarity": similarity_score,
            })

        return structured_chunks

    def build_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Constructs the context block matrix to feed directly into the model context window.
        Kept deterministic and separate to support simple assertion test execution.
        """
        if not chunks:
            context_block = "(No relevant context was found in the database matching the evaluation request.)"
        else:
            context_block = "\n\n".join(
                f"[Source: {c['filename']}, Page {c['page_number']}]\n{c['content']}"
                for c in chunks
            )

        return (
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION:\n{query}\n\n"
            f"Answer the question using only the context above. Cite the source filename/page."
        )
    
    # SYSTEM_PROMPT = (
    #     "You are a careful assistant answering questions about uploaded documents. "
    #     "Only use information from the provided context to answer. "
    #     "If the answer is not present in the context, say clearly that the documents "
    #     "do not contain that information — do not guess or make up an answer. "
    #     "When you answer, mention which source (filename/page) the information came from."
    # )
    SYSTEM_PROMPT = """
    You are a clinical document retrieval assistant.

    Answer using ONLY the supplied context.

    Requirements:

    - Ground every factual statement in retrieved context.
    - Do not hallucinate.
    - Do not use prior medical knowledge.
    - If information is unavailable, say so clearly.
    - Include source citations.
    - Maintain patient safety by avoiding assumptions.

    Output JSON:

    {
    "answer": "...",
    "confidence": "high|medium|low",
    "sources": [
        {
        "file": "...",
        "page": 1
        }
    ]
    }
    """