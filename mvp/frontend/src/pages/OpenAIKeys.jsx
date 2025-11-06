import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { openAIKeyService } from '../services/services'
import './OpenAIKeys.css'

function OpenAIKeys() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({ key_name: '', api_key: '' })

  const { data: keys, isLoading } = useQuery({
    queryKey: ['openai-keys'],
    queryFn: openAIKeyService.list,
  })

  const createMutation = useMutation({
    mutationFn: openAIKeyService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['openai-keys'])
      setShowAddForm(false)
      setFormData({ key_name: '', api_key: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: openAIKeyService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['openai-keys'])
    },
  })

  const toggleMutation = useMutation({
    mutationFn: openAIKeyService.toggle,
    onSuccess: () => {
      queryClient.invalidateQueries(['openai-keys'])
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="openai-keys">
      <div className="page-header">
        <h1>OpenAI API Keys</h1>
        <button onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : '+ Add Key'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="add-key-form">
          <input
            type="text"
            placeholder="Key Name"
            value={formData.key_name}
            onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="API Key"
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            required
          />
          <button type="submit">Add Key</button>
        </form>
      )}

      <div className="keys-list">
        {keys?.map((key) => (
          <div key={key.id} className="key-card">
            <div className="key-info">
              <h3>{key.key_name}</h3>
              <span className={`status ${key.is_active ? 'active' : 'inactive'}`}>
                {key.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="key-actions">
              <button onClick={() => toggleMutation.mutate(key.id)}>
                {key.is_active ? 'Deactivate' : 'Activate'}
              </button>
              <button
                onClick={() => deleteMutation.mutate(key.id)}
                className="delete-btn"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {keys?.length === 0 && <p>No API keys added yet.</p>}
      </div>
    </div>
  )
}

export default OpenAIKeys

