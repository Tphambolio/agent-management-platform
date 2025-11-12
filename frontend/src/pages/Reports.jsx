import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { reportsAPI } from '../api/client'
import { FileText, X } from 'lucide-react'

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState(null)

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.list().then(res => res.data),
  })

  const { data: reportDetail } = useQuery({
    queryKey: ['report', selectedReport],
    queryFn: () => reportsAPI.get(selectedReport).then(res => res.data),
    enabled: !!selectedReport,
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Reports</h2>
        <p className="text-gray-600 mt-2">View agent-generated reports</p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      ) : reports && reports.length === 0 ? (
        <div className="card text-center py-12">
          <FileText size={48} className="text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No reports generated yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports?.map((report) => (
            <div
              key={report.id}
              onClick={() => setSelectedReport(report.id)}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText size={24} className="text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2">{report.title}</h3>
                  <p className="text-sm text-gray-600 mt-1 truncate">
                    Agent: {report.agent_id}
                  </p>
                  <p className="text-sm text-gray-600">
                    Format: {report.format}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(report.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Report Detail Modal */}
      {selectedReport && reportDetail && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">{reportDetail.title}</h3>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Agent:</span>
                  <span className="ml-2 text-gray-900">{reportDetail.agent_id}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Task ID:</span>
                  <span className="ml-2 text-gray-900 font-mono text-sm">{reportDetail.task_id}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Created:</span>
                  <span className="ml-2 text-gray-900">
                    {new Date(reportDetail.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="border-t pt-4 mt-4">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Content</h4>
                  <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                      {JSON.stringify(reportDetail.content, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
