"""Strategist Agent — senior startup strategy and business analysis."""

import logging
from backend.routing.model_router import model_router
from backend.agents.prompts import get_system_prompt

logger = logging.getLogger(__name__)

async def run(state: dict) -> dict:
    """Run the Strategist agent on the current state."""
    messages = [
        {"role": "system", "content": get_system_prompt("strategist")},
    ]
    # Add conversation history
    for msg in state.get("messages", []):
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # Get the model for this agent
    model = model_router.get_model_for_agent("strategist")

    # Get response
    full_response = ""
    async for chunk in model_router.chat(model, messages, stream=False, temperature=0.7, max_tokens=2048):
        full_response += chunk

    return {
        **state,
        "strategy": full_response,
        "final_output": full_response,
        "current_agent": "strategist",
    }