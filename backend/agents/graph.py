"""LangGraph Multi-Agent Graph — orchestrates all 6 FounderOS agents."""

import logging
from typing import AsyncGenerator, Optional

from backend.agents import strategist, researcher, writer, analyst, coder, coach
from backend.agents.prompts import AGENT_INFO, get_system_prompt
from backend.routing.model_router import model_router, AGENT_MODEL_MAP

logger = logging.getLogger(__name__)

# Agent module mapping
AGENT_MODULES = {
    "strategist": strategist,
    "researcher": researcher,
    "writer": writer,
    "analyst": analyst,
    "coder": coder,
    "coach": coach,
}

# Default state for a new conversation
def create_initial_state(user_message: str, agent_id: str = "strategist") -> dict:
    """Create the initial state for a new agent conversation."""
    return {
        "messages": [{"role": "user", "content": user_message}],
        "user_input": user_message,
        "current_agent": agent_id,
        "strategy": None,
        "research_data": None,
        "content": None,
        "analysis": None,
        "code": None,
        "coaching": None,
        "final_output": None,
    }


class AgentGraph:
    """Orchestrates the FounderOS multi-agent system."""

    def get_agents(self) -> list[dict]:
        """Return list of all available agents with metadata."""
        agents = []
        for agent_id, info in AGENT_INFO.items():
            agents.append({
                "id": agent_id,
                "name": info["name"],
                "role": info["role"],
                "description": info["description"],
                "model": AGENT_MODEL_MAP.get(agent_id, "unknown"),
                "icon": info["icon"],
                "color": info["color"],
                "example_prompts": info["example_prompts"],
            })
        return agents

    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get info for a specific agent."""
        info = AGENT_INFO.get(agent_id)
        if not info:
            return None
        return {
            "id": agent_id,
            "name": info["name"],
            "role": info["role"],
            "description": info["description"],
            "model": AGENT_MODEL_MAP.get(agent_id, "unknown"),
            "icon": info["icon"],
            "color": info["color"],
            "example_prompts": info["example_prompts"],
        }

    async def run_agent(self, agent_id: str, message: str, conversation_history: Optional[list[dict]] = None) -> str:
        """
        Run a single agent and return its full response.
        This is the main method called by the API.
        """
        if agent_id not in AGENT_MODULES:
            logger.warning(f"Unknown agent '{agent_id}', falling back to strategist")
            agent_id = "strategist"

        module = AGENT_MODULES[agent_id]

        # Build state
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        state = {
            "messages": messages,
            "user_input": message,
            "current_agent": agent_id,
            "strategy": None,
            "research_data": None,
            "content": None,
            "analysis": None,
            "code": None,
            "coaching": None,
            "final_output": None,
        }

        try:
            result = await module.run(state)
            return result.get("final_output", "I wasn't able to generate a response. Please try again.")
        except Exception as e:
            logger.error(f"Agent '{agent_id}' failed: {e}", exc_info=True)
            return f"⚠️ An error occurred while the {AGENT_INFO[agent_id]['name']} agent was processing your request. Please try again or choose a different agent. Error: {str(e)}"

    async def stream_agent(self, agent_id: str, message: str, conversation_history: Optional[list[dict]] = None) -> AsyncGenerator[dict, None]:
        """
        Run a single agent and stream the response token by token.
        Yields dicts like: {"type": "token", "content": "..."} or {"type": "done"}
        """
        if agent_id not in AGENT_MODULES:
            agent_id = "strategist"

        agent_info = AGENT_INFO[agent_id]
        module = AGENT_MODULES[agent_id]

        # Yield agent start event
        yield {
            "type": "agent",
            "agent": agent_id,
            "agent_name": agent_info["name"],
        }

        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        # Build messages with system prompt
        full_messages = [
            {"role": "system", "content": get_system_prompt(agent_id)},
        ]

        # Add RAG context for researcher
        if agent_id == "researcher":
            try:
                from backend.rag.pipeline import rag_pipeline
                results = await rag_pipeline.retrieve(message, n_results=5)
                if results:
                    context = "\n\n".join([
                        f"[Source: {r['metadata'].get('source', 'unknown')}]\n{r['content']}"
                        for r in results
                    ])
                    full_messages.append({
                        "role": "system",
                        "content": f"Relevant knowledge base context:\n\n{context}\n\nUse this to enhance your research.",
                    })
            except Exception as e:
                logger.warning(f"RAG context failed: {e}")

        for msg in messages:
            full_messages.append(msg)

        model = model_router.get_model_for_agent(agent_id)

        # Temperature per agent type
        temperatures = {"writer": 0.8, "analyst": 0.3, "coder": 0.2, "coach": 0.7}
        temperature = temperatures.get(agent_id, 0.7)

        total_tokens = 0
        try:
            async for chunk in model_router.chat(
                model, full_messages, stream=True, temperature=temperature, max_tokens=2048
            ):
                if chunk:
                    total_tokens += len(chunk.split())
                    yield {
                        "type": "token",
                        "content": chunk,
                        "agent": agent_id,
                    }
        except Exception as e:
            logger.error(f"Streaming failed for agent '{agent_id}': {e}")
            yield {
                "type": "token",
                "content": f"\n\n⚠️ Error: {str(e)}",
                "agent": agent_id,
            }

        yield {
            "type": "done",
            "agent": agent_id,
            "agent_name": agent_info["name"],
            "total_tokens": total_tokens,
        }

    async def run_multi_agent(self, message: str) -> dict:
        """
        Run the full multi-agent pipeline: Strategist → Researcher → Writer → Output
        Used for complex queries that benefit from multiple perspectives.
        Returns combined output.
        """
        results = {}

        # Step 1: Strategist
        state = create_initial_state(message, "strategist")
        result = await strategist.run(state)
        results["strategy"] = result.get("final_output", "")

        # Step 2: Researcher (with context from strategist)
        research_message = f"Based on this strategic analysis:\n\n{results['strategy'][:500]}\n\nNow research: {message}"
        state = create_initial_state(research_message, "researcher")
        result = await researcher.run(state)
        results["research"] = result.get("final_output", "")

        # Step 3: Coach (synthesis and actionable advice)
        coach_message = f"A founder asked: {message}\n\nStrategic analysis:\n{results['strategy'][:300]}\n\nResearch findings:\n{results['research'][:300]}\n\nProvide coaching advice synthesizing these insights."
        state = create_initial_state(coach_message, "coach")
        result = await coach.run(state)
        results["coaching"] = result.get("final_output", "")

        return results


# Singleton instance
agent_graph = AgentGraph()