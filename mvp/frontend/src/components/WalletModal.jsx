import React, { useState, useEffect } from 'react'
import { useAuthStore } from '../context/authStore'
import { authService, walletService } from '../services/services'
import { showError, showSuccess } from '../utils/toast'
import '../styles/WalletModal.css'

function WalletModal({ isOpen, onClose, onWalletUpdate }) {
  const { user, setAuth } = useAuthStore()
  const [amount, setAmount] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedAmount, setSelectedAmount] = useState(null)

  const quickAmounts = [10, 25, 50, 100, 250, 500]

  const handleQuickAmount = (value) => {
    setAmount(value.toString())
    setSelectedAmount(value)
  }

  const handleAmountChange = (e) => {
    const value = e.target.value
    // Allow only numbers and one decimal point
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmount(value)
      setSelectedAmount(null)
    }
  }

  // Load Razorpay SDK
  useEffect(() => {
    if (!window.Razorpay) {
      const script = document.createElement('script')
      script.src = 'https://checkout.razorpay.com/v1/checkout.js'
      script.async = true
      document.body.appendChild(script)
    }
  }, [])

  const handleAddMoney = async () => {
    const amountValue = parseFloat(amount)
    
    if (!amount || isNaN(amountValue) || amountValue <= 0) {
      showError('Please enter a valid amount')
      return
    }

    if (amountValue < 1) {
      showError('Minimum amount is $1.00')
      return
    }

    setIsProcessing(true)

    try {
      // Create Razorpay order for wallet top-up
      const orderData = await walletService.createTopUpOrder({ amount: amountValue })
      
      // Check if test mode
      if (orderData.razorpay_key_id === 'rzp_test_MOCK_KEY') {
        // Test mode - auto-verify payment
        const verifyResponse = await walletService.verifyTopUp({
          razorpay_order_id: orderData.razorpay_order_id,
          razorpay_payment_id: `pay_wallet_test_${orderData.transaction_id}`,
          razorpay_signature: 'test_signature',
          transaction_id: orderData.transaction_id
        })
        
        if (verifyResponse.success) {
          showSuccess(`Successfully added $${amountValue.toFixed(2)} to your wallet`)
          
          // Refresh user data
          const userInfo = await authService.getMe()
          setAuth(null, userInfo)
          
          if (onWalletUpdate) {
            onWalletUpdate(userInfo.wallet_balance)
          }
          
          setAmount('')
          setSelectedAmount(null)
          onClose()
        } else {
          showError(verifyResponse.message || 'Failed to add money to wallet')
        }
        setIsProcessing(false)
        return
      }

      // Production mode - Initialize Razorpay
      if (!window.Razorpay) {
        showError('Payment gateway is loading. Please try again in a moment.')
        setIsProcessing(false)
        return
      }

      const options = {
        key: orderData.razorpay_key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'VoiceAI Platform',
        description: `Wallet Top-up: $${amountValue.toFixed(2)}`,
        order_id: orderData.razorpay_order_id,
        handler: async function (response) {
          try {
            // Verify payment
            const verifyResponse = await walletService.verifyTopUp({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              transaction_id: orderData.transaction_id
            })
            
            if (verifyResponse.success) {
              showSuccess(`Successfully added $${amountValue.toFixed(2)} to your wallet`)
              
              // Refresh user data
              const userInfo = await authService.getMe()
              setAuth(null, userInfo)
              
              if (onWalletUpdate) {
                onWalletUpdate(userInfo.wallet_balance)
              }
              
              setAmount('')
              setSelectedAmount(null)
              onClose()
            } else {
              showError(verifyResponse.message || 'Payment verification failed')
            }
          } catch (error) {
            console.error('Payment verification error:', error)
            showError(error?.response?.data?.detail || 'Payment verification failed')
          } finally {
            setIsProcessing(false)
          }
        },
        prefill: {
          email: user?.email || '',
          name: user?.username || ''
        },
        theme: {
          color: '#667eea'
        },
        modal: {
          ondismiss: function () {
            setIsProcessing(false)
          }
        }
      }

      const razorpay = new window.Razorpay(options)
      razorpay.open()
      
    } catch (error) {
      console.error('Add money error:', error)
      showError(error?.response?.data?.detail || 'Failed to initiate payment. Please try again.')
      setIsProcessing(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="wallet-modal-overlay" onClick={onClose}>
      <div className="wallet-modal" onClick={(e) => e.stopPropagation()}>
        <div className="wallet-modal-header">
          <h2>💰 Manage Wallet</h2>
          <button className="wallet-modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="wallet-modal-content">
          <div className="wallet-current-balance">
            <span className="balance-label">Current Balance:</span>
            <span className={`balance-amount ${user?.wallet_balance <= 2.0 ? 'low-balance' : ''}`}>
              ${user?.wallet_balance?.toFixed(2) || '0.00'}
            </span>
          </div>

          <div className="wallet-add-section">
            <label className="wallet-input-label">Add Money to Wallet</label>
            
            <div className="quick-amounts">
              {quickAmounts.map((value) => (
                <button
                  key={value}
                  className={`quick-amount-btn ${selectedAmount === value ? 'selected' : ''}`}
                  onClick={() => handleQuickAmount(value)}
                >
                  ${value}
                </button>
              ))}
            </div>

            <div className="wallet-input-group">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                className="wallet-amount-input"
                placeholder="0.00"
                value={amount}
                onChange={handleAmountChange}
                disabled={isProcessing}
              />
            </div>

            <button
              className="wallet-add-btn"
              onClick={handleAddMoney}
              disabled={isProcessing || !amount || parseFloat(amount) <= 0}
            >
              {isProcessing ? 'Processing...' : 'Add Money'}
            </button>
          </div>

          <div className="wallet-info">
            <p className="wallet-info-text">
              💡 Your wallet balance is used to pay for voice assistant calls. 
              Each call is charged based on usage.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WalletModal
