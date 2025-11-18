"""
MCP Client for Agent Communication

This client provides a unified interface for agents to interact with MCP servers,
following the Model Context Protocol standards.

Implements the recommendations from "Multi-Agent System Architecture: Best Practices"
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

try:
    from mcp.client import Client, StdioServerParameters
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  MCP SDK not available")

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Unified MCP client for agent-tool communication

    This replaces direct REST API calls with context-aware MCP protocol,
    reducing boilerplate and improving context management.

    Features:
    - Automatic tool discovery
    - Context-aware requests
    - Session management
    - Graceful degradation
    """

    def __init__(self, server_name: str = "geospatial-tools"):
        """
        Initialize MCP client

        Args:
            server_name: Name of the MCP server to connect to
        """
        self.server_name = server_name
        self.client: Optional[Client] = None
        self.session_id: Optional[str] = None
        self.available_tools: List[Dict[str, Any]] = []
        self._connected = False

        if not MCP_AVAILABLE:
            logger.warning("MCP SDK not available - client will operate in fallback mode")

    async def connect(self):
        """Connect to MCP server"""
        if not MCP_AVAILABLE:
            logger.info("MCP not available - skipping connection")
            return False

        try:
            # In-process connection (servers are part of the same app)
            # For production, you might use stdio or HTTP transport
            from app.mcp_servers import geospatial_server, research_server

            # Map server names to server instances
            server_map = {
                "geospatial-tools": geospatial_server.server,
                "research-tools": research_server.server
            }

            server = server_map.get(self.server_name)
            if not server:
                logger.error(f"Unknown MCP server: {self.server_name}")
                return False

            # Direct in-process connection
            self.client = server
            self._connected = True

            # Discover available tools
            await self.discover_tools()

            logger.info(f"Connected to MCP server: {self.server_name}")
            logger.info(f"Available tools: {[t['name'] for t in self.available_tools]}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server_name}: {e}")
            return False

    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover available tools from the MCP server

        Returns:
            List of tool definitions
        """
        if not self._connected or not self.client:
            logger.warning("Not connected to MCP server")
            return []

        try:
            # Call list_tools on the server
            # Note: In a real MCP setup, this would be a protocol message
            # For now, we'll access the server's tools directly
            from app.mcp_servers import geospatial_server, research_server

            if self.server_name == "geospatial-tools":
                tools_response = await geospatial_server.server._handlers["list_tools"]()
            elif self.server_name == "research-tools":
                tools_response = await research_server.server._handlers["list_tools"]()
            else:
                return []

            self.available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_response
            ]

            return self.available_tools

        except Exception as e:
            logger.error(f"Failed to discover tools: {e}")
            return []

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            context: Additional context (agent ID, task ID, etc.)

        Returns:
            Tool execution result
        """
        if not self._connected or not self.client:
            logger.warning("Not connected to MCP server - falling back to mock response")
            return {
                "status": "error",
                "error": "MCP client not connected",
                "tool": tool_name
            }

        try:
            # Add context to the request
            request_context = {
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                **(context or {})
            }

            logger.info(f"Calling MCP tool: {tool_name} with context: {request_context}")

            # Call the tool
            from app.mcp_servers import geospatial_server, research_server

            if self.server_name == "geospatial-tools":
                result_content = await geospatial_server.server._handlers["call_tool"](
                    tool_name, arguments
                )
            elif self.server_name == "research-tools":
                result_content = await research_server.server._handlers["call_tool"](
                    tool_name, arguments
                )
            else:
                return {
                    "status": "error",
                    "error": f"Unknown server: {self.server_name}"
                }

            # Parse the result (TextContent -> dict)
            if result_content and len(result_content) > 0:
                result_text = result_content[0].text
                result = json.loads(result_text)
                return result
            else:
                return {
                    "status": "error",
                    "error": "Empty response from MCP server"
                }

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "tool": tool_name
            }

    async def get_geospatial_context(
        self,
        location: str,
        bbox: Optional[List[float]] = None,
        data_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for getting geospatial context

        This is a high-level wrapper around the MCP geospatial server
        """
        if self.server_name != "geospatial-tools":
            logger.error("Wrong server - this method requires geospatial-tools server")
            return {"error": "Wrong MCP server"}

        arguments = {
            "location": location,
            "data_sources": data_sources or []
        }

        if bbox:
            arguments["bbox"] = bbox

        return await self.call_tool("get_geospatial_context", arguments)

    async def conduct_research(
        self,
        topic: str,
        depth: str = "standard",
        agent_type: str = "research"
    ) -> Dict[str, Any]:
        """
        Convenience method for conducting research

        This is a high-level wrapper around the MCP research server
        """
        if self.server_name != "research-tools":
            logger.error("Wrong server - this method requires research-tools server")
            return {"error": "Wrong MCP server"}

        arguments = {
            "topic": topic,
            "depth": depth,
            "agent_type": agent_type
        }

        return await self.call_tool("conduct_research", arguments)

    async def web_search(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Convenience method for web search"""
        if self.server_name != "research-tools":
            return {"error": "Wrong MCP server"}

        return await self.call_tool("web_search", {"query": query, "count": count})

    async def disconnect(self):
        """Disconnect from MCP server"""
        self._connected = False
        self.client = None
        logger.info(f"Disconnected from MCP server: {self.server_name}")

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return self.available_tools


# Factory functions for easy client creation

async def create_geospatial_client() -> MCPClient:
    """Create and connect a geospatial MCP client"""
    client = MCPClient("geospatial-tools")
    await client.connect()
    return client


async def create_research_client() -> MCPClient:
    """Create and connect a research MCP client"""
    client = MCPClient("research-tools")
    await client.connect()
    return client
