// src/auth/bootstrapAuth.js
import { authService } from '../services/services'
import { agentAuthService } from '../services/agentAuth'
import { useAuthStore } from '../context/authStore'

export async function bootstrapAuth(setAuth) {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  
  if (!token) return
  
  let user = null
  try {
    user = userStr ? JSON.parse(userStr) : null
  } catch (e) {
    console.error("Failed to parse user from storage", e)
  }

  console.log("Bootstrap called for role:", user?.role || 'user')
  
  try {
    let userInfo
    if (user?.role === 'agent') {
      userInfo = await agentAuthService.getMe()
      // Always ensure role is preserved
      if (!userInfo.role) userInfo.role = 'agent'
    } else {
      userInfo = await authService.getMe()
    }
    setAuth(token, userInfo)
  } catch (error) {
    console.error("Bootstrap auth failed:", error)
    // Only remove if it's a real auth error, not a network error
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      setAuth(null, null)
    }
  }
}
