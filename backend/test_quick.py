"""Quick test to debug LLM extraction."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.orchestrator import Orchestrator
from app.llm import get_llm_provider

DATABASE_URL = "sqlite:///./finbank.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def test_update():
    """Test UPDATE to see LLM extraction."""
    print("\n" + "="*60)
    print("Quick UPDATE Test")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = "Update customer 14, change email to test@updated.com"
    print(f"Message: {message}\n")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            print(f"Response: {msg[10:][:200]}")

    db.close()

async def test_delete():
    """Test DELETE to see LLM extraction."""
    print("\n" + "="*60)
    print("Quick DELETE Test")
    print("="*60)

    db = SessionLocal()
    llm = get_llm_provider()
    orchestrator = Orchestrator(db, llm)

    message = "Delete customer ChatTest User"
    print(f"Message: {message}\n")

    async for msg in orchestrator.process(message):
        if msg.startswith("[RESPONSE]"):
            print(f"Response: {msg[10:][:200]}")

    db.close()

async def main():
    await test_update()
    await test_delete()

if __name__ == "__main__":
    asyncio.run(main())
