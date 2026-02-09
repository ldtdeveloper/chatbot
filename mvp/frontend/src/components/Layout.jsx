// src/components/Layout.jsx
import React, { useState, useRef, useEffect } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import WalletModal from './WalletModal'
import PlansPopup from './PlansPopup'
import '../styles/Layout.css'

function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [walletModalOpen, setWalletModalOpen] = useState(false)
  const [showWalletMessage, setShowWalletMessage] = useState(false)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)

  const dropdownRef = useRef(null)
  const walletRef = useRef(null)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isTrial = user?.is_trial === true
  const displayedBalance = isTrial ? 2.0 : (user?.wallet_balance ?? 0)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
      if (walletRef.current && !walletRef.current.contains(e.target)) {
        setShowWalletMessage(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>🎙️ Voice Assistant Platform</h1>
        </div>

        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>

          {user?.role === 'superadmin' && (
            <Link to="/openai-keys">API Keys</Link>
          )}

          {user?.role === 'default' && (
            <>
              <Link to="/agents">Agents</Link>

              {/* ✅ UPGRADE BUTTON — AGENTS KE BAAD */}
              {isTrial && (
                <button
                  className="upgrade-btn"
                  onClick={() => setShowUpgradeModal(true)}
                >
                  Upgrade
                </button>
              )}
            </>
          )}

          {/* WALLET */}
          {user?.role !== 'superadmin' && (
            <div className="wallet-wrapper" ref={walletRef}>
              <button
                className={`wallet-icon-btn ${isTrial ? 'wallet-trial-limited' : ''}`}
                onMouseEnter={() => isTrial && setShowWalletMessage(true)}
                onMouseLeave={() => isTrial && setShowWalletMessage(false)}
                onClick={() => !isTrial && setWalletModalOpen(true)}
                disabled={isTrial}
              >
                <span className="wallet-amount-text">
                  ${displayedBalance.toFixed(2)}
                  {isTrial && <small className="trial-hint"> trial</small>}
                </span>
              </button>

              {isTrial && showWalletMessage && (
                <div className="wallet-message-card">
                  <h4>Trial Wallet</h4>
                  <p>Limited to $2.00. Upgrade to unlock full wallet.</p>
                  <button
                    className="upgrade-from-wallet-btn"
                    onClick={() => setShowUpgradeModal(true)}
                  >
                    Upgrade Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* USER DROPDOWN */}
          <div className="navbar-user" ref={dropdownRef}>
            <button
              className="navbar-user-toggle"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <span>{user?.username}</span>
              {isTrial && <span className="role-badge trial">TRIAL</span>}
              <span className="dropdown-arrow">▼</span>
            </button>

            {dropdownOpen && (
              <div className="dropdown-menu">
                <Link to={`/users/${user?.id}/profile-update`}>
                  Edit Profile
                </Link>

                {user?.role === 'superadmin' && (
                  <>
                    <Link to="/users">Manage Users</Link>
                    <Link to="/plans">Manage Plans</Link>
                  </>
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
      />

      <PlansPopup
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
      />
    </div>
  )
}

export default Layout
