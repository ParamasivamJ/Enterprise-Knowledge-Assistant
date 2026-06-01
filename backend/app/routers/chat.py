"""
Chat Router — the core RAG endpoint.
POST /api/chat → ask a question, get a cited answer.
Implements: retrieval → confidence check → generation → logging.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import ChatMessage
from app.config import get_settings
from app.services.embedding_service import embed_query
from app.services.qdrant_service import search_chunks
from app.services.llm_service import generate_answer
import time
import uuid

router = APIRouter(prefix="/api", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str | None = None  # optional: search within a specific document


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[dict]
    session_id: str
    message_id: str
    latency: dict  # breakdown: retrieval_ms, generation_ms, total_ms


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Full RAG pipeline:
    1. Embed the query
    2. Retrieve relevant chunks from Qdrant
    3. Check confidence (fallback if too low)
    4. Generate answer via Groq with citations
    5. Log everything to Postgres
    """
    total_start = time.perf_counter()

    # ── Step 1: Embed query ──
    retrieval_start = time.perf_counter()
    query_vector = embed_query(request.query)

    # ── Step 2: Retrieve chunks ──
    chunks = search_chunks(
        query_vector=query_vector,
        top_k=settings.retrieval_top_k,
        document_id=request.document_id,
    )
    retrieval_ms = int((time.perf_counter() - retrieval_start) * 1000)

    # ── Step 3: Confidence check ──
    top_score = chunks[0]["score"] if chunks else 0.0

    if not chunks or top_score < settings.confidence_threshold:
        # Fallback: not enough evidence
        message_id = str(uuid.uuid4())
        total_ms = int((time.perf_counter() - total_start) * 1000)

        # Log the failed retrieval
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            role="user",
            content=request.query,
        )
        assistant_msg = ChatMessage(
            id=message_id,
            session_id=request.session_id,
            role="assistant",
            content="I don't have enough information in the uploaded documents to answer this question. Please upload relevant documents or rephrase your question.",
            sources=[],
            top_retrieval_score=top_score,
            retrieval_latency_ms=retrieval_ms,
            latency_ms=total_ms,
        )
        db.add(user_msg)
        db.add(assistant_msg)

        return ChatResponse(
            answer="I don't have enough information in the uploaded documents to answer this question. Please upload relevant documents or rephrase your question.",
            confidence=0.0,
            sources=[],
            session_id=request.session_id,
            message_id=message_id,
            latency={"retrieval_ms": retrieval_ms, "generation_ms": 0, "total_ms": total_ms},
        )

    # ── Step 4: Generate answer ──
    generation_start = time.perf_counter()
    result = generate_answer(request.query, chunks)
    generation_ms = int((time.perf_counter() - generation_start) * 1000)

    total_ms = int((time.perf_counter() - total_start) * 1000)

    # ── Step 5: Build source list for response ──
    sources = [
        {
            "filename": c["filename"],
            "page": c["page"],
            "score": c["score"],
            "preview": c["text"][:150] + "..." if len(c["text"]) > 150 else c["text"],
        }
        for c in chunks
    ]

    # ── Step 6: Log to Postgres ──
    message_id = str(uuid.uuid4())

    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=request.session_id,
        role="user",
        content=request.query,
    )
    assistant_msg = ChatMessage(
        id=message_id,
        session_id=request.session_id,
        role="assistant",
        content=result["answer"],
        sources=sources,
        model_used=result.get("model_used"),
        input_tokens=result.get("input_tokens"),
        output_tokens=result.get("output_tokens"),
        latency_ms=total_ms,
        retrieval_latency_ms=retrieval_ms,
        generation_latency_ms=generation_ms,
        top_retrieval_score=top_score,
    )
    db.add(user_msg)
    db.add(assistant_msg)

    return ChatResponse(
        answer=result["answer"],
        confidence=result.get("confidence", 0.5),
        sources=sources,
        session_id=request.session_id,
        message_id=message_id,
        latency={
            "retrieval_ms": retrieval_ms,
            "generation_ms": generation_ms,
            "total_ms": total_ms,
        },
    )
