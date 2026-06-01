"""
Upload Router — handles document upload, parsing, chunking, and indexing.
POST /api/upload → upload a file
GET  /api/documents → list all documents
DELETE /api/documents/{id} → delete a document and its vectors
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Document, DocumentChunk
from app.config import get_settings
from app.services.document_parser import parse_document
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import upsert_chunks, delete_document_vectors
import os
import uuid

router = APIRouter(prefix="/api", tags=["documents"])
settings = get_settings()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document → parse → chunk → embed → store in Qdrant + Postgres.
    Supports: .pdf, .docx, .txt
    """
    # ── Validate file type ──
    allowed_types = {".pdf", ".docx", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {allowed_types}")

    # ── Save file to disk ──
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # ── Create document record ──
    doc = Document(
        id=file_id,
        filename=file.filename,
        file_type=ext.replace(".", ""),
        file_size_bytes=len(content),
        status="processing",
    )
    db.add(doc)
    await db.flush()  # get the ID without committing

    try:
        # ── Step 1: Parse ──
        pages = parse_document(file_path)
        if not pages:
            raise ValueError("No text could be extracted from the file.")

        # ── Step 2: Chunk ──
        chunks = chunk_pages(pages)
        if not chunks:
            raise ValueError("No chunks generated from the document.")

        # ── Step 3: Embed ──
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)

        # ── Step 4: Store in Qdrant ──
        num_stored = upsert_chunks(chunks, embeddings, file_id, file.filename)

        # ── Step 5: Save chunk metadata to Postgres ──
        for chunk in chunks:
            db_chunk = DocumentChunk(
                document_id=file_id,
                chunk_index=chunk["chunk_index"],
                page_number=chunk["page"],
                content=chunk["text"],
                char_count=chunk["char_count"],
            )
            db.add(db_chunk)

        # ── Update document status ──
        doc.total_chunks = num_stored
        doc.status = "ready"
        await db.flush()

        return {
            "document_id": file_id,
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": num_stored,
            "status": "ready",
        }

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        await db.flush()
        raise HTTPException(500, f"Processing failed: {str(e)}")


@router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all uploaded documents with their status."""
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size_bytes": doc.file_size_bytes,
            "total_chunks": doc.total_chunks,
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }
        for doc in docs
    ]


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a document, its chunks from Postgres, and its vectors from Qdrant."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")

    # Delete from Qdrant
    delete_document_vectors(document_id)

    # Delete from Postgres (cascade deletes chunks too)
    await db.delete(doc)

    # Delete file from disk
    upload_path = os.path.join(settings.upload_dir, f"{document_id}.{doc.file_type}")
    if os.path.exists(upload_path):
        os.remove(upload_path)

    return {"message": f"Document '{doc.filename}' deleted successfully."}
