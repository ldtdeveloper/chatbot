import axios from 'axios'
import config from '../config/env'

const api = axios.create({
  baseURL: config.API_BASE_URL,

  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((requestConfig) => {
  const token = localStorage.getItem('token')
  if (token) {
    requestConfig.headers.Authorization = `Bearer ${token}`
  }
  return requestConfig
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    // Handle payment required (402) - don't redirect, let components handle it
    if (error.response?.status === 402) {
      // Payment required - components will handle this
      console.warn('Payment required:', error.response?.data?.detail)
    }
    return Promise.reject(error)
  }
)

export default api

