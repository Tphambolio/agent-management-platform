"""
Model Context Protocol (MCP) Server Implementation

Provides standardized, context-aware communication for AI agents
following the research recommendations in report 02d3e616.

This MCP server exposes geospatial processing tools using JSON-RPC 2.0,
enabling agents to discover and use capabilities without hard-coding.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server implementing JSON-RPC 2.0 for agent-tool communication

    Based on research findings: MCP standardizes context exchange and
    reduces custom integration code compared to REST APIs.
    """

    def __init__(self):
        """Initialize MCP server with tool registry"""
        self.tools_registry = {}
        self.resources_registry = {}
        self._register_default_tools()
        logger.info("🔧 MCP Server initialized with tool registry")

    def _register_default_tools(self):
        """Register built-in geospatial tools"""

        # Geospatial satellite download tool
        self.register_tool(
            tool_name="geospatial.download_satellite",
            description="Download real Sentinel-2 satellite imagery from Microsoft Planetary Computer",
            parameters={
                "location_name": {"type": "string", "description": "Human-readable location name"},
                "bbox": {"type": "array", "description": "Bounding box [min_lon, min_lat, max_lon, max_lat]"},
                "bands": {"type": "array", "description": "List of Sentinel-2 bands (e.g., B04, B08, B11)"},
                "days_back": {"type": "integer", "description": "Days to search back", "default": 30},
                "max_cloud_cover": {"type": "number", "description": "Max cloud cover %", "default": 20.0}
            },
            handler=self._handle_satellite_download
        )

        # NDVI calculation tool
        self.register_tool(
            tool_name="geospatial.calculate_ndvi",
            description="Calculate NDVI from red and NIR bands",
            parameters={
                "red_band_path": {"type": "string", "description": "Path to red band GeoTIFF"},
                "nir_band_path": {"type": "string", "description": "Path to NIR band GeoTIFF"},
                "output_path": {"type": "string", "description": "Output path for NDVI raster"}
            },
            handler=self._handle_ndvi_calculation
        )

        # Geospatial RAG enhancement tool
        self.register_tool(
            tool_name="rag.enhance_with_geospatial",
            description="Enhance RAG context with geospatial data analysis",
            parameters={
                "query": {"type": "string", "description": "User query"},
                "location_bbox": {"type": "array", "description": "Area of interest bbox"},
                "raster_path": {"type": "string", "description": "Path to geospatial data"}
            },
            handler=self._handle_rag_enhancement
        )

    def register_tool(self, tool_name: str, description: str,
                     parameters: Dict[str, Any], handler: callable):
        """
        Register a new tool in the MCP registry

        Args:
            tool_name: Dot-notation tool name (e.g., "geospatial.download")
            description: Human-readable tool description
            parameters: JSON schema for tool parameters
            handler: Callable that executes the tool
        """
        self.tools_registry[tool_name] = {
            "name": tool_name,
            "description": description,
            "parameters": parameters,
            "handler": handler
        }
        logger.info(f"   Registered tool: {tool_name}")

    def register_resource(self, resource_name: str, description: str,
                         getter: callable):
        """
        Register a data resource (application-controlled)

        Args:
            resource_name: Resource identifier
            description: Human-readable description
            getter: Callable that retrieves the resource
        """
        self.resources_registry[resource_name] = {
            "name": resource_name,
            "description": description,
            "getter": getter
        }
        logger.info(f"   Registered resource: {resource_name}")

    def handle_json_rpc(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming JSON-RPC 2.0 request

        Args:
            request: JSON-RPC request with method, params, id

        Returns:
            JSON-RPC response with result or error
        """
        request_id = request.get("id", 1)
        method = request.get("method", "")
        params = request.get("params", {})

        logger.info(f"📨 MCP Request: {method}")

        try:
            # Handle MCP meta-methods
            if method == "mcp.list_tools":
                return self._list_tools_response(request_id)

            elif method == "mcp.list_resources":
                return self._list_resources_response(request_id)

            elif method == "mcp.get_resource":
                resource_name = params.get("name")
                return self._get_resource_response(resource_name, request_id)

            # Handle tool invocations
            elif method in self.tools_registry:
                tool = self.tools_registry[method]
                args = params.get("args", {})
                context = params.get("context", {})

                # Execute tool handler
                result = tool["handler"](args, context)

                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }

        except Exception as e:
            logger.error(f"❌ MCP Error: {str(e)}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": f"Server error: {str(e)}"
                },
                "id": request_id
            }

    def _list_tools_response(self, request_id: int) -> Dict[str, Any]:
        """Return list of available tools"""
        tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools_registry.values()
        ]

        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": request_id
        }

    def _list_resources_response(self, request_id: int) -> Dict[str, Any]:
        """Return list of available resources"""
        resources = [
            {
                "name": res["name"],
                "description": res["description"]
            }
            for res in self.resources_registry.values()
        ]

        return {
            "jsonrpc": "2.0",
            "result": {"resources": resources},
            "id": request_id
        }

    def _get_resource_response(self, resource_name: str,
                              request_id: int) -> Dict[str, Any]:
        """Retrieve a specific resource"""
        if resource_name not in self.resources_registry:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {resource_name}"
                },
                "id": request_id
            }

        resource = self.resources_registry[resource_name]
        data = resource["getter"]()

        return {
            "jsonrpc": "2.0",
            "result": data,
            "id": request_id
        }

    # === Tool Handlers === #

    def _handle_satellite_download(self, args: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle satellite data download tool invocation

        Delegates to existing satellite_data module
        """
        from .satellite_data import get_satellite_downloader

        downloader = get_satellite_downloader()

        result = downloader.download_scene_for_location(
            location_name=args.get("location_name", "Unknown"),
            bbox=tuple(args.get("bbox", [])),
            bands=args.get("bands", ["B04", "B08"]),
            days_back=args.get("days_back", 30),
            max_cloud_cover=args.get("max_cloud_cover", 20.0)
        )

        return result

    def _handle_ndvi_calculation(self, args: Dict[str, Any],
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle NDVI calculation tool invocation

        Delegates to existing geospatial_pipeline module
        """
        from .geospatial_pipeline import get_geospatial_processor

        processor = get_geospatial_processor()

        result = processor.calculate_ndvi_from_files(
            red_band_path=args.get("red_band_path"),
            nir_band_path=args.get("nir_band_path"),
            output_path=args.get("output_path")
        )

        return result

    def _handle_rag_enhancement(self, args: Dict[str, Any],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle RAG enhancement with geospatial data

        Extracts geospatial insights and returns enriched context
        """
        import rasterio
        import numpy as np

        query = args.get("query", "")
        bbox = args.get("location_bbox", [])
        raster_path = args.get("raster_path", "")

        try:
            with rasterio.open(raster_path) as src:
                # Read data from bounding box window
                window = src.window(*bbox) if bbox else None
                data = src.read(1, window=window)

                # Filter no-data values
                if src.nodata is not None:
                    data = data[data != src.nodata]

                if data.size > 0:
                    geospatial_context = {
                        "average_value": float(np.mean(data)),
                        "min_value": float(np.min(data)),
                        "max_value": float(np.max(data)),
                        "std_dev": float(np.std(data)),
                        "area_analyzed": f"{bbox}" if bbox else "full raster"
                    }
                else:
                    geospatial_context = {"message": "No valid data in specified area"}

            # Return enriched context for RAG injection
            return {
                "status": "success",
                "query": query,
                "geospatial_insights": geospatial_context,
                "enriched_prompt": f"Geospatial analysis: {geospatial_context}\n\nQuery: {query}"
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
_mcp_server = None

def get_mcp_server() -> MCPServer:
    """Get or create singleton MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
