import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { agentsAPI, tasksAPI, reportsAPI, healthAPI } from '../api/client'
import { Users, CheckSquare, FileText, Activity } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthAPI.check().then(res => res.data),
    refetchInterval: 5000,
  })

  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsAPI.list().then(res => res.data),
    refetchInterval: 10000,
  })

  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksAPI.list().then(res => res.data),
    refetchInterval: 5000,
  })

  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.list().then(res => res.data),
  })

  const stats = [
    {
      name: 'Total Agents',
      value: agents?.length || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Tasks',
      value: tasks?.filter(t => t.status === 'running').length || 0,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Total Tasks',
      value: tasks?.length || 0,
      icon: CheckSquare,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      name: 'Reports Generated',
      value: reports?.length || 0,
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  const activeAgents = agents?.filter(a => a.status === 'running') || []
  const idleAgents = agents?.filter(a => a.status === 'idle') || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-2">Overview of your agent workforce</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.name}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`${stat.bgColor} p-3 rounded-lg`}>
                  <Icon className={stat.color} size={24} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Agent Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Agents */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Active Agents ({activeAgents.length})
          </h3>
          <div className="space-y-3">
            {activeAgents.length === 0 ? (
              <p className="text-gray-500 text-sm">No agents currently running</p>
            ) : (
              activeAgents.map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{agent.name}</p>
                    <p className="text-sm text-gray-600">{agent.type}</p>
                  </div>
                  <span className="badge badge-running">Running</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Tasks
          </h3>
          <div className="space-y-3">
            {!tasks || tasks.length === 0 ? (
              <p className="text-gray-500 text-sm">No tasks yet</p>
            ) : (
              tasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  onClick={() => task.status === 'completed' && navigate('/reports')}
                  className={`flex items-center justify-between p-3 bg-gray-50 rounded-lg transition-all ${
                    task.status === 'completed'
                      ? 'cursor-pointer hover:bg-blue-50 hover:shadow-md'
                      : ''
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{task.title}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(task.created_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`badge badge-${task.status} ml-2`}>
                    {task.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* System Health */}
      {health && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="text-lg font-semibold text-green-600">{health.status}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Agents Discovered</p>
              <p className="text-lg font-semibold text-gray-900">{health.agents_discovered}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Tasks</p>
              <p className="text-lg font-semibold text-gray-900">{health.tasks_total}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Reports</p>
              <p className="text-lg font-semibold text-gray-900">{health.reports_total}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
