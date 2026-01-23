"""
Search Agent for FinBank AI.
Handles full-text and partial match searches for customers and accounts.
"""

from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class SearchAgent(BaseAgent):
    """Agent for searching customers, accounts, and other entities."""

    name = "search"
    description = "Searches for customers, accounts by name, account number, or partial match"

    async def execute(self, task: str) -> AgentResult:
        """Execute a search task."""
        try:
            # Generate SQL with LIKE patterns
            system_prompt = f"""You are a SQL query generator for search operations. Generate ONLY valid SQLite SELECT queries.
{self.get_search_schema()}

Rules:
- Return ONLY the SQL query, nothing else
- Use LIKE with % wildcards for partial matches
- Use LOWER() for case-insensitive searches
- Use SQLite syntax
"""

            response = await self.llm.generate(
                prompt=f"Generate a search SELECT query for: {task}",
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
                    message="Search agent can only execute SELECT queries",
                    sql=sql,
                )

            # Execute the query
            result = self.db.execute(text(sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            return AgentResult(
                success=True,
                data=rows,
                message=f"Found {len(rows)} matching records",
                sql=sql,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Search failed: {str(e)}",
            )

    def get_search_schema(self) -> str:
        """Get schema optimized for search queries."""
        return self.get_schema() + """

Search patterns:
- Partial name match: WHERE first_name LIKE '%john%' OR last_name LIKE '%john%'
- Account number search: WHERE account_number LIKE 'CHK-%'
- Email search: WHERE email LIKE '%@example.com'
- City search: WHERE city LIKE '%seattle%'
- Case insensitive: Use LOWER() function

Always use LIKE with % wildcards for partial matches.
Use ILIKE or LOWER() for case-insensitive searches.
"""
