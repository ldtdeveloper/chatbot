import React, { useState, useRef, useEffect } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import WalletModal from './WalletModal'
import '../styles/Layout.css';

function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [walletModalOpen, setWalletModalOpen] = useState(false)
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
          {/* {user?.role === 'default' && <Link to="/assistants">Assistants</Link>} */}
          {user?.role==="superadmin"&&<Link to="/openai-keys">API Keys</Link>}
          {/* <Link to="/openai-keys">API Keys</Link> */}
          {user?.role === 'default' && <Link to="/agents">Agents</Link>}
          {/* <Link to="/agents">Agents</Link> */}
          {/* {user?.role === 'default' && <Link to="/widget-generator">Widget</Link>} */}

          {user?.role !== 'superadmin' && user?.wallet_balance !== undefined && (
            <button 
              className="wallet-icon-btn"
              onClick={() => setWalletModalOpen(true)}
              title={`Wallet Balance: $${user.wallet_balance.toFixed(2)}`}
            >
              <svg 
                className={`wallet-icon ${user.wallet_balance <= 2.0 ? 'low-balance' : ''}`}
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
                <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
                <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path>
              </svg>
              <span className="wallet-amount-text">
                ${user.wallet_balance.toFixed(2)}
              </span>
            </button>
          )}
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
                {/* Edit Profile - only for non-superadmin */}
                {user?.role !== 'superadmin' && (
                  <Link
                    to={`/users/${user.id}/profile-update`}
                    onClick={() => {
                      setDropdownOpen(false)
                    }}
                  >
                    Edit Profile
                  </Link>
                )}

                {/* Manage Users - only superadmin */}
                {user?.role === 'superadmin' && (
                  <Link to="/users" onClick={() => setDropdownOpen(false)}>
                    Manage Users
                  </Link>
                )}

                {/* Manage Plans - only superadmin */}
                {user?.role === 'superadmin' && (
                  <Link to="/plans" onClick={()=> setDropdownOpen(false)}>
                  Manage Plans
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

      <WalletModal 
        isOpen={walletModalOpen}
        onClose={() => setWalletModalOpen(false)}
        onWalletUpdate={(newBalance) => {
          // Wallet balance updated, modal will handle user refresh
        }}
      />
    </div>
  )
}

export default Layout
