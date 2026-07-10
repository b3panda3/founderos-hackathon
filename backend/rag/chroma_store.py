"""ChromaDB vector store wrapper for FounderOS."""

import logging
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings

logger = logging.getLogger(__name__)


class ChromaStore:
    """Wrapper around ChromaDB for vector storage and retrieval."""

    def __init__(self):
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection: Optional[chromadb.Collection] = None

    @property
    def client(self) -> chromadb.ClientAPI:
        """Lazy-initialize ChromaDB client."""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at {settings.CHROMA_PERSIST_DIR}")
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the default collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"description": "FounderOS knowledge base"},
            )
            logger.info(f"Collection '{settings.CHROMA_COLLECTION}' ready")
        return self._collection

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """Add documents to the vector store."""
        if not documents:
            return

        metadatas = metadatas or [{}] * len(documents)

        # ChromaDB has a batch size limit, process in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_embeds = embeddings[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]

            self.collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=batch_embeds,
                metadatas=batch_meta,
            )

        logger.info(f"Added {len(documents)} documents to collection")

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> dict:
        """Search for similar documents."""
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count() or 1),
        }
        if where:
            kwargs["where"] = where

        return self.collection.query(**kwargs)

    def delete(self, ids: list[str]) -> None:
        """Delete documents by IDs."""
        if ids:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")

    def count(self) -> int:
        """Return number of documents in collection."""
        return self.collection.count()

    def reset(self) -> None:
        """Delete and recreate the collection (clear all data)."""
        if self._collection is not None:
            self.client.delete_collection(settings.CHROMA_COLLECTION)
            self._collection = None
            logger.info("Collection reset")


# Singleton
chroma_store = ChromaStore()