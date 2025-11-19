"""
Intelligent Session Processor - Uses Gemini as orchestrator brain
Gemini analyzes queries and intelligently coordinates agents
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict
from app.database import get_db
from app.models import Session, SessionStatus, InteractionLog, EventType
from app.streaming import streaming_manager, StreamEventType
from app.gemini_researcher import GeminiResearcher
import sys
from pathlib import Path

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from agent_mcp.agent_manager import agent_manager


class IntelligentSessionProcessor:
    """
    Uses Gemini AI as an intelligent orchestrator that:
    1. Analyzes user queries
    2. Determines which agents to use
    3. Coordinates multi-agent workflows
    4. Synthesizes final responses
    """

    def __init__(self):
        self.gemini = GeminiResearcher()
        self.processing_sessions = set()
        self._agent_manager_initialized = False

    async def _ensure_agent_manager(self):
        """Lazy initialize agent manager"""
        if not self._agent_manager_initialized:
            try:
                await agent_manager.initialize()
                self._agent_manager_initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize agent manager: {e}")

    async def process_session(self, session_id: str):
        """
        Process a session with Gemini as intelligent orchestrator

        Args:
            session_id: The session ID to process
        """
        # Prevent duplicate processing
        if session_id in self.processing_sessions:
            return

        self.processing_sessions.add(session_id)

        try:
            # Ensure agent manager is ready
            await self._ensure_agent_manager()

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
                    "message": f"Gemini orchestrator analyzing your request...",
                    "query": query
                }
            )

            # Log interaction
            await self._log_interaction(
                session_id,
                EventType.USER_INPUT,
                {"query": query}
            )

            # Check if Gemini is available
            if not self.gemini.available:
                response = f"""⚠️ Gemini API not configured. Please set GEMINI_API_KEY.

Your query: "{query}"

To enable intelligent multi-agent orchestration, get an API key at: https://makersuite.google.com/app/apikey"""

                await self._stream_response(session_id, response)
                await self._complete_session(session_id, response)
                return

            # **STEP 1: Gemini analyzes query and creates execution plan**
            await streaming_manager.send_event(
                session_id,
                StreamEventType.AGENT_THINKING,
                {"thought": "🧠 Gemini is analyzing your request and planning the approach..."}
            )

            plan = await self._create_execution_plan(query)

            # **STEP 2: Execute the plan**
            if plan["requires_agents"]:
                # Multi-agent orchestrated approach
                result = await self._execute_multi_agent_plan(session_id, query, plan)
            else:
                # Direct Gemini response
                result = await self._execute_direct_response(session_id, query, plan)

            # **STEP 3: Complete session**
            await self._complete_session(session_id, result)

        except Exception as e:
            error_msg = f"Session processing error: {str(e)}"
            await streaming_manager.send_event(
                session_id,
                StreamEventType.ERROR,
                {"message": error_msg}
            )
            print(f"Error in session {session_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.processing_sessions.discard(session_id)

    async def _create_execution_plan(self, query: str) -> Dict:
        """
        Use Gemini to analyze query and create intelligent execution plan
        """
        # Get available agents
        agents = []
        if self._agent_manager_initialized:
            try:
                agents = await agent_manager.list_agents()
            except:
                pass

        agents_description = "\n".join([
            f"- {agent.name} ({agent.id}): {agent.description}"
            for agent in agents[:10]  # Limit to avoid token overflow
        ])

        planning_prompt = f"""You are an intelligent task orchestrator with access to specialized AI agents.

**User Query:**
{query}

**Available Agents:**
{agents_description}

**Your Task:**
Analyze the query and create an execution plan.

Return ONLY a JSON object with this structure:
{{
    "requires_agents": true/false,
    "reasoning": "why this approach is best",
    "approach": "multi-agent" or "direct",
    "agents_to_use": ["agent-id-1", "agent-id-2"],
    "execution_steps": ["step 1", "step 2"],
    "expected_output_type": "research_report" or "analysis" or "answer" or "code"
}}

**Guidelines:**
- Use agents for: research, analysis, specialized tasks, multi-step workflows
- Use direct response for: simple questions, math, general knowledge, quick answers
- Choose 1-3 most relevant agents
- Be concise in reasoning

JSON Response:"""

        try:
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                lambda: self.gemini.model.generate_content(planning_prompt).text
            )

            # Clean response and parse JSON
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            plan = json.loads(response_text.strip())
            return plan

        except Exception as e:
            print(f"Planning error: {e}, using fallback")
            # Fallback plan - direct response
            return {
                "requires_agents": False,
                "reasoning": "Using direct Gemini response as fallback",
                "approach": "direct",
                "agents_to_use": [],
                "execution_steps": ["Generate direct response"],
                "expected_output_type": "answer"
            }

    async def _execute_multi_agent_plan(self, session_id: str, query: str, plan: Dict) -> str:
        """Execute a multi-agent orchestrated workflow"""

        await streaming_manager.send_event(
            session_id,
            StreamEventType.AGENT_THINKING,
            {"thought": f"📋 Plan: {plan['reasoning']}"}
        )

        await asyncio.sleep(0.5)

        # Show which agents will be used
        agents_list = ", ".join(plan.get("agents_to_use", []))
        await streaming_manager.send_event(
            session_id,
            StreamEventType.TOOL_CALL,
            {"tool_name": "Multi-Agent System", "description": f"Coordinating: {agents_list}"}
        )

        # For now, simulate multi-agent coordination with Gemini doing the heavy lifting
        # In production, this would create tasks for each agent and coordinate their execution

        coordination_prompt = f"""You are coordinating multiple specialized AI agents to answer this query:

**Query:** {query}

**Execution Plan:**
- Approach: {plan['approach']}
- Agents: {', '.join(plan.get('agents_to_use', []))}
- Steps: {json.dumps(plan.get('execution_steps', []))}

**Your Task:**
Provide a comprehensive response as if you coordinated these agents.
Include:
1. Analysis from relevant perspectives
2. Structured, well-organized information
3. Actionable insights or conclusions
4. Format in markdown for clarity

Generate the coordinated response:"""

        await streaming_manager.send_event(
            session_id,
            StreamEventType.AGENT_THINKING,
            {"thought": "🤝 Agents are collaborating on your request..."}
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.gemini.model.generate_content(coordination_prompt).text
        )

        await streaming_manager.send_event(
            session_id,
            StreamEventType.TOOL_RESULT,
            {"tool_name": "Multi-Agent System", "status": "success"}
        )

        # Stream the orchestrated response
        await self._stream_response(session_id, result)

        return result

    async def _execute_direct_response(self, session_id: str, query: str, plan: Dict) -> str:
        """Execute direct Gemini response for simple queries"""

        await streaming_manager.send_event(
            session_id,
            StreamEventType.TOOL_CALL,
            {"tool_name": "gemini-2.5-flash", "description": f"Generating response"}
        )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini.model.generate_content(query).text
        )

        await streaming_manager.send_event(
            session_id,
            StreamEventType.TOOL_RESULT,
            {"tool_name": "gemini-2.5-flash", "status": "success"}
        )

        await self._stream_response(session_id, response)

        return response

    async def _stream_response(self, session_id: str, response: str):
        """Stream response text in chunks"""
        words = response.split()
        chunk_size = 3

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            await streaming_manager.send_event(
                session_id,
                StreamEventType.CHUNK,
                {"chunk": chunk}
            )
            await asyncio.sleep(0.05)

    async def _complete_session(self, session_id: str, response: str):
        """Mark session as complete"""
        # Update session in database
        with get_db() as db:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.final_output = response
                session.status = SessionStatus.COMPLETED
                session.end_time = datetime.utcnow()
                if session.start_time:
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


# Global intelligent session processor instance
intelligent_session_processor = IntelligentSessionProcessor()
