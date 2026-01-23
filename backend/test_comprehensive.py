#!/usr/bin/env python3
"""
Comprehensive test suite for FinBank AI CRUD operations.
Tests both API endpoints and Chat-based operations.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/farida/finbank-ai/backend')

from sqlalchemy import text
from app.database import SessionLocal
from app.orchestrator import Orchestrator
from app.llm import get_llm_provider

# Test results tracking
results = {"passed": 0, "failed": 0, "tests": []}

def log_result(test_name: str, passed: bool, message: str):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if not passed:
        print(f"   → {message}")
    results["tests"].append({"name": test_name, "passed": passed, "message": message})
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1


async def test_chat_create():
    """Test CREATE customer via chat."""
    db = SessionLocal()
    try:
        # Clean up any existing test customer
        db.execute(text("DELETE FROM customers WHERE email = 'chatcreate@test.com'"))
        db.commit()

        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = "Add a new customer named ChatCreate TestUser with email chatcreate@test.com and phone 555-1234"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Verify in database
        customer = db.execute(text(
            "SELECT id, first_name, last_name, email FROM customers WHERE email = 'chatcreate@test.com'"
        )).first()

        if customer:
            log_result("Chat CREATE customer", True, f"Created: {customer[1]} {customer[2]} (ID: {customer[0]})")
            return customer[0]  # Return ID for later tests
        else:
            log_result("Chat CREATE customer", False, f"Customer not found in database. Response: {response_text[:100]}")
            return None
    finally:
        db.close()


async def test_chat_update_by_id(customer_id: int):
    """Test UPDATE customer by ID via chat."""
    if not customer_id:
        log_result("Chat UPDATE by ID", False, "Skipped - no customer ID")
        return

    db = SessionLocal()
    try:
        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = f"Update customer {customer_id} email to updated_by_id@test.com"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Verify update
        customer = db.execute(text(
            "SELECT email FROM customers WHERE id = :id"
        ), {"id": customer_id}).first()

        if customer and customer[0] == "updated_by_id@test.com":
            log_result("Chat UPDATE by ID", True, f"Email updated to: {customer[0]}")
        else:
            actual = customer[0] if customer else "not found"
            log_result("Chat UPDATE by ID", False, f"Expected 'updated_by_id@test.com', got '{actual}'")
    finally:
        db.close()


async def test_chat_update_by_name():
    """Test UPDATE customer by name via chat."""
    db = SessionLocal()
    try:
        # First create a test customer
        db.execute(text("DELETE FROM customers WHERE email LIKE '%nameupdate%'"))
        db.execute(text("""
            INSERT INTO customers (first_name, last_name, email, phone, tier_id, branch_id)
            VALUES ('NameUpdate', 'TestUser', 'nameupdate@test.com', '555-NAME', 1, 1)
        """))
        db.commit()

        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = "Update customer NameUpdate TestUser, change email to nameupdate_changed@test.com"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Verify update
        customer = db.execute(text(
            "SELECT email FROM customers WHERE first_name = 'NameUpdate' AND last_name = 'TestUser'"
        )).first()

        if customer and "changed" in customer[0]:
            log_result("Chat UPDATE by name", True, f"Email updated to: {customer[0]}")
        else:
            actual = customer[0] if customer else "not found"
            log_result("Chat UPDATE by name", False, f"Expected email with 'changed', got '{actual}'. Response: {response_text[:100]}")
    finally:
        db.close()


async def test_chat_delete_by_id():
    """Test DELETE customer by ID via chat."""
    db = SessionLocal()
    try:
        # Create a customer to delete
        db.execute(text("DELETE FROM customers WHERE email = 'deletebyid@test.com'"))
        result = db.execute(text("""
            INSERT INTO customers (first_name, last_name, email, phone, tier_id, branch_id)
            VALUES ('DeleteById', 'TestUser', 'deletebyid@test.com', '555-DEL1', 1, 1)
        """))
        db.commit()
        customer_id = result.lastrowid

        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = f"Delete customer {customer_id}"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Verify deletion
        customer = db.execute(text(
            "SELECT id FROM customers WHERE id = :id"
        ), {"id": customer_id}).first()

        if not customer:
            log_result("Chat DELETE by ID", True, f"Customer {customer_id} deleted successfully")
        else:
            log_result("Chat DELETE by ID", False, f"Customer still exists. Response: {response_text[:100]}")
    finally:
        db.close()


async def test_chat_delete_by_name():
    """Test DELETE customer by name via chat."""
    db = SessionLocal()
    try:
        # Create a customer to delete
        db.execute(text("DELETE FROM customers WHERE email = 'deletebyname@test.com'"))
        db.execute(text("""
            INSERT INTO customers (first_name, last_name, email, phone, tier_id, branch_id)
            VALUES ('DeleteByName', 'TestUser', 'deletebyname@test.com', '555-DEL2', 1, 1)
        """))
        db.commit()

        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = "Delete customer DeleteByName TestUser"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Verify deletion
        customer = db.execute(text(
            "SELECT id FROM customers WHERE email = 'deletebyname@test.com'"
        )).first()

        if not customer:
            log_result("Chat DELETE by name", True, "Customer deleted successfully")
        else:
            log_result("Chat DELETE by name", False, f"Customer still exists. Response: {response_text[:100]}")
    finally:
        db.close()


async def test_chat_delete_protected():
    """Test that customers with active accounts cannot be deleted."""
    db = SessionLocal()
    try:
        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        # Customer 1 has accounts
        message = "Delete customer 1"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Customer should still exist
        customer = db.execute(text("SELECT id FROM customers WHERE id = 1")).first()

        if customer:
            log_result("Chat DELETE protection", True, "Customer with accounts protected from deletion")
        else:
            log_result("Chat DELETE protection", False, "Customer was deleted despite having accounts!")
    finally:
        db.close()


async def test_chat_query():
    """Test query operations."""
    db = SessionLocal()
    try:
        llm = get_llm_provider()
        orchestrator = Orchestrator(db, llm)

        message = "Show me all customers"

        response_text = ""
        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response_text = msg[10:]

        # Check if response mentions customers
        if "customer" in response_text.lower() or "john" in response_text.lower():
            log_result("Chat QUERY customers", True, "Query returned customer data")
        else:
            log_result("Chat QUERY customers", False, f"Response didn't contain customer data: {response_text[:100]}")
    finally:
        db.close()


async def cleanup_test_data():
    """Clean up test data after tests."""
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM customers WHERE email LIKE '%test.com'"))
        db.commit()
        print("\n🧹 Cleaned up test data")
    finally:
        db.close()


async def main():
    print("=" * 60)
    print("COMPREHENSIVE CRUD TESTING")
    print("=" * 60)

    # Run tests
    print("\n--- CHAT CREATE ---")
    customer_id = await test_chat_create()

    print("\n--- CHAT UPDATE ---")
    await test_chat_update_by_id(customer_id)
    await test_chat_update_by_name()

    print("\n--- CHAT DELETE ---")
    await test_chat_delete_by_id()
    await test_chat_delete_by_name()
    await test_chat_delete_protected()

    print("\n--- CHAT QUERY ---")
    await test_chat_query()

    # Cleanup
    await cleanup_test_data()

    # Summary
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {results['passed']}/{results['passed'] + results['failed']} passed")
    print("=" * 60)

    return results['failed'] == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
