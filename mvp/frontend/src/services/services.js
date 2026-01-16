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
  
  // Get basic user info
  get: async (id) => {
    const response = await api.get(`/api/users/${id}`)
    return response.data
  },
  
  // Get full user profile with agents, assistants, keys
  getProfile: async (id) => {
    console.log("get in the get user profiles"+id)
    const response = await api.get(`/api/users/${id}/profile`)
   console.log(response)
    return response.data
  },
  
  
  updateProfile: async (id, data) => {
    const response = await api.patch(`/api/users/${id}`, data)
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
export const forgotPassword={
forgotPassword:async(data)=>{
  const response= await api.post(`/api/auth/forget-password`,data)
  return response.data
}
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
    return response
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/agents/${id}`)
    return response.data
  },
  
  generateWidgetCode: async (id) => {
    const response = await api.get(`/api/widget/code/agent/${id}`)
    return response.data
  },
  generateWidgetCodeFixed: async (id) => {
    const response = await api.get(`/api/widget/codeFixed/agent/${id}`)
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

export const dashboardService = {
  getStats: async (days = '30d', keyId = null) => {
    const params = { days }
    if (keyId && keyId !== 'all') {
      params.key_id = keyId
    }
    const response = await api.get('/api/dashboard/stats', { params })
    console.log(response.data)
    return response.data
  },
  getExpensesPerUser: async (days = '30d') => {
    const response = await api.get('/api/dashboard/expenses-per-user', { params: { days } })
    return response.data
  },
  sendExpensesReportEmail: async (days = '30d') => {
    const response = await api.post('/api/dashboard/expenses-per-user/send-email', null, { params: { days } })
    return response.data
  },
}

export const integrationConfigService = {
   list: async (id) => {
    const response = await api.get('/api/integration-config', {
      params: { agent_id: id }
    })
    return response.data
  },
  
  create: async (data) => {
    const response = await api.post('/api/integration-config', data)
    return response.data
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/integration-config/${id}`)
    return response.data
  },

  update: async (id, data) => {
    const response = await api.put(`/api/integration-config/${id}`, data)
    return response.data
  },

  getDecryptedKey: async (id) => {
    const response = await api.get(`/api/integration-config/${id}/decrypted-key`)
    return response.data
  },

  // HubSpot OAuth endpoints
  getHubSpotOAuthUrl: async (agentId) => {
    const response = await api.get('/api/integration-config/hubspot/oauth/install-url', {
      params: { agent_id: agentId }
    })
    return response.data
  },

  refreshHubSpotToken: async (agentId) => {
    const response = await api.post('/api/integration-config/hubspot/oauth/refresh', null, {
      params: { agent_id: agentId }
    })
    return response.data
  },

  disconnectHubSpotOAuth: async (agentId) => {
    const response = await api.post('/api/integration-config/hubspot/oauth/disconnect', null, {
      params: { agent_id: agentId }
    })
    return response.data
  },
}
// export const serviceAccount={
//  createServiceAccount : async (id)=>{
//   const response = await api.post('/api/serviceAccount/create-service-account')
//   return response.data
//  }

// }

export const serviceAccountService  = {
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

export const resetPasswordService = {
    resetPassword: async (token,password) => {
    const response = await api.post('/api/auth/reset-password',{ new_password: password},{headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        }})
    return response.data
  }
}

export const userCreate = {
  createUser: async (data, token) => {
    const response = await api.post(
      '/api/auth/register-with-plan',
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
    return response.data
  },
}