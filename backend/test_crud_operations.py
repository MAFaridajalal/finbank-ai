"""
Test script for CRUD operations via chat orchestrator.
Tests CREATE, UPDATE, DELETE operations that go through the agent system.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.orchestrator import Orchestrator
from app.llm import get_llm_provider

# Database setup
DATABASE_URL = "sqlite:///./finbank.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def test_chat_create():
    """Test CREATE customer via chat."""
    print("\n" + "="*60)
    print("TEST 1: CREATE Customer via Chat")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = "Add a new customer named ChatTest User with email chattest@bank.com, phone 555-CREATE"

    print(f"\nSending: {message}")

    result_messages = []
    async for msg in orchestrator.process(message):
        result_messages.append(msg)
        if msg.startswith("[RESPONSE]"):
            print(f"\nResponse: {msg[10:]}")

    # Verify in database
    customer = db.execute(text(
        "SELECT id, first_name, last_name, email FROM customers WHERE email = 'chattest@bank.com'"
    )).first()

    if customer:
        print(f"✅ Customer created successfully: ID {customer[0]}, {customer[1]} {customer[2]}")
        return customer[0]  # Return ID for next tests
    else:
        print(f"❌ Customer NOT found in database")
        return None

    db.close()


async def test_chat_update_by_name(customer_id):
    """Test UPDATE customer by name via chat."""
    print("\n" + "="*60)
    print("TEST 2: UPDATE Customer by Name via Chat")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = "Update ChatTest User, change last name to UpdatedUser"

    print(f"\nSending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            print(f"\nResponse: {msg[10:]}")

    # Verify in database
    customer = db.execute(text(
        "SELECT id, first_name, last_name FROM customers WHERE id = :id"
    ), {"id": customer_id}).first()

    if customer and customer[2] == "UpdatedUser":
        print(f"✅ Customer updated successfully: {customer[1]} {customer[2]}")
        return True
    else:
        print(f"❌ Customer NOT updated. Current last_name: {customer[2] if customer else 'NOT FOUND'}")
        return False

    db.close()


async def test_chat_update_by_id(customer_id):
    """Test UPDATE customer by ID via chat."""
    print("\n" + "="*60)
    print("TEST 3: UPDATE Customer by ID via Chat")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = f"Update customer {customer_id}, change email to updated.email@bank.com"

    print(f"\nSending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            print(f"\nResponse: {msg[10:]}")

    # Verify in database
    customer = db.execute(text(
        "SELECT id, email FROM customers WHERE id = :id"
    ), {"id": customer_id}).first()

    if customer and customer[1] == "updated.email@bank.com":
        print(f"✅ Customer email updated successfully: {customer[1]}")
        return True
    else:
        print(f"❌ Customer email NOT updated. Current email: {customer[1] if customer else 'NOT FOUND'}")
        return False

    db.close()


async def test_chat_delete_by_name(customer_id):
    """Test DELETE customer by name via chat."""
    print("\n" + "="*60)
    print("TEST 4: DELETE Customer by Name via Chat")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = "Delete customer ChatTest UpdatedUser"

    print(f"\nSending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            print(f"\nResponse: {msg[10:]}")

    # Verify in database
    customer = db.execute(text(
        "SELECT id FROM customers WHERE id = :id"
    ), {"id": customer_id}).first()

    if not customer:
        print(f"✅ Customer deleted successfully")
        return True
    else:
        print(f"❌ Customer still exists in database")
        return False

    db.close()


async def test_chat_query():
    """Test QUERY operations via chat."""
    print("\n" + "="*60)
    print("TEST 5: QUERY Customers via Chat")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    # Test 1: List all customers
    message = "List all customers"
    print(f"\nSending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            response = msg[10:]
            if "erik" in response.lower() or "maria" in response.lower():
                print(f"✅ Query returned customer data")
            else:
                print(f"❌ Query response doesn't contain customer data")
                print(f"Response: {response[:200]}")

    # Test 2: Filter by tier
    message = "Show all Premium tier customers"
    print(f"\n\nSending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            response = msg[10:]
            if "premium" in response.lower():
                print(f"✅ Premium tier query returned data")
            else:
                print(f"❌ Premium tier query issue")
                print(f"Response: {response[:200]}")

    db.close()


async def test_banking_edge_cases():
    """Test banking-specific edge cases."""
    print("\n" + "="*60)
    print("TEST 6: Banking Edge Cases")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    # Test: Try to delete customer with accounts (should fail)
    print("\nTest 6a: Delete customer with active accounts (should fail)")

    # Find a customer with accounts
    customer_with_accounts = db.execute(text("""
        SELECT c.id, c.first_name, c.last_name, COUNT(a.id) as account_count
        FROM customers c
        JOIN accounts a ON c.id = a.customer_id
        GROUP BY c.id
        HAVING account_count > 0
        LIMIT 1
    """)).first()

    if customer_with_accounts:
        customer_id, first_name, last_name, account_count = customer_with_accounts
        print(f"Found customer: {first_name} {last_name} (ID: {customer_id}) with {account_count} accounts")

        message = f"Delete customer {first_name} {last_name}"
        print(f"Sending: {message}")

        async for msg in orchestrator.process(message):
            if msg.startswith("[RESPONSE]"):
                response = msg[10:]
                if "cannot" in response.lower() or "account" in response.lower():
                    print(f"✅ Correctly prevented deletion: {response[:150]}")
                else:
                    print(f"❌ Should have prevented deletion")
                    print(f"Response: {response}")
    else:
        print("⚠️  No customers with accounts found for testing")

    # Test: Case-insensitive name search
    print("\n\nTest 6b: Case-insensitive name search")
    message = "Find customer ERIK MOL"
    print(f"Sending: {message}")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            response = msg[10:]
            if "erik" in response.lower() and "mol" in response.lower():
                print(f"✅ Case-insensitive search works")
            else:
                print(f"❌ Case-insensitive search failed")
                print(f"Response: {response[:200]}")

    db.close()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE CRUD TESTING - BANKING APPLICATION")
    print("="*60)

    try:
        # Test 1: CREATE
        customer_id = await test_chat_create()

        if customer_id:
            # Test 2: UPDATE by name
            await test_chat_update_by_name(customer_id)

            # Test 3: UPDATE by ID
            await test_chat_update_by_id(customer_id)

            # Test 4: DELETE
            await test_chat_delete_by_name(customer_id)

        # Test 5: QUERY
        await test_chat_query()

        # Test 6: Edge cases
        await test_banking_edge_cases()

        print("\n" + "="*60)
        print("TESTING COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
