"""
Database models — SQLAlchemy async ORM.
Tables:  
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Document(Base):
    """Tracks every uploaded document and its processing status."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)          # pdf, docx, txt
    file_size_bytes = Column(Integer)
    total_chunks = Column(Integer, default=0)
    status = Column(String, default="processing")       # processing, ready, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Metadata for each chunk stored in Qdrant. The vector itself lives in Qdrant."""
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    char_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")


class ChatMessage(Base):
    """Logs every user query and assistant response for audit + evaluation."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)               # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)                # [{doc_id, chunk_id, page, score}]
    model_used = Column(String, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)          # total response time
    retrieval_latency_ms = Column(Integer, nullable=True)
    generation_latency_ms = Column(Integer, nullable=True)
    top_retrieval_score = Column(Float, nullable=True)   # highest chunk similarity score
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to feedback
    feedback = relationship("Feedback", back_populates="message", uselist=False)


class Feedback(Base):
    """User feedback on assistant answers (thumbs up/down + optional comment)."""
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    message_id = Column(String, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    is_positive = Column(Boolean, nullable=False)        # True = thumbs up
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("ChatMessage", back_populates="feedback")


class EvalScore(Base):
    """Evaluation scores from Ragas/DeepEval runs."""
    __tablename__ = "eval_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    message_id = Column(String, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())


class PromptVersion(Base):
    """Track prompt templates for versioning and rollback."""
    __tablename__ = "prompt_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    version = Column(String, nullable=False, unique=True)   # e.g., "v1.0", "v1.1"
    system_prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
