from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://docintel:docintel@localhost:5432/docintel"
    SQL_ECHO: bool = False
    # ollama_base_url: str = "http://localhost:11434"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2:3b"
    embedding_model: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # chunking defaults — tune these as you experiment in Phase 4
    chunk_size: int = 800        # characters per chunk (fixed strategy)
    chunk_overlap: int = 150     # overlap between consecutive chunks

    # retrieval defaults
    top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Settings()
