"""Startup Ecosystem Knowledge Graph using NetworkX."""

import json
import logging
import os
from typing import Optional

import networkx as nx

from backend.graph.schema import Entity, EntityType, Relation, RelationType

logger = logging.getLogger(__name__)

GRAPH_DATA_PATH = "./data/knowledge_graph.json"


class KnowledgeGraph:
    """In-memory knowledge graph for the startup ecosystem."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._load()

    def _load(self):
        """Load graph from disk if exists."""
        if os.path.exists(GRAPH_DATA_PATH):
            try:
                with open(GRAPH_DATA_PATH, "r") as f:
                    data = json.load(f)
                self.graph = nx.node_link_graph(data, directed=True)
                logger.info(f"Loaded knowledge graph with {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.warning(f"Failed to load graph: {e}")

    def _save(self):
        """Persist graph to disk."""
        os.makedirs(os.path.dirname(GRAPH_DATA_PATH), exist_ok=True)
        data = nx.node_link_data(self.graph)
        with open(GRAPH_DATA_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def add_entity(self, entity_type: str, name: str, properties: Optional[dict] = None) -> str:
        """Add an entity node. Returns the entity ID."""
        entity_id = f"{entity_type}_{name.lower().replace(' ', '_')}"
        if entity_id not in self.graph:
            self.graph.add_node(
                entity_id,
                type=entity_type,
                name=name,
                **(properties or {}),
            )
            self._save()
        return entity_id

    def add_relation(self, source_id: str, target_id: str, relation_type: str, properties: Optional[dict] = None) -> None:
        """Add a directed relation between two entities."""
        self.graph.add_edge(source_id, target_id, type=relation_type, **(properties or {}))
        self._save()

    def get_entity(self, entity_id: str) -> Optional[dict]:
        """Get entity details."""
        if entity_id in self.graph:
            node = self.graph.nodes[entity_id]
            return {
                "id": entity_id,
                "name": node.get("name", entity_id),
                "type": node.get("type", "unknown"),
                "properties": {k: v for k, v in node.items() if k not in ("type", "name")},
                "connections": {
                    "outgoing": list(self.graph.successors(entity_id)),
                    "incoming": list(self.graph.predecessors(entity_id)),
                },
            }
        return None

    def find_connections(self, entity_name: str, depth: int = 2) -> dict:
        """Find entities connected to a given entity name (fuzzy match)."""
        matching = [
            n for n in self.graph.nodes
            if entity_name.lower() in self.graph.nodes[n].get("name", "").lower()
        ]

        if not matching:
            return {"query": entity_name, "results": []}

        subgraph_nodes = set(matching)
        for node_id in list(matching):
            # BFS up to depth
            current_level = {node_id}
            for _ in range(depth):
                next_level = set()
                for n in current_level:
                    next_level.update(self.graph.predecessors(n))
                    next_level.update(self.graph.successors(n))
                subgraph_nodes.update(next_level)
                current_level = next_level

        subgraph = self.graph.subgraph(subgraph_nodes)
        nodes = [
            {
                "id": n,
                "name": subgraph.nodes[n].get("name", n),
                "type": subgraph.nodes[n].get("type", "unknown"),
            }
            for n in subgraph.nodes()
        ]
        edges = [
            {
                "source": u,
                "target": v,
                "type": subgraph.edges[u, v].get("type", "related"),
            }
            for u, v in subgraph.edges()
        ]
        return {"query": entity_name, "nodes": nodes, "edges": edges}

    def get_all_entities(self) -> list[dict]:
        """Get all entities."""
        return [
            {
                "id": n,
                "name": self.graph.nodes[n].get("name", n),
                "type": self.graph.nodes[n].get("type", "unknown"),
            }
            for n in self.graph.nodes()
        ]

    def stats(self) -> dict:
        """Get graph statistics."""
        return {
            "total_entities": self.graph.number_of_nodes(),
            "total_relations": self.graph.number_of_edges(),
            "entity_types": dict(nx.degree(self.graph, self.graph.nodes())),
        }


# Singleton
knowledge_graph = KnowledgeGraph()