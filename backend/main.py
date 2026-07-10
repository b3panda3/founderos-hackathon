"""FounderOS — Multi-Agent AI Operating System for Startup Founders.

FastAPI application serving both the API and the Next.js static frontend.
AMD AI Developer Hackathon Track 3 (Unicorn/Open Innovation) Submission.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.models.schemas import (
    ChatRequest,
    HealthResponse,
    KnowledgeIngestRequest,
    KnowledgeResult,
    KnowledgeSearchRequest,
)
from backend.agents.graph import AgentGraph, agent_graph
from backend.rag.pipeline import rag_pipeline
from backend.graph.seed_data import seed_knowledge_graph
from backend.graph.api import router as graph_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("founderos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("  FounderOS v1.0.0 — Starting up...")
    logger.info("=" * 60)
    logger.info(f"  DEV_MODE: {settings.DEV_MODE}")
    logger.info(f"  Host: {settings.APP_HOST}:{settings.APP_PORT}")

    # Seed knowledge graph
    try:
        seed_knowledge_graph()
        logger.info("  Knowledge graph seeded")
    except Exception as e:
        logger.warning(f"  Knowledge graph seeding failed: {e}")

    # Build startup knowledge base (RAG)
    try:
        count = await rag_pipeline.build_startup_kb()
        logger.info(f"  Startup KB built: {count} chunks ingested")
    except Exception as e:
        logger.warning(f"  Startup KB build failed: {e}")

    logger.info("=" * 60)
    logger.info("  FounderOS is ready at http://localhost:8000")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("FounderOS shutting down...")
    await rag_pipeline.close()


# Create FastAPI app
app = FastAPI(
    title="FounderOS API",
    description="Multi-Agent AI Operating System for Startup Founders | AMD AI Developer Hackathon Track 3",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Proxy-compatible redirects for React hydration
# React's client-side routing uses /dashboard, /agents (absolute).
# Behind the hackathon proxy, only relative paths work.
# These redirects catch the React-hydrated clicks and send to .html files.
# ============================================================

@app.get("/dashboard", include_in_schema=False)
async def redirect_dashboard():
    return HTMLResponse(
        content=(Path(settings.FRONTEND_DIR) / "dashboard.html").read_text(encoding="utf-8"),
        status_code=200,
    )

@app.get("/agents", include_in_schema=False)
async def redirect_agents():
    return HTMLResponse(
        content=(Path(settings.FRONTEND_DIR) / "agents.html").read_text(encoding="utf-8"),
        status_code=200,
    )


# ============================================================
# API Endpoints
# ============================================================


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Serve the Next.js static frontend (index.html)."""
    index_path = Path(settings.FRONTEND_DIR) / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse(
        content="""
        <div style="display:flex;align-items:center;justify-content:center;height:100vh;
                    background:#020617;color:#f8fafc;font-family:system-ui;text-align:center;">
            <div>
                <h1 style="font-size:2rem;margin-bottom:0.5rem;">FounderOS API</h1>
                <p style="color:#94a3b8;">Frontend not built. Run <code style="background:#1e293b;padding:2px 8px;border-radius:4px;">cd frontend && npm install && npm run build</code></p>
                <p style="margin-top:1rem;"><a href="/docs" style="color:#6366f1;">API Documentation</a> | <a href="/health" style="color:#6366f1;">Health Check</a></p>
            </div>
        </div>
        """,
        status_code=200,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (used by Docker and hackathon validators)."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        dev_mode=settings.DEV_MODE,
        timestamp=datetime.utcnow(),
    )


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Send a message to a specific agent.
    If stream=true, returns SSE (Server-Sent Events) stream.
    If stream=false, returns JSON with the full response.
    """
    if request.stream:
        return StreamingResponse(
            _stream_chat(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming: return full response as JSON
        response_text = await agent_graph.run_agent(
            agent_id=request.agent,
            message=request.message,
            conversation_history=request.conversation_history,
        )
        return {"agent": request.agent, "content": response_text}


async def _stream_chat(request: ChatRequest):
    """Generator for SSE streaming of agent responses."""
    try:
        async for event in agent_graph.stream_agent(
            agent_id=request.agent,
            message=request.message,
            conversation_history=request.conversation_history,
        ):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        error_event = {
            "type": "token",
            "content": f"\n\nAn error occurred: {str(e)}",
            "agent": request.agent,
        }
        yield f"data: {json.dumps(error_event)}\n\n"
        yield "data: [DONE]\n\n"


@app.post("/knowledge")
async def ingest_knowledge(request: KnowledgeIngestRequest):
    """Add content to the knowledge base."""
    total_chunks = 0

    if request.text:
        chunks = await rag_pipeline.ingest_text(
            text=request.text,
            metadata=request.metadata or {"source": "manual"},
        )
        total_chunks += chunks

    if request.url:
        chunks = await rag_pipeline.ingest_url(request.url)
        total_chunks += chunks

    return {
        "status": "ok",
        "chunks_added": total_chunks,
        "total_documents": chroma_store.count(),
    }


@app.get("/knowledge/search")
async def search_knowledge(q: str, n: int = 5):
    """Semantic search in the knowledge base."""
    results = await rag_pipeline.retrieve(q, n_results=n)
    return {
        "query": q,
        "results": results,
        "total": len(results),
    }


# Mount knowledge graph router
app.include_router(graph_router, prefix="/graph")

# Mount static frontend files (Next.js export)
# This serves all /dashboard, /agents, etc. routes from the static build
frontend_dir = Path(settings.FRONTEND_DIR)
if frontend_dir.exists():
    app.mount("/_next", StaticFiles(directory=frontend_dir / "_next"), name="next_static")
    # Serve static assets
    static_dir = frontend_dir
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    logger.info(f"Frontend mounted from {static_dir}")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}. Run 'cd frontend && npm run build' to build it.")


# Import chroma_store for document count in knowledge endpoints
from backend.rag.chroma_store import chroma_store