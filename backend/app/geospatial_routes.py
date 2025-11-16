"""
Geospatial API Routes for Multi-Agent Platform

Provides REST endpoints for:
- NDVI calculation from uploaded raster data
- Geospatial processing capabilities check
- Raster file processing and transformations

Frontend Integration:
- Upload red/NIR bands via multipart/form-data
- Receive GeoTIFF outputs or base64-encoded results
- Check available geospatial features
"""

import logging
import os
import tempfile
from typing import Optional
from fastapi import UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .geospatial_pipeline import get_geospatial_processor

logger = logging.getLogger(__name__)


# === Pydantic Models === #

class GeospatialCapabilitiesResponse(BaseModel):
    """Response for geospatial capabilities check"""
    rasterio_available: bool
    dask_available: bool
    features: dict
    missing_dependencies: list
    status: str


class NDVICalculationResponse(BaseModel):
    """Response from NDVI calculation"""
    status: str
    output_path: Optional[str] = None
    ndvi_min: Optional[float] = None
    ndvi_max: Optional[float] = None
    ndvi_mean: Optional[float] = None
    shape: Optional[tuple] = None
    error: Optional[str] = None
    download_url: Optional[str] = None


class RasterProcessingRequest(BaseModel):
    """Request for raster processing operations"""
    operation: str = Field(default="identity", description="Operation: identity, scale, threshold")
    chunk_size: int = Field(default=256, description="Chunk size for Dask processing")


class RasterProcessingResponse(BaseModel):
    """Response from raster processing"""
    status: str
    output_path: Optional[str] = None
    shape: Optional[tuple] = None
    chunks: Optional[str] = None
    operation: Optional[str] = None
    error: Optional[str] = None
    download_url: Optional[str] = None


# === Route Registration === #

def register_geospatial_routes(app):
    """Register geospatial routes with the FastAPI app"""

    @app.get("/api/geospatial/capabilities", response_model=GeospatialCapabilitiesResponse)
    async def get_geospatial_capabilities():
        """
        Check available geospatial processing capabilities.

        Returns information about installed dependencies and available features.

        **Use Case:** Frontend can query this endpoint to show/hide geospatial features
        based on what's actually available on the backend.
        """
        logger.info("📊 Checking geospatial capabilities")

        processor = get_geospatial_processor()
        caps = processor.get_capabilities()

        return GeospatialCapabilitiesResponse(
            status="success",
            **caps
        )

    @app.post("/api/geospatial/calculate-ndvi", response_model=NDVICalculationResponse)
    async def calculate_ndvi(
        red_band: UploadFile = File(..., description="Red band GeoTIFF file"),
        nir_band: UploadFile = File(..., description="NIR band GeoTIFF file"),
        output_filename: Optional[str] = Form(default="ndvi_output.tif")
    ):
        """
        Calculate NDVI from uploaded red and NIR band GeoTIFF files.

        **Frontend Integration:**
        ```javascript
        const formData = new FormData();
        formData.append('red_band', redBandFile);
        formData.append('nir_band', nirBandFile);
        formData.append('output_filename', 'my_ndvi.tif');

        const response = await fetch('/api/geospatial/calculate-ndvi', {
          method: 'POST',
          body: formData
        });
        const result = await response.json();

        // Download result GeoTIFF
        window.location.href = result.download_url;
        ```

        **Use Case:** User uploads satellite imagery from their local machine,
        backend calculates NDVI, and returns downloadable GeoTIFF.
        """
        logger.info(f"🌱 NDVI calculation requested")
        logger.info(f"   Red band: {red_band.filename} ({red_band.content_type})")
        logger.info(f"   NIR band: {nir_band.filename} ({nir_band.content_type})")

        processor = get_geospatial_processor()

        if not processor.rasterio_available:
            raise HTTPException(
                status_code=503,
                detail="Geospatial processing unavailable - rasterio not installed"
            )

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save uploaded files
                red_path = os.path.join(temp_dir, "red_band.tif")
                nir_path = os.path.join(temp_dir, "nir_band.tif")
                output_path = os.path.join(temp_dir, output_filename)

                # Write uploaded data to temp files
                with open(red_path, "wb") as f:
                    f.write(await red_band.read())

                with open(nir_path, "wb") as f:
                    f.write(await nir_band.read())

                logger.info(f"   Saved to temp dir: {temp_dir}")

                # Calculate NDVI
                result = processor.calculate_ndvi_from_files(
                    red_band_path=red_path,
                    nir_band_path=nir_path,
                    output_path=output_path
                )

                if result["status"] == "error":
                    raise HTTPException(status_code=500, detail=result["error"])

                # Move output to persistent location for download
                output_dir = os.path.join("/tmp", "geospatial_outputs")
                os.makedirs(output_dir, exist_ok=True)

                final_output = os.path.join(output_dir, output_filename)

                # Copy file to persistent location
                import shutil
                shutil.copy(output_path, final_output)

                logger.info(f"✅ NDVI calculation complete: {final_output}")

                # Generate download URL
                download_url = f"/api/geospatial/download/{output_filename}"

                return NDVICalculationResponse(
                    **result,
                    download_url=download_url
                )

            except Exception as e:
                logger.error(f"❌ NDVI calculation failed: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/geospatial/process-raster", response_model=RasterProcessingResponse)
    async def process_raster(
        input_file: UploadFile = File(..., description="Input GeoTIFF file"),
        operation: str = Form(default="identity", description="Operation to perform"),
        chunk_size: int = Form(default=256, description="Chunk size for processing"),
        output_filename: Optional[str] = Form(default="processed_output.tif")
    ):
        """
        Process large raster files with memory-efficient chunking.

        **Operations:**
        - `identity`: Pass-through (useful for format conversion)
        - `scale`: Scale values by 0.5 and add 100
        - `threshold`: Set negative values to zero

        **Frontend Integration:**
        ```javascript
        const formData = new FormData();
        formData.append('input_file', geotiffFile);
        formData.append('operation', 'threshold');
        formData.append('chunk_size', '512');

        const response = await fetch('/api/geospatial/process-raster', {
          method: 'POST',
          body: formData
        });
        ```

        **Use Case:** Process large satellite imagery that doesn't fit in memory,
        using chunked processing for cloud deployment.
        """
        logger.info(f"🗺️  Raster processing requested: {operation}")
        logger.info(f"   Input: {input_file.filename}")
        logger.info(f"   Chunk size: {chunk_size}px")

        processor = get_geospatial_processor()

        if not processor.dask_available:
            raise HTTPException(
                status_code=503,
                detail="Memory-efficient processing unavailable - rioxarray/dask not installed"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save uploaded file
                input_path = os.path.join(temp_dir, "input.tif")
                output_path = os.path.join(temp_dir, output_filename)

                with open(input_path, "wb") as f:
                    f.write(await input_file.read())

                # Process raster
                result = processor.process_large_raster_chunked(
                    input_path=input_path,
                    output_path=output_path,
                    chunk_size=chunk_size,
                    operation=operation
                )

                if result["status"] == "error":
                    raise HTTPException(status_code=500, detail=result["error"])

                # Move to persistent location
                output_dir = os.path.join("/tmp", "geospatial_outputs")
                os.makedirs(output_dir, exist_ok=True)

                final_output = os.path.join(output_dir, output_filename)

                import shutil
                shutil.copy(output_path, final_output)

                logger.info(f"✅ Raster processing complete: {final_output}")

                download_url = f"/api/geospatial/download/{output_filename}"

                return RasterProcessingResponse(
                    **result,
                    download_url=download_url
                )

            except Exception as e:
                logger.error(f"❌ Raster processing failed: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/geospatial/download/{filename}")
    async def download_geospatial_output(filename: str):
        """
        Download processed geospatial output files.

        **Frontend Integration:**
        ```javascript
        // After getting download_url from NDVI calculation
        const link = document.createElement('a');
        link.href = result.download_url;
        link.download = 'ndvi_result.tif';
        link.click();
        ```

        **Use Case:** Allow users to download their processed GeoTIFF files.
        """
        output_dir = os.path.join("/tmp", "geospatial_outputs")
        file_path = os.path.join(output_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        logger.info(f"📥 Downloading geospatial output: {filename}")

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=filename
        )

    logger.info("✅ Geospatial routes registered successfully")
