# FounderOS — Multi-Agent AI Operating System for Startup Founders

> **AMD AI Developer Hackathon — Track 3 (Unicorn/Open Innovation)**

FounderOS is an AI-powered operating system that gives startup founders access to 6 specialized AI agents, each powered by different models optimized for their specific task. From strategic planning to financial analysis, from content creation to technical architecture — FounderOS is the co-founder every founder wishes they had.

All models run on **AMD Instinct GPUs** via Fireworks AI, with optional **local vLLM inference** on AMD GPUs for maximum performance.

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![Models](https://img.shields.io/badge/Models-GLM_5.2%20%7C%20Llama_3.1%20%7C%20Gemma_4-green)
![AMD](https://img.shields.io/badge/GPU-AMD_Instinct_%7C_ROCm_7.2-red)
![Hackathon](https://img.shields.io/badge/Hackathon-AMD_AI_Track_3-orange)

## Architecture

```
┌─────────────────────────────────────────────┐
│              Next.js Frontend                │
│     (Dashboard, Chat UI, Agent Selector)     │
└──────────────────┬──────────────────────────┘
                   │ REST + SSE Streaming
┌──────────────────▼──────────────────────────┐
│              FastAPI Backend                 │
│  ┌───────────────────────────────────────┐  │
│  │        LangGraph Agent Engine         │  │
│  │  ┌─────┐ ┌──────┐ ┌──────┐          │  │
│  │  │Strat│ │Resrch│ │Writer│ ...       │  │
│  │  └──┬──┘ └──┬───┘ └──┬───┘          │  │
│  │     └───────┼────────┘               │  │
│  │     Model Router (FIREWORKS_BASE_URL) │  │
│  └───────────────┬───────────────────────┘  │
│  ┌───────────────┼───────────────────────┐  │
│  │     RAG Pipeline     Knowledge Graph  │  │
│  │     (ChromaDB)       (NetworkX)       │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  Fireworks AI           Local vLLM
  (AMD GPUs, routed      (AMD GPU
  via FIREWORKS_BASE_URL)  direct)
```

## AMD Compute Usage

FounderOS demonstrates AMD compute usage in **two ways**:

### 1. Fireworks AI (Cloud AMD GPUs)
All 6 agents route their LLM inference through **Fireworks AI**, which runs on AMD Instinct GPUs. The app reads:
- `FIREWORKS_BASE_URL` — injected by the hackathon platform, ensures all API calls are tracked as AMD compute
- `ALLOWED_MODELS` — validated at runtime to ensure only approved AMD-hosted models are used

### 2. Local vLLM Inference (Direct AMD GPU)
The `notebooks/amd_gpu_demo.ipynb` notebook demonstrates **direct AMD GPU compute** by:
- Loading and serving an LLM via vLLM 0.16.0 on the AMD cloud instance
- Running inference benchmarks with token throughput and latency metrics
- Connecting to FounderOS via `USE_LOCAL_GPU=true`

See the notebook for step-by-step AMD GPU verification, vLLM deployment, and performance benchmarks.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS | Interactive dashboard with real-time streaming |
| Backend | FastAPI (Python 3.11) | REST API with SSE streaming |
| Agent Orchestration | LangGraph | Multi-agent state management and routing |
| Vector Database | ChromaDB | Semantic search for RAG pipeline |
| Knowledge Graph | NetworkX | Startup ecosystem relationship mapping |
| Primary LLM | GLM 5.2 (Fireworks AI / AMD GPU) | Strategist agent |
| Research LLM | Llama 3.1 70B (Fireworks AI / AMD GPU) | Researcher agent |
| Creative LLM | Mistral Large (Fireworks AI / AMD GPU) | Writer agent |
| Analysis LLM | Qwen 2.5 72B (Fireworks AI / AMD GPU) | Analyst agent |
| Code LLM | DeepSeek V4 Pro (Fireworks AI / AMD GPU) | Coder agent |
| Bonus LLM | Gemma 4 26B (Fireworks AI / AMD GPU) | Coach agent (Bonus Challenge) |
| Local GPU | vLLM 0.16.0 + ROCm 7.2 + PyTorch 2.9 | Optional direct AMD GPU inference |
| Deployment | Docker (linux/amd64) | Containerized single-service deployment |

## The 6 Agents

### 🎯 Strategist (GLM 5.2)
Senior startup strategist providing business strategy, market analysis, competitive landscape, and prioritized action plans.

### 🔍 Researcher (Llama 3.1 70B)
Market research specialist that searches the knowledge base for relevant data, trends, competitor analysis, and opportunities.

### ✍️ Writer (Mistral Large)
Content creator for pitch narratives, investor emails, landing page copy, blog posts, and social media content.

### 📊 Analyst (Qwen 2.5 72B)
Financial analyst providing unit economics, revenue projections, burn rate analysis, runway calculations, and fundraising strategy.

### 💻 Coder (DeepSeek V4 Pro)
Technical architect for MVP design, tech stack recommendations, API design, code generation, and deployment guidance.

### 🧠 Coach (Gemma 4 26B) ⭐ Bonus Challenge
Startup coach and mentor providing decision frameworks, accountability, founder well-being support, and personalized mentorship.

## Setup on AMD Cloud Instance

### Prerequisites
- AMD cloud instance (ROCm 7.2 + vLLM + PyTorch pre-installed)
- A Fireworks AI API key
- Node.js 18+ (for frontend build)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/founderos-hackathon.git
cd founderos-hackathon

# Create virtual environment and install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..
```

### Step 2: Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env — at minimum set:
# FIREWORKS_API_KEY=fw_your-key-here
# DEV_MODE=false  (set to true for zero-cost mock testing)
```

**On the hackathon cloud instance**, `FIREWORKS_BASE_URL` and `ALLOWED_MODELS` are injected automatically. Do not set them manually.

### Step 3: Run the Application

```bash
# Start the backend (serves both API and static frontend)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

### Step 4 (Optional): Enable Local GPU Inference

```bash
# In a separate terminal, start vLLM on the AMD GPU
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 --port 8080 \
  --max-model-len 2048

# Then set in your .env:
# USE_LOCAL_GPU=true
# LOCAL_VLLM_URL=http://localhost:8080/v1
```

### AMD GPU Demo Notebook

Run the `notebooks/amd_gpu_demo.ipynb` notebook on the AMD cloud instance to demonstrate:
- GPU detection and ROCm verification
- vLLM model loading on AMD GPU
- Inference benchmarks (throughput, latency, TTFT)
- GPU memory utilization

## Development Mode (Zero API Cost)

Set `DEV_MODE=true` in your `.env` file. Agents will return realistic mock responses with simulated streaming without making any API calls. Perfect for UI development, testing, and demo preparation.

## API Documentation

### `POST /chat`
Send a message to an agent and receive a streamed response.

**Request:**
```json
{
  "message": "Help me validate my startup idea",
  "agent": "strategist",
  "stream": true,
  "conversation_history": []
}
```

**Response (SSE stream):**
```
data: {"type": "agent", "agent": "strategist", "agent_name": "Strategist"}
data: {"type": "token", "content": "## ", "agent": "strategist"}
data: {"type": "token", "content": "Strategic", "agent": "strategist"}
data: {"type": "done", "agent": "strategist", "agent_name": "Strategist", "total_tokens": 245}
data: [DONE]
```

### `GET /agents`
List all available agents with metadata.

### `GET /health`
Health check endpoint.

### `POST /knowledge`
Add content to the RAG knowledge base.

### `GET /knowledge/search?q=query&n=5`
Semantic search in the knowledge base.

### `GET /graph/entities`
List all entities in the knowledge graph.

### `GET /graph/connections/{entity_name}`
Find connected entities.

## Project Structure

```
founderos-hackathon/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration (reads FIREWORKS_BASE_URL, ALLOWED_MODELS)
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── agents/
│   │   ├── graph.py            # LangGraph agent orchestrator
│   │   ├── prompts.py          # All agent system prompts + metadata
│   │   ├── strategist.py       # Strategist agent
│   │   ├── researcher.py       # Researcher agent (with RAG)
│   │   ├── writer.py           # Writer agent
│   │   ├── analyst.py          # Analyst agent
│   │   ├── coder.py            # Coder agent
│   │   └── coach.py            # Coach agent (Gemma 4)
│   ├── routing/
│   │   └── model_router.py     # Routes to Fireworks (AMD) or local vLLM
│   ├── rag/
│   │   ├── pipeline.py         # RAG ingestion and retrieval
│   │   ├── chroma_store.py     # ChromaDB wrapper
│   │   └── chunker.py          # Text chunking utility
│   └── graph/
│       ├── knowledge_graph.py  # NetworkX knowledge graph
│       ├── seed_data.py        # Startup ecosystem seed data
│       └── api.py              # Graph API endpoints
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx            # Landing page
│   │   ├── dashboard/page.tsx  # Main workspace
│   │   └── agents/page.tsx     # Agent gallery
│   └── package.json
├── notebooks/
│   └── amd_gpu_demo.ipynb      # AMD GPU compute demonstration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Hackathon Compliance

### AMD Compute Usage ✅
1. **Fireworks AI**: All 6 agents use models hosted on AMD Instinct GPUs via Fireworks, with `FIREWORKS_BASE_URL` routing for tracking
2. **Local GPU**: The `amd_gpu_demo.ipynb` notebook demonstrates direct AMD GPU inference using vLLM + ROCm 7.2 + PyTorch 2.9

### Bonus Challenge: Best Use of Gemma 4 ✅
The **Coach agent** is powered by **Gemma 4 26B** via Fireworks AI on AMD GPUs.

### Submission Requirements
- [x] Public GitHub repository
- [x] AMD compute demonstrated (Fireworks API + local vLLM notebook)
- [x] No hardcoded answers
- [x] English only
- [x] Demo video
- [x] Slide deck PDF

## License

MIT License — free to use, modify, and distribute.