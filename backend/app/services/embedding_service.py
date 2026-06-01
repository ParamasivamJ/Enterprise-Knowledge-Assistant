"""
Embedding Service — generates vector embeddings using sentence-transformers.
Runs 100% locally on CPU. No API key needed. No rate limits.
Model: all-MiniLM-L6-v2 (384 dimensions, ~80MB, fast on CPU).
"""

from sentence_transformers import SentenceTransformer
from app.config import get_settings
import numpy as np
from functools import lru_cache

settings = get_settings()


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """Load the embedding model once and cache it in memory."""
    print(f"[Embeddings] Loading model: {settings.embedding_model}...")
    model = SentenceTransformer(settings.embedding_model)
    print(f"[Embeddings] Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of texts into vectors.
    
    Args:
        texts: List of strings to embed.
    Returns:
        List of embedding vectors (each is a list of floats).
    """
    model = _load_model()
    # normalize_embeddings=True ensures cosine similarity = dot product
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
