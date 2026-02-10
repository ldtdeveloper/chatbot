// src/auth/bootstrapAuth.js
import { authService } from '../services/services'
import { useAuthStore } from '../context/authStore'

export async function bootstrapAuth(setAuth) {
  const token = localStorage.getItem('token')
  if (!token) return
  console.log("Bootstap called ..........")
  try {
    const userInfo = await authService.getMe()
    setAuth(token, userInfo)
  } catch {
    localStorage.removeItem('token')
    setAuth(null, null)
  }
}
