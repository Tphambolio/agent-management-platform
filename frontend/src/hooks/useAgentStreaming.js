import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Custom hook for WebSocket-based agent streaming
 * Connects to backend streaming endpoint and manages real-time events
 */
export function useAgentStreaming(sessionId, options = {}) {
  const { onComplete, onError, autoConnect = true } = options

  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [status, setStatus] = useState('idle') // idle, connecting, connected, disconnected, error
  const [currentActivity, setCurrentActivity] = useState(null)

  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  // Use refs for callbacks to avoid reconnection loops
  const onCompleteRef = useRef(onComplete)
  const onErrorRef = useRef(onError)

  // Update refs when callbacks change
  useEffect(() => {
    onCompleteRef.current = onComplete
    onErrorRef.current = onError
  }, [onComplete, onError])

  const connect = useCallback(() => {
    if (!sessionId) return

    // Don't connect if already connected or connecting
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting, skipping')
      return
    }

    try {
      setStatus('connecting')

      // Get WebSocket URL - handle both http and https
      const backendUrl = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-production.onrender.com'
      const wsUrl = backendUrl.replace(/^http/, 'ws')
      const fullWsUrl = `${wsUrl}/ws/stream/${sessionId}`

      console.log('[WebSocket] Connecting to:', fullWsUrl)

      const ws = new WebSocket(fullWsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[WebSocket] Connected')
        setIsConnected(true)
        setStatus('connected')
        reconnectAttempts.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('[WebSocket] Event:', data.type, data)

          switch (data.type) {
            case 'session_start':
              setMessages([{
                id: Date.now(),
                type: 'system',
                content: data.data.message || 'Session started',
                timestamp: data.timestamp
              }])
              break

            case 'agent_thinking':
              setCurrentActivity({
                type: 'thinking',
                message: data.data.thought || 'Agent is thinking...'
              })
              break

            case 'tool_call':
              setCurrentActivity({
                type: 'tool',
                tool: data.data.tool_name,
                message: `Using ${data.data.tool_name}...`
              })

              // Add tool activity message
              setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'tool',
                tool: data.data.tool_name,
                content: `🔧 ${data.data.tool_name}`,
                timestamp: data.timestamp
              }])
              break

            case 'tool_result':
              setCurrentActivity(null)
              break

            case 'chunk':
              // Streaming text chunk
              setMessages(prev => {
                const last = prev[prev.length - 1]
                if (last && last.streaming) {
                  // Append to existing streaming message
                  return [
                    ...prev.slice(0, -1),
                    { ...last, content: last.content + data.data.chunk }
                  ]
                }
                // Start new streaming message
                return [...prev, {
                  id: Date.now(),
                  type: 'agent',
                  content: data.data.chunk,
                  streaming: true,
                  timestamp: data.timestamp
                }]
              })
              break

            case 'status_update':
              // Only add status message if messages array is empty (first connection)
              setMessages(prev => {
                if (prev.length === 0) {
                  return [{
                    id: Date.now(),
                    type: 'status',
                    content: data.data.message,
                    timestamp: data.timestamp
                  }]
                }
                return prev
              })
              break

            case 'session_complete':
              // Mark last message as complete
              setMessages(prev => {
                const last = prev[prev.length - 1]
                if (last && last.streaming) {
                  return [
                    ...prev.slice(0, -1),
                    { ...last, streaming: false, complete: true }
                  ]
                }
                return prev
              })

              setCurrentActivity(null)
              setStatus('completed')

              if (onCompleteRef.current) {
                onCompleteRef.current(data.data)
              }
              break

            case 'artifact_created':
              setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'artifact',
                artifact: data.data,
                content: `📄 Created: ${data.data.title}`,
                timestamp: data.timestamp
              }])
              break

            case 'error':
              setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'error',
                content: data.data.message || 'An error occurred',
                timestamp: data.timestamp
              }])

              if (onErrorRef.current) {
                onErrorRef.current(data.data)
              }
              break

            default:
              console.log('[WebSocket] Unknown event type:', data.type)
          }
        } catch (err) {
          console.error('[WebSocket] Error parsing message:', err)
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        setStatus('error')

        if (onErrorRef.current) {
          onErrorRef.current({ message: 'WebSocket connection error' })
        }
      }

      ws.onclose = () => {
        console.log('[WebSocket] Connection closed')
        setIsConnected(false)
        setStatus('disconnected')

        // Attempt reconnection if not max attempts
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
          console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)

          reconnectAttempts.current++
          reconnectTimeoutRef.current = setTimeout(connect, delay)
        }
      }
    } catch (err) {
      console.error('[WebSocket] Connection error:', err)
      setStatus('error')

      if (onErrorRef.current) {
        onErrorRef.current({ message: err.message })
      }
    }
  }, [sessionId]) // Only depend on sessionId, not callbacks

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
    setStatus('disconnected')
    reconnectAttempts.current = 0
  }, [])

  const sendMessage = useCallback((message) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] Cannot send message - not connected')
    }
  }, [isConnected])

  // Auto-connect on mount or when sessionId changes
  useEffect(() => {
    if (autoConnect && sessionId) {
      // Reset messages when session changes
      setMessages([])
      connect()
    }

    return () => {
      disconnect()
    }
  }, [sessionId, autoConnect]) // Remove connect/disconnect from deps - they're stable

  return {
    messages,
    isConnected,
    status,
    currentActivity,
    connect,
    disconnect,
    sendMessage
  }
}
