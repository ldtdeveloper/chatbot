import api from './api'

export const agentAuthService = {
  getOwnerInfo: async (username) => {
    const response = await api.get(`/human-agent/owner-info/${username}`)
    return response.data
  },

  sendOtp: async (email, slug) => {
    const response = await api.post('/human-agent/send-otp', { email, slug })
    return response.data
  },

  verifyOtp: async (data, slug) => {
    const response = await api.post('/human-agent/verify-otp', { ...data, slug })
    return response.data
  },

  getMe: async () => {
    const response = await api.get('/human-agent/me')
    return response.data
  }
}
