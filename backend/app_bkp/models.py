from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app_bkp.db import Base
from app_bkp.config import settings


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    doc_type = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    raw_text_chars = Column(Integer, nullable=True)
    chunk_strategy = Column(String, default="fixed")
    uploaded_at = Column(TIMESTAMP, server_default=func.now())

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    embedding = Column(Vector(settings.embedding_dim), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    document = relationship("Document", back_populates="chunks")
