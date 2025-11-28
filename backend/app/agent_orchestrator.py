"""
Agent Orchestrator using LangGraph

This module implements sophisticated multi-agent coordination using LangGraph,
following the recommendations from "Multi-Agent System Architecture: Best Practices"

Key Features:
- Stateful agent workflows
- MCP-based tool integration
- Context-aware task routing
- Multi-agent collaboration patterns
"""

import os
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from datetime import datetime
import logging

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph not available")

# Try to import Gemini (preferred - free tier)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Gemini not available")

# Fallback to Anthropic
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from app.mcp_client import create_research_client, create_geospatial_client

logger = logging.getLogger(__name__)


# Define the agent state
class AgentState(TypedDict):
    """State for multi-agent workflow"""
    task_id: str
    task_title: str
    task_description: str
    agent_name: str
    agent_type: str
    messages: List[Any]  # List of messages
    research_data: Optional[Dict[str, Any]]
    geospatial_data: Optional[Dict[str, Any]]
    code_blocks: List[Dict[str, Any]]
    final_report: Optional[str]
    status: str
    errors: List[str]


class AgentOrchestrator:
    """
    LangGraph-based agent orchestrator

    Manages complex multi-agent workflows using a state machine approach:
    1. Research phase (web search + synthesis)
    2. Analysis phase (specialized agent processing)
    3. Integration phase (combine findings)
    4. Report generation phase
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph not available - orchestrator disabled")
            self.enabled = False
            return

        # Prefer Gemini (free tier), fallback to Anthropic
        if self.gemini_api_key and GEMINI_AVAILABLE:
            logger.info("Using Google Gemini (free tier)")
            self.enabled = True
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=self.gemini_api_key,
                max_output_tokens=4000,
                temperature=0.7
            )
            self.llm_provider = "gemini"
        elif self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            logger.info("Using Anthropic Claude")
            self.enabled = True
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=self.anthropic_api_key,
                max_tokens=4000
            )
            self.llm_provider = "anthropic"
        else:
            logger.warning("No API key configured (set GEMINI_API_KEY or ANTHROPIC_API_KEY)")
            self.enabled = False
            return

        # Build the agent workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for multi-agent coordination"""

        workflow = StateGraph(AgentState)

        # Define workflow nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("integrate", self._integrate_node)
        workflow.add_node("generate_report", self._generate_report_node)

        # Define workflow edges
        workflow.set_entry_point("research")
        workflow.add_edge("research", "analyze")
        workflow.add_edge("analyze", "integrate")
        workflow.add_edge("integrate", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    async def _research_node(self, state: AgentState) -> AgentState:
        """
        Research node: Conduct web research using MCP research server

        This node:
        1. Creates research MCP client
        2. Conducts web search
        3. Synthesizes findings
        """
        logger.info(f"[Research Node] Starting research for: {state['task_title']}")

        try:
            # Create MCP client for research
            research_client = await create_research_client()

            if not research_client.is_connected():
                state["errors"].append("Failed to connect to research MCP server")
                state["research_data"] = {"status": "error", "error": "MCP connection failed"}
                return state

            # Conduct research via MCP
            research_result = await research_client.conduct_research(
                topic=state["task_title"],
                depth="comprehensive",
                agent_type=state["agent_type"]
            )

            state["research_data"] = research_result

            # Add research summary to messages
            if research_result.get("status") == "success":
                state["messages"].append(
                    AIMessage(content=f"Research completed: {research_result.get('sources_found', 0)} sources analyzed")
                )

            await research_client.disconnect()

            logger.info(f"[Research Node] Completed - found {research_result.get('sources_found', 0)} sources")

        except Exception as e:
            logger.error(f"[Research Node] Error: {e}")
            state["errors"].append(f"Research error: {str(e)}")
            state["research_data"] = {"status": "error", "error": str(e)}

        return state

    async def _analyze_node(self, state: AgentState) -> AgentState:
        """
        Analysis node: Apply agent-specific analysis

        This node uses the LLM to perform specialized analysis based on
        the agent's type and the research findings
        """
        logger.info(f"[Analysis Node] Analyzing with {state['agent_name']}")

        try:
            research_content = state.get("research_data", {}).get("content", "No research data")

            # Build analysis prompt based on agent type
            system_prompt = self._get_agent_system_prompt(state["agent_type"])

            analysis_prompt = f"""Based on the research findings, provide specialized analysis for: {state['task_title']}

Task Description: {state['task_description']}

Research Findings:
{research_content[:2000]}  # Limit context

Please provide:
1. Technical analysis specific to your expertise
2. Implementation recommendations
3. Code examples (if applicable)
4. Risk assessment
5. Next steps"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=analysis_prompt)
            ]

            response = self.llm.invoke(messages)
            analysis_content = response.content

            state["messages"].append(AIMessage(content=f"Analysis completed by {state['agent_name']}"))

            # Store analysis in state (could add as separate field if needed)
            if "analysis_results" not in state:
                state["analysis_results"] = []
            state["analysis_results"].append({
                "agent": state["agent_name"],
                "content": analysis_content
            })

            logger.info(f"[Analysis Node] Completed")

        except Exception as e:
            logger.error(f"[Analysis Node] Error: {e}")
            state["errors"].append(f"Analysis error: {str(e)}")

        return state

    async def _integrate_node(self, state: AgentState) -> AgentState:
        """
        Integration node: Combine findings from research and analysis

        This node synthesizes all gathered information into a cohesive narrative
        """
        logger.info(f"[Integration Node] Integrating findings")

        try:
            research_data = state.get("research_data", {})
            analysis_results = state.get("analysis_results", [])

            # Check if we have geospatial context (if applicable)
            if "geospatial" in state.get("task_description", "").lower():
                geospatial_client = await create_geospatial_client()
                if geospatial_client.is_connected():
                    # Extract location from task description (simplified)
                    geo_context = await geospatial_client.get_geospatial_context(
                        location="task area",
                        data_sources=[]
                    )
                    state["geospatial_data"] = geo_context
                    await geospatial_client.disconnect()

            integration_prompt = f"""Integrate the following research and analysis into a cohesive narrative:

Research Sources: {research_data.get('sources_found', 0)}
Analysis Completed: {len(analysis_results)}

Create a unified synthesis that:
1. Combines research findings with specialized analysis
2. Resolves any conflicting information
3. Highlights key insights
4. Provides actionable recommendations

Keep the synthesis focused and technically accurate."""

            messages = [
                SystemMessage(content="You are a synthesis expert combining multiple sources of information."),
                HumanMessage(content=integration_prompt)
            ]

            response = self.llm.invoke(messages)
            integration_content = response.content

            state["messages"].append(AIMessage(content="Integration completed"))
            state["integration_synthesis"] = integration_content

            logger.info(f"[Integration Node] Completed")

        except Exception as e:
            logger.error(f"[Integration Node] Error: {e}")
            state["errors"].append(f"Integration error: {str(e)}")

        return state

    async def _generate_report_node(self, state: AgentState) -> AgentState:
        """
        Report generation node: Create final comprehensive report

        This node produces the final deliverable in the requested format
        """
        logger.info(f"[Report Generation Node] Generating final report")

        try:
            research_data = state.get("research_data", {})
            integration = state.get("integration_synthesis", "")

            report_prompt = f"""Generate a comprehensive research report on: {state['task_title']}

Task Description: {state['task_description']}

Integration Synthesis:
{integration}

Create a professional report with:
1. **Executive Summary** - 2-3 paragraphs
2. **Background & Context**
3. **Research Findings** - organized by theme
4. **Technical Analysis** - implementation details, code examples
5. **Practical Applications** - real-world use cases
6. **Recommendations** - high/medium/future priority
7. **References** - cited sources

Format: Scientific/Technical Markdown
Include code blocks where applicable.
Be comprehensive but focused."""

            messages = [
                SystemMessage(content=f"You are {state['agent_name']}, a specialized research agent."),
                HumanMessage(content=report_prompt)
            ]

            response = self.llm.invoke(messages)
            final_report = response.content

            state["final_report"] = final_report
            state["status"] = "completed"

            logger.info(f"[Report Generation Node] Report generated ({len(final_report)} chars)")

        except Exception as e:
            logger.error(f"[Report Generation Node] Error: {e}")
            state["errors"].append(f"Report generation error: {str(e)}")
            state["status"] = "failed"

        return state

    def _get_agent_system_prompt(self, agent_type: str) -> str:
        """Get specialized system prompt based on agent type"""
        prompts = {
            "security": "You are a cybersecurity expert analyzing systems for vulnerabilities and best practices.",
            "analytics": "You are a data analytics specialist focused on insights and patterns.",
            "architecture": "You are a software architect designing scalable, maintainable systems.",
            "optimization": "You are a performance optimization expert improving efficiency and speed.",
            "research": "You are a research specialist conducting comprehensive analysis.",
            "qa": "You are a QA engineer focusing on testing strategies and quality assurance.",
            "default": "You are a technical specialist providing expert analysis."
        }

        return prompts.get(agent_type, prompts["default"])

    async def execute_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        agent_name: str,
        agent_type: str
    ) -> Dict[str, Any]:
        """
        Execute a task using the LangGraph orchestration workflow

        Args:
            task_id: Unique task identifier
            task_title: Task title
            task_description: Task description
            agent_name: Name of the assigned agent
            agent_type: Type/specialization of the agent

        Returns:
            Execution result with final report
        """
        if not self.enabled:
            return {
                "status": "error",
                "error": "Agent orchestrator not enabled (missing LangGraph or API key)"
            }

        logger.info(f"[Orchestrator] Executing task {task_id} with agent {agent_name}")

        # Initialize state
        initial_state: AgentState = {
            "task_id": task_id,
            "task_title": task_title,
            "task_description": task_description,
            "agent_name": agent_name,
            "agent_type": agent_type,
            "messages": [
                HumanMessage(content=f"Execute task: {task_title}")
            ],
            "research_data": None,
            "geospatial_data": None,
            "code_blocks": [],
            "final_report": None,
            "status": "running",
            "errors": []
        }

        try:
            # Execute the workflow
            final_state = await self.workflow.ainvoke(initial_state)

            return {
                "status": final_state.get("status", "completed"),
                "task_id": task_id,
                "agent_name": agent_name,
                "final_report": final_state.get("final_report", ""),
                "research_sources": final_state.get("research_data", {}).get("sources_found", 0),
                "errors": final_state.get("errors", []),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Workflow execution failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "task_id": task_id
            }


# Singleton instance
agent_orchestrator = AgentOrchestrator()
