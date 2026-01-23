"""
Risk Agent for FinBank AI.
Handles fraud detection and suspicious transaction analysis.
"""

from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class RiskAgent(BaseAgent):
    """Agent for detecting suspicious transactions and fraud patterns."""

    name = "risk"
    description = "Detects suspicious transactions, anomalies, and potential fraud"

    async def execute(self, task: str) -> AgentResult:
        """Execute a risk analysis task."""
        try:
            # Generate SQL for risk analysis
            sql = await self.llm.generate_sql(task, self.get_risk_schema())

            # Validate it's a SELECT query
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith("SELECT"):
                return AgentResult(
                    success=False,
                    data=None,
                    message="Risk agent can only execute SELECT queries",
                    sql=sql,
                )

            # Execute the query
            result = self.db.execute(text(sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            # Add risk assessment
            flagged = []
            for row in rows:
                risk_level = self._assess_risk(row)
                row["risk_level"] = risk_level
                if risk_level in ["HIGH", "CRITICAL"]:
                    flagged.append(row)

            return AgentResult(
                success=True,
                data={
                    "all_results": rows,
                    "flagged": flagged,
                    "flagged_count": len(flagged),
                    "total_count": len(rows),
                },
                message=f"Analyzed {len(rows)} transactions, {len(flagged)} flagged for review",
                sql=sql,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Risk analysis failed: {str(e)}",
            )

    def _assess_risk(self, transaction: dict) -> str:
        """Assess risk level for a transaction."""
        amount = float(transaction.get("amount", 0) or 0)

        if amount >= 50000:
            return "CRITICAL"
        elif amount >= 25000:
            return "HIGH"
        elif amount >= 10000:
            return "MEDIUM"
        else:
            return "LOW"

    def get_risk_schema(self) -> str:
        """Get schema optimized for risk queries."""
        return self.get_schema() + """

Risk detection patterns:
- Large transactions: WHERE amount > 10000
- Recent large transactions: WHERE amount > 10000 AND created_at >= DATEADD(day, -7, GETDATE())
- Multiple transactions same day: GROUP BY account_id, CAST(created_at AS DATE) HAVING COUNT(*) > 5
- Unusual withdrawal pattern: WHERE type = 'withdrawal' AND amount > (SELECT AVG(amount) * 3 FROM transactions WHERE type = 'withdrawal')
- New account large withdrawal: accounts opened < 30 days with withdrawals > 5000
- Transfers to new recipients: first-time recipient_account_id

Sort results by amount DESC to show largest first.
Include customer name and account number in results.
"""
