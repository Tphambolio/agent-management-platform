import { useState, useRef, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAgentStreaming } from '../hooks/useAgentStreaming'
import { Send, Loader2, RotateCcw, FileText } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-production.onrender.com'

export default function ResearchIntake() {
  const [query, setQuery] = useState('')
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()

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
    },
    onError: (error) => {
      console.error('Failed to start research:', error)
      alert('Failed to start research: ' + (error.response?.data?.detail || error.message))
    }
  })

  // WebSocket streaming
  const { messages, isConnected, status, currentActivity } = useAgentStreaming(currentSessionId, {
    onComplete: () => {
      queryClient.invalidateQueries(['sessions'])
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

  const isProcessing = createSessionMutation.isPending || (currentSessionId && status !== 'completed' && status !== 'error')

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      {/* Research Input Section */}
      {!currentSessionId ? (
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-full max-w-2xl">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                What would you like to research?
              </h2>
              <p className="text-gray-600">
                Enter any topic and I'll generate a comprehensive research report with analysis and code examples.
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

              <button
                type="submit"
                disabled={!query.trim() || createSessionMutation.isPending}
                className="w-full py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg"
              >
                {createSessionMutation.isPending ? (
                  <>
                    <Loader2 size={22} className="animate-spin" />
                    Starting Research...
                  </>
                ) : (
                  <>
                    <Send size={22} />
                    Start Research
                  </>
                )}
              </button>
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
                <p className="text-sm text-gray-500">
                  {status === 'completed' ? 'Complete' : 'Generating...'}
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

              <button
                onClick={handleReset}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                <RotateCcw size={16} />
                New Research
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
              {messages.map((msg) => (
                <MessageContent key={msg.id} message={msg} />
              ))}
            </div>

            {/* Loading indicator while streaming */}
            {isProcessing && messages.length === 0 && (
              <div className="flex items-center gap-3 text-gray-500">
                <Loader2 size={20} className="animate-spin" />
                <span>Preparing research...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
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

  // Main content - render as pre-formatted text for now
  // Could add markdown rendering later
  return (
    <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
      {message.content}
    </pre>
  )
}
