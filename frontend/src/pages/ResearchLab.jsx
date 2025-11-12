import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { knowledgeAPI } from '../api/client'
import { FileText, Search, X, Download, BookOpen, TrendingUp } from 'lucide-react'

export default function ResearchLab() {
  const [selectedReport, setSelectedReport] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState('list') // 'list' or 'pdf'

  // Fetch knowledge base reports
  const { data: knowledgeData, isLoading } = useQuery({
    queryKey: ['knowledge'],
    queryFn: () => knowledgeAPI.list({ limit: 50 }).then(res => res.data),
  })

  // Fetch knowledge base stats
  const { data: stats } = useQuery({
    queryKey: ['knowledge-stats'],
    queryFn: () => knowledgeAPI.stats().then(res => res.data),
  })

  // Search knowledge base
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ['knowledge-search', searchQuery],
    queryFn: () => knowledgeAPI.search(searchQuery).then(res => res.data),
    enabled: searchQuery.length > 2,
  })

  // Get full report details
  const { data: reportDetail } = useQuery({
    queryKey: ['knowledge-report', selectedReport],
    queryFn: () => knowledgeAPI.get(selectedReport).then(res => res.data),
    enabled: !!selectedReport,
  })

  const reports = searchQuery.length > 2 ? searchResults?.results : knowledgeData?.reports

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Research Lab</h2>
          <p className="text-gray-600 mt-2">AI-generated research reports and knowledge base</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="flex gap-4">
            <div className="bg-blue-50 px-4 py-2 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_reports || 0}</div>
              <div className="text-xs text-blue-800">Reports</div>
            </div>
            <div className="bg-green-50 px-4 py-2 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.agent_types || 0}</div>
              <div className="text-xs text-green-800">Agents</div>
            </div>
            <div className="bg-purple-50 px-4 py-2 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {stats.total_words ? (stats.total_words / 1000).toFixed(0) + 'k' : '0'}
              </div>
              <div className="text-xs text-purple-800">Words</div>
            </div>
          </div>
        )}
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
          )}
        </div>
        {searchQuery.length > 0 && searchQuery.length <= 2 && (
          <p className="text-sm text-gray-500 mt-2">Type at least 3 characters to search</p>
        )}
        {isSearching && (
          <p className="text-sm text-gray-500 mt-2">Searching...</p>
        )}
      </div>

      {/* Reports Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      ) : !reports || reports.length === 0 ? (
        <div className="card text-center py-12">
          <BookOpen size={48} className="text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchQuery ? 'No reports found matching your search' : 'No research reports yet'}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Run <code className="bg-gray-100 px-2 py-1 rounded">./research.py "topic"</code> to generate reports
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports?.map((report) => (
            <div
              key={report.id}
              onClick={() => setSelectedReport(report.id)}
              className="card hover:shadow-lg transition-shadow cursor-pointer group"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                  <FileText size={24} className="text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600">
                    {report.topic}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {report.agent_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {report.word_count?.toLocaleString()} words
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(report.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </p>
                  {report.pdf_path && (
                    <div className="mt-2 text-xs text-green-600 flex items-center gap-1">
                      <Download size={12} />
                      PDF Available
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Report Detail Modal with PDF Viewer */}
      {selectedReport && reportDetail && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex-1 min-w-0 mr-4">
                <h3 className="text-2xl font-bold text-gray-900 truncate">{reportDetail.topic}</h3>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                    {reportDetail.agent_type}
                  </span>
                  <span className="text-sm text-gray-600">
                    {reportDetail.word_count?.toLocaleString()} words
                  </span>
                  <span className="text-sm text-gray-600">
                    {new Date(reportDetail.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* View Mode Toggle & Actions */}
              <div className="flex items-center gap-3">
                {reportDetail.pdf_path && (
                  <>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`px-3 py-1 rounded ${
                        viewMode === 'list'
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      Markdown
                    </button>
                    <button
                      onClick={() => setViewMode('pdf')}
                      className={`px-3 py-1 rounded ${
                        viewMode === 'pdf'
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      PDF
                    </button>
                    <a
                      href={knowledgeAPI.getPDF(reportDetail.id)}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary flex items-center gap-2"
                    >
                      <Download size={16} />
                      Download PDF
                    </a>
                  </>
                )}
                <button
                  onClick={() => {
                    setSelectedReport(null)
                    setViewMode('list')
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {viewMode === 'pdf' && reportDetail.pdf_path ? (
                /* PDF Viewer */
                <iframe
                  src={knowledgeAPI.getPDF(reportDetail.id)}
                  className="w-full h-full min-h-[600px] border rounded-lg"
                  title="PDF Viewer"
                />
              ) : (
                /* Markdown Content */
                <div className="prose prose-blue max-w-none">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans leading-relaxed">
                      {reportDetail.content}
                    </pre>
                  </div>

                  {/* Metadata Section */}
                  <div className="mt-6 pt-6 border-t grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Report ID:</span>
                      <p className="font-mono text-xs text-gray-700 mt-1">{reportDetail.id}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Model:</span>
                      <p className="text-sm text-gray-700 mt-1">{reportDetail.model || 'Claude Sonnet 4'}</p>
                    </div>
                    {reportDetail.tags && reportDetail.tags.length > 0 && (
                      <div className="col-span-2">
                        <span className="text-sm font-medium text-gray-500">Tags:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {reportDetail.tags.map((tag, i) => (
                            <span key={i} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
