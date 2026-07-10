"""FounderOS Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from frontend."""
    message: str = Field(..., min_length=1, description="User's message")
    agent: str = Field(default="strategist", description="Agent ID to route to")
    context: Optional[str] = Field(None, description="Additional context")
    stream: bool = Field(default=True, description="Whether to stream response")
    conversation_id: Optional[str] = Field(None, description="Conversation thread ID")
    conversation_history: Optional[list[dict[str, str]]] = Field(None, description="Previous messages for context")


class ChatToken(BaseModel):
    """A single streamed token."""
    type: str = "token"
    content: str
    agent: str


class AgentEvent(BaseModel):
    """Agent switch event in stream."""
    type: str = "agent"
    agent: str
    agent_name: str


class StreamDone(BaseModel):
    """Stream completion event."""
    type: str = "done"
    agent: str
    agent_name: str
    total_tokens: int = 0


class AgentInfo(BaseModel):
    """Information about a single agent."""
    id: str
    name: str
    role: str
    description: str
    model: str
    icon: str  # emoji
    color: str  # tailwind color class
    example_prompts: list[str] = []


class KnowledgeIngestRequest(BaseModel):
    """Request to add content to knowledge base."""
    text: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class KnowledgeSearchRequest(BaseModel):
    """Search request for knowledge base."""
    query: str = Field(..., min_length=1)
    n_results: int = Field(default=5, ge=1, le=20)


class KnowledgeResult(BaseModel):
    """A single knowledge base search result."""
    content: str
    metadata: dict[str, Any]
    score: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    dev_mode: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIInfo(BaseModel):
    """API information response."""
    name: str = "FounderOS API"
    version: str = "1.0.0"
    description: str = "Multi-Agent AI Operating System for Startup Founders"
    endpoints: list[dict[str, str]]
    agents: int = 6