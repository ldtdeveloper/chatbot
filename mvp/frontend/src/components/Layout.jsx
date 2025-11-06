import React from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import './Layout.css'

function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>🎙️ Voice Assistant Platform</h1>
        </div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>
          <Link to="/openai-keys">API Keys</Link>
          <Link to="/prompts">Prompts</Link>
          <Link to="/assistant-config">Settings</Link>
          <Link to="/widget-generator">Widget</Link>
          <div className="navbar-user">
            <span>{user?.username || 'User'}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

