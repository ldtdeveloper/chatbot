import api from './api'

export const authService = {
  register: async (data) => {
    const response = await api.post('/api/auth/register', data)
    return response.data
  },
  
  login: async (data) => {
    const response = await api.post('/api/auth/login', data)
    return response.data
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me')
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
}

export const promptService = {
  list: async () => {
    const response = await api.get('/api/prompts')
    return response.data
  },
  
  get: async (id) => {
    const response = await api.get(`/api/prompts/${id}`)
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/prompts', data)
    return response.data
  },
  
  createVersion: async (promptId, data) => {
    const response = await api.post(`/api/prompts/${promptId}/versions`, data)
    return response.data
  },
  
  updateVersion: async (promptId, versionId, data) => {
    const response = await api.put(`/api/prompts/${promptId}/versions/${versionId}`, data)
    return response.data
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/prompts/${id}`)
    return response.data
  },
}

export const assistantConfigService = {
  get: async () => {
    const response = await api.get('/api/assistant-config')
    return response.data
  },
  
  update: async (data) => {
    const response = await api.put('/api/assistant-config', data)
    return response.data
  },
}

export const widgetService = {
  generateCode: async () => {
    const response = await api.get('/api/widget/code')
    return response.data
  },
}

