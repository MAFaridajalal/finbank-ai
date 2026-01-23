"""
Analytics Agent for FinBank AI.
Handles financial aggregations, reports, and statistics.
"""

from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class AnalyticsAgent(BaseAgent):
    """Agent for generating financial reports and analytics."""

    name = "analytics"
    description = "Generates financial aggregations, reports, and statistics"

    async def execute(self, task: str) -> AgentResult:
        """Execute an analytics task."""
        try:
            # Generate SQL with aggregations
            system_prompt = f"""You are a SQL query generator for analytics. Generate ONLY valid SQLite SELECT queries with aggregations.
{self.get_analytics_schema()}

Rules:
- Return ONLY the SQL query, nothing else
- Use SQLite syntax (not T-SQL)
- Use SUM(), COUNT(), AVG() for aggregations
- Use strftime() for date operations
- Use || for string concatenation
"""

            response = await self.llm.generate(
                prompt=f"Generate an analytics SELECT query for: {task}",
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

            # Validate it's a read-only query with aggregations
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith("SELECT"):
                return AgentResult(
                    success=False,
                    data=None,
                    message="Analytics agent can only execute SELECT queries",
                    sql=sql,
                )

            # Execute the query
            result = self.db.execute(text(sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            # Format numeric values
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, (int, float)) and ('balance' in key.lower() or 'amount' in key.lower() or 'total' in key.lower()):
                        row[key] = f"${value:,.2f}" if value else "$0.00"

            return AgentResult(
                success=True,
                data=rows,
                message=f"Generated analytics with {len(rows)} rows",
                sql=sql,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Analytics failed: {str(e)}",
            )

    def get_analytics_schema(self) -> str:
        """Get schema optimized for analytics queries."""
        return self.get_schema() + """

Common analytics patterns (SQLite):
- Total balance: SUM(balance)
- Transaction count: COUNT(*)
- Average amount: AVG(amount)
- Group by month: GROUP BY strftime('%Y-%m', created_at)
- Group by branch: GROUP BY b.name
- Group by customer tier: GROUP BY ct.name
- Recent 30 days: WHERE created_at >= date('now', '-30 days')
- This month: WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
"""
