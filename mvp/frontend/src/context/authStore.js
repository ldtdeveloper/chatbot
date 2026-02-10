import { create } from 'zustand'

// Helper to get initial token from localStorage
const getInitialToken = () => {
  return localStorage.getItem('token') || null
}

// Helper to get initial user from localStorage
const getInitialUser = () => {
  try {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

export const useAuthStore = create((set, get) => ({
  token: getInitialToken(),
  user: getInitialUser(),
  setAuth: (token, user) => {
    if (token) {
      localStorage.setItem('token', token)
      console.log("token set ")
    }
    console.log(`No token ${token}`)
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
      set({ token, user })
    } else if (token) {
      // Update token only if user is null
      set({ token })
    }
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('subscription_active')
    localStorage.removeItem('subscription_plan')
    set({ token: null, user: null })
  },
  // Method to refresh token from localStorage (useful after redirect)
  refreshAuth: () => {
    const token = getInitialToken()
    const user = getInitialUser()
    set({ token, user })
    return { token, user }
  },
}))

