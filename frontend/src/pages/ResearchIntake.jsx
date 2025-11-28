import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAgentStreaming } from '../hooks/useAgentStreaming'
import { Send, Loader2, RotateCcw, FileText, Archive, Clock, ChevronRight, X } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-production.onrender.com'

export default function ResearchIntake() {
  const [query, setQuery] = useState('')
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [showArchive, setShowArchive] = useState(false)
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()

  // Fetch sessions archive
  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/sessions?limit=50`)
      return res.data
    },
    refetchInterval: 10000
  })

  // Create research session
  const createSessionMutation = useMutation({
    mutationFn: async (userQuery) => {
      const res = await axios.post(`${API_URL}/api/sessions`, {
        agent_id: 'research-agent',
        query: userQuery
      })
      return res.data
    },
    onSuccess: (data) => {
      setCurrentSessionId(data.id)
      queryClient.invalidateQueries(['sessions'])
    },
    onError: (error) => {
      console.error('Failed to start research:', error)
      alert('Failed to start research: ' + (error.response?.data?.detail || error.message))
    }
  })

  // Fetch specific session details
  const { data: sessionDetails } = useQuery({
    queryKey: ['session', currentSessionId],
    queryFn: async () => {
      if (!currentSessionId) return null
      const res = await axios.get(`${API_URL}/api/sessions/${currentSessionId}`)
      return res.data
    },
    enabled: !!currentSessionId,
    refetchInterval: (data) => data?.status === 'completed' ? false : 2000
  })

  // WebSocket streaming
  const { messages, isConnected, status, currentActivity } = useAgentStreaming(currentSessionId, {
    onComplete: () => {
      queryClient.invalidateQueries(['sessions'])
      queryClient.invalidateQueries(['session', currentSessionId])
    }
  })

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    createSessionMutation.mutate(query)
    setQuery('')
  }

  const handleReset = () => {
    setCurrentSessionId(null)
    setQuery('')
  }

  const handleViewSession = (sessionId) => {
    setCurrentSessionId(sessionId)
    setShowArchive(false)
  }

  const isProcessing = createSessionMutation.isPending || (currentSessionId && status !== 'completed' && status !== 'error')

  // Get content to display - either streaming messages or stored session output
  const displayContent = messages.length > 0
    ? messages
    : sessionDetails?.final_output
      ? [{ id: 'stored', type: 'response', content: sessionDetails.final_output }]
      : []

  return (
    <div className="flex h-[calc(100vh-120px)] gap-4">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Research Input Section */}
        {!currentSessionId ? (
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className="w-full max-w-2xl">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  What would you like to research?
                </h2>
                <p className="text-gray-600">
                  Enter any topic and I'll generate a comprehensive research report.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., Research fire spread algorithms and provide Python implementations..."
                  className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-lg"
                  rows={4}
                  disabled={createSessionMutation.isPending}
                />

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={!query.trim() || createSessionMutation.isPending}
                    className="flex-1 py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg"
                  >
                    {createSessionMutation.isPending ? (
                      <>
                        <Loader2 size={22} className="animate-spin" />
                        Starting...
                      </>
                    ) : (
                      <>
                        <Send size={22} />
                        Start Research
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowArchive(!showArchive)}
                    className="px-6 py-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 flex items-center gap-2"
                  >
                    <Archive size={20} />
                    Archive
                    {sessions?.length > 0 && (
                      <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-sm">
                        {sessions.length}
                      </span>
                    )}
                  </button>
                </div>
              </form>

              <div className="mt-8 text-sm text-gray-500 text-center">
                <p className="mb-2">Example topics:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {[
                    'Machine learning basics',
                    'Fire behavior prediction',
                    'REST API design',
                    'Climate data analysis'
                  ].map((example) => (
                    <button
                      key={example}
                      onClick={() => setQuery(example)}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Results Section */
          <div className="flex-1 flex flex-col bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div className="flex items-center gap-3">
                <FileText className="text-blue-600" size={24} />
                <div>
                  <h3 className="font-semibold text-gray-900">Research Report</h3>
                  <p className="text-sm text-gray-500 truncate max-w-md">
                    {sessionDetails?.initial_query || 'Loading...'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {isConnected && status !== 'completed' && (
                  <div className="flex items-center gap-2 text-blue-600 text-sm">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                    Processing
                  </div>
                )}

                {sessionDetails?.status === 'completed' && (
                  <div className="text-green-600 text-sm flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Complete
                  </div>
                )}

                <button
                  onClick={() => setShowArchive(!showArchive)}
                  className="px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg flex items-center gap-2"
                >
                  <Archive size={18} />
                </button>

                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
                >
                  <RotateCcw size={16} />
                  New
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Activity Indicator */}
              {currentActivity && (
                <div className="flex items-center gap-3 text-gray-600 mb-4 p-3 bg-blue-50 rounded-lg">
                  <Loader2 size={18} className="animate-spin text-blue-600" />
                  <span>{currentActivity.message}</span>
                </div>
              )}

              {/* Messages/Content */}
              <div className="prose prose-lg max-w-none">
                {displayContent.map((msg) => (
                  <MessageContent key={msg.id} message={msg} />
                ))}
              </div>

              {/* Loading indicator while streaming */}
              {isProcessing && displayContent.length === 0 && (
                <div className="flex items-center gap-3 text-gray-500">
                  <Loader2 size={20} className="animate-spin" />
                  <span>Generating research report...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Footer with metadata */}
            {sessionDetails?.status === 'completed' && sessionDetails?.duration_seconds && (
              <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-500 flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <Clock size={14} />
                  {sessionDetails.duration_seconds}s
                </span>
                <span>
                  {sessionDetails.final_output?.length?.toLocaleString() || 0} characters
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Archive Sidebar */}
      {showArchive && (
        <div className="w-80 bg-white rounded-lg border border-gray-200 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Archive size={18} />
              Research Archive
            </h3>
            <button
              onClick={() => setShowArchive(false)}
              className="text-gray-400 hover:text-gray-600 p-1"
            >
              <X size={18} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {sessions?.map((session) => (
              <button
                key={session.id}
                onClick={() => handleViewSession(session.id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  session.id === currentSessionId
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900 line-clamp-2">
                    {session.initial_query}
                  </p>
                  <ChevronRight size={16} className="text-gray-400 flex-shrink-0 mt-0.5" />
                </div>

                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span className={`px-2 py-0.5 rounded-full ${
                    session.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : session.status === 'in_progress'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {session.status}
                  </span>
                  {session.duration_seconds && (
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {session.duration_seconds}s
                    </span>
                  )}
                </div>

                {session.start_time && (
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(session.start_time).toLocaleDateString()}
                  </div>
                )}
              </button>
            ))}

            {(!sessions || sessions.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                <Archive size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No research sessions yet</p>
                <p className="text-xs mt-1">Start your first research above</p>
              </div>
            )}
          </div>

          {sessions?.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
              {sessions.length} research sessions
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function MessageContent({ message }) {
  if (message.type === 'system' || message.type === 'status') {
    return (
      <div className="text-sm text-gray-500 italic mb-2">
        {message.content}
      </div>
    )
  }

  if (message.type === 'tool') {
    return (
      <div className="text-sm text-blue-600 mb-2 flex items-center gap-2">
        <Loader2 size={14} className="animate-spin" />
        {message.content}
      </div>
    )
  }

  if (message.type === 'error') {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded-lg mb-4">
        {message.content}
      </div>
    )
  }

  // Main content - render as pre-formatted text
  return (
    <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
      {message.content}
    </pre>
  )
}
