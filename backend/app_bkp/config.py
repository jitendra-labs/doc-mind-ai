from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://docintel:docintel@localhost:5432/docintel"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # chunking defaults — tune these as you experiment in Phase 4
    chunk_size: int = 800        # characters per chunk (fixed strategy)
    chunk_overlap: int = 150     # overlap between consecutive chunks

    # retrieval defaults
    top_k: int = 4

    class Config:
        env_file = ".env"


settings = Settings()
