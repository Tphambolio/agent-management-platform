"""
Satellite Data Acquisition Module

Downloads real satellite imagery from public STAC catalogs:
- Microsoft Planetary Computer (Sentinel-2, Landsat-8)
- AWS Element84 Earth Search (Sentinel-2)
- No authentication required for public data

Provides functions to:
1. Search for satellite scenes by location and date
2. Download specific spectral bands (Red, NIR, SWIR, etc.)
3. Save as GeoTIFF files ready for processing
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import tempfile

logger = logging.getLogger(__name__)

# Check if STAC libraries are available
try:
    from pystac_client import Client
    import planetary_computer
    import stackstac
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import numpy as np
    STAC_AVAILABLE = True
    logger.info("✅ STAC libraries loaded successfully")
except ImportError as e:
    STAC_AVAILABLE = False
    logger.warning(f"⚠️  STAC libraries not available: {e}")
    logger.warning("   Install with: pip install pystac-client planetary-computer stackstac")


class SatelliteDataDownloader:
    """
    Download satellite imagery from public STAC catalogs
    """

    def __init__(self):
        """Initialize the downloader with Microsoft Planetary Computer catalog"""
        if not STAC_AVAILABLE:
            logger.error("❌ STAC libraries not available - cannot initialize downloader")
            self.available = False
            return

        self.available = True

        # Microsoft Planetary Computer STAC API (free, no auth required for search)
        self.catalog_url = "https://planetarycomputer.microsoft.com/api/stac/v1"

        logger.info(f"🛰️  Satellite data downloader initialized")
        logger.info(f"   Catalog: Microsoft Planetary Computer")
        logger.info(f"   Collections: Sentinel-2 L2A, Landsat-8/9")

    def search_sentinel2_scenes(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        max_cloud_cover: float = 20.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for Sentinel-2 scenes covering an area of interest.

        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            max_cloud_cover: Maximum cloud cover percentage (0-100)
            limit: Maximum number of scenes to return

        Returns:
            List of scene metadata dictionaries

        Example:
            # Calgary, Alberta bounding box
            bbox = (-114.3, 50.8, -113.8, 51.2)
            scenes = downloader.search_sentinel2_scenes(
                bbox=bbox,
                start_date="2024-06-01",
                end_date="2024-09-01",
                max_cloud_cover=10
            )
        """
        if not self.available:
            logger.error("❌ Satellite data downloader not available")
            return []

        try:
            logger.info(f"🔍 Searching Sentinel-2 scenes...")
            logger.info(f"   Area: {bbox}")
            logger.info(f"   Dates: {start_date} to {end_date}")
            logger.info(f"   Max cloud cover: {max_cloud_cover}%")

            # Connect to catalog
            catalog = Client.open(
                self.catalog_url,
                modifier=planetary_computer.sign_inplace,
            )

            # Search for Sentinel-2 Level-2A (surface reflectance) scenes
            search = catalog.search(
                collections=["sentinel-2-l2a"],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                query={
                    "eo:cloud_cover": {"lt": max_cloud_cover}
                },
                limit=limit
            )

            items = list(search.items())

            logger.info(f"✅ Found {len(items)} scenes")

            # Extract useful metadata
            scenes = []
            for item in items:
                scene = {
                    "id": item.id,
                    "datetime": item.datetime.isoformat(),
                    "cloud_cover": item.properties.get("eo:cloud_cover", 0),
                    "bbox": item.bbox,
                    "assets": list(item.assets.keys()),
                    "item": item  # Keep full item for downloading
                }
                scenes.append(scene)
                logger.info(f"   - {scene['id']}: {scene['cloud_cover']:.1f}% clouds")

            return scenes

        except Exception as e:
            logger.error(f"❌ Error searching scenes: {str(e)}", exc_info=True)
            return []

    def download_bands(
        self,
        scene: Dict,
        bands: List[str],
        output_dir: str,
        bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> Dict[str, str]:
        """
        Download specific spectral bands from a scene.

        Args:
            scene: Scene metadata from search_sentinel2_scenes()
            bands: List of band names to download (e.g., ["B04", "B08", "B11"])
                   Common Sentinel-2 bands:
                   - B02: Blue (490nm)
                   - B03: Green (560nm)
                   - B04: Red (665nm)
                   - B08: NIR (842nm)
                   - B11: SWIR1 (1610nm)
                   - B12: SWIR2 (2190nm)
            output_dir: Directory to save downloaded GeoTIFF files
            bbox: Optional bounding box to clip data (min_lon, min_lat, max_lon, max_lat)

        Returns:
            Dictionary mapping band names to file paths

        Example:
            # Download Red and NIR bands for NDVI calculation
            file_paths = downloader.download_bands(
                scene=scenes[0],
                bands=["B04", "B08"],
                output_dir="/tmp/satellite_data"
            )
            # Result: {"B04": "/tmp/satellite_data/B04.tif", "B08": "/tmp/satellite_data/B08.tif"}
        """
        if not self.available:
            logger.error("❌ Satellite data downloader not available")
            return {}

        try:
            item = scene["item"]
            os.makedirs(output_dir, exist_ok=True)

            logger.info(f"📥 Downloading bands from {scene['id']}")
            logger.info(f"   Bands: {bands}")
            logger.info(f"   Output: {output_dir}")

            downloaded_files = {}

            for band in bands:
                try:
                    # Check if band exists in assets
                    if band not in item.assets:
                        logger.warning(f"⚠️  Band {band} not found in scene assets")
                        continue

                    # Get signed URL from Planetary Computer
                    asset = item.assets[band]
                    signed_href = planetary_computer.sign(asset.href)

                    # Download and save as GeoTIFF
                    output_file = os.path.join(output_dir, f"{band}.tif")

                    logger.info(f"   Downloading {band}...")

                    # Use rasterio to read and save the band
                    with rasterio.open(signed_href) as src:
                        # Read the data
                        data = src.read(1)

                        # If bbox is provided, clip the data
                        if bbox:
                            # Calculate window from bbox
                            window = rasterio.windows.from_bounds(
                                *bbox,
                                transform=src.transform
                            )
                            data = src.read(1, window=window)
                            transform = src.window_transform(window)
                        else:
                            transform = src.transform

                        # Write to output file
                        profile = src.profile.copy()
                        profile.update({
                            'height': data.shape[0],
                            'width': data.shape[1],
                            'transform': transform,
                            'compress': 'lzw'
                        })

                        with rasterio.open(output_file, 'w', **profile) as dst:
                            dst.write(data, 1)

                    downloaded_files[band] = output_file
                    logger.info(f"   ✅ {band} saved to {output_file}")

                except Exception as e:
                    logger.error(f"   ❌ Error downloading {band}: {str(e)}")
                    continue

            logger.info(f"✅ Downloaded {len(downloaded_files)} bands successfully")
            return downloaded_files

        except Exception as e:
            logger.error(f"❌ Error downloading bands: {str(e)}", exc_info=True)
            return {}

    def download_scene_for_location(
        self,
        location_name: str,
        bbox: Tuple[float, float, float, float],
        bands: List[str] = ["B04", "B08"],
        days_back: int = 30,
        max_cloud_cover: float = 20.0
    ) -> Dict:
        """
        High-level function to search and download the best recent scene for a location.

        Args:
            location_name: Human-readable location name (for logging and file naming)
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            bands: List of bands to download
            days_back: How many days back to search
            max_cloud_cover: Maximum acceptable cloud cover

        Returns:
            Dictionary with:
                - status: "success" or "error"
                - scene_id: ID of downloaded scene
                - bands: Dictionary of band name -> file path
                - cloud_cover: Cloud cover percentage
                - datetime: Scene acquisition datetime
                - error: Error message if failed

        Example:
            # Download latest low-cloud Sentinel-2 scene for Calgary
            result = downloader.download_scene_for_location(
                location_name="Calgary",
                bbox=(-114.3, 50.8, -113.8, 51.2),
                bands=["B04", "B08", "B11"],  # Red, NIR, SWIR
                days_back=60,
                max_cloud_cover=15
            )

            if result["status"] == "success":
                red_band_file = result["bands"]["B04"]
                nir_band_file = result["bands"]["B08"]
        """
        if not self.available:
            return {
                "status": "error",
                "error": "STAC libraries not installed - cannot download satellite data"
            }

        try:
            logger.info(f"🌍 Downloading satellite data for {location_name}")

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Search for scenes
            scenes = self.search_sentinel2_scenes(
                bbox=bbox,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                max_cloud_cover=max_cloud_cover,
                limit=5  # Get top 5 scenes
            )

            if not scenes:
                return {
                    "status": "error",
                    "error": f"No scenes found for {location_name} in last {days_back} days with <{max_cloud_cover}% clouds"
                }

            # Use the scene with lowest cloud cover
            best_scene = min(scenes, key=lambda s: s["cloud_cover"])

            logger.info(f"📸 Selected scene: {best_scene['id']}")
            logger.info(f"   Cloud cover: {best_scene['cloud_cover']:.1f}%")
            logger.info(f"   Date: {best_scene['datetime']}")

            # Create output directory
            output_dir = os.path.join("/tmp", "satellite_downloads", location_name, best_scene["id"])

            # Download bands
            band_files = self.download_bands(
                scene=best_scene,
                bands=bands,
                output_dir=output_dir,
                bbox=bbox
            )

            if not band_files:
                return {
                    "status": "error",
                    "error": "Failed to download any bands"
                }

            return {
                "status": "success",
                "scene_id": best_scene["id"],
                "cloud_cover": best_scene["cloud_cover"],
                "datetime": best_scene["datetime"],
                "bands": band_files,
                "output_dir": output_dir
            }

        except Exception as e:
            logger.error(f"❌ Error in download_scene_for_location: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
_downloader = None

def get_satellite_downloader() -> SatelliteDataDownloader:
    """Get or create singleton satellite downloader instance"""
    global _downloader
    if _downloader is None:
        _downloader = SatelliteDataDownloader()
    return _downloader


# Convenience function for quick downloads
def download_sentinel2_for_calgary(bands: List[str] = ["B04", "B08"]) -> Dict:
    """
    Quick helper to download Sentinel-2 data for Calgary.

    Args:
        bands: List of band names (default: Red and NIR for NDVI)

    Returns:
        Result dictionary with downloaded file paths

    Example:
        result = download_sentinel2_for_calgary(bands=["B04", "B08", "B11"])
        if result["status"] == "success":
            print(f"Downloaded {len(result['bands'])} bands to {result['output_dir']}")
    """
    # Calgary, Alberta bounding box
    calgary_bbox = (-114.3, 50.8, -113.8, 51.2)

    downloader = get_satellite_downloader()
    return downloader.download_scene_for_location(
        location_name="Calgary",
        bbox=calgary_bbox,
        bands=bands,
        days_back=60,
        max_cloud_cover=20
    )
