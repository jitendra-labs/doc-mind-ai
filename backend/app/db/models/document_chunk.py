from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.config import config

from ..config import Base


class DocumentChunk(Base):    
    __tablename__ = "document_chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("documents.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)

    # RAG Evaluation Metas
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    char_length: Mapped[int] = mapped_column(Integer, nullable=False)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(config.EMBEDDING_DIM), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    document = relationship("Document", back_populates="chunks")