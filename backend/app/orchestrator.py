"""
Main AI Orchestrator for FinBank AI.
Coordinates agents to process user requests.
"""

from typing import AsyncGenerator
from sqlalchemy.orm import Session

from app.agents import get_agent, get_available_agents
from app.llm import BaseLLMProvider, get_llm_provider


class Orchestrator:
    """
    Main orchestrator that routes user requests to appropriate agents.
    """

    def __init__(self, db: Session, llm: BaseLLMProvider | None = None):
        self.db = db
        self.llm = llm or get_llm_provider()

    async def process(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Process a user message and stream the response.

        Yields status updates and the final response.
        """
        # Step 1: Plan which agents to use
        yield "[STATUS] Planning tasks..."
        available = [a["name"] for a in get_available_agents()]
        plan = await self.llm.plan_tasks(user_message, available)

        # DEBUG: Print the plan
        print(f"\n{'='*60}")
        print(f"USER MESSAGE: {user_message}")
        print(f"PLAN: {plan}")
        print(f"{'='*60}\n")

        if not plan:
            yield "[STATUS] Processing directly..."
            response = await self.llm.generate(
                prompt=user_message,
                system_prompt="You are a helpful banking assistant. Answer the user's question directly.",
            )
            yield f"[RESPONSE]{response.content}"
            return

        yield f"[STATUS] Using {len(plan)} agent(s)"

        # Step 2: Execute each agent task
        results = {}
        for task in plan:
            agent_name = task.get("agent", "query")
            task_desc = task.get("task", user_message)

            # For CRUD operations, pass original message to preserve exact names/values
            if agent_name == "crud":
                task_desc = user_message

            yield f"[AGENT:{agent_name}] {task_desc}"

            try:
                agent = get_agent(agent_name, self.db, self.llm)
                result = await agent.execute(task_desc)
                results[agent_name] = result.model_dump()
                yield f"[AGENT:{agent_name}:DONE] {result.message}"
            except Exception as e:
                yield f"[AGENT:{agent_name}:ERROR] {str(e)}"
                results[agent_name] = {"error": str(e)}

        # Step 3: Synthesize final response
        yield "[STATUS] Generating response..."
        response = await self.llm.synthesize(user_message, results)
        yield f"[RESPONSE]{response}"

    async def process_simple(self, user_message: str) -> dict:
        """
        Process a user message and return the complete response.

        Returns a dict with all results and the final response.
        """
        messages = []
        final_response = ""

        async for msg in self.process(user_message):
            messages.append(msg)
            if msg.startswith("[RESPONSE]"):
                final_response = msg[10:]

        return {
            "messages": messages,
            "response": final_response,
        }
