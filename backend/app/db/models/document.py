from datetime import datetime
from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import Base


class Document(Base):    
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(30)) # "discharge_summary", "lab_report"
    status: Mapped[str] = mapped_column(String(30), default="uploaded")  # uploaded, processing, indexed, failed
    
    page_count: Mapped[int] = mapped_column(Integer)
    raw_text_chars: Mapped[int] = mapped_column(Integer)
    chunk_strategy: Mapped[str] = mapped_column(String, default="fixed")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    chunks = relationship(
        "DocumentChunk", 
        back_populates="document", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )