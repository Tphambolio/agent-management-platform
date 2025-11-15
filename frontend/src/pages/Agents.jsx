import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentsAPI } from '../api/client'
import { RefreshCw, Plus, X, Sparkles } from 'lucide-react'

export default function Agents() {
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showIntelligentModal, setShowIntelligentModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: agents, isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsAPI.list().then(res => res.data),
    refetchInterval: 10000,
  })

  const handleRediscover = async () => {
    await agentsAPI.sync()
    refetch()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Agents</h2>
          <p className="text-gray-600 mt-2">Manage your AI agent workforce</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => setShowIntelligentModal(true)} className="btn-primary flex items-center gap-2">
            <Sparkles size={16} />
            Create Intelligent Agent
          </button>
          <button onClick={() => setShowRegisterModal(true)} className="btn-secondary flex items-center gap-2">
            <Plus size={16} />
            Manual Register
          </button>
          <button onClick={handleRediscover} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} />
            Sync
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading agents...</p>
        </div>
      ) : agents && agents.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">No agents found. Add agent definitions to .agents/ directory.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents?.map((agent) => (
            <div key={agent.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                    <span className={`badge badge-${agent.status}`}>
                      {agent.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{agent.type}</p>
                  <p className="text-gray-700 mt-3 text-sm">{agent.description}</p>

                  {agent.capabilities && agent.capabilities.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Capabilities:</p>
                      <div className="flex flex-wrap gap-2">
                        {agent.capabilities.slice(0, 3).map((cap, idx) => (
                          <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            {cap}
                          </span>
                        ))}
                        {agent.capabilities.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{agent.capabilities.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {agent.current_task && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-900">Current Task</p>
                      <p className="text-sm text-blue-700">{agent.current_task}</p>
                    </div>
                  )}

                  {agent.last_activity && (
                    <p className="text-xs text-gray-500 mt-4">
                      Last activity: {new Date(agent.last_activity).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showIntelligentModal && (
        <IntelligentAgentModal
          onClose={() => setShowIntelligentModal(false)}
          onSuccess={() => {
            setShowIntelligentModal(false)
            queryClient.invalidateQueries(['agents'])
          }}
        />
      )}

      {showRegisterModal && (
        <RegisterAgentModal
          onClose={() => setShowRegisterModal(false)}
          onSuccess={() => {
            setShowRegisterModal(false)
            queryClient.invalidateQueries(['agents'])
          }}
        />
      )}
    </div>
  )
}

function IntelligentAgentModal({ onClose, onSuccess }) {
  const [description, setDescription] = useState('')
  const [requirements, setRequirements] = useState('')
  const [createdAgent, setCreatedAgent] = useState(null)

  const createMutation = useMutation({
    mutationFn: (data) => {
      const reqs = data.requirements
        ? data.requirements.split('\n').map(r => r.trim()).filter(Boolean)
        : []

      return agentsAPI.createIntelligent({
        description: data.description,
        ...(reqs.length > 0 && { requirements: reqs })
      })
    },
    onSuccess: (response) => {
      setCreatedAgent(response.data)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    setCreatedAgent(null)
    createMutation.mutate({ description, requirements })
  }

  const handleClose = () => {
    if (createdAgent) {
      onSuccess()
    } else {
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Sparkles size={24} className="text-purple-600" />
            <h3 className="text-2xl font-bold text-gray-900">Create Intelligent Agent</h3>
          </div>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        {!createdAgent ? (
          <>
            <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="text-sm text-purple-900 font-medium">Powered by Gemini AI</p>
              <p className="text-sm text-purple-700 mt-1">
                Describe what you want your agent to do in plain English. Gemini will automatically generate the agent profile, assign relevant skills, and create starter code templates.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">What should this agent do? *</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input"
                  rows={4}
                  placeholder="Example: I need an agent that analyzes satellite imagery for wildfire detection and predicts fire spread patterns"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">Be as specific as possible about the agent's purpose and capabilities</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Specific Requirements (optional)</label>
                <textarea
                  value={requirements}
                  onChange={(e) => setRequirements(e.target.value)}
                  className="input"
                  rows={3}
                  placeholder={"Must use Python\nShould integrate with NASA FIRMS data\nGenerate PDF reports with visualizations"}
                />
                <p className="text-xs text-gray-500 mt-1">One requirement per line (optional but helps create better agents)</p>
              </div>

              {createMutation.isError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    Error: {createMutation.error?.response?.data?.detail || createMutation.error?.message || 'Failed to create agent'}
                  </p>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
                  {createMutation.isPending ? (
                    <span className="flex items-center gap-2 justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Creating with Gemini AI...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2 justify-center">
                      <Sparkles size={16} />
                      Create Intelligent Agent
                    </span>
                  )}
                </button>
                <button type="button" onClick={onClose} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="space-y-6">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-900 font-medium">Agent Created Successfully!</p>
              <p className="text-sm text-green-700 mt-1">{createdAgent.message}</p>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Agent Details</h4>
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div><span className="font-medium">Name:</span> {createdAgent.agent.name}</div>
                  <div><span className="font-medium">Type:</span> {createdAgent.agent.type}</div>
                  <div><span className="font-medium">Specialization:</span> {createdAgent.agent.specialization}</div>
                  <div><span className="font-medium">Evolution Stage:</span> {createdAgent.agent.evolution_stage}</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Generated Skills</h4>
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-blue-50 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-900">{createdAgent.skills_created.technical}</div>
                    <div className="text-sm text-blue-700">Technical Skills</div>
                  </div>
                  <div className="bg-purple-50 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-900">{createdAgent.skills_created.domain}</div>
                    <div className="text-sm text-purple-700">Domain Skills</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-900">{createdAgent.skills_created.templates}</div>
                    <div className="text-sm text-green-700">Code Templates</div>
                  </div>
                </div>
                <div className="mt-2 text-center">
                  <span className="text-sm text-gray-600">
                    Total: <span className="font-semibold">{createdAgent.skills_created.total} skills</span> created automatically
                  </span>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button onClick={handleClose} className="btn-primary flex-1">
                  View Agent
                </button>
                <button
                  onClick={() => {
                    setCreatedAgent(null)
                    setDescription('')
                    setRequirements('')
                  }}
                  className="btn-secondary"
                >
                  Create Another
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function RegisterAgentModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'development',
    specialization: '',
    capabilities: '',
    config: '{}',
    prompt_file: '',
  })

  const createMutation = useMutation({
    mutationFn: (data) => {
      // Parse capabilities from comma-separated string
      const capabilities = data.capabilities
        ? data.capabilities.split(',').map(c => c.trim()).filter(Boolean)
        : []

      // Parse config JSON
      let config = {}
      try {
        config = data.config ? JSON.parse(data.config) : {}
      } catch (e) {
        throw new Error('Invalid JSON in config field')
      }

      return agentsAPI.create({
        name: data.name,
        type: data.type,
        specialization: data.specialization,
        capabilities,
        config,
        prompt_file: data.prompt_file || null,
      })
    },
    onSuccess,
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">Register New Agent</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              placeholder="e.g., Code Quality Agent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="input"
              required
            >
              <option value="development">Development</option>
              <option value="domain_specialist">Domain Specialist</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="research">Research</option>
              <option value="general">General</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Specialization *</label>
            <input
              type="text"
              value={formData.specialization}
              onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
              className="input"
              placeholder="e.g., Code review and quality assurance"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Capabilities</label>
            <input
              type="text"
              value={formData.capabilities}
              onChange={(e) => setFormData({ ...formData, capabilities: e.target.value })}
              className="input"
              placeholder="e.g., code review, testing, linting (comma-separated)"
            />
            <p className="text-xs text-gray-500 mt-1">Enter capabilities separated by commas</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Prompt File Path</label>
            <input
              type="text"
              value={formData.prompt_file}
              onChange={(e) => setFormData({ ...formData, prompt_file: e.target.value })}
              className="input"
              placeholder="e.g., /app/.agents/code-quality-agent.txt"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Config (JSON)</label>
            <textarea
              value={formData.config}
              onChange={(e) => setFormData({ ...formData, config: e.target.value })}
              className="input font-mono text-sm"
              rows={3}
              placeholder='{"key": "value"}'
            />
            <p className="text-xs text-gray-500 mt-1">Optional JSON configuration</p>
          </div>

          {createMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                Error: {createMutation.error?.response?.data?.detail || createMutation.error?.message || 'Failed to register agent'}
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Registering...' : 'Register Agent'}
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
