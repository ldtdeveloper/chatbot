import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assistantConfigService, promptService } from '../services/services'
import './AssistantConfig.css'

function AssistantConfig() {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({})

  const { data: config, isLoading: configLoading } = useQuery({
    queryKey: ['assistant-config'],
    queryFn: assistantConfigService.get,
  })

  const { data: prompts } = useQuery({
    queryKey: ['prompts'],
    queryFn: promptService.list,
  })

  const updateMutation = useMutation({
    mutationFn: assistantConfigService.update,
    onSuccess: () => {
      queryClient.invalidateQueries(['assistant-config'])
    },
  })

  React.useEffect(() => {
    if (config) {
      setFormData({
        prompt_id: config.prompt_id || '',
        prompt_version_id: config.prompt_version_id || '',
        voice: config.voice || 'alloy',
        noise_reduction_mode: config.noise_reduction_mode || 'near_field',
        noise_reduction_threshold: config.noise_reduction_threshold || '0.5',
        noise_reduction_prefix_padding_ms: config.noise_reduction_prefix_padding_ms || 300,
        noise_reduction_silence_duration_ms: config.noise_reduction_silence_duration_ms || 500,
      })
    }
  }, [config])

  const handleSubmit = (e) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  const selectedPrompt = prompts?.find((p) => p.id === formData.prompt_id)

  if (configLoading) return <div>Loading...</div>

  return (
    <div className="assistant-config">
      <h1>Assistant Configuration</h1>
      <form onSubmit={handleSubmit} className="config-form">
        <div className="form-section">
          <h2>Prompt Settings</h2>
          <div className="form-group">
            <label>Select Prompt</label>
            <select
              value={formData.prompt_id || ''}
              onChange={(e) =>
                setFormData({ ...formData, prompt_id: parseInt(e.target.value) || null })
              }
            >
              <option value="">None</option>
              {prompts?.map((prompt) => (
                <option key={prompt.id} value={prompt.id}>
                  {prompt.name}
                </option>
              ))}
            </select>
          </div>

          {selectedPrompt && (
            <div className="form-group">
              <label>Prompt Version</label>
              <select
                value={formData.prompt_version_id || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    prompt_version_id: parseInt(e.target.value) || null,
                  })
                }
              >
                <option value="">Latest</option>
                {selectedPrompt.versions?.map((version) => (
                  <option key={version.id} value={version.id}>
                    Version {version.version_number}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="form-section">
          <h2>Voice Settings</h2>
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
        </div>

        <div className="form-section">
          <h2>Noise Reduction</h2>
          <div className="form-group">
            <label>Mode</label>
            <select
              value={formData.noise_reduction_mode}
              onChange={(e) =>
                setFormData({ ...formData, noise_reduction_mode: e.target.value })
              }
            >
              <option value="near_field">Near Field</option>
              <option value="far_field">Far Field</option>
            </select>
          </div>
          <div className="form-group">
            <label>Threshold</label>
            <input
              type="text"
              value={formData.noise_reduction_threshold}
              onChange={(e) =>
                setFormData({ ...formData, noise_reduction_threshold: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label>Prefix Padding (ms)</label>
            <input
              type="number"
              value={formData.noise_reduction_prefix_padding_ms}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  noise_reduction_prefix_padding_ms: parseInt(e.target.value),
                })
              }
            />
          </div>
          <div className="form-group">
            <label>Silence Duration (ms)</label>
            <input
              type="number"
              value={formData.noise_reduction_silence_duration_ms}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  noise_reduction_silence_duration_ms: parseInt(e.target.value),
                })
              }
            />
          </div>
        </div>

        <button type="submit" disabled={updateMutation.isLoading}>
          {updateMutation.isLoading ? 'Saving...' : 'Save Configuration'}
        </button>
      </form>
    </div>
  )
}

export default AssistantConfig

