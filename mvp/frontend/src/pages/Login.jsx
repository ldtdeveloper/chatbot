import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { authService, forgotPassword } from '../services/services'
import { toast } from 'sonner'
import '../assets/Login.css'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [cooldown, setCooldown] = useState(false)

  const navigate = useNavigate()
  const { setAuth } = useAuthStore()


  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await authService.login({ email, password })
      setAuth(response.access_token, null)

      const userInfo = await authService.getMe()
      setAuth(response.access_token, userInfo)

      toast.success('Login successful')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }


 const handleForgotPassword = async () => {
  if (!email) {
    toast.error('Please enter your email first')
    return
  }

  setLoading(true)
  setCooldown(true)

 
  const toastId = toast.loading('Sending reset email...')

  try {
    await forgotPassword.forgotPassword({ email })

  
    toast.dismiss(toastId)

    toast.success(
      'Reset link has been sent. Please wait 1–2 minutes.'
    )

    setTimeout(() => setCooldown(false), 60000)
  } catch (err) {
    toast.dismiss(toastId)

    toast.error(err.response?.data?.detail || 'Failed to send reset email')
    setCooldown(false)
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Login</h1>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Please wait...' : 'Login'}
          </button>
        </form>


        <div className="forgot-password">
          <button
            type="button"
            className="link-button"
            onClick={handleForgotPassword}
            disabled={loading || cooldown}
          >
            {cooldown ? 'Try again in 1 min' : 'Forgot password?'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Login
