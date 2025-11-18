"""
Research Tools MCP Server

This MCP server exposes web research and AI synthesis tools using the Model Context Protocol.
It provides standardized access to Brave Search, Anthropic Claude, and research capabilities.

Following the research recommendations from "Multi-Agent System Architecture: Best Practices"
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import requests
    import anthropic
    RESEARCH_AVAILABLE = True
except ImportError:
    RESEARCH_AVAILABLE = False
    print("⚠️  Research dependencies not available")

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel


class ResearchServer:
    """
    MCP Server for research and web analysis tools

    Exposes Tools for:
    - Web search (Brave API)
    - AI-powered research synthesis (Claude)
    - Knowledge extraction
    - Report generation
    """

    def __init__(self):
        self.server = Server("research-tools")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if self.anthropic_api_key:
            self.claude = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.claude = None

        self._register_tools()

    def _register_tools(self):
        """Register all research tools with the MCP server"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available research tools"""
            return [
                Tool(
                    name="web_search",
                    description="Search the web using Brave Search API for current information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="synthesize_research",
                    description="Use Claude AI to synthesize research findings into a structured report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic"
                            },
                            "sources": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "List of source materials"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "scientific", "executive"],
                                "description": "Output format (default: markdown)",
                                "default": "markdown"
                            }
                        },
                        "required": ["topic", "sources"]
                    }
                ),
                Tool(
                    name="extract_code",
                    description="Extract executable code blocks from research content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to extract code from"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language filter (optional)"
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="conduct_research",
                    description="Comprehensive research pipeline: search → analyze → synthesize → report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic or question"
                            },
                            "depth": {
                                "type": "string",
                                "enum": ["quick", "standard", "comprehensive"],
                                "description": "Research depth (default: standard)",
                                "default": "standard"
                            },
                            "agent_type": {
                                "type": "string",
                                "description": "Agent specialization for context"
                            }
                        },
                        "required": ["topic"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a research tool"""

            if not RESEARCH_AVAILABLE:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Research dependencies not available",
                        "message": "Install requests and anthropic SDK"
                    })
                )]

            try:
                if name == "web_search":
                    result = await self._web_search(
                        arguments["query"],
                        arguments.get("count", 10)
                    )
                elif name == "synthesize_research":
                    result = await self._synthesize_research(
                        arguments["topic"],
                        arguments["sources"],
                        arguments.get("format", "markdown")
                    )
                elif name == "extract_code":
                    result = await self._extract_code(
                        arguments["content"],
                        arguments.get("language")
                    )
                elif name == "conduct_research":
                    result = await self._conduct_research(
                        arguments["topic"],
                        arguments.get("depth", "standard"),
                        arguments.get("agent_type", "research")
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "tool": name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )]

    async def _web_search(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Search the web using Brave Search API"""

        if not self.brave_api_key:
            return {
                "status": "mock",
                "message": "No BRAVE_API_KEY - using mock results",
                "results": [
                    {
                        "title": f"Research on {query}",
                        "url": "https://example.com",
                        "description": f"Information about {query}"
                    }
                ]
            }

        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }

            params = {"q": query, "count": count}

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "age": item.get("age", ""),
                        "page_age": item.get("page_age", "")
                    })

                return {
                    "status": "success",
                    "query": query,
                    "count": len(results),
                    "results": results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Brave API returned {response.status_code}",
                    "query": query
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }

    async def _synthesize_research(
        self,
        topic: str,
        sources: List[Dict],
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """Use Claude to synthesize research findings"""

        if not self.claude:
            return {
                "error": "No ANTHROPIC_API_KEY - synthesis not available"
            }

        # Build synthesis prompt
        sources_text = "\n\n".join([
            f"**Source {i+1}:** {src.get('title', 'Untitled')}\n"
            f"URL: {src.get('url', 'N/A')}\n"
            f"{src.get('description', '')}"
            for i, src in enumerate(sources)
        ])

        format_instructions = {
            "markdown": "Use markdown formatting with headers, lists, and code blocks.",
            "scientific": "Use scientific paper format with Abstract, Methods, Results, Discussion.",
            "executive": "Use executive summary format with key findings and recommendations."
        }

        prompt = f"""Synthesize the following research sources on the topic: "{topic}"

{sources_text}

Please create a comprehensive research report using {format} format.
{format_instructions.get(format, '')}

Include:
1. Executive Summary
2. Key Findings
3. Technical Analysis (if applicable)
4. Practical Applications
5. References

Focus on actionable insights and technical depth."""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = message.content[0].text

            return {
                "status": "success",
                "topic": topic,
                "format": format,
                "content": content,
                "word_count": len(content.split()),
                "sources_used": len(sources),
                "model": "claude-sonnet-4",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Claude synthesis failed: {str(e)}"
            }

    async def _extract_code(
        self,
        content: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract code blocks from content"""

        import re

        # Pattern for markdown code blocks
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        code_blocks = []
        for lang, code in matches:
            if language and lang != language:
                continue

            code_blocks.append({
                "language": lang or "unknown",
                "code": code.strip(),
                "lines": len(code.strip().split('\n'))
            })

        return {
            "status": "success",
            "blocks_found": len(code_blocks),
            "code_blocks": code_blocks,
            "filter": language if language else "all"
        }

    async def _conduct_research(
        self,
        topic: str,
        depth: str = "standard",
        agent_type: str = "research"
    ) -> Dict[str, Any]:
        """Comprehensive research pipeline"""

        # Step 1: Web search
        search_count = {"quick": 5, "standard": 10, "comprehensive": 15}[depth]
        search_result = await self._web_search(topic, search_count)

        if search_result.get("status") != "success":
            return search_result

        # Step 2: Synthesize findings
        synthesis_result = await self._synthesize_research(
            topic,
            search_result["results"],
            format="scientific" if depth == "comprehensive" else "markdown"
        )

        if synthesis_result.get("status") != "success":
            return synthesis_result

        # Step 3: Extract code (if any)
        code_result = await self._extract_code(synthesis_result["content"])

        return {
            "status": "success",
            "topic": topic,
            "depth": depth,
            "agent_type": agent_type,
            "sources_found": search_result["count"],
            "content": synthesis_result["content"],
            "word_count": synthesis_result["word_count"],
            "code_blocks": code_result["blocks_found"],
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
research_server = ResearchServer()
