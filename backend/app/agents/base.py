"""
Base agent class for FinBank AI.
All agents inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.llm import BaseLLMProvider


class AgentResult(BaseModel):
    """Result from an agent execution."""
    success: bool
    data: Any
    message: str | None = None
    sql: str | None = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    name: str = "base"
    description: str = "Base agent"

    def __init__(self, db: Session, llm: BaseLLMProvider):
        self.db = db
        self.llm = llm

    @abstractmethod
    async def execute(self, task: str) -> AgentResult:
        """Execute the agent's task."""
        pass

    async def generate_sql(self, task: str, schema: str, query_type: str = "SELECT") -> str:
        """Helper method to generate SQL using the LLM."""
        system_prompt = f"""You are a SQL query generator. Generate ONLY valid SQLite {query_type} queries.
Database Schema:
{schema}

Rules:
- Return ONLY the SQL query, nothing else
- Use SQLite syntax
- Use || for string concatenation
- Use LIMIT and OFFSET for pagination
- For dates, use strftime()
- For INSERT/UPDATE, use standard SQL syntax
"""

        response = await self.llm.generate(
            prompt=f"Generate a {query_type} query for: {task}",
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=500
        )

        sql = response.content.strip()
        # Remove markdown code blocks if present
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()

        return sql

    def get_schema(self) -> str:
        """Get the database schema for SQL generation."""
        return """
Tables:
- customer_tiers (id, name, min_balance, benefits)
- branches (id, name, address, city, manager_name)
- customers (id, first_name, last_name, email, phone, address, city, tier_id, branch_id, created_at)
- account_types (id, name, interest_rate, min_balance)
- accounts (id, account_number, customer_id, type_id, balance, status, opened_at)
- transactions (id, transaction_id, account_id, type, amount, description, recipient_account_id, created_at)
- loans (id, loan_number, customer_id, type, principal, interest_rate, term_months, monthly_payment, remaining_balance, status, created_at)
- cards (id, card_number, account_id, type, credit_limit, expiry_date, status)

Relationships:
- customers.tier_id -> customer_tiers.id
- customers.branch_id -> branches.id
- accounts.customer_id -> customers.id
- accounts.type_id -> account_types.id
- transactions.account_id -> accounts.id
- transactions.recipient_account_id -> accounts.id (nullable, for transfers)
- loans.customer_id -> customers.id
- cards.account_id -> accounts.id
"""
