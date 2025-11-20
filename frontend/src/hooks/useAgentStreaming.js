import { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-3g16.onrender.com'

/**
 * Custom hook for agent streaming with WebSocket + HTTP polling fallback
 * Tries WebSocket first, falls back to polling if WebSocket fails (HTTP 403)
 */
export function useAgentStreaming(sessionId, options = {}) {
  const { onComplete, onError, autoConnect = true } = options

  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [status, setStatus] = useState('idle') // idle, connecting, connected, disconnected, error
  const [currentActivity, setCurrentActivity] = useState(null)
  const [usingPolling, setUsingPolling] = useState(false) // Track if using polling fallback

  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const pollingIntervalRef = useRef(null)
  const lastLogIndexRef = useRef(0) // Track processed logs for polling
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const isConnectingRef = useRef(false) // Prevent duplicate connections

  // Polling fallback when WebSocket fails
  const startPolling = useCallback(() => {
    if (!sessionId) return

    console.log('[Polling] Starting HTTP polling fallback')
    setUsingPolling(true)
    setIsConnected(true) // Consider "connected" when polling
    setStatus('connected')

    const poll = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/sessions/${sessionId}`)
        const data = response.data

        // Process new interaction logs
        if (data.interaction_logs && data.interaction_logs.length > lastLogIndexRef.current) {
          const newLogs = data.interaction_logs.slice(lastLogIndexRef.current)
          lastLogIndexRef.current = data.interaction_logs.length

          // Convert logs to messages
          newLogs.forEach(log => {
            const msg = {
              id: Date.now() + Math.random(),
              timestamp: log.timestamp,
              content: log.content.message || JSON.stringify(log.content)
            }

            // Map event types to message types
            if (log.event_type === 'llm_response') {
              msg.type = 'agent'
              msg.content = log.content.response || log.content.chunk || ''
              setMessages(prev => [...prev, msg])
            } else if (log.event_type === 'tool_use') {
              msg.type = 'tool'
              setMessages(prev => [...prev, msg])
            }
          })
        }

        // Check if session complete
        if (data.status === 'completed') {
          console.log('[Polling] Session complete')
          setStatus('completed')
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
          }
          if (onComplete) {
            onComplete({ final_output: data.final_output })
          }
        }
      } catch (err) {
        console.error('[Polling] Error:', err)
      }
    }

    // Poll every 2 seconds
    poll() // Initial poll
    pollingIntervalRef.current = setInterval(poll, 2000)
  }, [sessionId, onComplete])

  const connect = useCallback(() => {
    if (!sessionId) return

    // Prevent duplicate connections
    if (isConnectingRef.current || (wsRef.current && wsRef.current.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting, skipping duplicate connection')
      return
    }

    isConnectingRef.current = true

    try {
      setStatus('connecting')

      // Get WebSocket URL - handle both http and https
      const backendUrl = import.meta.env.VITE_API_URL || 'https://agent-platform-backend-3g16.onrender.com'
      const wsUrl = backendUrl.replace(/^http/, 'ws')
      const fullWsUrl = `${wsUrl}/ws/stream/${sessionId}`

      console.log('[WebSocket] Connecting to:', fullWsUrl)

      const ws = new WebSocket(fullWsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[WebSocket] Connected')
        setIsConnected(true)
        setStatus('connected')
        setUsingPolling(false)
        reconnectAttempts.current = 0
        isConnectingRef.current = false // Connection successful
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
              setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'status',
                content: data.data.message,
                timestamp: data.timestamp
              }])
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

              if (onComplete) {
                onComplete(data.data)
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

              if (onError) {
                onError(data.data)
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
        isConnectingRef.current = false // Connection failed

        // If we haven't tried polling yet, fall back to it
        if (!usingPolling && reconnectAttempts.current >= maxReconnectAttempts) {
          console.log('[WebSocket] Max reconnect attempts reached, falling back to HTTP polling')
          startPolling()
        } else if (onError) {
          onError({ message: 'WebSocket connection error' })
        }
      }

      ws.onclose = (event) => {
        console.log('[WebSocket] Connection closed', event.code, event.reason)
        setIsConnected(false)
        setStatus('disconnected')

        // If close code is 403 (Forbidden) or 1006 (abnormal closure from 403), fall back to polling immediately
        if ((event.code === 403 || event.code === 1006) && !usingPolling) {
          console.log('[WebSocket] Connection forbidden (likely Cloudflare WAF), falling back to HTTP polling')
          isConnectingRef.current = false
          startPolling()
          return
        }

        // Attempt reconnection if not max attempts
        if (reconnectAttempts.current < maxReconnectAttempts && !usingPolling) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
          console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)

          reconnectAttempts.current++
          reconnectTimeoutRef.current = setTimeout(connect, delay)
        } else if (!usingPolling) {
          // Max attempts reached, fall back to polling
          console.log('[WebSocket] Max reconnect attempts reached, falling back to HTTP polling')
          startPolling()
        }
      }
    } catch (err) {
      console.error('[WebSocket] Connection error:', err)
      setStatus('error')
      isConnectingRef.current = false // Connection failed

      if (onError) {
        onError({ message: err.message })
      }
    }
  }, [sessionId, onComplete, onError])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    isConnectingRef.current = false // Reset connecting flag
    setIsConnected(false)
    setStatus('disconnected')
    setUsingPolling(false)
  }, [])

  const sendMessage = useCallback((message) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] Cannot send message - not connected')
    }
  }, [isConnected])

  // Auto-connect on mount - only depend on sessionId and autoConnect
  useEffect(() => {
    if (autoConnect && sessionId) {
      connect()
    }

    return () => {
      disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, autoConnect]) // Only re-run when sessionId or autoConnect changes

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
