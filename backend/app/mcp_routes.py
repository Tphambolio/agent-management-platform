"""
MCP Routes - Model Context Protocol API Endpoints

Adds MCP JSON-RPC endpoint alongside existing REST APIs.
This is NON-BREAKING: all existing REST endpoints continue to work.

Research recommendation: "Begin by implementing an MCP server for existing
internal tools and refactor agents to use MCP client. This can run alongside
existing REST endpoints initially."
"""

import logging
from typing import Dict, Any
from fastapi import Request
from pydantic import BaseModel

from .mcp_server import get_mcp_server

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request model"""
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = {}
    id: int = 1


def register_mcp_routes(app):
    """
    Register MCP endpoint with FastAPI app

    NON-BREAKING: This adds a new endpoint at /api/mcp
    All existing /api/* REST endpoints remain unchanged
    """

    @app.post("/api/mcp")
    async def mcp_endpoint(request: MCPRequest):
        """
        Model Context Protocol (MCP) JSON-RPC 2.0 endpoint

        Provides standardized, context-aware tool access for AI agents.
        Coexists with existing REST API endpoints.

        Example request:
        ```json
        {
          "jsonrpc": "2.0",
          "method": "mcp.list_tools",
          "params": {},
          "id": 1
        }
        ```

        Example tool invocation:
        ```json
        {
          "jsonrpc": "2.0",
          "method": "geospatial.download_satellite",
          "params": {
            "args": {
              "location_name": "Calgary",
              "bbox": [-114.3, 50.8, -113.8, 51.2],
              "bands": ["B04", "B08"]
            }
          },
          "id": 1
        }
        ```
        """
        mcp_server = get_mcp_server()

        # Convert Pydantic model to dict for processing
        request_dict = {
            "jsonrpc": request.jsonrpc,
            "method": request.method,
            "params": request.params,
            "id": request.id
        }

        # Process JSON-RPC request
        response = mcp_server.handle_json_rpc(request_dict)

        return response

    logger.info("✅ MCP routes registered at /api/mcp (NON-BREAKING: coexists with REST API)")
