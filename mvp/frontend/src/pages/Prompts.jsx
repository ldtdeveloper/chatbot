import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { promptService } from '../services/services'
import './Prompts.css'

function Prompts() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedPrompt, setSelectedPrompt] = useState(null)
  const [formData, setFormData] = useState({ name: '', description: '' })

  const { data: prompts, isLoading } = useQuery({
    queryKey: ['prompts'],
    queryFn: promptService.list,
  })

  const createMutation = useMutation({
    mutationFn: promptService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['prompts'])
      setShowAddForm(false)
      setFormData({ name: '', description: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: promptService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['prompts'])
      setSelectedPrompt(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="prompts">
      <div className="page-header">
        <h1>Prompts</h1>
        <button onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : '+ Create Prompt'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="add-prompt-form">
          <input
            type="text"
            placeholder="Prompt Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <button type="submit">Create</button>
        </form>
      )}

      <div className="prompts-list">
        {prompts?.map((prompt) => (
          <div
            key={prompt.id}
            className={`prompt-card ${selectedPrompt?.id === prompt.id ? 'selected' : ''}`}
            onClick={() => setSelectedPrompt(prompt)}
          >
            <h3>{prompt.name}</h3>
            {prompt.description && <p>{prompt.description}</p>}
            <div className="prompt-meta">
              <span>Version {prompt.current_version}</span>
              <span>{prompt.versions?.length || 0} versions</span>
            </div>
            {selectedPrompt?.id === prompt.id && (
              <div className="prompt-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteMutation.mutate(prompt.id)
                  }}
                  className="delete-btn"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
        {prompts?.length === 0 && <p>No prompts created yet.</p>}
      </div>

      {selectedPrompt && (
        <div className="prompt-details">
          <h2>{selectedPrompt.name} - Versions</h2>
          <PromptVersions prompt={selectedPrompt} />
        </div>
      )}
    </div>
  )
}

function PromptVersions({ prompt }) {
  const queryClient = useQueryClient()
  const [showAddVersion, setShowAddVersion] = useState(false)
  const [versionData, setVersionData] = useState({ system_instructions: '' })

  const createVersionMutation = useMutation({
    mutationFn: (data) => promptService.createVersion(prompt.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['prompts'])
      setShowAddVersion(false)
      setVersionData({ system_instructions: '' })
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createVersionMutation.mutate(versionData)
  }

  return (
    <div>
      <button onClick={() => setShowAddVersion(!showAddVersion)}>
        {showAddVersion ? 'Cancel' : '+ Add Version'}
      </button>

      {showAddVersion && (
        <form onSubmit={handleSubmit} className="add-version-form">
          <textarea
            placeholder="System Instructions"
            value={versionData.system_instructions}
            onChange={(e) => setVersionData({ system_instructions: e.target.value })}
            required
            rows={10}
          />
          <button type="submit">Create Version</button>
        </form>
      )}

      <div className="versions-list">
        {prompt.versions?.map((version) => (
          <div key={version.id} className="version-card">
            <h4>Version {version.version_number}</h4>
            <p>{version.system_instructions}</p>
            {version.is_active && <span className="badge">Active</span>}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Prompts

