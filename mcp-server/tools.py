"""
Banking tools for MCP server.
Provides tools for querying customers, accounts, transactions, and more.
"""

from typing import Any
import httpx

# Backend API URL
BACKEND_URL = "http://localhost:8000"


async def get_customer(customer_id: int) -> dict[str, Any]:
    """Get customer details by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/data/customers/{customer_id}")
        if response.status_code == 200:
            return response.json()
        return {"error": f"Customer {customer_id} not found"}


async def search_customers(query: str) -> dict[str, Any]:
    """Search customers by name or email."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/data/customers",
            params={"search": query}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Search failed"}


async def get_account(account_number: str) -> dict[str, Any]:
    """Get account details by account number."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/data/accounts/{account_number}")
        if response.status_code == 200:
            return response.json()
        return {"error": f"Account {account_number} not found"}


async def get_customer_accounts(customer_id: int) -> dict[str, Any]:
    """Get all accounts for a customer."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/data/accounts",
            params={"customer_id": customer_id}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"No accounts found for customer {customer_id}"}


async def get_account_transactions(
    account_number: str,
    limit: int = 20
) -> dict[str, Any]:
    """Get recent transactions for an account."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/data/transactions",
            params={"account_number": account_number, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"No transactions found for account {account_number}"}


async def transfer_funds(
    from_account: str,
    to_account: str,
    amount: float,
    description: str = "Transfer"
) -> dict[str, Any]:
    """Transfer funds between accounts."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/transactions/transfer",
            json={
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "description": description
            }
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Transfer failed", "details": response.text}


async def deposit(
    account_number: str,
    amount: float,
    description: str = "Deposit"
) -> dict[str, Any]:
    """Deposit funds into an account."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/transactions/deposit",
            json={
                "account_number": account_number,
                "amount": amount,
                "description": description
            }
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Deposit failed", "details": response.text}


async def withdraw(
    account_number: str,
    amount: float,
    description: str = "Withdrawal"
) -> dict[str, Any]:
    """Withdraw funds from an account."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/transactions/withdraw",
            json={
                "account_number": account_number,
                "amount": amount,
                "description": description
            }
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Withdrawal failed", "details": response.text}


async def get_account_balance(account_number: str) -> dict[str, Any]:
    """Get current balance for an account."""
    account = await get_account(account_number)
    if "error" in account:
        return account
    return {
        "account_number": account_number,
        "balance": account.get("balance", 0),
        "type": account.get("type", "Unknown")
    }


async def get_branch_stats() -> dict[str, Any]:
    """Get statistics for all branches."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/dashboard/stats")
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to get branch stats"}


async def flag_transaction(
    transaction_id: str,
    reason: str
) -> dict[str, Any]:
    """Flag a transaction for review."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/risk/flag",
            json={
                "transaction_id": transaction_id,
                "reason": reason
            }
        )
        if response.status_code == 200:
            return response.json()
        return {"success": True, "message": f"Transaction {transaction_id} flagged: {reason}"}


async def get_flagged_transactions(days: int = 7) -> dict[str, Any]:
    """Get flagged/suspicious transactions from the past N days."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/risk/flagged",
            params={"days": days}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to get flagged transactions"}


# Tool definitions for MCP
TOOLS = {
    "get_customer": {
        "function": get_customer,
        "description": "Get customer details by their ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique customer ID"
                }
            },
            "required": ["customer_id"]
        }
    },
    "search_customers": {
        "function": search_customers,
        "description": "Search for customers by name or email",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (name or email)"
                }
            },
            "required": ["query"]
        }
    },
    "get_account": {
        "function": get_account,
        "description": "Get account details by account number",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The account number (e.g., CHK-001234)"
                }
            },
            "required": ["account_number"]
        }
    },
    "get_customer_accounts": {
        "function": get_customer_accounts,
        "description": "Get all accounts belonging to a customer",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The customer ID"
                }
            },
            "required": ["customer_id"]
        }
    },
    "get_account_transactions": {
        "function": get_account_transactions,
        "description": "Get recent transactions for an account",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The account number"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of transactions to return",
                    "default": 20
                }
            },
            "required": ["account_number"]
        }
    },
    "transfer_funds": {
        "function": transfer_funds,
        "description": "Transfer funds between two accounts",
        "parameters": {
            "type": "object",
            "properties": {
                "from_account": {
                    "type": "string",
                    "description": "Source account number"
                },
                "to_account": {
                    "type": "string",
                    "description": "Destination account number"
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to transfer"
                },
                "description": {
                    "type": "string",
                    "description": "Transfer description",
                    "default": "Transfer"
                }
            },
            "required": ["from_account", "to_account", "amount"]
        }
    },
    "deposit": {
        "function": deposit,
        "description": "Deposit funds into an account",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "Account number to deposit into"
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to deposit"
                },
                "description": {
                    "type": "string",
                    "description": "Deposit description",
                    "default": "Deposit"
                }
            },
            "required": ["account_number", "amount"]
        }
    },
    "withdraw": {
        "function": withdraw,
        "description": "Withdraw funds from an account",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "Account number to withdraw from"
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to withdraw"
                },
                "description": {
                    "type": "string",
                    "description": "Withdrawal description",
                    "default": "Withdrawal"
                }
            },
            "required": ["account_number", "amount"]
        }
    },
    "get_account_balance": {
        "function": get_account_balance,
        "description": "Get the current balance of an account",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The account number"
                }
            },
            "required": ["account_number"]
        }
    },
    "get_branch_stats": {
        "function": get_branch_stats,
        "description": "Get statistics for all bank branches",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    "flag_transaction": {
        "function": flag_transaction,
        "description": "Flag a suspicious transaction for review",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "The transaction ID to flag"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for flagging"
                }
            },
            "required": ["transaction_id", "reason"]
        }
    },
    "get_flagged_transactions": {
        "function": get_flagged_transactions,
        "description": "Get all flagged/suspicious transactions",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back",
                    "default": 7
                }
            }
        }
    }
}
