import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksAPI, agentsAPI } from '../api/client'
import { Play, Plus, X, Loader2, Clock, CheckCircle2, XCircle, ChevronDown, ChevronUp, Search, LayoutGrid, List } from 'lucide-react'

export default function Tasks() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterStatus, setFilterStatus] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [compactView, setCompactView] = useState(false)
  const queryClient = useQueryClient()

  // Auto-cleanup stale tasks on mount
  useEffect(() => {
    tasksAPI.cleanupStale().catch(err => console.error('Failed to cleanup stale tasks:', err))
  }, [])

  const { data: tasksData, isLoading } = useQuery({
    queryKey: ['tasks', filterStatus],
    queryFn: () => tasksAPI.list({ status: filterStatus || undefined }).then(res => res.data),
    refetchInterval: 5000,
  })

  // Filter tasks by search query
  const tasks = tasksData?.filter(task => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return task.title.toLowerCase().includes(query) ||
           task.description.toLowerCase().includes(query)
  })

  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsAPI.list().then(res => res.data),
  })

  const executeMutation = useMutation({
    mutationFn: (taskId) => tasksAPI.execute(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks'])
    },
  })

  const cancelMutation = useMutation({
    mutationFn: (taskId) => tasksAPI.cancel(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks'])
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Tasks</h2>
          <p className="text-gray-600 mt-2">Manage and monitor agent tasks</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          Create Task
        </button>
      </div>

      {/* Filters & Search */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 flex items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks..."
                className="input pl-10 w-full"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700 whitespace-nowrap">Status:</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="input w-auto"
              >
                <option value="">All</option>
                <option value="pending">Pending</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCompactView(false)}
              className={`p-2 rounded ${!compactView ? 'bg-primary-100 text-primary-600' : 'text-gray-600 hover:bg-gray-100'}`}
              title="Detailed view"
            >
              <LayoutGrid size={18} />
            </button>
            <button
              onClick={() => setCompactView(true)}
              className={`p-2 rounded ${compactView ? 'bg-primary-100 text-primary-600' : 'text-gray-600 hover:bg-gray-100'}`}
              title="Compact view"
            >
              <List size={18} />
            </button>
          </div>
        </div>
        {searchQuery && (
          <div className="mt-3 text-sm text-gray-600">
            Found {tasks?.length || 0} task{tasks?.length !== 1 ? 's' : ''} matching "{searchQuery}"
          </div>
        )}
      </div>

      {/* Tasks List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      ) : tasks && tasks.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">No tasks found. Create your first task to get started!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks?.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              compactView={compactView}
              onExecute={(taskId) => executeMutation.mutate(taskId)}
              onCancel={(taskId) => cancelMutation.mutate(taskId)}
              isExecuting={executeMutation.isPending}
              isCancelling={cancelMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Create Task Modal */}
      {showCreateModal && (
        <CreateTaskModal
          agents={agents || []}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries(['tasks'])
          }}
        />
      )}
    </div>
  )
}

function TaskCard({ task, compactView, onExecute, onCancel, isExecuting, isCancelling }) {
  const [elapsedTime, setElapsedTime] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    if (task.status !== 'running' || !task.started_at) return

    const interval = setInterval(() => {
      const started = new Date(task.started_at)
      const now = new Date()
      const seconds = Math.floor((now - started) / 1000)
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      setElapsedTime(`${mins}m ${secs}s`)
    }, 1000)

    return () => clearInterval(interval)
  }, [task.status, task.started_at])

  // Format relative time
  const getRelativeTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffSecs < 60) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  // Truncate description
  const truncateText = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const needsTruncation = task.description && task.description.length > 150

  const getStatusIcon = () => {
    switch (task.status) {
      case 'running':
        return <Loader2 size={18} className="animate-spin text-blue-600" />
      case 'completed':
        return <CheckCircle2 size={18} className="text-green-600" />
      case 'failed':
        return <XCircle size={18} className="text-red-600" />
      default:
        return <Clock size={18} className="text-gray-400" />
    }
  }

  const priorityLabels = {
    1: 'low',
    2: 'medium',
    3: 'high',
    4: 'critical'
  }

  // Different styling for failed tasks
  const cardClass = task.status === 'failed'
    ? 'card hover:shadow-md transition-shadow border-2 border-red-200 bg-red-50'
    : 'card hover:shadow-md transition-shadow'

  if (compactView) {
    // Compact view - single line with essential info
    return (
      <div className={cardClass}>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {getStatusIcon()}
            <h3 className="font-semibold text-gray-900 truncate flex-1">{task.title}</h3>
            <span className={`badge badge-${task.status}`}>{task.status}</span>
            <span className="text-xs text-gray-500 whitespace-nowrap">{getRelativeTime(task.created_at)}</span>
          </div>
          <div className="flex gap-2">
            {task.status === 'pending' && (
              <button onClick={() => onExecute(task.id)} className="btn-primary p-2" disabled={isExecuting} title="Execute">
                <Play size={16} />
              </button>
            )}
            {(task.status === 'running' || task.status === 'pending') && (
              <button onClick={() => onCancel(task.id)} className="btn-secondary p-2 text-red-600" disabled={isCancelling} title="Cancel">
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Detailed view - full card with description
  return (
    <div className={cardClass}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            {getStatusIcon()}
            <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
            <span className={`badge badge-${task.status}`}>{task.status}</span>
            <span className="text-xs text-gray-500">{priorityLabels[task.priority]} priority</span>
            {task.status === 'running' && elapsedTime && (
              <span className="text-xs font-medium text-blue-600 flex items-center gap-1">
                <Clock size={12} />
                {elapsedTime}
              </span>
            )}
          </div>

          {/* Description with expand/collapse */}
          <div className="mt-2">
            <p className="text-gray-700">
              {isExpanded || !needsTruncation ? task.description : truncateText(task.description)}
            </p>
            {needsTruncation && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-primary-600 hover:text-primary-700 text-sm mt-1 flex items-center gap-1"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp size={16} />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown size={16} />
                    Show more
                  </>
                )}
              </button>
            )}
          </div>

          {/* Metadata - relative time */}
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-600 flex-wrap">
            <span className="font-medium">{getRelativeTime(task.created_at)}</span>
            <span className="text-gray-400">•</span>
            <span>Agent: {task.agent_id?.slice(0, 8)}...</span>
            {task.completed_at && (
              <>
                <span className="text-gray-400">•</span>
                <span>Completed: {getRelativeTime(task.completed_at)}</span>
              </>
            )}
          </div>

          {/* Running progress indicator */}
          {task.status === 'running' && (
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Processing...</p>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 ml-4">
          {task.status === 'pending' && (
            <button
              onClick={() => onExecute(task.id)}
              className="btn-primary flex items-center gap-2"
              disabled={isExecuting}
            >
              <Play size={16} />
              Execute
            </button>
          )}
          {(task.status === 'running' || task.status === 'pending') && (
            <button
              onClick={() => onCancel(task.id)}
              className="btn-secondary flex items-center gap-2 text-red-600 hover:bg-red-50"
              disabled={isCancelling}
            >
              <X size={16} />
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function CreateTaskModal({ agents, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    agent_id: '',
    title: '',
    description: '',
    priority: 'medium',
  })

  const createMutation = useMutation({
    mutationFn: (data) => tasksAPI.create(data),
    onSuccess,
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    // Convert priority string to integer
    const priorityMap = {
      'low': 1,
      'medium': 2,
      'high': 3,
      'critical': 4
    }

    const taskData = {
      ...formData,
      priority: priorityMap[formData.priority] || 2
    }

    createMutation.mutate(taskData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">Create New Task</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Agent</label>
            <select
              value={formData.agent_id}
              onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Select an agent</option>
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name} ({agent.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={4}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              className="input"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Task'}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
