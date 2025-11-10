import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('token') || null,
  user: (() => {
    try {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })(),
  setAuth: (token, user) => {
    if (token) {
      localStorage.setItem('token', token)
    }
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
    set({ token: null, user: null })
  },
}))

