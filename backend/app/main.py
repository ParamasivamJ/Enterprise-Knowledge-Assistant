"""
Enterprise Knowledge Assistant — FastAPI Backend
Main application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.services.qdrant_service import ensure_collection
from app.routers import upload, chat, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle.
    - Creates DB tables on startup
    - Ensures Qdrant collection exists
    """
    print("=" * 60)
    print("  Enterprise Knowledge Assistant — Starting Up")
    print("=" * 60)

    # Initialize PostgreSQL tables
    await init_db()
    print("[DB] PostgreSQL tables ready.")

    # Initialize Qdrant collection
    ensure_collection()
    print("[Qdrant] Vector collection ready.")

    print("[Server] All systems go! API docs at http://localhost:8000/docs")
    print("=" * 60)

    yield  # App runs here

    print("[Server] Shutting down gracefully...")


# ── Create FastAPI App ──
app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="A production-grade RAG system with citations, eval dashboard, and admin controls.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (allow Next.js frontend) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(admin.router)


# ── Health Check ──
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Enterprise Knowledge Assistant",
        "version": "1.0.0",
    }
