"""
WebSocket handlers for FinBank AI.
Handles real-time chat communication.
"""

import json
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.orchestrator import Orchestrator
from app.llm import get_llm_provider, ProviderType


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and track a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        """Send a JSON message to a specific client."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def handle_chat_websocket(websocket: WebSocket, db: Session):
    """
    Handle a chat WebSocket connection.

    Message format (incoming):
    {
        "type": "message",
        "content": "user message",
        "provider": "openai" | "claude" | "ollama" (optional)
    }

    Message format (outgoing):
    {
        "type": "status" | "agent" | "response" | "error",
        "content": "...",
        "agent": "agent_name" (for agent type),
        "status": "running" | "done" | "error" (for agent type)
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            if data.get("type") == "message":
                content = data.get("content", "")
                provider = data.get("provider")

                # Get LLM provider
                llm = get_llm_provider(provider)

                # Create orchestrator
                orchestrator = Orchestrator(db, llm)

                # Process and stream response
                async for msg in orchestrator.process(content):
                    if msg.startswith("[STATUS]"):
                        await manager.send_message(websocket, {
                            "type": "status",
                            "content": msg[8:].strip(),
                        })
                    elif msg.startswith("[AGENT:"):
                        # Parse agent message
                        # Format: [AGENT:name] task or [AGENT:name:DONE] result
                        end_bracket = msg.index("]")
                        agent_info = msg[7:end_bracket]
                        content = msg[end_bracket + 1:].strip()

                        if ":DONE" in agent_info:
                            agent_name = agent_info.replace(":DONE", "")
                            await manager.send_message(websocket, {
                                "type": "agent",
                                "agent": agent_name,
                                "status": "done",
                                "content": content,
                            })
                        elif ":ERROR" in agent_info:
                            agent_name = agent_info.replace(":ERROR", "")
                            await manager.send_message(websocket, {
                                "type": "agent",
                                "agent": agent_name,
                                "status": "error",
                                "content": content,
                            })
                        else:
                            await manager.send_message(websocket, {
                                "type": "agent",
                                "agent": agent_info,
                                "status": "running",
                                "content": content,
                            })
                    elif msg.startswith("[RESPONSE]"):
                        await manager.send_message(websocket, {
                            "type": "response",
                            "content": msg[10:],
                        })

            elif data.get("type") == "ping":
                await manager.send_message(websocket, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message(websocket, {
            "type": "error",
            "content": str(e),
        })
        manager.disconnect(websocket)
