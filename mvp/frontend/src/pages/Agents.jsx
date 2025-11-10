import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService, openAIKeyService } from '../services/services'
import './Agents.css'

function Agents() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showWidgetModal, setShowWidgetModal] = useState(false)
  const [editingAgent, setEditingAgent] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [selectedInstructionsAgent, setSelectedInstructionsAgent] = useState(null)
  const [selectedApiKeyId, setSelectedApiKeyId] = useState('')
  const [fetchApiKeyId, setFetchApiKeyId] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    instructions: '',
    voice: 'alloy',
    noise_reduction_mode: 'near_field',
    noise_reduction_threshold: '0.5',
    noise_reduction_prefix_padding_ms: 300,
    noise_reduction_silence_duration_ms: 500
  })
  const [selectedAgentForWidget, setSelectedAgentForWidget] = useState(null)
  const [widgetCode, setWidgetCode] = useState(null)
  const [copied, setCopied] = useState(false)

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents', fetchApiKeyId],
    queryFn: () => {
      if (!fetchApiKeyId) {
        return Promise.resolve([])
      }
      return agentService.list(parseInt(fetchApiKeyId))
    },
    enabled: !!fetchApiKeyId,
  })

  const { data: apiKeys, isLoading: keysLoading } = useQuery({
    queryKey: ['openai-keys'],
    queryFn: openAIKeyService.list,
  })

  const activeApiKeys = apiKeys?.filter(key => key.is_active) || []

  const createMutation = useMutation({
    mutationFn: agentService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setShowAddForm(false)
      handleCancelEdit()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => agentService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setEditingAgent(null)
      setShowEditModal(false)
      setSelectedAgent(null)
      handleCancelEdit()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: agentService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setSelectedAgent(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (editingAgent) {
      // Update existing agent
      if (!formData.instructions.trim()) {
        alert('Instructions are required')
        return
      }
      updateMutation.mutate({
        id: editingAgent.id,
        data: formData
      })
    } else {
      // Create new agent
      if (!selectedApiKeyId) {
        alert('Please select an API key')
        return
      }
      if (!formData.instructions.trim()) {
        alert('Instructions are required')
        return
      }
      createMutation.mutate({
        ...formData,
        openai_key_id: parseInt(selectedApiKeyId)
      })
    }
  }

  const handleEdit = (agent) => {
    setEditingAgent(agent)
    setFormData({
      name: agent.name,
      domain: agent.domain,
      instructions: agent.instructions,
      voice: agent.voice,
      noise_reduction_mode: agent.noise_reduction_mode,
      noise_reduction_threshold: agent.noise_reduction_threshold,
      noise_reduction_prefix_padding_ms: agent.noise_reduction_prefix_padding_ms,
      noise_reduction_silence_duration_ms: agent.noise_reduction_silence_duration_ms
    })
    setShowEditModal(true)
  }

  const handleGenerateWidget = async (agent) => {
    try {
      const data = await agentService.generateWidgetCode(agent.id)
      setWidgetCode(data.widget_code)
      setSelectedAgentForWidget(agent)
      setShowWidgetModal(true)
    } catch (error) {
      console.error('Error generating widget code:', error)
      alert('Failed to generate widget code: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleCopyWidgetCode = () => {
    if (widgetCode) {
      navigator.clipboard.writeText(widgetCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleCancelEdit = () => {
    setEditingAgent(null)
    setShowAddForm(false)
    setShowEditModal(false)
    setFormData({
      name: '',
      domain: '',
      instructions: '',
      voice: 'alloy',
      noise_reduction_mode: 'near_field',
      noise_reduction_threshold: '0.5',
      noise_reduction_prefix_padding_ms: 300,
      noise_reduction_silence_duration_ms: 500
    })
    setSelectedApiKeyId('')
  }

  // Auto-select first API key if none selected
  useEffect(() => {
    if (!fetchApiKeyId && activeApiKeys.length > 0) {
      setFetchApiKeyId(String(activeApiKeys[0].id))
    }
  }, [activeApiKeys, fetchApiKeyId])

  if (keysLoading) return <div>Loading...</div>

  // Check if user has active API keys
  if (activeApiKeys.length === 0) {
    return (
      <div className="agents">
        <div className="page-header">
          <h1>Agents</h1>
        </div>
        <div className="no-api-keys-message">
          <p>You must create an Open AI Api Key First</p>
        </div>
      </div>
    )
  }

  return (
    <div className="agents">
      <div className="page-header">
        <h1>Agents</h1>
        <div className="header-actions">
          <select
            value={fetchApiKeyId}
            onChange={(e) => {
              setFetchApiKeyId(e.target.value)
              queryClient.invalidateQueries(['agents'])
            }}
            className="api-key-selector"
            title="Select API Key to fetch agents"
            required
          >
            <option value="">Select API Key</option>
            {activeApiKeys.map((key) => (
              <option key={key.id} value={key.id}>
                {key.key_name}
              </option>
            ))}
          </select>
          <button onClick={() => {
            if (showAddForm) {
              handleCancelEdit()
            } else {
              setShowAddForm(true)
              setShowEditModal(false)
            }
          }}>
            {showAddForm ? 'Cancel' : '+ Create Agent'}
          </button>
        </div>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="add-agent-form">
          <div className="form-info">
            <p><strong>Note:</strong> Agent configurations are stored locally and will be used when making WebRTC calls to OpenAI Realtime API.</p>
          </div>
          <select
            value={selectedApiKeyId}
            onChange={(e) => setSelectedApiKeyId(e.target.value)}
            autoComplete="off"
            required
          >
            <option value="">Select API Key</option>
            {activeApiKeys.map((key) => (
              <option key={key.id} value={key.id}>
                {key.key_name}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Agent Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            autoComplete="off"
            required
          />
          <input
            type="text"
            placeholder="Domain (e.g., example.com)"
            value={formData.domain}
            onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            autoComplete="off"
            required
            pattern="^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
            title="Enter a valid TLD domain (e.g., example.com)"
          />
          <textarea
            placeholder="System Instructions *"
            value={formData.instructions}
            onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
            autoComplete="off"
            required
            rows={10}
          />
          <label>
            Assistant Voice:
            <select
              value={formData.voice}
              onChange={(e) => setFormData({ ...formData, voice: e.target.value })}
              autoComplete="off"
            >
              <option value="alloy">Alloy</option>
              <option value="ash">Ash</option>
              <option value="ballad">Ballad</option>
              <option value="cedar">Cedar</option>
              <option value="coral">Coral</option>
              <option value="echo">Echo</option>
              <option value="marin">Marin</option>
              <option value="sage">Sage</option>
              <option value="shimmer">Shimmer</option>
              <option value="verse">Verse</option>
            </select>
          </label>
          <label>
            Noise Reduction:
            <select
              value={formData.noise_reduction_mode}
              onChange={(e) => setFormData({ ...formData, noise_reduction_mode: e.target.value })}
              autoComplete="off"
            >
              <option value="near_field">Near Field</option>
              <option value="far_field">Far Field</option>
            </select>
          </label>
          <label>
            VAD Threshold:
            <input
              type="text"
              value={formData.noise_reduction_threshold}
              onChange={(e) => setFormData({ ...formData, noise_reduction_threshold: e.target.value })}
              autoComplete="off"
              placeholder="0.5"
            />
          </label>
          <label>
            Prefix Padding (ms):
            <input
              type="number"
              value={formData.noise_reduction_prefix_padding_ms}
              onChange={(e) => setFormData({ ...formData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 300 })}
              autoComplete="off"
              min="0"
            />
          </label>
          <label>
            Silence Duration (ms):
            <input
              type="number"
              value={formData.noise_reduction_silence_duration_ms}
              onChange={(e) => setFormData({ ...formData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 500 })}
              autoComplete="off"
              min="0"
            />
          </label>
          <button type="submit" disabled={createMutation.isLoading}>
            {createMutation.isLoading ? 'Creating...' : 'Create Agent'}
          </button>
        </form>
      )}

      <div className="agents-list">
        {isLoading ? (
          <div>Loading agents...</div>
        ) : agents?.length === 0 ? (
          <p>No agents created yet.</p>
        ) : (
          agents?.map((agent) => (
            <div
              key={agent.id}
              className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
              onClick={() => setSelectedAgent(agent)}
            >
              <div className="agent-card-header">
                <h3>{agent.name}</h3>
                <button
                  className="view-instructions-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedInstructionsAgent(agent)
                  }}
                  title="View Instructions"
                >
                  ℹ️
                </button>
              </div>
              <div className="agent-meta">
                <span><strong>Domain:</strong> {agent.domain}</span>
                <span>Voice: {agent.voice}</span>
                <span>Noise Reduction: {agent.noise_reduction_mode}</span>
              </div>
              {selectedAgent?.id === agent.id && (
                <div className="agent-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleGenerateWidget(agent)
                    }}
                    className="widget-btn"
                  >
                    Get Widget Code
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEdit(agent)
                    }}
                    className="edit-btn"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (window.confirm('Are you sure you want to delete this agent?')) {
                        deleteMutation.mutate(agent.id)
                      }
                    }}
                    className="delete-btn"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {selectedAgent && (
        <div className="agent-details">
          <h2>{selectedAgent.name} - Configuration</h2>
          <div className="agent-info">
            <div className="info-section">
              <h3>Settings</h3>
              <div className="settings-grid">
                <div><strong>Domain:</strong> {selectedAgent.domain}</div>
                <div><strong>Voice:</strong> {selectedAgent.voice}</div>
                <div><strong>Noise Reduction:</strong> {selectedAgent.noise_reduction_mode}</div>
                <div><strong>VAD Threshold:</strong> {selectedAgent.noise_reduction_threshold}</div>
                <div><strong>Prefix Padding:</strong> {selectedAgent.noise_reduction_prefix_padding_ms}ms</div>
                <div><strong>Silence Duration:</strong> {selectedAgent.noise_reduction_silence_duration_ms}ms</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editingAgent && (
        <div className="modal-overlay" onClick={() => handleCancelEdit()}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Agent: {editingAgent.name}</h3>
              <button className="modal-close" onClick={() => handleCancelEdit()}>×</button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleSubmit} className="add-agent-form">
                <input
                  type="text"
                  placeholder="Agent Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  autoComplete="off"
                  required
                />
                <input
                  type="text"
                  placeholder="Domain (e.g., example.com)"
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  autoComplete="off"
                  required
                  pattern="^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
                  title="Enter a valid TLD domain (e.g., example.com)"
                />
                <textarea
                  placeholder="System Instructions *"
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  autoComplete="off"
                  required
                  rows={10}
                />
                <label>
                  Assistant Voice:
                  <select
                    value={formData.voice}
                    onChange={(e) => setFormData({ ...formData, voice: e.target.value })}
                    autoComplete="off"
                  >
                    <option value="alloy">Alloy</option>
                    <option value="ash">Ash</option>
                    <option value="ballad">Ballad</option>
                    <option value="cedar">Cedar</option>
                    <option value="coral">Coral</option>
                    <option value="echo">Echo</option>
                    <option value="marin">Marin</option>
                    <option value="sage">Sage</option>
                    <option value="shimmer">Shimmer</option>
                    <option value="verse">Verse</option>
                  </select>
                </label>
                <label>
                  Noise Reduction:
                  <select
                    value={formData.noise_reduction_mode}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_mode: e.target.value })}
                    autoComplete="off"
                  >
                    <option value="near_field">Near Field</option>
                    <option value="far_field">Far Field</option>
                  </select>
                </label>
                <label>
                  VAD Threshold:
                  <input
                    type="text"
                    value={formData.noise_reduction_threshold}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_threshold: e.target.value })}
                    autoComplete="off"
                    placeholder="0.5"
                  />
                </label>
                <label>
                  Prefix Padding (ms):
                  <input
                    type="number"
                    value={formData.noise_reduction_prefix_padding_ms}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 300 })}
                    autoComplete="off"
                    min="0"
                  />
                </label>
                <label>
                  Silence Duration (ms):
                  <input
                    type="number"
                    value={formData.noise_reduction_silence_duration_ms}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 500 })}
                    autoComplete="off"
                    min="0"
                  />
                </label>
                <div className="form-actions">
                  <button type="button" onClick={() => handleCancelEdit()} className="cancel-btn">
                    Cancel
                  </button>
                  <button type="submit" disabled={updateMutation.isLoading}>
                    {updateMutation.isLoading ? 'Updating...' : 'Update Agent'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showWidgetModal && widgetCode && selectedAgentForWidget && (
        <div className="modal-overlay" onClick={() => setShowWidgetModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Widget Code - {selectedAgentForWidget.name}</h3>
              <button className="modal-close" onClick={() => setShowWidgetModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="widget-code-section">
                <div className="code-header">
                  <span>Copy this code to integrate the widget on <strong>{selectedAgentForWidget.domain}</strong></span>
                  <button onClick={handleCopyWidgetCode} className="copy-btn">
                    {copied ? '✓ Copied!' : 'Copy Code'}
                  </button>
                </div>
                <pre className="widget-code">
                  <code>{widgetCode}</code>
                </pre>
                <div className="widget-info">
                  <p><strong>Widget ID:</strong> {widgetCode.match(/widgetId\s*=\s*['"]([^'"]+)['"]/)?.[1] || 'N/A'}</p>
                  <p><strong>Agent ID:</strong> {selectedAgentForWidget.id}</p>
                  <p><strong>Domain:</strong> {selectedAgentForWidget.domain}</p>
                  <p className="widget-note"><strong>Note:</strong> This widget code should only be used on <strong>{selectedAgentForWidget.domain}</strong> or its subdomains.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedInstructionsAgent && (
        <div className="modal-overlay" onClick={() => setSelectedInstructionsAgent(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>System Instructions - {selectedInstructionsAgent.name}</h3>
              <button className="modal-close" onClick={() => setSelectedInstructionsAgent(null)}>×</button>
            </div>
            <div className="modal-body">
              <pre className="instructions-text">{selectedInstructionsAgent.instructions}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Agents

