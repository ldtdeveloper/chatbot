import React, { useState, useRef, useEffect } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import './Layout.css'

function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>🎙️ Voice Assistant Platform</h1>
        </div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>
          {user?.role === 'default' && <Link to="/assistants">Assistants</Link>}
          <Link to="/openai-keys">API Keys</Link>
          <Link to="/agents">Agents</Link>
          {user?.role === 'default' && <Link to="/widget-generator">Widget</Link>}
          <div className="navbar-user" ref={dropdownRef}>
            <button 
              className="navbar-user-toggle"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <span>{user?.username || 'User'}</span>
              {user?.role === 'superadmin' && <span className="role-badge">Admin</span>}
              <span className="dropdown-arrow">▼</span>
            </button>
            {dropdownOpen && (
              <div className="dropdown-menu">
                {user?.role === 'superadmin' && (
                  <Link to="/users" onClick={() => setDropdownOpen(false)}>
                    Manage Users
                  </Link>
                )}
                <button onClick={handleLogout}>Logout</button>
              </div>
            )}
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

