"""
Geospatial Data Processing Pipeline for Multi-Agent Platform

This module provides production-ready geospatial processing capabilities including:
- NDVI calculation from satellite imagery
- Memory-efficient raster processing with Dask
- GeoTIFF I/O with proper metadata preservation
- Coordinate transformations and projections

Based on research: "Production-Ready Geospatial Data Processing Pipeline for Multi-Agent Systems"
"""

import logging
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
import numpy as np

logger = logging.getLogger(__name__)

# Optional imports - these will be checked at runtime
try:
    import rasterio
    from rasterio.plot import show
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logger.warning("rasterio not available - geospatial features will be limited")

try:
    import rioxarray as rxr
    import dask.array as da
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    logger.warning("rioxarray/dask not available - memory-efficient processing disabled")


class GeospatialProcessor:
    """
    Handles geospatial raster operations for the agent platform.

    Features:
    - NDVI calculation from red and NIR bands
    - Memory-efficient processing of large rasters
    - GeoTIFF generation with metadata
    - Cloud-optimized workflows
    """

    def __init__(self):
        """Initialize the geospatial processor with dependency checks."""
        self.rasterio_available = RASTERIO_AVAILABLE
        self.dask_available = DASK_AVAILABLE

        if not self.rasterio_available:
            logger.error("rasterio is required for geospatial operations")

    def calculate_ndvi(
        self,
        red_band_data: np.ndarray,
        nir_band_data: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calculate NDVI from red and NIR bands.

        NDVI = (NIR - Red) / (NIR + Red)

        Args:
            red_band_data: Red band array
            nir_band_data: Near-infrared band array
            metadata: Optional metadata for output GeoTIFF

        Returns:
            Tuple of (ndvi_array, metadata_dict)
        """
        logger.info(f"Calculating NDVI for {red_band_data.shape} array")

        # Convert to float32 for calculations
        red = red_band_data.astype(np.float32)
        nir = nir_band_data.astype(np.float32)

        # Allow division by zero (results in NaN)
        np.seterr(divide='ignore', invalid='ignore')

        # Calculate NDVI with zero-division handling
        ndvi = np.where(
            (nir + red) == 0.,
            0.,  # Set to 0 where sum is zero
            (nir - red) / (nir + red)
        )

        # Build output metadata
        out_metadata = metadata.copy() if metadata else {}
        out_metadata.update({
            "dtype": "float32",
            "count": 1,
            "description": "NDVI calculated from red and NIR bands"
        })

        logger.info(f"✅ NDVI calculated: min={np.nanmin(ndvi):.3f}, max={np.nanmax(ndvi):.3f}")

        return ndvi, out_metadata

    def calculate_ndvi_from_files(
        self,
        red_band_path: str,
        nir_band_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """
        Calculate NDVI from GeoTIFF files and save result.

        Args:
            red_band_path: Path to red band GeoTIFF
            nir_band_path: Path to NIR band GeoTIFF
            output_path: Output path for NDVI GeoTIFF

        Returns:
            Dict with status and metadata
        """
        if not self.rasterio_available:
            return {
                "status": "error",
                "error": "rasterio not installed - install with: pip install rasterio"
            }

        try:
            # Open red and NIR bands
            with rasterio.open(red_band_path) as red_src, \
                 rasterio.open(nir_band_path) as nir_src:

                # Read bands as float32
                red = red_src.read(1).astype(np.float32)
                nir = nir_src.read(1).astype(np.float32)

                # Calculate NDVI
                ndvi, _ = self.calculate_ndvi(red, nir)

                # Update metadata for output
                out_meta = red_src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": ndvi.shape[0],
                    "width": ndvi.shape[1],
                    "count": 1,
                    "dtype": "float32",
                    "compress": "lzw"
                })

                # Write NDVI GeoTIFF
                with rasterio.open(output_path, "w", **out_meta) as dst:
                    dst.write(ndvi, 1)
                    dst.set_band_description(1, "NDVI")

            logger.info(f"✅ NDVI GeoTIFF saved to: {output_path}")

            return {
                "status": "success",
                "output_path": output_path,
                "ndvi_min": float(np.nanmin(ndvi)),
                "ndvi_max": float(np.nanmax(ndvi)),
                "ndvi_mean": float(np.nanmean(ndvi)),
                "shape": ndvi.shape
            }

        except Exception as e:
            logger.error(f"❌ NDVI calculation failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def process_large_raster_chunked(
        self,
        input_path: str,
        output_path: str,
        chunk_size: int = 256,
        operation: str = "identity"
    ) -> Dict[str, Any]:
        """
        Process large raster files with Dask for memory efficiency.

        Args:
            input_path: Input GeoTIFF path
            output_path: Output GeoTIFF path
            chunk_size: Size of chunks in pixels
            operation: Operation to perform ("identity", "scale", "threshold")

        Returns:
            Dict with status and metadata
        """
        if not self.dask_available:
            return {
                "status": "error",
                "error": "rioxarray/dask not installed - install with: pip install rioxarray dask"
            }

        try:
            logger.info(f"Opening {input_path} with Dask chunks={chunk_size}...")

            # Open raster with chunking
            src_data = rxr.open_rasterio(
                input_path,
                chunks={'x': chunk_size, 'y': chunk_size}
            )

            # Ensure Dask array
            if not isinstance(src_data.data, da.Array):
                src_data.data = da.from_array(
                    src_data.data,
                    chunks=(1, chunk_size, chunk_size)
                )

            logger.info(f"Data shape: {src_data.shape}, chunks: {src_data.chunks}")

            # Apply operation (lazy)
            if operation == "scale":
                processed_data = src_data * 0.5 + 100
            elif operation == "threshold":
                processed_data = src_data.where(src_data > 0, 0)
            else:  # identity
                processed_data = src_data

            # Ensure float32 dtype
            processed_data = processed_data.astype(np.float32)

            # Write output (this triggers computation)
            logger.info(f"Writing to {output_path} (computing chunks)...")
            processed_data.rio.to_raster(output_path, compress="lzw")

            logger.info(f"✅ Processed raster saved to: {output_path}")

            return {
                "status": "success",
                "output_path": output_path,
                "shape": tuple(src_data.shape),
                "chunks": str(src_data.chunks),
                "operation": operation
            }

        except Exception as e:
            logger.error(f"❌ Raster processing failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return current geospatial capabilities based on installed dependencies.

        Returns:
            Dict describing available features
        """
        return {
            "rasterio_available": self.rasterio_available,
            "dask_available": self.dask_available,
            "features": {
                "ndvi_calculation": self.rasterio_available,
                "geotiff_io": self.rasterio_available,
                "memory_efficient_processing": self.dask_available,
                "chunked_operations": self.dask_available
            },
            "missing_dependencies": self._get_missing_dependencies()
        }

    def _get_missing_dependencies(self) -> list:
        """Get list of missing dependencies."""
        missing = []
        if not self.rasterio_available:
            missing.append("rasterio")
        if not self.dask_available:
            missing.extend(["rioxarray", "dask"])
        return missing


# Global singleton instance
_geospatial_processor: Optional[GeospatialProcessor] = None


def get_geospatial_processor() -> GeospatialProcessor:
    """
    Get or create the global geospatial processor instance.

    Returns:
        GeospatialProcessor singleton instance
    """
    global _geospatial_processor

    if _geospatial_processor is None:
        _geospatial_processor = GeospatialProcessor()

    return _geospatial_processor
