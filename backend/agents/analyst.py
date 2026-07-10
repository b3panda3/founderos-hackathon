"""Analyst Agent — financial analysis, unit economics, and growth modeling."""

import logging
from backend.routing.model_router import model_router
from backend.agents.prompts import get_system_prompt

logger = logging.getLogger(__name__)

async def run(state: dict) -> dict:
    """Run the Analyst agent on the current state."""
    messages = [
        {"role": "system", "content": get_system_prompt("analyst")},
    ]
    # Add conversation history
    for msg in state.get("messages", []):
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # Get the model for this agent
    model = model_router.get_model_for_agent("analyst")

    # Get response — lower temperature for precise, analytical output
    full_response = ""
    async for chunk in model_router.chat(model, messages, stream=False, temperature=0.3, max_tokens=2048):
        full_response += chunk

    return {
        **state,
        "analysis": full_response,
        "final_output": full_response,
        "current_agent": "analyst",
    }