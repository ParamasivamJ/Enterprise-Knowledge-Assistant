"""
Qdrant Service — manages vector storage and retrieval.
Handles: collection creation, upsert, search, deletion.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue,
    SearchParams,
)
from app.config import get_settings
from functools import lru_cache
import uuid

settings = get_settings()


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Get a cached Qdrant client connection."""
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection():
    """Create the collection if it doesn't exist."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]

    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimension,  # 384 for MiniLM
                distance=Distance.COSINE,
            ),
        )
        print(f"[Qdrant] Created collection: {settings.qdrant_collection}")
    else:
        print(f"[Qdrant] Collection exists: {settings.qdrant_collection}")


def upsert_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    document_id: str,
    filename: str,
) -> int:
    """
    Insert chunk vectors into Qdrant with metadata payload.

    Args:
        chunks: List of chunk dicts from chunking_service
        embeddings: Corresponding embedding vectors
        document_id: UUID of the source document
        filename: Original filename for citation display

    Returns:
        Number of points upserted
    """
    client = get_qdrant_client()

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(uuid.uuid4())
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "char_count": chunk["char_count"],
                },
            )
        )

    # Batch upsert (Qdrant handles batching internally)
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )
    return len(points)


def search_chunks(
    query_vector: list[float],
    top_k: int = None,
    document_id: str = None,
) -> list[dict]:
    """
    Search for similar chunks in Qdrant.

    Args:
        query_vector: The embedded query vector.
        top_k: Number of results to return.
        document_id: Optional filter to search within a specific document.

    Returns:
        List of dicts with text, metadata, and similarity score.
    """
    client = get_qdrant_client()
    top_k = top_k or settings.retrieval_top_k

    # Optional metadata filtering (e.g., search within a specific document)
    search_filter = None
    if document_id:
        search_filter = Filter(
            must=[
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ]
        )

    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
        query_filter=search_filter,
        search_params=SearchParams(hnsw_ef=128, exact=False),
        with_payload=True,
    )
    results = response.points

    return [
        {
            "id": str(hit.id),
            "score": round(hit.score, 4),
            "text": hit.payload.get("text", ""),
            "filename": hit.payload.get("filename", ""),
            "page": hit.payload.get("page", 0),
            "chunk_index": hit.payload.get("chunk_index", 0),
            "document_id": hit.payload.get("document_id", ""),
        }
        for hit in results
    ]


def delete_document_vectors(document_id: str):
    """Delete all vectors belonging to a specific document."""
    client = get_qdrant_client()
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ]
        ),
    )
