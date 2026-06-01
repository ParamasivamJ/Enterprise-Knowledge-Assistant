# Enterprise Knowledge Assistant

> A production-grade RAG system with document upload, citation-aware chat, and an admin evaluation dashboard.

## Architecture

```
┌─────────────┐     ┌──────────────────────────┐     ┌──────────────┐
│  Next.js     │────→│  FastAPI Backend          │────→│  Qdrant      │
│  Frontend    │     │  (Async, Streaming)       │     │  (Docker)    │
│  Port 3000   │     │  Port 8000                │     │  Port 6333   │
└─────────────┘     │                            │     └──────────────┘
                    │  Services:                 │     ┌──────────────┐
                    │  • /api/upload (ingest)    │────→│  PostgreSQL  │
                    │  • /api/chat   (RAG)       │     │  (Docker)    │
                    │  • /api/admin  (metrics)   │     │  Port 5432   │
                    └──────────────────────────┘     └──────────────┘
                              │
                    ┌─────────┴──────────┐
                    │  Groq API          │  (LLM inference - free tier)
                    │  sentence-transformers │  (Embeddings - local CPU)
                    └────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14, Tailwind CSS | Modern React, SSR, streaming support |
| Backend | FastAPI (Python 3.11) | Async, dependency injection, streaming |
| LLM | Groq API (Llama 3) | Free tier, 800+ tok/s, blazing fast |
| Embeddings | sentence-transformers (local) | Free, CPU-friendly, no API limits |
| Vector DB | Qdrant (Docker) | Production-grade, hybrid search, dashboard |
| SQL DB | PostgreSQL (Docker) | Chat logs, eval scores, admin metrics |
| Evaluation | Ragas / DeepEval | Faithfulness, answer relevance scoring |

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Start frontend
cd frontend
npm install
npm run dev
```

## Features

- ✅ PDF/DOCX/TXT upload with automatic parsing
- ✅ Semantic chunking with overlap
- ✅ Hybrid retrieval (dense vectors + metadata filtering)
- ✅ Citation-grounded answers with source references
- ✅ Confidence-based fallback ("not enough evidence")
- ✅ Streaming responses for low perceived latency
- ✅ Admin dashboard with eval scores and latency metrics
- ✅ User feedback (thumbs up/down) on answers
- ✅ Prompt versioning and history
- ✅ Docker-based infrastructure

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/knowledge_assistant
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama-3.1-8b-instant
```
