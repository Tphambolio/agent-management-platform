"""WebSocket API for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()

            # Echo back (can be extended for specific commands)
            await manager.send_personal_message({
                "type": "echo",
                "data": data
            }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_agent_update(agent_id: str, status: str):
    """Broadcast agent status update to all connected clients"""
    await manager.broadcast({
        "type": "agent_update",
        "agent_id": agent_id,
        "status": status,
    })


async def broadcast_task_update(task_id: str, status: str, agent_id: str):
    """Broadcast task status update to all connected clients"""
    await manager.broadcast({
        "type": "task_update",
        "task_id": task_id,
        "agent_id": agent_id,
        "status": status,
    })
