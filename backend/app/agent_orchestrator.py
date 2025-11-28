"""
Simple Research Orchestrator

Streamlined research engine that takes a query and generates a comprehensive report.
"""

import os
from typing import Any, Dict
from datetime import datetime
import logging

# Try to import Gemini (preferred - free tier)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Gemini not available")

# Fallback to Anthropic
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Simple research orchestrator - one input, one output"""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Prefer Gemini (free tier), fallback to Anthropic
        if self.gemini_api_key and GEMINI_AVAILABLE:
            logger.info("Using Google Gemini")
            self.enabled = True
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self.gemini_api_key,
                max_output_tokens=8000,
                temperature=0.7
            )
            self.llm_provider = "gemini"
        elif self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            logger.info("Using Anthropic Claude")
            self.enabled = True
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=self.anthropic_api_key,
                max_tokens=8000
            )
            self.llm_provider = "anthropic"
        else:
            logger.warning("No API key configured - orchestrator disabled")
            self.enabled = False
            self.llm_provider = "none"

    async def execute_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        agent_name: str = "Research Agent",
        agent_type: str = "research"
    ) -> Dict[str, Any]:
        """
        Execute a research task and generate a comprehensive report.

        Args:
            task_id: Unique task identifier
            task_title: The research topic/question
            task_description: Additional context
            agent_name: Name of agent (for logging)
            agent_type: Type of research

        Returns:
            Result dictionary with final_report
        """
        if not self.enabled:
            return {
                "status": "error",
                "error": "Research engine not enabled - no API key configured"
            }

        logger.info(f"[Research] Processing: {task_title}")

        try:
            # Build the research prompt
            prompt = f"""You are a research assistant. Generate a comprehensive research report on the following topic.

## Research Topic
{task_title}

{f"## Additional Context" if task_description != task_title else ""}
{task_description if task_description != task_title else ""}

## Instructions
Create a well-structured research report that includes:

1. **Executive Summary** - Brief overview of key findings
2. **Background** - Context and importance of this topic
3. **Main Findings** - Detailed analysis organized by themes
4. **Practical Applications** - Real-world use cases and examples
5. **Code Examples** - If applicable, include working code snippets
6. **Recommendations** - Actionable next steps
7. **Conclusion** - Summary and future directions

Format the report in clear Markdown with proper headings, bullet points, and code blocks where appropriate.
Be comprehensive but focused. Provide specific, actionable information."""

            # Call the LLM
            response = self.llm.invoke(prompt)
            report_content = response.content

            logger.info(f"[Research] Completed - {len(report_content)} chars")

            return {
                "status": "completed",
                "task_id": task_id,
                "final_report": report_content,
                "timestamp": datetime.utcnow().isoformat(),
                "provider": self.llm_provider
            }

        except Exception as e:
            logger.error(f"[Research] Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "task_id": task_id
            }


# Singleton instance
agent_orchestrator = AgentOrchestrator()
