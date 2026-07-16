"""
Local embedding model wrapper. Loaded once (module-level singleton) so we
don't reload the model on every request — this matters even more once you
add concurrent requests.
"""

from sentence_transformers import SentenceTransformer
import anyio  # Standard dependency of FastAPI / Starlette
from app.config import config

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(config.embedding_model)

    def _sync_embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Internal synchronous execution driver."""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of texts asynchronously. 
        Offloads computation to a worker thread so the FastAPI event loop stays free.
        """
        return await anyio.to_thread.run_sync(self._sync_embed_texts, texts)

    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query string asynchronously."""
        res = await self.embed_texts([query])
        return res[0]
