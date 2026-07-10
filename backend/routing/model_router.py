"""Model Router — routes all LLM requests to Fireworks AI (AMD GPUs).

Supports:
- Standard Fireworks API with hackathon-injected FIREWORKS_BASE_URL
- ALLOWED_MODELS validation (read from env at runtime)
- Optional local vLLM inference on AMD GPU (USE_LOCAL_GPU=true)
- DEV_MODE for zero-cost development with mock streaming
"""

import asyncio
import json
import logging
import os
from typing import AsyncGenerator
import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Parse ALLOWED_MODELS from env (comma-separated, injected by hackathon platform)
_allowed_models_list: list[str] = []
if settings.ALLOWED_MODELS:
    _allowed_models_list = [m.strip() for m in settings.ALLOWED_MODELS.split(",") if m.strip()]
    logger.info(f"Using {len(_allowed_models_list)} allowed models from hackathon platform")

# Agent-to-model mapping (ALL models on Fireworks)
AGENT_MODEL_MAP = {
    "strategist": settings.MODEL_STRATEGIST,
    "researcher": settings.MODEL_RESEARCHER,
    "writer": settings.MODEL_WRITER,
    "analyst": settings.MODEL_ANALYST,
    "coder": settings.MODEL_CODER,
    "coach": settings.MODEL_COACH,
}

# Validate models against ALLOWED_MODELS if provided
def _validate_model(model_id: str) -> str:
    """If ALLOWED_MODELS is set, ensure the model is in the list."""
    if not _allowed_models_list:
        return model_id
    if model_id in _allowed_models_list:
        return model_id
    # Try short name match
    short = model_id.split("/")[-1]
    for allowed in _allowed_models_list:
        if short in allowed or allowed in short:
            logger.info(f"Model {model_id} matched to allowed model {allowed}")
            return allowed
    # Fallback to first allowed model
    logger.warning(f"Model {model_id} not in ALLOWED_MODELS, falling back to {_allowed_models_list[0]}")
    return _allowed_models_list[0]


# Mock responses for DEV_MODE (zero API cost during development)
MOCK_RESPONSES = {
    "strategist": """## Strategic Analysis

Based on your startup challenge, here's my strategic framework:

**1. Core Problem Validation**
Your target market shows clear pain points that aren't adequately addressed. The timing is favorable given recent market shifts.

**2. Competitive Landscape**
I've identified 3-5 direct competitors and 8-10 indirect alternatives. Your key differentiator should focus on your unique advantage in the market.

**3. Recommended Approach**
- Phase 1: Validate with 50 target users in 2 weeks
- Phase 2: Build MVP with core feature set
- Phase 3: Launch to early adopters and iterate

**4. Key Metrics to Track**
- User activation rate (target: 40%+)
- Weekly retention (target: 30%+)
- NPS score (target: 50+)

**5. Risks & Mitigations**
- Risk: Market timing — Mitigation: Run rapid validation experiments
- Risk: Resource constraints — Mitigation: Focus on single core workflow first

Would you like me to deep-dive into any of these areas?""",

    "researcher": """## Research Findings

I've conducted research on your topic. Here are the key findings:

**Market Data:**
- TAM (Total Addressable Market): Estimated at $2.4B globally, growing at 18% CAGR
- SAM (Serviceable Addressable Market): Approximately $340M in your primary geography
- SOM (Serviceable Obtainable Market): $15-25M achievable in Year 1-2

**Key Trends:**
1. AI-native solutions are seeing 3x faster adoption than traditional SaaS
2. Enterprise buyers are shifting from annual to usage-based contracts
3. Regulatory changes are creating new compliance requirements

**Competitor Analysis:**
| Competitor | Funding | Strengths | Weaknesses |
|------------|---------|-----------|------------|
| Competitor A | $45M Series B | Strong brand | Slow innovation |
| Competitor B | $12M Series A | Best UX | Limited features |
| Competitor C | Bootstrapped | Niche focus | Scaling issues |

**Sources:** Market research reports, competitor websites, industry databases.

Shall I dive deeper into any specific area?""",

    "writer": """## Created Content

Here's the polished content based on your request:

**Headline:** Your Startup, Supercharged by AI

**Body:**

In today's fast-moving startup landscape, founders need every advantage they can get. The difference between a startup that thrives and one that merely survives often comes down to execution speed and strategic clarity.

Our approach addresses this by providing AI-powered agents that handle the heavy lifting — from strategic analysis to content creation, financial modeling to technical architecture. Unlike generic AI tools, every agent is purpose-built for startup founders.

The results speak for themselves: early users report 3x faster decision-making, and our multi-agent approach ensures every angle is covered.

**Call to Action:** Ready to transform your founder journey? Start with a focused conversation about your biggest challenge.

---

*This content can be adapted for email, social media, or website copy. Let me know which format and tone you prefer.*""",

    "analyst": """## Financial Analysis

Here's the analytical breakdown:

**Unit Economics:**
- CAC (Customer Acquisition Cost): $45 (target: under $50)
- LTV (Customer Lifetime Value): $540 (12-month avg)
- LTV:CAC Ratio: 12x (healthy — target is 3x+)
- Payback Period: 1.2 months

**Revenue Projections (Monthly):**
| Month | Users | MRR | ARR | Growth |
|-------|-------|-----|-----|--------|
| M1 | 50 | $750 | $9K | — |
| M3 | 300 | $4.5K | $54K | 140% |
| M6 | 1,200 | $18K | $216K | 58% |
| M12 | 5,000 | $75K | $900K | 33% |

**Burn Rate Analysis:**
- Current monthly burn: $15,000
- Runway (at current burn): 20 months
- Break-even target: Month 8-10
- Fundraising recommendation: Raise $500K pre-seed

**Key Metrics Dashboard:**
- MRR Growth Rate: 15% MoM
- Churn Rate: 3.2% (target: <5%)
- Net Revenue Retention: 115%
- Gross Margin: 82%

Shall I model a specific scenario or assumption?""",

    "coder": """## Technical Architecture & Code

Here's the technical guidance:

**Recommended Stack:**
```
Frontend: Next.js 14 + TypeScript + Tailwind CSS
Backend: FastAPI (Python) + LangGraph
Database: PostgreSQL + ChromaDB (vectors)
Deployment: Docker + Railway/Render
```

**Project Structure:**
```
founderos/
├── frontend/           # Next.js app
│   ├── src/app/        # Pages (dashboard, agents)
│   ├── src/components/ # React components
│   └── src/lib/        # API client
├── backend/
│   ├── agents/         # 6 AI agents
│   ├── routing/        # Model router
│   ├── rag/            # RAG pipeline + ChromaDB
│   └── graph/          # Knowledge graph
├── Dockerfile
└── docker-compose.yml
```

**Sample API Endpoint:**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for token in agent_stream(request):
            yield f"data: {json.dumps({'content': token})}\\n\\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Key Technical Decisions:**
1. Use SSE for real-time streaming (simpler than WebSocket, sufficient for chat)
2. ChromaDB for vector search (runs locally, no external service needed)
3. LangGraph for agent orchestration (maintains conversation state)
4. Single Docker container serves both frontend and backend

Want me to elaborate on any component or write specific implementation code?""",

    "coach": """## Startup Coaching Session

Great question. Let me share some frameworks and actionable advice:

**Immediate Priorities (This Week):**
1. **Talk to 10 customers** — Not about your solution, but about their problems
2. **Define your 3 key assumptions** — What MUST be true for this to work?
3. **Set up a simple tracking dashboard** — Measure what matters

**Coaching Framework: The 5 Whys for Startups**

Ask yourself:
1. WHY does this problem exist? → Root cause analysis
2. WHY now? → Timing and market readiness
3. WHY you? → Founder-market fit
4. WHY this solution? → Your unique approach
5. WHY will it scale? → Growth mechanism

**Common Founder Pitfalls to Avoid:**
- Building before validating (spend 80% time on problem, 20% on solution)
- Trying to serve everyone (pick ONE ideal customer profile)
- Ignoring unit economics from day one
- Hiring too fast before product-market fit

**Accountability Check-in:**
- What's the #1 thing you accomplished this week?
- What's the #1 blocker?
- What commitment are you making for next week?

Remember: speed of learning > speed of building. Every conversation with a customer is progress.

How would you like to structure our next coaching session?"""
}


class ModelRouter:
    """Routes all LLM requests to Fireworks AI (running on AMD GPUs).

    Supports hackathon-injected FIREWORKS_BASE_URL and ALLOWED_MODELS.
    Optionally routes to local vLLM server on AMD GPU.
    """

    def __init__(self):
        # Determine base URL — hackathon injection takes precedence
        base_url = settings.FIREWORKS_BASE_URL
        logger.info(f"ModelRouter initialized with FIREWORKS_BASE_URL: {base_url}")

        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {settings.FIREWORKS_API_KEY}"},
            timeout=30.0,
        )

        # Local vLLM client (optional, for AMD GPU direct inference)
        self.local_client: httpx.AsyncClient | None = None
        if settings.USE_LOCAL_GPU:
            self.local_client = httpx.AsyncClient(
                base_url=settings.LOCAL_VLLM_URL,
                timeout=60.0,
            )
            logger.info(f"Local GPU mode enabled: {settings.LOCAL_VLLM_URL}")

    def get_model_for_agent(self, agent_id: str) -> str:
        """Get the Fireworks model ID for a given agent."""
        model = AGENT_MODEL_MAP.get(agent_id, settings.MODEL_STRATEGIST)
        # Validate against ALLOWED_MODELS if set
        return _validate_model(model)

    async def chat(
        self,
        model: str,
        messages: list[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """
        Send a chat completion request and yield response tokens.
        Routes to: local vLLM (if USE_LOCAL_GPU) or Fireworks (AMD GPUs).
        """
        if settings.DEV_MODE:
            # In dev mode, simulate streaming by yielding word-by-word
            agent_id = "strategist"
            for aid, mid in AGENT_MODEL_MAP.items():
                if mid == model:
                    agent_id = aid
                    break
            mock_text = MOCK_RESPONSES.get(agent_id, MOCK_RESPONSES["strategist"])

            if stream:
                words = mock_text.split(" ")
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.02)  # 20ms delay for realistic feel
            else:
                yield mock_text
            return

        # Decide: local GPU or Fireworks API
        use_local = settings.USE_LOCAL_GPU and self.local_client is not None
        client = self.local_client if use_local else self.client

        if use_local:
            # For local vLLM, use the short model name (no "accounts/fireworks/models/" prefix)
            short_model = model.split("/")[-1]
            logger.info(f"Routing to local AMD GPU (vLLM): {short_model}")
            model = short_model
        else:
            logger.info(f"Routing to Fireworks API (AMD): {model}")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if stream:
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        else:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            yield content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via Fireworks API."""
        if settings.DEV_MODE:
            return [[0.0] * 768 for _ in texts]

        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": texts,
        }
        response = await self.client.post("/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    async def close(self):
        """Close HTTP clients."""
        await self.client.aclose()
        if self.local_client:
            await self.local_client.aclose()


# Singleton instance
model_router = ModelRouter()