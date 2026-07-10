"""RAG Pipeline — ingests, chunks, embeds, and retrieves knowledge."""

import logging
import uuid
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from backend.config import settings
from backend.rag.chroma_store import chroma_store
from backend.rag.chunker import TextChunker

logger = logging.getLogger(__name__)


class RAGPipeline:
    """End-to-end RAG pipeline for FounderOS knowledge base."""

    def __init__(self):
        self.chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True,
                headers={"User-Agent": "FounderOS-Bot/1.0"},
            )
        return self._http_client

    async def ingest_text(
        self, text: str, metadata: Optional[dict] = None
    ) -> int:
        """Ingest raw text into the knowledge base. Returns number of chunks added."""
        if not text or not text.strip():
            return 0

        metadata = metadata or {"source": "manual"}
        chunks = self.chunker.split_text(text, metadata)

        if not chunks:
            return 0

        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Get embeddings
        embeddings = await self._get_embeddings(documents)

        # Store in ChromaDB
        chroma_store.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(f"Ingested {len(chunks)} chunks from text")
        return len(chunks)

    async def ingest_url(self, url: str) -> int:
        """Fetch a URL, extract text, and ingest into knowledge base."""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")

            # Remove scripts, styles, nav, footer
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            if not text:
                logger.warning(f"No text extracted from {url}")
                return 0

            metadata = {
                "source": "url",
                "url": url,
                "title": soup.title.string if soup.title else url,
            }

            return await self.ingest_text(text, metadata)

        except Exception as e:
            logger.error(f"Failed to ingest URL {url}: {e}")
            return 0

    async def ingest_file(self, file_path: str, metadata: Optional[dict] = None) -> int:
        """Read a text/PDF file and ingest it."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            metadata = metadata or {}
            metadata["source"] = "file"
            metadata["filename"] = file_path.split("/")[-1]

            return await self.ingest_text(text, metadata)
        except Exception as e:
            logger.error(f"Failed to ingest file {file_path}: {e}")
            return 0

    async def retrieve(self, query: str, n_results: int = 5) -> list[dict]:
        """Retrieve relevant chunks for a query."""
        if chroma_store.count() == 0:
            return []

        # Embed the query
        query_embeddings = await self._get_embeddings([query])
        query_embedding = query_embeddings[0]

        # Search
        results = chroma_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
        )

        # Format results
        retrieved = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                retrieved.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1.0 - distance,  # Convert distance to similarity score
                })

        return retrieved

    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings from Fireworks API or return dummies in dev mode."""
        if settings.DEV_MODE:
            return [[0.0] * 768 for _ in texts]

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": settings.EMBEDDING_MODEL,
                "input": texts,
            }
            response = await client.post(
                f"{settings.FIREWORKS_BASE_URL}/embeddings",
                json=payload,
                headers={"Authorization": f"Bearer {settings.FIREWORKS_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]

    async def build_startup_kb(self) -> int:
        """Pre-populate knowledge base with foundational startup content."""
        startup_content = """
# FounderOS Startup Knowledge Base

## Y Combinator Startup Advice
The best startups tend to have three things:
1. A problem the founders themselves have experienced
2. A solution that is significantly better than existing alternatives
3. A market that is growing and large enough to build a meaningful company

## Key Startup Metrics
- Monthly Recurring Revenue (MRR): The predictable revenue earned each month
- Annual Recurring Revenue (ARR): MRR x 12
- Customer Acquisition Cost (CAC): Total sales & marketing spend / number of new customers
- Lifetime Value (LTV): Average revenue per customer over their lifetime
- LTV:CAC Ratio: Should be 3:1 or higher for a healthy business
- Churn Rate: Percentage of customers lost per month (target under 5%)
- Net Dollar Retention: Measures expansion revenue from existing customers

## Paul Graham's Startup Advice
"Do things that don't scale" — In the early days, do whatever it takes to make users happy.
"Write software for people like you" — Build what you understand.
"Startup = Growth" — A startup is a company designed to grow fast.

## Fundraising Stages
- Pre-seed: $50K-$500K, typically from angels or pre-seed funds
- Seed: $500K-$3M, from seed funds and early-stage VCs
- Series A: $3M-$15M, from institutional VCs
- Series B: $15M-$50M, growth stage
- Series C+: $50M+, late stage or pre-IPO

## Lean Startup Methodology
1. Build-Measure-Learn feedback loop
2. Minimum Viable Product (MVP) — smallest thing that tests your hypothesis
3. Validated Learning — progress measured by validated learning about customers
4. Innovation Accounting — metrics that guide startup decision-making
5. Pivot or Persevere — when to change direction vs. double down

## Common Startup Mistakes
1. Building a product nobody wants (42% of startups fail for this reason)
2. Running out of cash (29% fail for this)
3. Wrong team (23% fail for this)
4. Getting outcompeted (19% fail for this)
5. Pricing/cost issues (18% fail for this)

## Product-Market Fit
Product-market fit means being in a good market with a product that can satisfy that market.
Signs of PMF:
- Users are pulling the product from you
- Word of mouth is driving growth
- You're seeing organic retention
- Customer satisfaction scores are high

Marc Andreessen: "You can always feel when product-market fit is happening. The customers are buying the product just as fast as you can make it."
"""

        return await self.ingest_text(
            startup_content,
            metadata={"source": "seed", "type": "startup_fundamentals"},
        )

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()


# Singleton
rag_pipeline = RAGPipeline()