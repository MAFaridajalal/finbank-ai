"""
Query Agent for FinBank AI.
Handles SELECT queries for customer, account, and transaction data.
"""

from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class QueryAgent(BaseAgent):
    """Agent for reading data from the database."""

    name = "query"
    description = "Handles SELECT queries for customer, account, transaction, and loan data"

    async def execute(self, task: str) -> AgentResult:
        """Execute a query task."""
        try:
            # Generate SQL from the task description
            system_prompt = f"""You are a SQL query generator. Generate ONLY valid SQLite SELECT queries.
Database Schema:
{self.get_schema()}

Rules:
- Return ONLY the SQL query, nothing else
- Use SQLite syntax
- Use || for string concatenation
- Use LIMIT and OFFSET for pagination
- For dates, use strftime()
"""

            response = await self.llm.generate(
                prompt=f"Generate a SELECT query for: {task}",
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

            # Validate it's a SELECT query
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith("SELECT"):
                return AgentResult(
                    success=False,
                    data=None,
                    message="Query agent can only execute SELECT queries",
                    sql=sql,
                )

            # Execute the query
            result = self.db.execute(text(sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            return AgentResult(
                success=True,
                data=rows,
                message=f"Found {len(rows)} records",
                sql=sql,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Query failed: {str(e)}",
            )
