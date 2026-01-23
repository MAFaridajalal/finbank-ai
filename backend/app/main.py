"""
FinBank AI - Multi-Agent Banking Assistant
Main FastAPI application entry point.
"""

from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional

from app.config import get_settings
from app.database import get_db, init_db
from app.orchestrator import Orchestrator
from app.websocket import handle_chat_websocket
from app.agents import get_available_agents
from app.llm import get_llm_provider, ProviderType

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="FinBank AI",
    description="Multi-Agent Banking Assistant with AI-powered orchestration",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "finbank-ai"}


# API Models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    provider: Optional[ProviderType] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    agents_used: list[str]


# REST API Endpoints
@app.get("/api/agents")
async def list_agents():
    """List available agents."""
    return {"agents": get_available_agents()}


@app.get("/api/providers")
async def list_providers():
    """List available LLM providers."""
    return {
        "providers": [
            {"name": "openai", "description": "OpenAI GPT-4"},
            {"name": "claude", "description": "Anthropic Claude"},
            {"name": "azure", "description": "Azure OpenAI"},
            {"name": "ollama", "description": "Local Ollama"},
        ],
        "default": settings.default_llm_provider,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response (non-streaming).
    For streaming responses, use the WebSocket endpoint.
    """
    try:
        llm = get_llm_provider(request.provider)
        orchestrator = Orchestrator(db, llm)
        result = await orchestrator.process_simple(request.message)

        # Extract agents used from messages
        agents_used = [
            msg.split(":")[1].split("]")[0]
            for msg in result["messages"]
            if msg.startswith("[AGENT:")
        ]

        return ChatResponse(
            response=result["response"],
            agents_used=list(set(agents_used)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for streaming chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat with streaming responses."""
    await handle_chat_websocket(websocket, db)


# Data API endpoints
@app.get("/api/data/customers")
async def list_customers(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    """List customers."""
    from sqlalchemy import text

    # Get total count
    total = db.execute(text("SELECT COUNT(*) FROM customers")).scalar()

    # Get paginated data
    result = db.execute(text(f"""
        SELECT c.*, ct.name as tier_name, b.name as branch_name
        FROM customers c
        LEFT JOIN customer_tiers ct ON c.tier_id = ct.id
        LEFT JOIN branches b ON c.branch_id = b.id
        ORDER BY c.id
        LIMIT {limit} OFFSET {offset}
    """))
    columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in result.fetchall()], "total": total}


@app.get("/api/data/accounts")
async def list_accounts(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    """List accounts."""
    from sqlalchemy import text

    # Get total count
    total = db.execute(text("SELECT COUNT(*) FROM accounts")).scalar()

    # Get paginated data
    result = db.execute(text(f"""
        SELECT a.*, at.name as type_name,
               c.first_name || ' ' || c.last_name as customer_name
        FROM accounts a
        LEFT JOIN account_types at ON a.type_id = at.id
        LEFT JOIN customers c ON a.customer_id = c.id
        ORDER BY a.id
        LIMIT {limit} OFFSET {offset}
    """))
    columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in result.fetchall()], "total": total}


@app.get("/api/data/transactions")
async def list_transactions(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    """List transactions."""
    from sqlalchemy import text

    # Get total count
    total = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar()

    # Get paginated data
    result = db.execute(text(f"""
        SELECT t.*, a.account_number,
               c.first_name || ' ' || c.last_name as customer_name
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        LEFT JOIN customers c ON a.customer_id = c.id
        ORDER BY t.created_at DESC
        LIMIT {limit} OFFSET {offset}
    """))
    columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in result.fetchall()], "total": total}


@app.get("/api/data/loans")
async def list_loans(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    """List loans."""
    from sqlalchemy import text

    # Get total count
    total = db.execute(text("SELECT COUNT(*) FROM loans")).scalar()

    # Get paginated data
    result = db.execute(text(f"""
        SELECT l.*, c.first_name || ' ' || c.last_name as customer_name
        FROM loans l
        LEFT JOIN customers c ON l.customer_id = c.id
        ORDER BY l.id
        LIMIT {limit} OFFSET {offset}
    """))
    columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in result.fetchall()], "total": total}


@app.get("/api/data/branches")
async def list_branches(db: Session = Depends(get_db)):
    """List branches."""
    from sqlalchemy import text
    result = db.execute(text("SELECT * FROM branches ORDER BY id"))
    columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in result.fetchall()]}


# Dashboard API
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    from sqlalchemy import text

    # Total customers
    total_customers = db.execute(text("SELECT COUNT(*) FROM customers")).scalar()

    # Total accounts and balance
    account_stats = db.execute(text("""
        SELECT COUNT(*) as count, COALESCE(SUM(balance), 0) as total_balance
        FROM accounts WHERE status = 'active'
    """)).fetchone()

    # Total deposits this month
    deposits_this_month = db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions
        WHERE type = 'deposit'
        AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
    """)).scalar()

    # Active loans
    loan_stats = db.execute(text("""
        SELECT COUNT(*) as count, COALESCE(SUM(remaining_balance), 0) as total
        FROM loans WHERE status = 'active'
    """)).fetchone()

    return {
        "total_customers": total_customers,
        "total_accounts": account_stats[0],
        "total_balance": float(account_stats[1]),
        "deposits_this_month": float(deposits_this_month),
        "active_loans": loan_stats[0],
        "loan_balance": float(loan_stats[1]),
    }


# Customer API Models
class CustomerCreateRequest(BaseModel):
    """Customer creation request model."""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    tier: Optional[str] = "Basic"
    branch: Optional[str] = "Downtown"


class CustomerCreateResponse(BaseModel):
    """Customer creation response model."""
    success: bool
    customer_id: Optional[int] = None
    message: str
    errors: Optional[dict] = None


class CustomerUpdateRequest(BaseModel):
    """Customer update request model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    tier: Optional[str] = None
    branch: Optional[str] = None


class CustomerResponse(BaseModel):
    """Generic customer response model."""
    success: bool
    message: str
    customer_id: Optional[int] = None
    errors: Optional[dict] = None


# Settings API Models
class ProviderUpdateRequest(BaseModel):
    """Provider update request model."""
    provider: str
    model: str


class SettingsResponse(BaseModel):
    """Settings response model."""
    provider: str
    model: str
    temperature: float
    ollama_base_url: Optional[str] = None


# Customer API
@app.post("/api/customers", response_model=CustomerCreateResponse)
async def create_customer(request: CustomerCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new customer with validation.

    Validates:
    - Email uniqueness
    - Phone number uniqueness (if provided)
    - Required fields
    - Valid tier and branch values
    """
    try:
        errors = {}

        # Validate email uniqueness
        existing_email = db.execute(text(
            "SELECT id, first_name, last_name FROM customers WHERE LOWER(email) = LOWER(:email)"
        ), {"email": request.email}).first()

        if existing_email:
            errors["email"] = f"Email already exists for customer: {existing_email[1]} {existing_email[2]} (ID: {existing_email[0]})"

        # Validate phone uniqueness (if provided and not empty)
        if request.phone and request.phone.strip():
            existing_phone = db.execute(text(
                "SELECT id, first_name, last_name FROM customers WHERE phone = :phone"
            ), {"phone": request.phone}).first()

            if existing_phone:
                errors["phone"] = f"Phone number already exists for customer: {existing_phone[1]} {existing_phone[2]} (ID: {existing_phone[0]})"

        # Validate email format (basic)
        if "@" not in request.email or "." not in request.email:
            errors["email"] = "Invalid email format"

        # Validate tier
        tier_map = {"basic": 1, "premium": 2, "vip": 3}
        tier_id = tier_map.get(request.tier.lower())
        if not tier_id:
            errors["tier"] = f"Invalid tier. Must be one of: Basic, Premium, VIP"

        # Validate branch
        branch_map = {"downtown": 1, "westside": 2, "airport": 3, "bellevue": 4}
        branch_id = branch_map.get(request.branch.lower())
        if not branch_id:
            errors["branch"] = f"Invalid branch. Must be one of: Downtown, Westside, Airport, Bellevue"

        # If there are validation errors, return them
        if errors:
            return CustomerCreateResponse(
                success=False,
                message="Validation failed",
                errors=errors
            )

        # Insert customer
        result = db.execute(text("""
            INSERT INTO customers
            (first_name, last_name, email, phone, address, city, tier_id, branch_id)
            VALUES
            (:first_name, :last_name, :email, :phone, :address, :city, :tier_id, :branch_id)
        """), {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "phone": request.phone or "",
            "address": request.address or "",
            "city": request.city or "",
            "tier_id": tier_id,
            "branch_id": branch_id
        })

        db.commit()
        customer_id = result.lastrowid

        return CustomerCreateResponse(
            success=True,
            customer_id=customer_id,
            message=f"Successfully created customer: {request.first_name} {request.last_name} (ID: {customer_id})"
        )

    except Exception as e:
        db.rollback()
        return CustomerCreateResponse(
            success=False,
            message=f"Failed to create customer: {str(e)}"
        )


@app.put("/api/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, request: CustomerUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing customer.
    Only updates fields that are provided (non-None).
    """
    try:
        # Check if customer exists
        existing = db.execute(text(
            "SELECT id, first_name, last_name FROM customers WHERE id = :id"
        ), {"id": customer_id}).first()

        if not existing:
            return CustomerResponse(
                success=False,
                message=f"Customer with ID {customer_id} not found"
            )

        errors = {}
        updates = []
        params = {"id": customer_id}

        # Build dynamic update query
        if request.first_name is not None:
            updates.append("first_name = :first_name")
            params["first_name"] = request.first_name

        if request.last_name is not None:
            updates.append("last_name = :last_name")
            params["last_name"] = request.last_name

        if request.email is not None:
            # Check email uniqueness
            dup = db.execute(text(
                "SELECT id FROM customers WHERE LOWER(email) = LOWER(:email) AND id != :id"
            ), {"email": request.email, "id": customer_id}).first()
            if dup:
                errors["email"] = "Email already exists"
            else:
                updates.append("email = :email")
                params["email"] = request.email

        if request.phone is not None:
            # Check phone uniqueness
            if request.phone.strip():
                dup = db.execute(text(
                    "SELECT id FROM customers WHERE phone = :phone AND id != :id"
                ), {"phone": request.phone, "id": customer_id}).first()
                if dup:
                    errors["phone"] = "Phone already exists"
                else:
                    updates.append("phone = :phone")
                    params["phone"] = request.phone
            else:
                updates.append("phone = :phone")
                params["phone"] = request.phone

        if request.address is not None:
            updates.append("address = :address")
            params["address"] = request.address

        if request.city is not None:
            updates.append("city = :city")
            params["city"] = request.city

        if request.tier is not None:
            tier_map = {"basic": 1, "premium": 2, "vip": 3}
            tier_id = tier_map.get(request.tier.lower())
            if not tier_id:
                errors["tier"] = "Invalid tier. Must be: Basic, Premium, VIP"
            else:
                updates.append("tier_id = :tier_id")
                params["tier_id"] = tier_id

        if request.branch is not None:
            branch_map = {"downtown": 1, "westside": 2, "airport": 3, "bellevue": 4}
            branch_id = branch_map.get(request.branch.lower())
            if not branch_id:
                errors["branch"] = "Invalid branch"
            else:
                updates.append("branch_id = :branch_id")
                params["branch_id"] = branch_id

        if errors:
            return CustomerResponse(success=False, message="Validation failed", errors=errors)

        if not updates:
            return CustomerResponse(success=False, message="No fields to update")

        # Execute update
        db.execute(text(f"UPDATE customers SET {', '.join(updates)} WHERE id = :id"), params)
        db.commit()

        return CustomerResponse(
            success=True,
            customer_id=customer_id,
            message=f"Updated customer {existing[1]} {existing[2]} (ID: {customer_id})"
        )
    except Exception as e:
        db.rollback()
        return CustomerResponse(success=False, message=f"Update failed: {str(e)}")


@app.delete("/api/customers/{customer_id}", response_model=CustomerResponse)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete a customer by ID.
    Prevents deletion if customer has active accounts.
    """
    try:
        # Check if customer exists
        existing = db.execute(text(
            "SELECT id, first_name, last_name FROM customers WHERE id = :id"
        ), {"id": customer_id}).first()

        if not existing:
            return CustomerResponse(
                success=False,
                message=f"Customer with ID {customer_id} not found"
            )

        # Check for active accounts
        active_accounts = db.execute(text(
            "SELECT COUNT(*) FROM accounts WHERE customer_id = :id AND status = 'active'"
        ), {"id": customer_id}).scalar()

        if active_accounts > 0:
            return CustomerResponse(
                success=False,
                message=f"Cannot delete customer {existing[1]} {existing[2]}: has {active_accounts} active account(s). Close accounts first."
            )

        # Delete customer
        db.execute(text("DELETE FROM customers WHERE id = :id"), {"id": customer_id})
        db.commit()

        return CustomerResponse(
            success=True,
            customer_id=customer_id,
            message=f"Deleted customer {existing[1]} {existing[2]} (ID: {customer_id})"
        )
    except Exception as e:
        db.rollback()
        return CustomerResponse(success=False, message=f"Delete failed: {str(e)}")


# Settings API
@app.get("/api/settings", response_model=SettingsResponse)
async def get_settings_api():
    """Get current application settings."""
    return SettingsResponse(
        provider=settings.default_llm_provider,
        model="llama3.2" if settings.default_llm_provider == "ollama" else "gpt-4",
        temperature=0.7,
        ollama_base_url=settings.ollama_base_url if settings.default_llm_provider == "ollama" else None,
    )


@app.post("/api/settings/provider")
async def update_provider_settings(request: ProviderUpdateRequest):
    """
    Update LLM provider settings.

    Note: This endpoint updates the runtime settings but does not persist
    changes to the .env file. For persistent changes, update the .env file directly.
    """
    try:
        # Validate provider
        valid_providers = ["openai", "claude", "azure", "ollama"]
        if request.provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )

        # Update runtime settings
        settings.default_llm_provider = request.provider

        # Verify the provider can be initialized
        try:
            _ = get_llm_provider(request.provider)  # Test initialization
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize provider '{request.provider}': {str(e)}"
            )

        return {
            "success": True,
            "message": f"Provider updated to {request.provider} with model {request.model}",
            "provider": request.provider,
            "model": request.model,
            "note": "Settings updated for current session only. Update .env file for persistent changes."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
