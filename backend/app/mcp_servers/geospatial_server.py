"""
Geospatial Tools MCP Server

This MCP server exposes geospatial analysis tools to AI agents using the Model Context Protocol.
It provides standardized access to GDAL, rasterio, and Sentinel-2 STAC capabilities.

Following the research recommendations from "Multi-Agent System Architecture: Best Practices"
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import rasterio
    from rasterio.windows import Window
    import numpy as np
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("⚠️  Geospatial dependencies (rasterio, numpy) not available")

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field


class GeospatialServer:
    """
    MCP Server for geospatial analysis tools

    Exposes Tools for:
    - Raster data extraction (Sentinel-2, STAC)
    - Bounding box analysis
    - NDVI calculation
    - Geospatial context for RAG
    """

    def __init__(self):
        self.server = Server("geospatial-tools")
        self._register_tools()

    def _register_tools(self):
        """Register all geospatial tools with the MCP server"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available geospatial tools"""
            return [
                Tool(
                    name="extract_raster_bbox",
                    description="Extract raster data statistics for a bounding box from a geospatial file (e.g., Sentinel-2 imagery)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "raster_path": {
                                "type": "string",
                                "description": "Path to the raster file (GeoTIFF, etc.)"
                            },
                            "bbox": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 4,
                                "maxItems": 4,
                                "description": "Bounding box [min_x, min_y, max_x, max_y] in raster CRS"
                            },
                            "band": {
                                "type": "integer",
                                "description": "Band number to extract (default: 1)",
                                "default": 1
                            }
                        },
                        "required": ["raster_path", "bbox"]
                    }
                ),
                Tool(
                    name="calculate_ndvi",
                    description="Calculate NDVI (Normalized Difference Vegetation Index) for a bounding box using NIR and Red bands",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "nir_path": {
                                "type": "string",
                                "description": "Path to Near-Infrared band raster"
                            },
                            "red_path": {
                                "type": "string",
                                "description": "Path to Red band raster"
                            },
                            "bbox": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 4,
                                "maxItems": 4,
                                "description": "Bounding box [min_x, min_y, max_x, max_y]"
                            }
                        },
                        "required": ["nir_path", "red_path", "bbox"]
                    }
                ),
                Tool(
                    name="get_geospatial_context",
                    description="Get comprehensive geospatial context for RAG (Retrieval-Augmented Generation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Location description or coordinates"
                            },
                            "data_sources": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of data source paths to analyze"
                            },
                            "bbox": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Optional bounding box"
                            }
                        },
                        "required": ["location", "data_sources"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a geospatial tool"""

            if not GEOSPATIAL_AVAILABLE:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Geospatial dependencies not available",
                        "message": "Install rasterio and numpy to use geospatial tools"
                    })
                )]

            try:
                if name == "extract_raster_bbox":
                    result = await self._extract_raster_bbox(
                        arguments["raster_path"],
                        arguments["bbox"],
                        arguments.get("band", 1)
                    )
                elif name == "calculate_ndvi":
                    result = await self._calculate_ndvi(
                        arguments["nir_path"],
                        arguments["red_path"],
                        arguments["bbox"]
                    )
                elif name == "get_geospatial_context":
                    result = await self._get_geospatial_context(
                        arguments["location"],
                        arguments["data_sources"],
                        arguments.get("bbox")
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

    async def _extract_raster_bbox(
        self,
        raster_path: str,
        bbox: List[float],
        band: int = 1
    ) -> Dict[str, Any]:
        """Extract raster data statistics for a bounding box"""

        if not os.path.exists(raster_path):
            return {
                "error": "Raster file not found",
                "path": raster_path
            }

        try:
            with rasterio.open(raster_path) as src:
                # Get window from bounding box
                window = src.window(*bbox)

                # Read data from the window
                data = src.read(band, window=window)

                # Filter out no-data values
                no_data_val = src.nodata
                if no_data_val is not None:
                    data = data[data != no_data_val]

                if data.size > 0:
                    return {
                        "status": "success",
                        "raster_path": raster_path,
                        "bbox": bbox,
                        "band": band,
                        "statistics": {
                            "mean": float(np.mean(data)),
                            "median": float(np.median(data)),
                            "std": float(np.std(data)),
                            "min": float(np.min(data)),
                            "max": float(np.max(data)),
                            "count": int(data.size)
                        },
                        "crs": str(src.crs),
                        "units": "reflectance" if "Sentinel" in raster_path else "DN",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "error": "No valid data in bounding box",
                        "bbox": bbox
                    }

        except Exception as e:
            return {
                "error": f"Raster extraction failed: {str(e)}",
                "raster_path": raster_path
            }

    async def _calculate_ndvi(
        self,
        nir_path: str,
        red_path: str,
        bbox: List[float]
    ) -> Dict[str, Any]:
        """Calculate NDVI from NIR and Red bands"""

        try:
            # Extract NIR data
            with rasterio.open(nir_path) as nir_src:
                window = nir_src.window(*bbox)
                nir_data = nir_src.read(1, window=window).astype(float)

            # Extract Red data
            with rasterio.open(red_path) as red_src:
                window = red_src.window(*bbox)
                red_data = red_src.read(1, window=window).astype(float)

            # Calculate NDVI: (NIR - Red) / (NIR + Red)
            # Avoid division by zero
            denominator = nir_data + red_data
            ndvi = np.where(
                denominator != 0,
                (nir_data - red_data) / denominator,
                0
            )

            # Filter valid NDVI values (-1 to 1)
            valid_ndvi = ndvi[(ndvi >= -1) & (ndvi <= 1)]

            if valid_ndvi.size > 0:
                return {
                    "status": "success",
                    "metric": "NDVI",
                    "bbox": bbox,
                    "statistics": {
                        "mean": float(np.mean(valid_ndvi)),
                        "median": float(np.median(valid_ndvi)),
                        "std": float(np.std(valid_ndvi)),
                        "min": float(np.min(valid_ndvi)),
                        "max": float(np.max(valid_ndvi))
                    },
                    "interpretation": self._interpret_ndvi(float(np.mean(valid_ndvi))),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"error": "No valid NDVI values calculated"}

        except Exception as e:
            return {"error": f"NDVI calculation failed: {str(e)}"}

    def _interpret_ndvi(self, ndvi_value: float) -> str:
        """Interpret NDVI value"""
        if ndvi_value < 0:
            return "Water or bare soil"
        elif ndvi_value < 0.2:
            return "Sparse vegetation or urban area"
        elif ndvi_value < 0.4:
            return "Moderate vegetation"
        elif ndvi_value < 0.6:
            return "Healthy vegetation"
        else:
            return "Dense, very healthy vegetation"

    async def _get_geospatial_context(
        self,
        location: str,
        data_sources: List[str],
        bbox: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive geospatial context for RAG

        This aggregates data from multiple sources and formats it
        for optimal LLM consumption
        """

        context = {
            "location": location,
            "analysis_time": datetime.utcnow().isoformat(),
            "data_layers": []
        }

        for source_path in data_sources:
            if not os.path.exists(source_path):
                context["data_layers"].append({
                    "source": source_path,
                    "status": "not_found"
                })
                continue

            try:
                if bbox:
                    layer_data = await self._extract_raster_bbox(source_path, bbox)
                else:
                    # Extract global statistics
                    with rasterio.open(source_path) as src:
                        data = src.read(1)
                        no_data = src.nodata
                        if no_data is not None:
                            data = data[data != no_data]

                        layer_data = {
                            "status": "success",
                            "statistics": {
                                "mean": float(np.mean(data)),
                                "std": float(np.std(data))
                            },
                            "crs": str(src.crs)
                        }

                context["data_layers"].append({
                    "source": os.path.basename(source_path),
                    "full_path": source_path,
                    "data": layer_data
                })

            except Exception as e:
                context["data_layers"].append({
                    "source": source_path,
                    "status": "error",
                    "error": str(e)
                })

        # Format for RAG
        context["rag_summary"] = self._format_for_rag(context)

        return context

    def _format_for_rag(self, context: Dict[str, Any]) -> str:
        """Format geospatial context for RAG injection"""

        lines = [
            f"**Geospatial Analysis for {context['location']}**",
            f"Analysis Time: {context['analysis_time']}",
            "",
            "**Data Layers:**"
        ]

        for layer in context["data_layers"]:
            if layer.get("status") == "success":
                stats = layer["data"].get("statistics", {})
                lines.append(f"- {layer['source']}: mean={stats.get('mean', 'N/A'):.2f}, std={stats.get('std', 'N/A'):.2f}")
            else:
                lines.append(f"- {layer['source']}: {layer.get('status', 'unknown')}")

        return "\n".join(lines)


# Singleton instance
geospatial_server = GeospatialServer()
