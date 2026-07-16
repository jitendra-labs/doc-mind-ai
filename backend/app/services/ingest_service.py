from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

# Repository Layer Imports
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.document_chunk_repo import DocumentChunkRepository

from app.services.ocr_service import OcrService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.db.models import Document
from app.core.logging_config import logger


class IngestService:

    def __init__(self):
        self.ocr_service = OcrService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

        self.doc_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()

    async def ingest_document(
        self, 
        session: AsyncSession, 
        file_path: str, 
        filename: str, 
        chunk_strategy: str = "fixed"
    ) -> Document:
        # pages = await self.ocr_service.extract_pages(file_path)
        pages: List[Dict[str, Any]] = await self.ocr_service.extract_pages(file_path)
        full_text_chars = sum(len(p["text"]) for p in pages)

        # Track Document creation using repository layer
        doc_data = {
            "filename": filename,
            "doc_type": "discharge_summary",  # Note: Dynamic derivation can be introduced here later
            "status": "processing",
            "page_count": len(pages),
            "raw_text_chars": full_text_chars,
            "chunk_strategy": chunk_strategy,
        }
        document = await self.doc_repo.create(session, doc_data)

        # Chunk per-page so we retain accurate page_number attribution for citations.
        all_chunks = []  # list of (content, page_number)
        chunk_index = 0

        for page in pages:
            # Chunk processing (Can be modified to async if tokenizers handle worker pooling)
            page_chunks = self.chunking_service.chunk_text(page["text"], strategy=chunk_strategy)

            for text_block in page_chunks:
                # Calculate necessary RAG evaluation dimensions
                char_length = len(text_block)
                
                # Fallback estimate helper if chunking service doesn't provide precise token metrics yet
                token_count = getattr(self.chunking_service, "count_tokens", lambda x: len(x) // 4)(text_block)
                
                all_chunks.append({
                    "document_id": document.id,
                    "chunk_index": chunk_index,
                    "content": text_block,
                    "page_number": page["page_number"],
                    "char_length": char_length,
                    "token_count": token_count
                })
                chunk_index += 1

        if not all_chunks:
            await self.doc_repo.update_status(session, document.id, "failed")
            await session.commit()
            return document
        

        try:
            # Generate batch vector arrays
            contents = [c["content"] for c in all_chunks]
            
            # Ensure your embedding service call is awaited if it calls a network endpoint like Ollama
            embeddings = await self.embedding_service.embed_texts(contents)

            # Map vectors safely back into our structural list
            for idx, embedding in enumerate(embeddings):
                all_chunks[idx]["embedding"] = embedding
            
            # Optimized batch ingestion via chunk repository execution
            await self.chunk_repo.bulk_create_chunks(session, all_chunks)
            
            # Finalize transaction markers
            await self.doc_repo.update_status(session, document.id, "indexed")
            await session.commit()
            await session.refresh(document)

            logger.info(f"Successfully indexed document: {filename}", extra={"document_id": document.id})
            return document, len(all_chunks)

        except Exception as e:
            await session.rollback()
            await self.doc_repo.update_status(session, document.id, "failed")
            await session.commit()
            logger.error(f"Failed to ingest document {filename} due to error: {str(e)}", exc_info=True)
            raise e

