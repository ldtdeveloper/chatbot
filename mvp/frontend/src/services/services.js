import api from './api'

export const authService = {
  login: async (data) => {
    const response = await api.post('/api/auth/login', data)
    return response.data
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

export const userService = {
  list: async () => {
    const response = await api.get('/api/users')
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/users', data)
    return response.data
  },
  
  get: async (id) => {
    const response = await api.get(`/api/users/${id}`)
    return response.data
  },
  
  getProfile: async (id) => {
    const response = await api.get(`/api/users/${id}/profile`)
    return response.data
  },
  
  getUserWidgets: async (id) => {
    const response = await api.get(`/api/users/${id}/widgets`)
    return response.data
  },
  
  toggleActive: async (id) => {
    const response = await api.patch(`/api/users/${id}/toggle-active`)
    return response.data
  },
}

export const openAIKeyService = {
  list: async () => {
    const response = await api.get('/api/openai-keys')
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/openai-keys', data)
    return response.data
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/openai-keys/${id}`)
    return response.data
  },
  
  toggle: async (id) => {
    const response = await api.patch(`/api/openai-keys/${id}/toggle`)
    return response.data
  },
  
  getMasked: async (id) => {
    const response = await api.get(`/api/openai-keys/${id}/masked`)
    return response.data
  },
}

export const agentService = {
  list: async (openaiKeyId = null) => {
    const params = openaiKeyId ? { openai_key_id: openaiKeyId } : {}
    const response = await api.get('/api/agents', { params })
    return response.data
  },
  
  get: async (id) => {
    const response = await api.get(`/api/agents/${id}`)
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/agents', data)
    return response.data
  },
  
  update: async (id, data) => {
    const response = await api.put(`/api/agents/${id}`, data)
    return response.data
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/agents/${id}`)
    return response.data
  },
  
  generateWidgetCode: async (id) => {
    const response = await api.get(`/api/widget/code/agent/${id}`)
    return response.data
  },
}

export const assistantConfigService = {
  list: async () => {
    const response = await api.get('/api/assistants')
    return response.data
  },
  
  get: async (id) => {
    const response = await api.get(`/api/assistants/${id}`)
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/assistants', data)
    return response.data
  },
  
  update: async (id, data) => {
    const response = await api.put(`/api/assistants/${id}`, data)
    return response.data
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/assistants/${id}`)
    return response.data
  },
}

export const widgetService = {
  generateCode: async (assistantId) => {
    const response = await api.get(`/api/widget/code/${assistantId}`)
    return response.data
  },
}

