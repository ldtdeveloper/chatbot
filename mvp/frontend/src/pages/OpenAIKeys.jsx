import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { openAIKeyService } from '../services/services'
import './OpenAIKeys.css'

function OpenAIKeys() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({ key_name: '', api_key: '' })
  const [visibleKeys, setVisibleKeys] = useState({}) // Track which keys are visible
  const [maskedKeys, setMaskedKeys] = useState({}) // Cache masked keys

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

  const toggleKeyVisibility = async (keyId) => {
    if (visibleKeys[keyId]) {
      // Hide the key
      setVisibleKeys(prev => ({ ...prev, [keyId]: false }))
    } else {
      // Show the key - fetch masked version if not cached
      if (!maskedKeys[keyId]) {
        try {
          const data = await openAIKeyService.getMasked(keyId)
          setMaskedKeys(prev => ({ ...prev, [keyId]: data.masked_key }))
        } catch (error) {
          console.error('Error fetching masked key:', error)
          return
        }
      }
      setVisibleKeys(prev => ({ ...prev, [keyId]: true }))
    }
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
            onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
            autoComplete="off"
            required
          />
          <input
            type="password"
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            autoComplete="off"
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
              {visibleKeys[key.id] && (
                <div className="masked-key">
                  <code>{maskedKeys[key.id] || 'Loading...'}</code>
                </div>
              )}
            </div>
            <div className="key-actions">
              <button
                onClick={() => toggleKeyVisibility(key.id)}
                className="view-key-btn"
              >
                {visibleKeys[key.id] ? 'Hide Key' : 'View Key'}
              </button>
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

