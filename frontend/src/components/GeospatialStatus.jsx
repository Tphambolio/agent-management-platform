import { useQuery } from '@tanstack/react-query'
import { geospatialAPI } from '../api/client'
import { Satellite, AlertCircle } from 'lucide-react'

export default function GeospatialStatus() {
  const { data: capabilities, isLoading, error } = useQuery({
    queryKey: ['geospatial-capabilities'],
    queryFn: () => geospatialAPI.capabilities().then(res => res.data),
    refetchInterval: 60000, // Check every minute
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <Satellite className="h-5 w-5 text-purple-600" />
            Geospatial Features
          </h3>
        </div>
        <p className="text-sm text-gray-500">Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <Satellite className="h-5 w-5 text-gray-400" />
            Geospatial Features
          </h3>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <AlertCircle className="h-4 w-4" />
          <span>Unable to load capabilities</span>
        </div>
      </div>
    )
  }

  const isFullyEnabled = capabilities?.rasterio_available && capabilities?.dask_available
  const hasPartialFeatures = capabilities?.rasterio_available || capabilities?.dask_available

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
          <Satellite className={`h-5 w-5 ${isFullyEnabled ? 'text-green-600' : hasPartialFeatures ? 'text-yellow-600' : 'text-gray-400'}`} />
          Geospatial Features
        </h3>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          isFullyEnabled ? 'bg-green-100 text-green-800' :
          hasPartialFeatures ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {isFullyEnabled ? 'Enabled' : hasPartialFeatures ? 'Partial' : 'Limited'}
        </span>
      </div>

      <div className="space-y-2">
        <FeatureItem
          label="NDVI Calculation"
          enabled={capabilities?.features?.ndvi_calculation}
        />
        <FeatureItem
          label="GeoTIFF I/O"
          enabled={capabilities?.features?.geotiff_io}
        />
        <FeatureItem
          label="Memory-Efficient Processing"
          enabled={capabilities?.features?.memory_efficient_processing}
        />
        <FeatureItem
          label="Chunked Operations"
          enabled={capabilities?.features?.chunked_operations}
        />
      </div>

      {capabilities?.missing_dependencies?.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-blue-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                Missing dependencies: <span className="font-medium">{capabilities.missing_dependencies.join(', ')}</span>
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Full geospatial features will be available after Docker GDAL setup.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function FeatureItem({ label, enabled }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-gray-700">{label}</span>
      <span className={`inline-flex items-center text-xs ${enabled ? 'text-green-600' : 'text-gray-400'}`}>
        {enabled ? '✓ Available' : '○ Unavailable'}
      </span>
    </div>
  )
}
