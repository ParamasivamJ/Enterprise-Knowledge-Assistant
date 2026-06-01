"""
Admin Router — dashboard metrics, feedback, and eval scores.
GET  /api/admin/metrics   → latency, cost, usage stats
GET  /api/admin/feedback  → user feedback list
POST /api/admin/feedback  → submit feedback on an answer
GET  /api/admin/documents → document ingestion status
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.database import get_db
from app.models import ChatMessage, Feedback, Document, EvalScore

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Feedback submission ──
class FeedbackRequest(BaseModel):
    message_id: str
    is_positive: bool
    comment: str | None = None


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """User submits thumbs up/down on an assistant answer."""
    # Verify the message exists
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == request.message_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")

    fb = Feedback(
        message_id=request.message_id,
        is_positive=request.is_positive,
        comment=request.comment,
    )
    db.add(fb)
    return {"message": "Feedback recorded. Thank you!"}


# ── Dashboard metrics ──
@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Returns aggregate metrics for the admin dashboard:
    - Total queries, avg latency, avg tokens, feedback ratio, document count.
    """
    # Query stats from chat_messages (assistant messages only)
    stats = await db.execute(
        select(
            func.count(ChatMessage.id).label("total_queries"),
            func.avg(ChatMessage.latency_ms).label("avg_latency_ms"),
            func.avg(ChatMessage.retrieval_latency_ms).label("avg_retrieval_ms"),
            func.avg(ChatMessage.generation_latency_ms).label("avg_generation_ms"),
            func.avg(ChatMessage.input_tokens).label("avg_input_tokens"),
            func.avg(ChatMessage.output_tokens).label("avg_output_tokens"),
            func.avg(ChatMessage.top_retrieval_score).label("avg_retrieval_score"),
        ).where(ChatMessage.role == "assistant")
    )
    row = stats.first()

    # Feedback stats
    feedback_stats = await db.execute(
        select(
            func.count(Feedback.id).label("total_feedback"),
            func.sum(case((Feedback.is_positive == True, 1), else_=0)).label("positive"),
            func.sum(case((Feedback.is_positive == False, 1), else_=0)).label("negative"),
        )
    )
    fb_row = feedback_stats.first()

    # Document count
    doc_count = await db.execute(select(func.count(Document.id)))

    # Eval score averages
    eval_stats = await db.execute(
        select(
            func.avg(EvalScore.faithfulness).label("avg_faithfulness"),
            func.avg(EvalScore.answer_relevancy).label("avg_answer_relevancy"),
            func.avg(EvalScore.context_precision).label("avg_context_precision"),
        )
    )
    eval_row = eval_stats.first()

    return {
        "queries": {
            "total": row.total_queries or 0,
            "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
            "avg_retrieval_ms": round(row.avg_retrieval_ms or 0, 1),
            "avg_generation_ms": round(row.avg_generation_ms or 0, 1),
            "avg_input_tokens": round(row.avg_input_tokens or 0, 1),
            "avg_output_tokens": round(row.avg_output_tokens or 0, 1),
            "avg_retrieval_score": round(row.avg_retrieval_score or 0, 4),
        },
        "feedback": {
            "total": fb_row.total_feedback or 0,
            "positive": fb_row.positive or 0,
            "negative": fb_row.negative or 0,
            "satisfaction_rate": round(
                (fb_row.positive or 0) / max(fb_row.total_feedback or 1, 1) * 100, 1
            ),
        },
        "documents": {
            "total": doc_count.scalar() or 0,
        },
        "evaluation": {
            "avg_faithfulness": round(eval_row.avg_faithfulness or 0, 4),
            "avg_answer_relevancy": round(eval_row.avg_answer_relevancy or 0, 4),
            "avg_context_precision": round(eval_row.avg_context_precision or 0, 4),
        },
    }


@router.get("/recent-queries")
async def get_recent_queries(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get recent chat messages with latency and score data for the dashboard."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.role == "assistant")
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {
            "id": msg.id,
            "session_id": msg.session_id,
            "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
            "sources": msg.sources,
            "model_used": msg.model_used,
            "input_tokens": msg.input_tokens,
            "output_tokens": msg.output_tokens,
            "latency_ms": msg.latency_ms,
            "retrieval_latency_ms": msg.retrieval_latency_ms,
            "generation_latency_ms": msg.generation_latency_ms,
            "top_retrieval_score": msg.top_retrieval_score,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
        for msg in messages
    ]
