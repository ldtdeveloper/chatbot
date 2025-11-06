import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assistantConfigService, agentService, widgetService } from '../services/services'
import { useAuthStore } from '../context/authStore'
import './Assistants.css'

function Assistants() {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedAssistant, setSelectedAssistant] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    agent_id: '',
    voice: 'alloy',
    noise_reduction_mode: 'near_field',
    noise_reduction_threshold: '0.5',
    noise_reduction_prefix_padding_ms: 300,
    noise_reduction_silence_duration_ms: 500,
  })

  const { data: assistants, isLoading } = useQuery({
    queryKey: ['assistants'],
    queryFn: assistantConfigService.list,
  })

  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentService.list(),
  })

  const createMutation = useMutation({
    mutationFn: assistantConfigService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['assistants'])
      setShowAddForm(false)
      setFormData({
        name: '',
        agent_id: '',
        voice: 'alloy',
        noise_reduction_mode: 'near_field',
        noise_reduction_threshold: '0.5',
        noise_reduction_prefix_padding_ms: 300,
        noise_reduction_silence_duration_ms: 500,
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: assistantConfigService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['assistants'])
      setSelectedAssistant(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const selectedAgent = agents?.find((a) => a.id === parseInt(formData.agent_id))

  if (isLoading) return <div>Loading...</div>

  // Only default users can access this page
  if (user?.role === 'superadmin') {
    return <div>Superadmins should use the Users page to view assistants.</div>
  }

  return (
    <div className="assistants">
      <div className="page-header">
        <h1>My Assistant Chatbots</h1>
        <button onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : '+ Create Assistant'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="add-assistant-form">
          <h2>Create New Assistant</h2>
          <div className="form-row">
            <div className="form-group">
              <label>Assistant Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Customer Support Bot"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Select Agent Configuration (Optional)</label>
              <select
                value={formData.agent_id}
                onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
              >
                <option value="">None - Use default settings</option>
                {agents?.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </select>
              {agents?.length === 0 && (
                <p className="form-hint">No agents created yet. Create an agent in the Agents page first.</p>
              )}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Voice</label>
              <select
                value={formData.voice}
                onChange={(e) => setFormData({ ...formData, voice: e.target.value })}
              >
                <option value="alloy">Alloy</option>
                <option value="echo">Echo</option>
                <option value="fable">Fable</option>
                <option value="onyx">Onyx</option>
                <option value="nova">Nova</option>
                <option value="shimmer">Shimmer</option>
              </select>
            </div>

            <div className="form-group">
              <label>Noise Reduction Mode</label>
              <select
                value={formData.noise_reduction_mode}
                onChange={(e) => setFormData({ ...formData, noise_reduction_mode: e.target.value })}
              >
                <option value="near_field">Near Field</option>
                <option value="far_field">Far Field</option>
              </select>
            </div>
          </div>

          {createMutation.error && (
            <div className="error">
              {createMutation.error.response?.data?.detail || 'Failed to create assistant'}
            </div>
          )}
          <button type="submit" disabled={createMutation.isLoading}>
            {createMutation.isLoading ? 'Creating...' : 'Create Assistant'}
          </button>
        </form>
      )}

      <div className="assistants-list">
        {assistants?.map((assistant) => (
          <AssistantCard
            key={assistant.id}
            assistant={assistant}
            onSelect={setSelectedAssistant}
            onDelete={deleteMutation.mutate}
            isSelected={selectedAssistant?.id === assistant.id}
          />
        ))}
        {assistants?.length === 0 && <p>No assistants created yet. Create your first assistant chatbot!</p>}
      </div>

      {selectedAssistant && (
        <AssistantDetails
          assistant={selectedAssistant}
          onClose={() => setSelectedAssistant(null)}
        />
      )}
    </div>
  )
}

function AssistantCard({ assistant, onSelect, onDelete, isSelected }) {
  return (
    <div
      className={`assistant-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(assistant)}
    >
      <div className="assistant-header">
        <h3>{assistant.name}</h3>
        <button
          onClick={(e) => {
            e.stopPropagation()
            if (window.confirm('Are you sure you want to delete this assistant?')) {
              onDelete(assistant.id)
            }
          }}
          className="delete-btn"
        >
          Delete
        </button>
      </div>
      <div className="assistant-meta">
        <span>Voice: {assistant.voice}</span>
        <span>Created: {new Date(assistant.created_at).toLocaleDateString()}</span>
      </div>
    </div>
  )
}

function AssistantDetails({ assistant, onClose }) {
  const [copied, setCopied] = useState(false)
  const { data: widgetData, isLoading: widgetLoading } = useQuery({
    queryKey: ['widget-code', assistant.id],
    queryFn: () => widgetService.generateCode(assistant.id),
    enabled: !!assistant.id,
  })

  const handleCopy = () => {
    if (widgetData?.widget_code) {
      navigator.clipboard.writeText(widgetData.widget_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="assistant-details-overlay" onClick={onClose}>
      <div className="assistant-details" onClick={(e) => e.stopPropagation()}>
        <div className="details-header">
          <h2>{assistant.name}</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="details-content">
          <div className="detail-section">
            <h3>Configuration</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Voice:</label>
                <span>{assistant.voice}</span>
              </div>
              <div className="detail-item">
                <label>Noise Reduction:</label>
                <span>{assistant.noise_reduction_mode}</span>
              </div>
              <div className="detail-item">
                <label>Threshold:</label>
                <span>{assistant.noise_reduction_threshold}</span>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3>Widget Code</h3>
            {widgetLoading ? (
              <div>Generating widget code...</div>
            ) : widgetData ? (
              <>
                <div className="code-header">
                  <span>Copy this code to integrate on your website</span>
                  <button onClick={handleCopy} className="copy-btn">
                    {copied ? '✓ Copied!' : 'Copy Code'}
                  </button>
                </div>
                <pre className="widget-code">
                  <code>{widgetData.widget_code}</code>
                </pre>
                <div className="widget-info">
                  <p><strong>Widget ID:</strong> {widgetData.widget_id}</p>
                  <p><strong>Assistant ID:</strong> {widgetData.assistant_id}</p>
                </div>
              </>
            ) : (
              <div className="error">Failed to generate widget code. Please check your configuration.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Assistants

