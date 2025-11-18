import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAgentStreaming } from '../hooks/useAgentStreaming'
import { Send, Sparkles, Archive, Cpu, Loader2, ChevronRight, Clock } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-3g16.onrender.com'

export default function AgentLab() {
  const [query, setQuery] = useState('')
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [showArchive, setShowArchive] = useState(false)
  const [showCapabilities, setShowCapabilities] = useState(false)

  const queryClient = useQueryClient()

  // Fetch agent capabilities
  const { data: capabilities } = useQuery({
    queryKey: ['capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/capabilities`)
      return res.data
    },
    staleTime: 5 * 60 * 1000 // 5 minutes
  })

  // Fetch recent sessions
  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/sessions?limit=20`)
      return res.data
    },
    refetchInterval: 5000 // Refetch every 5 seconds
  })

  // Create new session
  const createSessionMutation = useMutation({
    mutationFn: async (userQuery) => {
      const res = await axios.post(`${API_URL}/api/sessions`, {
        agent_id: 'general-agent',
        query: userQuery
      })
      return res.data
    },
    onSuccess: (data) => {
      setCurrentSessionId(data.id)
      queryClient.invalidateQueries(['sessions'])
    },
    onError: (error) => {
      console.error('Failed to create session:', error)
      alert('Failed to start session: ' + (error.response?.data?.detail || error.message))
    }
  })

  // WebSocket streaming hook
  const {
    messages,
    isConnected,
    status,
    currentActivity
  } = useAgentStreaming(currentSessionId, {
    onComplete: (data) => {
      console.log('Session complete:', data)
      queryClient.invalidateQueries(['sessions'])
    },
    onError: (error) => {
      console.error('Streaming error:', error)
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!query.trim()) return

    createSessionMutation.mutate(query)
    setQuery('')
  }

  const handleNewSession = () => {
    setCurrentSessionId(null)
    setQuery('')
  }

  return (
    <div className="flex h-[calc(100vh-200px)] gap-4">
      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="text-primary-600" size={28} />
              Agent Lab
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Ask anything - I'll research and build it for you
            </p>
          </div>

          <div className="flex items-center gap-3">
            {isConnected && (
              <div className="flex items-center gap-2 text-green-600 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Live
              </div>
            )}

            <button
              onClick={() => setShowCapabilities(!showCapabilities)}
              className="btn-secondary text-sm"
            >
              <Cpu size={16} />
              Capabilities
            </button>

            <button
              onClick={() => setShowArchive(!showArchive)}
              className="btn-secondary text-sm"
            >
              <Archive size={16} />
              Archive
            </button>

            {currentSessionId && (
              <button
                onClick={handleNewSession}
                className="btn-primary text-sm"
              >
                New Session
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {!currentSessionId ? (
            /* Welcome Screen */
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6">
                <Sparkles className="text-white" size={40} />
              </div>

              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Welcome to the Agent Lab
              </h3>

              <p className="text-gray-600 max-w-lg mb-8">
                This is your counter-style agent workspace. Ask me to research anything,
                build features, analyze data, or create documentation. I have access to {capabilities?.total_agents || 19} specialized agents.
              </p>

              {capabilities && (
                <div className="flex flex-wrap gap-2 justify-center max-w-2xl mb-8">
                  {capabilities.available_tools?.slice(0, 6).map((tool) => (
                    <span
                      key={tool}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      {tool.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              )}

              <div className="text-sm text-gray-500 space-y-2">
                <p>Try asking:</p>
                <div className="space-y-1 text-left bg-gray-50 rounded-lg p-4">
                  <p>• "Research fire spread algorithms and provide Python code"</p>
                  <p>• "Build a geospatial analysis tool for wildfire data"</p>
                  <p>• "Create a comprehensive report on FBP fuel models"</p>
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}

              {/* Current Activity Indicator */}
              {currentActivity && (
                <div className="flex items-center gap-3 text-gray-600 animate-pulse">
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-sm">{currentActivity.message}</span>
                </div>
              )}

              {/* Streaming Indicator */}
              {messages.length > 0 && messages[messages.length - 1]?.streaming && (
                <div className="flex items-center gap-2 text-gray-400">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="px-6 py-4 border-t border-gray-200">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What would you like me to research or build?"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={createSessionMutation.isPending}
            />

            <button
              type="submit"
              disabled={!query.trim() || createSessionMutation.isPending}
              className="btn-primary px-6 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createSessionMutation.isPending ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
              {createSessionMutation.isPending ? 'Starting...' : 'Send'}
            </button>
          </form>

          <p className="text-xs text-gray-500 mt-2">
            Powered by {capabilities?.total_agents || 19} specialized AI agents
          </p>
        </div>
      </div>

      {/* Archive Sidebar */}
      {showArchive && (
        <div className="w-80 bg-white rounded-lg shadow-sm border border-gray-200 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Recent Sessions</h3>
            <button
              onClick={() => setShowArchive(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2">
            {sessions?.map((session) => (
              <button
                key={session.id}
                onClick={() => setCurrentSessionId(session.id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  session.id === currentSessionId
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900 line-clamp-2">
                    {session.initial_query}
                  </p>
                  <span className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${
                    session.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : session.status === 'in_progress'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {session.status}
                  </span>
                </div>

                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                  <Clock size={12} />
                  {session.duration_seconds
                    ? `${session.duration_seconds}s`
                    : 'In progress'}
                </div>
              </button>
            ))}

            {(!sessions || sessions.length === 0) && (
              <p className="text-sm text-gray-500 text-center py-8">
                No sessions yet
              </p>
            )}
          </div>
        </div>
      )}

      {/* Capabilities Sidebar */}
      {showCapabilities && capabilities && (
        <div className="w-80 bg-white rounded-lg shadow-sm border border-gray-200 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Capabilities</h3>
            <button
              onClick={() => setShowCapabilities(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Available Tools</h4>
              <div className="flex flex-wrap gap-2">
                {capabilities.available_tools?.map((tool) => (
                  <span
                    key={tool}
                    className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                  >
                    {tool.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Agents by Type ({capabilities.total_agents} total)
              </h4>
              <div className="space-y-3">
                {Object.entries(capabilities.by_type || {}).map(([type, agents]) => (
                  <div key={type} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {type}
                      </span>
                      <span className="text-xs text-gray-500">{agents.length}</span>
                    </div>
                    <div className="space-y-1">
                      {agents.slice(0, 3).map((agent) => (
                        <div key={agent.name} className="text-xs text-gray-600">
                          <ChevronRight size={12} className="inline" />
                          {agent.name}
                        </div>
                      ))}
                      {agents.length > 3 && (
                        <div className="text-xs text-gray-500">
                          +{agents.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MessageBubble({ message }) {
  if (message.type === 'system') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded-full">
          {message.content}
        </div>
      </div>
    )
  }

  if (message.type === 'tool') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-blue-50 text-blue-700 text-sm rounded-full flex items-center gap-2">
          <Cpu size={14} />
          {message.content}
        </div>
      </div>
    )
  }

  if (message.type === 'artifact') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-green-50 text-green-700 text-sm rounded-full">
          {message.content}
        </div>
      </div>
    )
  }

  if (message.type === 'status') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-gray-100 text-gray-600 text-xs rounded-full">
          {message.content}
        </div>
      </div>
    )
  }

  if (message.type === 'error') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-red-50 text-red-700 text-sm rounded-full">
          ⚠️ {message.content}
        </div>
      </div>
    )
  }

  // Agent response message
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
        <Sparkles className="text-white" size={18} />
      </div>

      <div className="flex-1">
        <div className="bg-gray-50 rounded-lg px-4 py-3">
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-800">
              {message.content}
            </pre>
          </div>
        </div>

        {message.complete && (
          <div className="text-xs text-gray-500 mt-1">
            ✓ Complete
          </div>
        )}
      </div>
    </div>
  )
}
