"""
Export Agent for FinBank AI.
Handles generating statements, CSV exports, and reports.
"""

import csv
import io
from datetime import datetime
from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class ExportAgent(BaseAgent):
    """Agent for generating statements, CSV exports, and reports."""

    name = "export"
    description = "Generates account statements, CSV exports, and formatted reports"

    async def execute(self, task: str) -> AgentResult:
        """Execute an export task."""
        try:
            # Determine export type from task
            export_type = await self._determine_export_type(task)

            if export_type == "statement":
                return await self._generate_statement(task)
            elif export_type == "csv":
                return await self._generate_csv(task)
            else:
                return await self._generate_report(task)

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Export failed: {str(e)}",
            )

    async def _determine_export_type(self, task: str) -> str:
        """Determine the type of export from the task."""
        task_lower = task.lower()
        if "statement" in task_lower:
            return "statement"
        elif "csv" in task_lower:
            return "csv"
        else:
            return "report"

    async def _generate_statement(self, task: str) -> AgentResult:
        """Generate an account statement."""
        # Parse account from task
        sql = await self.llm.generate_sql(
            f"Get transactions for the account mentioned in: {task}. "
            "Include transaction_id, type, amount, description, created_at. "
            "Also get account balance and customer name.",
            self.get_schema()
        )

        result = self.db.execute(text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        # Format as statement
        statement = {
            "generated_at": datetime.now().isoformat(),
            "transactions": rows,
            "transaction_count": len(rows),
            "format": "statement",
        }

        return AgentResult(
            success=True,
            data=statement,
            message=f"Generated statement with {len(rows)} transactions",
            sql=sql,
        )

    async def _generate_csv(self, task: str) -> AgentResult:
        """Generate CSV export."""
        # Generate SQL for the requested data
        sql = await self.llm.generate_sql(task, self.get_schema())

        result = self.db.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()

        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        csv_content = output.getvalue()

        return AgentResult(
            success=True,
            data={
                "csv": csv_content,
                "columns": columns,
                "row_count": len(rows),
                "format": "csv",
            },
            message=f"Generated CSV with {len(rows)} rows and {len(columns)} columns",
            sql=sql,
        )

    async def _generate_report(self, task: str) -> AgentResult:
        """Generate a formatted report."""
        # Generate SQL for the report
        sql = await self.llm.generate_sql(task, self.get_schema())

        result = self.db.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        # Format as report
        report = {
            "title": "Financial Report",
            "generated_at": datetime.now().isoformat(),
            "columns": columns,
            "data": rows,
            "row_count": len(rows),
            "format": "report",
        }

        return AgentResult(
            success=True,
            data=report,
            message=f"Generated report with {len(rows)} rows",
            sql=sql,
        )
