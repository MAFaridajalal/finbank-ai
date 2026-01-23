"""
Transaction Agent for FinBank AI.
Handles deposits, withdrawals, and transfers.
"""

import uuid
from decimal import Decimal
from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult


class TransactionAgent(BaseAgent):
    """Agent for processing financial transactions."""

    name = "transaction"
    description = "Processes deposits, withdrawals, and transfers between accounts"

    async def execute(self, task: str) -> AgentResult:
        """Execute a transaction task."""
        try:
            # Parse the transaction details from the task
            operation = await self._parse_transaction(task)

            if operation["type"] == "deposit":
                return await self._process_deposit(operation)
            elif operation["type"] == "withdrawal":
                return await self._process_withdrawal(operation)
            elif operation["type"] == "transfer":
                return await self._process_transfer(operation)
            else:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Unknown transaction type: {operation['type']}",
                )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Transaction failed: {str(e)}",
            )

    async def _parse_transaction(self, task: str) -> dict:
        """Parse transaction details from task description."""
        system_prompt = """Parse the transaction request and return a JSON object with:
- type: "deposit", "withdrawal", or "transfer"
- amount: the amount as a number
- account: the source account number (e.g., "CHK-001234")
- to_account: destination account for transfers (optional)
- description: brief description of the transaction

Example response:
{"type": "transfer", "amount": 500, "account": "CHK-001234", "to_account": "SAV-001234", "description": "Monthly savings"}

Return only the JSON object."""

        response = await self.llm.generate(task, system_prompt, temperature=0.1)

        import json
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)

    async def _process_deposit(self, operation: dict) -> AgentResult:
        """Process a deposit transaction."""
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        amount = Decimal(str(operation["amount"]))
        account = operation["account"]

        # Update balance
        self.db.execute(
            text("UPDATE accounts SET balance = balance + :amount WHERE account_number = :account"),
            {"amount": amount, "account": account}
        )

        # Record transaction
        self.db.execute(
            text("""
                INSERT INTO transactions (transaction_id, account_id, type, amount, description, created_at)
                SELECT :txn_id, id, 'deposit', :amount, :description, GETDATE()
                FROM accounts WHERE account_number = :account
            """),
            {"txn_id": txn_id, "amount": amount, "account": account, "description": operation.get("description", "Deposit")}
        )
        self.db.commit()

        # Get new balance
        result = self.db.execute(
            text("SELECT balance FROM accounts WHERE account_number = :account"),
            {"account": account}
        )
        new_balance = result.scalar()

        return AgentResult(
            success=True,
            data={
                "transaction_id": txn_id,
                "type": "deposit",
                "amount": float(amount),
                "account": account,
                "new_balance": float(new_balance),
            },
            message=f"Deposited ${amount} to {account}. New balance: ${new_balance}",
        )

    async def _process_withdrawal(self, operation: dict) -> AgentResult:
        """Process a withdrawal transaction."""
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        amount = Decimal(str(operation["amount"]))
        account = operation["account"]

        # Check balance
        result = self.db.execute(
            text("SELECT balance FROM accounts WHERE account_number = :account"),
            {"account": account}
        )
        balance = result.scalar()

        if balance < amount:
            return AgentResult(
                success=False,
                data=None,
                message=f"Insufficient funds. Balance: ${balance}, Requested: ${amount}",
            )

        # Update balance
        self.db.execute(
            text("UPDATE accounts SET balance = balance - :amount WHERE account_number = :account"),
            {"amount": amount, "account": account}
        )

        # Record transaction
        self.db.execute(
            text("""
                INSERT INTO transactions (transaction_id, account_id, type, amount, description, created_at)
                SELECT :txn_id, id, 'withdrawal', :amount, :description, GETDATE()
                FROM accounts WHERE account_number = :account
            """),
            {"txn_id": txn_id, "amount": amount, "account": account, "description": operation.get("description", "Withdrawal")}
        )
        self.db.commit()

        new_balance = balance - amount

        return AgentResult(
            success=True,
            data={
                "transaction_id": txn_id,
                "type": "withdrawal",
                "amount": float(amount),
                "account": account,
                "new_balance": float(new_balance),
            },
            message=f"Withdrew ${amount} from {account}. New balance: ${new_balance}",
        )

    async def _process_transfer(self, operation: dict) -> AgentResult:
        """Process a transfer between accounts."""
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        amount = Decimal(str(operation["amount"]))
        from_account = operation["account"]
        to_account = operation["to_account"]

        # Check source balance
        result = self.db.execute(
            text("SELECT balance FROM accounts WHERE account_number = :account"),
            {"account": from_account}
        )
        from_balance = result.scalar()

        if from_balance < amount:
            return AgentResult(
                success=False,
                data=None,
                message=f"Insufficient funds. Balance: ${from_balance}, Requested: ${amount}",
            )

        # Debit source account
        self.db.execute(
            text("UPDATE accounts SET balance = balance - :amount WHERE account_number = :account"),
            {"amount": amount, "account": from_account}
        )

        # Credit destination account
        self.db.execute(
            text("UPDATE accounts SET balance = balance + :amount WHERE account_number = :account"),
            {"amount": amount, "account": to_account}
        )

        # Record transaction
        self.db.execute(
            text("""
                INSERT INTO transactions (transaction_id, account_id, type, amount, description, recipient_account_id, created_at)
                SELECT :txn_id, a1.id, 'transfer', :amount, :description, a2.id, GETDATE()
                FROM accounts a1, accounts a2
                WHERE a1.account_number = :from_account AND a2.account_number = :to_account
            """),
            {"txn_id": txn_id, "amount": amount, "from_account": from_account, "to_account": to_account,
             "description": operation.get("description", "Transfer")}
        )
        self.db.commit()

        # Get new balances
        result = self.db.execute(
            text("SELECT balance FROM accounts WHERE account_number = :account"),
            {"account": from_account}
        )
        new_from_balance = result.scalar()

        result = self.db.execute(
            text("SELECT balance FROM accounts WHERE account_number = :account"),
            {"account": to_account}
        )
        new_to_balance = result.scalar()

        return AgentResult(
            success=True,
            data={
                "transaction_id": txn_id,
                "type": "transfer",
                "amount": float(amount),
                "from_account": from_account,
                "to_account": to_account,
                "from_new_balance": float(new_from_balance),
                "to_new_balance": float(new_to_balance),
            },
            message=f"Transferred ${amount} from {from_account} to {to_account}",
        )
