"""
Streaming Module for Real-Time Agent Feedback

Implements WebSocket-based streaming for agent interactions,
following research recommendations for real-time feedback.
"""

import uuid
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

from app.database import get_db
from app.models import Session, InteractionLog, Artifact, EventType, SessionStatus, ArtifactType


class StreamEventType(str, Enum):
    """Types of streaming events"""
    SESSION_START = "session_start"
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOKEN = "token"  # Individual token streaming
    CHUNK = "chunk"  # Chunk of text
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    SESSION_COMPLETE = "session_complete"
    ARTIFACT_CREATED = "artifact_created"


class StreamingManager:
    """
    Manages WebSocket connections and streaming events for agent interactions

    Features:
    - Real-time token/chunk streaming
    - Session tracking
    - Event logging
    - Multi-client broadcast support
    """

    def __init__(self):
        # Map of session_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map of session_id -> Session data
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket client to a session"""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

        # Send connection confirmation
        await self.send_event(
            session_id,
            StreamEventType.STATUS_UPDATE,
            {"message": "Connected to agent session", "session_id": session_id}
        )

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)

            # Clean up if no more connections
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_event(
        self,
        session_id: str,
        event_type: StreamEventType,
        data: Dict[str, Any],
        log_to_db: bool = True
    ):
        """
        Send an event to all clients connected to a session

        Args:
            session_id: Session identifier
            event_type: Type of event
            data: Event data
            log_to_db: Whether to log this event to the database
        """
        event = {
            "type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        # Send to all connected clients
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(event)
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    disconnected.append(connection)

            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn, session_id)

        # Log to database
        if log_to_db and event_type not in [StreamEventType.TOKEN, StreamEventType.CHUNK]:
            # Don't log every token/chunk - too verbose
            await self._log_event(session_id, event_type, data)

    async def _log_event(
        self,
        session_id: str,
        event_type: StreamEventType,
        data: Dict[str, Any]
    ):
        """Log event to database"""
        try:
            # Map StreamEventType to EventType
            event_type_mapping = {
                StreamEventType.SESSION_START: EventType.STATUS_UPDATE,
                StreamEventType.AGENT_THINKING: EventType.AGENT_THOUGHT,
                StreamEventType.TOOL_CALL: EventType.TOOL_CALL,
                StreamEventType.TOOL_RESULT: EventType.TOOL_OUTPUT,
                StreamEventType.ERROR: EventType.ERROR,
                StreamEventType.SESSION_COMPLETE: EventType.STATUS_UPDATE,
                StreamEventType.STATUS_UPDATE: EventType.STATUS_UPDATE,
            }

            db_event_type = event_type_mapping.get(event_type, EventType.STATUS_UPDATE)

            with get_db() as db:
                log_entry = InteractionLog(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    event_type=db_event_type,
                    content=data,
                    token_count=data.get("token_count", 0),
                    cost_estimate_usd=data.get("cost_cents", 0)
                )
                db.add(log_entry)
                db.commit()
        except Exception as e:
            print(f"Error logging event: {e}")

    async def stream_agent_response(
        self,
        session_id: str,
        response_text: str,
        chunk_size: int = 20
    ):
        """
        Stream a response token-by-token or in chunks

        Args:
            session_id: Session identifier
            response_text: Full response text to stream
            chunk_size: Number of characters per chunk
        """
        # Stream in chunks for better UX
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i+chunk_size]
            await self.send_event(
                session_id,
                StreamEventType.CHUNK,
                {"chunk": chunk, "position": i},
                log_to_db=False
            )
            # Small delay to simulate streaming
            await asyncio.sleep(0.05)

    async def create_session(
        self,
        agent_id: str,
        initial_query: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Create a new session

        Returns:
            session_id
        """
        session_id = str(uuid.uuid4())

        with get_db() as db:
            session = Session(
                id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                initial_query=initial_query,
                status=SessionStatus.IN_PROGRESS,
                agent_model_id="claude-sonnet-4"
            )
            db.add(session)
            db.commit()

        # Track in memory
        self.active_sessions[session_id] = {
            "agent_id": agent_id,
            "query": initial_query,
            "start_time": datetime.utcnow()
        }

        # Broadcast session start
        await self.send_event(
            session_id,
            StreamEventType.SESSION_START,
            {
                "session_id": session_id,
                "agent_id": agent_id,
                "query": initial_query
            }
        )

        return session_id

    async def complete_session(
        self,
        session_id: str,
        final_output: str,
        artifacts: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Mark session as complete and save artifacts

        Args:
            session_id: Session identifier
            final_output: Final response/output
            artifacts: Optional list of artifacts to save
        """
        session_data = self.active_sessions.get(session_id, {})
        start_time = session_data.get("start_time", datetime.utcnow())
        duration = (datetime.utcnow() - start_time).total_seconds()

        with get_db() as db:
            # Update session
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.status = SessionStatus.COMPLETED
                session.final_output = final_output
                session.end_time = datetime.utcnow()
                session.duration_seconds = int(duration)
                db.commit()

            # Save artifacts
            if artifacts:
                for artifact_data in artifacts:
                    artifact = Artifact(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        artifact_type=artifact_data.get("type", ArtifactType.DOCUMENT),
                        title=artifact_data.get("title", ""),
                        content=artifact_data.get("content", ""),
                        tags=artifact_data.get("tags", []),
                        meta=artifact_data.get("meta", {})
                    )
                    db.add(artifact)
                db.commit()

        # Broadcast completion
        await self.send_event(
            session_id,
            StreamEventType.SESSION_COMPLETE,
            {
                "final_output": final_output,
                "duration": duration,
                "artifacts_count": len(artifacts) if artifacts else 0
            }
        )

        # Clean up
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]


# Singleton instance
streaming_manager = StreamingManager()
