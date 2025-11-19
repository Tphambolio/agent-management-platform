"""
Session Processor - Handles agent task execution for chat sessions
Uses Gemini API to process user queries and stream responses
"""

import asyncio
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import Session, SessionStatus, InteractionLog, EventType
from app.streaming import streaming_manager, StreamEventType
from app.gemini_researcher import GeminiResearcher


class SessionProcessor:
    """Processes agent sessions using Gemini API"""

    def __init__(self):
        self.gemini = GeminiResearcher()
        self.processing_sessions = set()

    async def process_session(self, session_id: str):
        """
        Process a session by executing the agent task with Gemini

        Args:
            session_id: The session ID to process
        """
        # Prevent duplicate processing
        if session_id in self.processing_sessions:
            return

        self.processing_sessions.add(session_id)

        try:
            # Get session from database
            with get_db() as db:
                session = db.query(Session).filter(Session.id == session_id).first()
                if not session:
                    await streaming_manager.send_event(
                        session_id,
                        StreamEventType.ERROR,
                        {"message": "Session not found"}
                    )
                    return

                query = session.initial_query
                agent_id = session.agent_id

            # Send session start event
            await streaming_manager.send_event(
                session_id,
                StreamEventType.SESSION_START,
                {
                    "message": f"Starting to process your request...",
                    "query": query
                }
            )

            # Log interaction
            await self._log_interaction(
                session_id,
                EventType.USER_INPUT,
                {"query": query}
            )

            # Send thinking event
            await streaming_manager.send_event(
                session_id,
                StreamEventType.AGENT_THINKING,
                {"thought": "Analyzing your request and formulating a response..."}
            )

            await asyncio.sleep(0.5)  # Small delay for UX

            # Check if Gemini is available
            if not self.gemini.available:
                response = f"""I received your message: "{query}"

However, the Gemini API is not configured. To enable AI responses, please set the GEMINI_API_KEY environment variable.

You can get a free API key at: https://makersuite.google.com/app/apikey

For now, I can confirm that:
- ✅ Your session was created successfully
- ✅ WebSocket connection is working
- ✅ Message streaming is functional
- ⚠️  AI processing requires GEMINI_API_KEY

Once the API key is added, I'll be able to provide intelligent responses to your queries!"""

                await self._stream_response(session_id, response)
            else:
                # Process with Gemini
                await streaming_manager.send_event(
                    session_id,
                    StreamEventType.TOOL_CALL,
                    {"tool_name": "gemini-pro", "description": "Generating AI response"}
                )

                try:
                    # Use Gemini to generate response
                    response = await self._generate_gemini_response(query)

                    await streaming_manager.send_event(
                        session_id,
                        StreamEventType.TOOL_RESULT,
                        {"tool_name": "gemini-pro", "status": "success"}
                    )

                    # Stream the response
                    await self._stream_response(session_id, response)

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    await streaming_manager.send_event(
                        session_id,
                        StreamEventType.ERROR,
                        {"message": error_msg}
                    )
                    response = f"I encountered an error while processing your request: {str(e)}"

            # Update session in database
            with get_db() as db:
                session = db.query(Session).filter(Session.id == session_id).first()
                if session:
                    session.final_output = response
                    session.status = SessionStatus.COMPLETED
                    session.end_time = datetime.utcnow()
                    if session.start_time:
                        # Ensure both datetimes are timezone-aware or both naive
                        start = session.start_time.replace(tzinfo=None) if session.start_time.tzinfo else session.start_time
                        end = session.end_time.replace(tzinfo=None) if session.end_time.tzinfo else session.end_time
                        duration = (end - start).total_seconds()
                        session.duration_seconds = int(duration)
                    db.commit()

            # Log final output
            await self._log_interaction(
                session_id,
                EventType.LLM_RESPONSE,
                {"response": response}
            )

            # Send completion event
            await streaming_manager.send_event(
                session_id,
                StreamEventType.SESSION_COMPLETE,
                {
                    "final_output": response,
                    "status": "completed"
                }
            )

        except Exception as e:
            await streaming_manager.send_event(
                session_id,
                StreamEventType.ERROR,
                {"message": f"Session processing error: {str(e)}"}
            )
        finally:
            self.processing_sessions.discard(session_id)

    async def _generate_gemini_response(self, query: str) -> str:
        """Generate response using Gemini API"""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini.model.generate_content(query).text
        )
        return response

    async def _stream_response(self, session_id: str, response: str):
        """Stream response text in chunks"""
        # Split into words for streaming effect
        words = response.split()
        chunk_size = 3  # Send 3 words at a time

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            await streaming_manager.send_event(
                session_id,
                StreamEventType.CHUNK,
                {"chunk": chunk}
            )
            await asyncio.sleep(0.05)  # Small delay between chunks for streaming effect

    async def _log_interaction(
        self,
        session_id: str,
        event_type: EventType,
        content: dict
    ):
        """Log interaction to database"""
        try:
            with get_db() as db:
                log = InteractionLog(
                    id=str(__import__('uuid').uuid4()),
                    session_id=session_id,
                    event_type=event_type,
                    content=content,
                    timestamp=datetime.utcnow()
                )
                db.add(log)
                db.commit()
        except Exception as e:
            print(f"Failed to log interaction: {e}")


# Global session processor instance
session_processor = SessionProcessor()
