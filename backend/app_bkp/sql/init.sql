-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table: one row per uploaded file
CREATE TABLE IF NOT EXISTS documents (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL,
    doc_type        TEXT,                 -- e.g. discharge_summary, lab_report (optional, can be inferred later)
    page_count      INTEGER,
    raw_text_chars  INTEGER,
    chunk_strategy  TEXT DEFAULT 'fixed',  -- 'fixed' or 'recursive' -- lets you compare strategies (Phase 4)
    uploaded_at     TIMESTAMP DEFAULT NOW()
);

-- Chunks table: one row per chunk, each with its own embedding
-- NOTE: vector(384) matches all-MiniLM-L6-v2 embedding dimension.
-- If you switch embedding models later, this dimension MUST match the new model's output size.
CREATE TABLE IF NOT EXISTS chunks (
    id              SERIAL PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    page_number     INTEGER,
    embedding       vector(384),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Index for fast approximate nearest-neighbor search.
-- lists=100 is a reasonable default for small-to-medium datasets; tune as data grows.
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON chunks(document_id);
