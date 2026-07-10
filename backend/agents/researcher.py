"""Researcher Agent — market research with RAG pipeline."""

import logging
from backend.routing.model_router import model_router
from backend.rag.pipeline import rag_pipeline
from backend.agents.prompts import get_system_prompt

logger = logging.getLogger(__name__)

async def run(state: dict) -> dict:
    """Run the Researcher agent — searches knowledge base for relevant context."""
    user_input = state.get("user_input", "")

    # Search knowledge base for relevant context
    context = ""
    try:
        results = await rag_pipeline.retrieve(user_input, n_results=5)
        if results:
            context = "\n\n".join([f"[Source: {r['metadata'].get('source', 'unknown')}]\n{r['content']}" for r in results])
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")

    messages = [
        {"role": "system", "content": get_system_prompt("researcher")},
    ]

    # If we have RAG context, add it as a system message
    if context:
        messages.append({
            "role": "system",
            "content": f"Here is relevant information from the FounderOS knowledge base:\n\n{context}\n\nUse this information to enhance your research. Cite sources where applicable."
        })

    # Add conversation history
    for msg in state.get("messages", []):
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    model = model_router.get_model_for_agent("researcher")

    full_response = ""
    async for chunk in model_router.chat(model, messages, stream=False, temperature=0.5, max_tokens=2500):
        full_response += chunk

    return {
        **state,
        "research_data": full_response,
        "final_output": full_response,
        "current_agent": "researcher",
    }