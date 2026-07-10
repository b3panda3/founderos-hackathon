"""FastAPI router for the Knowledge Graph endpoints."""

from fastapi import APIRouter, Query
from typing import Optional
from backend.graph.knowledge_graph import knowledge_graph

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("/entities")
async def list_entities(entity_type: Optional[str] = None):
    """List all entities, optionally filtered by type."""
    entities = knowledge_graph.get_all_entities()
    if entity_type:
        entities = [e for e in entities if e["type"] == entity_type]
    return {"entities": entities, "total": len(entities)}


@router.get("/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get entity details and connections."""
    entity = knowledge_graph.get_entity(entity_id)
    if not entity:
        return {"error": "Entity not found"}, 404
    return entity


@router.get("/connections/{entity_name}")
async def find_connections(entity_name: str, depth: int = Query(default=2, ge=1, le=4)):
    """Find entities connected to a given entity name."""
    return knowledge_graph.find_connections(entity_name, depth)


@router.get("/stats")
async def graph_stats():
    """Get knowledge graph statistics."""
    return knowledge_graph.stats()