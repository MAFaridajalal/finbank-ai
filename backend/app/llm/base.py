"""
Base LLM provider interface for FinBank AI.
All LLM providers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str
    model: str
    tokens_used: Optional[int] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        pass

    async def plan_tasks(self, user_message: str, available_agents: list[str]) -> list[dict]:
        """
        Ask the LLM to plan which agents to use for a user request.
        Returns a list of tasks with agent assignments.
        """
        system_prompt = f"""You are a task planner for a banking AI assistant.
Given a user request, determine which agents to use and what tasks to assign.

Available agents:
- query: For reading customer, account, transaction data (SELECT queries only)
- crud: For creating, updating, or deleting customer records (INSERT, UPDATE, DELETE)
- transaction: For processing deposits, withdrawals, transfers
- analytics: For aggregations, reports, statistics
- search: For finding customers/accounts by name or partial match
- risk: For detecting suspicious transactions, fraud patterns
- export: For generating statements, CSV reports

IMPORTANT ROUTING RULES:
- Use "crud" agent for: add, create, register, update, modify, change, delete, remove customer
- Use "query" agent for: list, show, find, get, display customer data (READ ONLY)
- Use "transaction" agent for: deposit, withdraw, transfer money
- Use "analytics" agent for: calculate, analyze, report, statistics
- Use "search" agent for: search by partial name or account number

Respond with a JSON array of tasks. Each task should have:
- "agent": the agent name
- "task": description of what the agent should do

Example response:
[
  {{"agent": "crud", "task": "Create a new customer named John Smith"}},
  {{"agent": "query", "task": "List all customers"}}
]

Only use agents that are needed. Be specific about the task."""

        response = await self.generate(
            prompt=f"User request: {user_message}",
            system_prompt=system_prompt,
            temperature=0.3,
        )

        # Parse JSON from response
        import json
        try:
            # Extract JSON array from response
            content = response.content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        return []

    async def generate_sql(self, task: str, schema: str) -> str:
        """Generate SQL based on a task and schema."""
        system_prompt = f"""You are a SQL expert. Generate SQL Server (T-SQL) queries.
Given a task description and database schema, generate the appropriate SQL query.

Database Schema:
{schema}

Rules:
- Use proper SQL Server syntax
- Return only the SQL query, no explanations
- Use JOINs when needed to get related data
- Use appropriate WHERE clauses for filtering
- Never use DROP, DELETE, or UPDATE unless explicitly requested for that purpose"""

        response = await self.generate(
            prompt=f"Task: {task}",
            system_prompt=system_prompt,
            temperature=0.2,
        )

        # Extract SQL from response
        content = response.content.strip()
        if content.startswith("```sql"):
            content = content[6:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

    async def synthesize(self, user_message: str, agent_results: dict) -> str:
        """Combine agent results into a natural language response."""
        system_prompt = """You are a helpful banking assistant.
Synthesize the results from various agents into a clear, friendly response.
Format numbers as currency when appropriate.
Use bullet points and formatting for clarity.
Be concise but informative."""

        results_text = "\n".join([
            f"{agent}: {result}"
            for agent, result in agent_results.items()
        ])

        response = await self.generate(
            prompt=f"User asked: {user_message}\n\nAgent results:\n{results_text}",
            system_prompt=system_prompt,
            temperature=0.7,
        )

        return response.content
