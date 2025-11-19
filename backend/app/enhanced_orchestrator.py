"""
Enhanced Intelligent Orchestrator
Integrates: Gemini Planning + RAG Context + Agent Skills + MCP Tools + Real Agent Execution
PRESERVES: All existing functionality - purely additive enhancements
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import sys

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from app.database import get_db
from app.models import Session, SessionStatus, InteractionLog, EventType, Task, TaskStatus
from app.streaming import streaming_manager, StreamEventType
from app.gemini_researcher import GeminiResearcher
from agent_mcp.agent_manager import agent_manager


class EnhancedOrchestrator:
    """
    Enhanced orchestrator that integrates:
    1. Gemini as planning brain (existing intelligent_session_processor)
    2. RAG for context augmentation (existing ChromaDB system)
    3. Agent Skills from genomes (existing genome system)
    4. MCP Tools integration (existing MCP server)
    5. Real agent execution (existing agent_executor)

    **PRESERVES ALL EXISTING FUNCTIONALITY** - only adds intelligent routing
    """

    def __init__(self):
        self.gemini = GeminiResearcher()
        self.processing_sessions = set()
        self._agent_manager_initialized = False
        self._vector_store = None
        self._agent_executor = None

    async def _ensure_systems(self):
        """Lazy initialize all systems - fail gracefully if unavailable"""

        # Initialize agent manager (existing)
        if not self._agent_manager_initialized:
            try:
                await agent_manager.initialize()
                self._agent_manager_initialized = True
                print("✅ Agent manager initialized")
            except Exception as e:
                print(f"⚠️  Agent manager unavailable: {e}")

        # Import vector store (existing RAG system)
        if not self._vector_store:
            try:
                from app.vector_store import vector_store
                self._vector_store = vector_store
                print("✅ RAG vector store connected")
            except Exception as e:
                print(f"⚠️  Vector store unavailable: {e}")

        # Import agent executor (existing)
        if not self._agent_executor:
            try:
                from app.agent_executor import agent_executor
                self._agent_executor = agent_executor
                print("✅ Agent executor connected")
            except Exception as e:
                print(f"⚠️  Agent executor unavailable: {e}")

    async def process_session(self, session_id: str):
        """
        Main orchestration entry point - routes to optimal execution strategy
        """
        if session_id in self.processing_sessions:
            return

        self.processing_sessions.add(session_id)

        try:
            await self._ensure_systems()

            # Get session
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

            # Start event
            await streaming_manager.send_event(
                session_id,
                StreamEventType.SESSION_START,
                {"message": "🧠 Enhanced orchestrator analyzing your request...", "query": query}
            )

            # Check Gemini availability
            if not self.gemini.available:
                response = "⚠️ Gemini API not configured. Set GEMINI_API_KEY to enable intelligent orchestration."
                await self._stream_response(session_id, response)
                await self._complete_session(session_id, response)
                return

            #  **STEP 1: Augment query with RAG context**
            augmented_query = await self._augment_with_rag(query, session_id)

            # **STEP 2: Gemini creates execution plan**
            await streaming_manager.send_event(
                session_id,
                StreamEventType.AGENT_THINKING,
                {"thought": "📋 Planning optimal execution strategy..."}
            )

            plan = await self._create_execution_plan(augmented_query, query)

            # **STEP 3: Execute based on plan**
            if plan["requires_agents"] and plan.get("agents_to_use"):
                # Real agent execution with skills
                result = await self._execute_with_real_agents(session_id, query, plan)
            else:
                # Direct Gemini response
                result = await self._execute_direct(session_id, query)

            # Complete
            await self._complete_session(session_id, result)

        except Exception as e:
            error_msg = f"Orchestration error: {str(e)}"
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

    async def _augment_with_rag(self, query: str, session_id: str) -> str:
        """
        Augment query with relevant context from RAG (existing ChromaDB)
        PRESERVES: Existing vector_store functionality
        """
        if not self._vector_store:
            return query  # Graceful fallback

        try:
            await streaming_manager.send_event(
                session_id,
                StreamEventType.AGENT_THINKING,
                {"thought": "🔍 Searching knowledge base for relevant context..."}
            )

            # Query shared organizational knowledge (existing collection)
            results = await asyncio.to_thread(
                self._vector_store.query_shared_knowledge,
                query,
                n_results=5
            )

            if results and results.get("documents") and results["documents"][0]:
                context_snippets = results["documents"][0][:3]  # Top 3 results

                augmented = f"""User Query: {query}

**Relevant Knowledge Context:**
{chr(10).join([f"- {snippet[:200]}..." for snippet in context_snippets])}

Please consider this context when planning the response."""

                await streaming_manager.send_event(
                    session_id,
                    StreamEventType.TOOL_RESULT,
                    {"tool_name": "RAG Knowledge Base", "status": "success", "context_found": len(context_snippets)}
                )

                return augmented

            return query  # No context found, use original

        except Exception as e:
            print(f"RAG augmentation error: {e}")
            return query  # Graceful fallback

    async def _create_execution_plan(self, augmented_query: str, original_query: str) -> Dict:
        """
        Use Gemini to create intelligent execution plan
        PRESERVES: Existing agent discovery and capabilities
        """
        # Get available agents with their skills (existing genome system)
        agents_with_skills = await self._get_agents_with_skills()

        planning_prompt = f"""You are an intelligent task orchestrator with access to specialized AI agents.

**User Query:**
{original_query}

**Available Agents with Skills:**
{agents_with_skills}

**Context-Augmented Query:**
{augmented_query}

Create an execution plan. Return ONLY valid JSON:
{{
    "requires_agents": true/false,
    "reasoning": "brief explanation",
    "approach": "real-agents" or "direct",
    "agents_to_use": ["agent-id-1"],
    "execution_steps": ["step1", "step2"],
    "expected_output": "research_report|analysis|answer|code"
}}

Guidelines:
- ALWAYS use "real-agents" for: research, analysis, build, create, develop, investigate, explore, any query with keywords like "research", "analyze", "build", "create", "find", "investigate"
- ONLY use "direct" for: trivial questions like "what is 2+2", "what color is the sky"
- When in doubt, use "real-agents" - always create visible tasks
- Select 1-2 most relevant agents based on their skills
- Be concise

JSON:"""

        try:
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                lambda: self.gemini.model.generate_content(planning_prompt).text
            )

            # Parse JSON
            response_text = response_text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            plan = json.loads(response_text.strip())
            return plan

        except Exception as e:
            print(f"Planning error: {e}, using fallback")
            return {
                "requires_agents": False,
                "reasoning": "Fallback to direct response",
                "approach": "direct",
                "agents_to_use": [],
                "execution_steps": ["Direct Gemini response"],
                "expected_output": "answer"
            }

    async def _get_agents_with_skills(self) -> str:
        """
        Get agents with their genome skills
        PRESERVES: Existing genome and agent discovery
        """
        if not self._agent_manager_initialized:
            return "No agents available"

        try:
            agents = await agent_manager.list_agents()

            agent_descriptions = []
            for agent in agents[:10]:  # Limit to avoid token overflow
                # Try to load genome (existing system)
                genome_file = Path(f".agents/dna/{agent.id}/genome.json")
                skills_summary = "General capabilities"

                if genome_file.exists():
                    try:
                        genome = json.loads(genome_file.read_text())
                        tech_skills = genome.get("technical_skills", [])
                        domain_skills = genome.get("domain_skills", [])

                        skills_list = []
                        for skill in tech_skills[:3]:
                            skills_list.append(f"{skill['name']} (L{skill['level']})")
                        for skill in domain_skills[:2]:
                            skills_list.append(f"{skill['name']} ({skill['proficiency']})")

                        if skills_list:
                            skills_summary = ", ".join(skills_list)
                    except:
                        pass

                agent_descriptions.append(
                    f"- **{agent.name}** ({agent.id}): {agent.description[:80]}... | Skills: {skills_summary}"
                )

            return "\n".join(agent_descriptions) if agent_descriptions else "No agents available"

        except Exception as e:
            print(f"Error loading agents with skills: {e}")
            return "Agents temporarily unavailable"

    async def _execute_with_real_agents(self, session_id: str, query: str, plan: Dict) -> str:
        """
        Execute using REAL agents from existing agent_executor and agent_manager
        PRESERVES: All existing agent execution logic
        """
        agent_ids = plan.get("agents_to_use", [])

        if not agent_ids:
            # Fallback to direct response
            return await self._execute_direct(session_id, query)

        await streaming_manager.send_event(
            session_id,
            StreamEventType.AGENT_THINKING,
            {"thought": f"🤝 Coordinating agents: {', '.join(agent_ids)}"}
        )

        results = []

        for agent_id in agent_ids:
            try:
                await streaming_manager.send_event(
                    session_id,
                    StreamEventType.TOOL_CALL,
                    {"tool_name": agent_id, "description": f"Executing {agent_id}"}
                )

                # Create and execute task using existing agent_manager (PRESERVES existing system)
                task = await agent_manager.create_task(
                    agent_id=agent_id,
                    title=f"Process query: {query[:50]}...",
                    description=query,
                    context={"session_id": session_id, "plan": plan}
                )

                # Execute task (existing agent_executor handles this)
                await agent_manager.execute_task(task.id)

                # Wait for completion with timeout
                max_wait = 30  # 30 seconds
                for _ in range(max_wait):
                    updated_task = await agent_manager.get_task(task.id)
                    if updated_task.status == TaskStatus.COMPLETED:
                        result_text = updated_task.result.get("output", "") if updated_task.result else ""
                        results.append(f"## {agent_id} Output:\n{result_text}")

                        await streaming_manager.send_event(
                            session_id,
                            StreamEventType.TOOL_RESULT,
                            {"tool_name": agent_id, "status": "success"}
                        )
                        break
                    elif updated_task.status == TaskStatus.FAILED:
                        error = updated_task.error or "Unknown error"
                        results.append(f"## {agent_id}: Task failed - {error}")
                        break

                    await asyncio.sleep(1)
                else:
                    # Timeout
                    results.append(f"## {agent_id}: Task timeout after {max_wait}s")

            except Exception as e:
                print(f"Error executing agent {agent_id}: {e}")
                results.append(f"## {agent_id}: Execution error - {str(e)}")

        # Synthesize results
        if results:
            combined = "\n\n".join(results)
            synthesis = await self._synthesize_results(query, combined)
            await self._stream_response(session_id, synthesis)
            return synthesis
        else:
            # Fallback to direct
            return await self._execute_direct(session_id, query)

    async def _synthesize_results(self, query: str, agent_outputs: str) -> str:
        """Use Gemini to synthesize multiple agent outputs"""
        synthesis_prompt = f"""Synthesize the following agent outputs into a cohesive response.

**Original Query:** {query}

**Agent Outputs:**
{agent_outputs}

**Task:** Create a comprehensive, well-structured response that combines insights from all agents.
Format in markdown. Be concise but thorough.

Synthesized Response:"""

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.gemini.model.generate_content(synthesis_prompt).text
            )
            return result
        except Exception as e:
            print(f"Synthesis error: {e}")
            return agent_outputs  # Return raw outputs as fallback

    async def _execute_direct(self, session_id: str, query: str) -> str:
        """Direct Gemini response for simple queries"""
        await streaming_manager.send_event(
            session_id,
            StreamEventType.TOOL_CALL,
            {"tool_name": "gemini-2.5-flash", "description": "Generating response"}
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
        """Stream response in chunks"""
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
        """Mark session complete"""
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

        await self._log_interaction(session_id, EventType.LLM_RESPONSE, {"response": response})

        await streaming_manager.send_event(
            session_id,
            StreamEventType.SESSION_COMPLETE,
            {"final_output": response, "status": "completed"}
        )

    async def _log_interaction(self, session_id: str, event_type: EventType, content: dict):
        """Log interaction"""
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


# Global instance
enhanced_orchestrator = EnhancedOrchestrator()
