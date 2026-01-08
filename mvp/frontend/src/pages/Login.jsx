import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { authService, forgotPassword } from '../services/services'
import Toastify from "toastify-js";
import "toastify-js/src/toastify.css";
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
      Toastify({
          text: `Login successful`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#16a34a",
          style: {
              borderRadius: "10px",
              width : "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          },
      }).showToast();
      navigate('/')
    } catch (err) {
      Toastify({
          text: `Login failed`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width : "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
      // toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }


 const handleForgotPassword = async () => {
  if (!email) {
    Toastify({
          text: `Please enter your email first`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width : "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
    return
  }

  setLoading(true)
  setCooldown(true)

  try {
    await forgotPassword.forgotPassword({ email })

  
    // toast.dismiss(toastId)
    Toastify({
          text: `Reset Link has been sent to your registered email`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#16a34a",
          style: {
              borderRadius: "10px",
              width : "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();

    setTimeout(() => setCooldown(false), 60000)
  } catch (err) {
    Toastify({
          text: `Failed to send reset email`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width: "200",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
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
