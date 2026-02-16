import React, { useState, useRef, useEffect } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import WalletModal from './WalletModal'
import PlansPopup from './PlansPopup'
import '../styles/Layout.css'
import logoIcon from '../assets/logo.png';

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
 
  const isTrial =user?.subscription_mode=== 'trial' 
 
  const displayedBalance=user?.remaining_minutes
  console.log(displayedBalance)

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
        {/* <div className="navbar-brand">
          <img src={logoIcon} alt="icon" style={{width:"auto", height:"auto"}}/><h1>Voice Assistant Platform</h1>
        </div> */}
        <div
  style={{
    display: "flex",
    alignItems: "center",
    gap: "12px", // gap-3 → 0.75rem → 12px
  }}
>
  <img
    src={logoIcon}
    alt="Logo"
    style={{
      width: "70px",  // w-10
      height: "50px", // h-10
    }}
  />
  <h1
    style={{
      margin: 0,               // m-0
      fontSize: "1.5rem",      // text-2xl
      fontWeight: 600,         // font-semibold
    }}
  >
    Voice Assistant Platform
  </h1>
</div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>

          {user?.role === 'superadmin' && <Link to="/openai-keys">API Keys</Link>}

          {user?.role === 'default' && (
            <>
              <Link to="/agents">Agents</Link>

              {/* Show Upgrade button only for trial users */}
              {isTrial && (
                <button
                  className="upgrade-btn"
                  onClick={() => setShowUpgradeModal(true)}
                >
                  Upgrade Now
                </button>
              )}
            </>
          )}

          {/* Wallet Section */}
          {user?.role !== 'superadmin' && (
            <div className="wallet-wrapper" ref={walletRef}>
              <button
                className={`wallet-icon-btn ${isTrial ? 'wallet-trial-limited' : ''}`}
                onMouseEnter={() => isTrial && setShowWalletMessage(true)}
                onMouseLeave={() => isTrial && setShowWalletMessage(false)}
                // onClick={() => !isTrial && setWalletModalOpen(true)

                // }
                disabled={isTrial}
                title={
                  isTrial
                    ? 'Trial  limited to 50 minutes – Upgrade to unlock full access'
                    : `Wallet: $${displayedBalance}`
                }
              >
                <span className="wallet-amount-text">
                  🕒{displayedBalance}
                  {isTrial && <small className="trial-hint"> trial</small>}
                </span>
              </button>

              {/* Hover message for trial */}
              {isTrial && showWalletMessage && (
                <div className="wallet-message-card">
                  <h4>Trial Wallet Limited</h4>
                  <p>Fixed at 50 minutes during trial. Upgrade to unlock full features.</p>
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

          {/* User Dropdown */}
          <div className="navbar-user" ref={dropdownRef}>
            <button
              className="navbar-user-toggle"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <span>{user?.username || 'User'}</span>
              {isTrial && <span className="role-badge trial">TRIAL</span>}
              <span className="dropdown-arrow">▼</span>
            </button>

            {dropdownOpen && (
              <div className="dropdown-menu">
                {user?.role != 'superadmin' && (
                <Link to={`/users/${user?.id}/profile-update`}>
                  Edit Profile
                </Link>
                )}

                {user?.role === 'superadmin' && (
                  <>
                    <Link to="/users" onClick={() => setDropdownOpen(false)}>
                      Manage Users
                    </Link>
                    <Link to="/plans" onClick={() => setDropdownOpen(false)}>
                      Manage Plans
                    </Link>
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

      {/* Modals */}
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
