"""
Local embedding model wrapper. Loaded once (module-level singleton) so we
don't reload the model on every request — this matters even more once you
add concurrent requests.
"""
from sentence_transformers import SentenceTransformer
from app_bkp.config import settings

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts, returns list of float vectors (length = settings.embedding_dim)."""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
