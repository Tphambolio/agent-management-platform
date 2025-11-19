import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksAPI, agentsAPI } from '../api/client'
import { Play, Plus, X, Loader2, Clock, CheckCircle2, XCircle } from 'lucide-react'

export default function Tasks() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterStatus, setFilterStatus] = useState('')
  const queryClient = useQueryClient()

  // Auto-cleanup stale tasks on mount
  useEffect(() => {
    tasksAPI.cleanupStale().catch(err => console.error('Failed to cleanup stale tasks:', err))
  }, [])

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', filterStatus],
    queryFn: () => tasksAPI.list({ status: filterStatus || undefined }).then(res => res.data),
    refetchInterval: 5000,
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

      {/* Filters */}
      <div className="card">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filter by status:</label>
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

function TaskCard({ task, onExecute, onCancel, isExecuting, isCancelling }) {
  const [elapsedTime, setElapsedTime] = useState('')

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

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
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
          <p className="text-gray-700 mt-2">{task.description}</p>
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
            <span>Agent: {task.agent_id?.slice(0, 8)}...</span>
            <span>Created: {new Date(task.created_at).toLocaleString()}</span>
            {task.started_at && task.status === 'running' && (
              <span>Started: {new Date(task.started_at).toLocaleString()}</span>
            )}
            {task.completed_at && (
              <span>Completed: {new Date(task.completed_at).toLocaleString()}</span>
            )}
          </div>
          {task.status === 'running' && (
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Processing...</p>
            </div>
          )}
        </div>
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
