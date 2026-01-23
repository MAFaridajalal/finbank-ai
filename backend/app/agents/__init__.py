"""
Agent registry for FinBank AI.
"""

from typing import Type
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent, AgentResult
from app.agents.query_agent import QueryAgent
from app.agents.transaction_agent import TransactionAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.search_agent import SearchAgent
from app.agents.risk_agent import RiskAgent
from app.agents.export_agent import ExportAgent
from app.agents.crud_agent import CRUDAgent
from app.llm import BaseLLMProvider


# Registry of all available agents
AGENT_REGISTRY: dict[str, Type[BaseAgent]] = {
    "query": QueryAgent,
    "transaction": TransactionAgent,
    "analytics": AnalyticsAgent,
    "search": SearchAgent,
    "risk": RiskAgent,
    "export": ExportAgent,
    "crud": CRUDAgent,
}


def get_agent(name: str, db: Session, llm: BaseLLMProvider) -> BaseAgent:
    """
    Get an agent instance by name.

    Args:
        name: The agent name
        db: Database session
        llm: LLM provider

    Returns:
        An agent instance

    Raises:
        ValueError: If agent name is not found
    """
    if name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENT_REGISTRY.keys())}")

    return AGENT_REGISTRY[name](db, llm)


def get_available_agents() -> list[dict]:
    """Get list of available agents with descriptions."""
    return [
        {"name": name, "description": agent_class.description}
        for name, agent_class in AGENT_REGISTRY.items()
    ]


__all__ = [
    "BaseAgent",
    "AgentResult",
    "QueryAgent",
    "TransactionAgent",
    "AnalyticsAgent",
    "SearchAgent",
    "RiskAgent",
    "ExportAgent",
    "CRUDAgent",
    "AGENT_REGISTRY",
    "get_agent",
    "get_available_agents",
]
