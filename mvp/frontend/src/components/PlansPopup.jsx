import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { planService, paymentService } from '../services/services'
import { useAuthStore } from '../context/authStore'
import { showSuccess,showError } from '../utils/toast'
import '../styles/PlansPopup.css'
import { bootstrapAuth } from '../auth/bootstrapAuth'

const PlansPopup = ({ isOpen, onClose }) => {
  const { user, updateUser } = useAuthStore()
  const [processingPlanId, setProcessingPlanId] = useState(null)
  const { setAuth } = useAuthStore()

  const { data: plans = [], isLoading, error } = useQuery({
    queryKey: ['plans'],
    queryFn: planService.listPlan,
    staleTime: 5 * 60 * 1000,
  })

  const handleUpgrade = async (plan) => {
    const isTrialUser = user?.subscription_mode === 'trial'

    const createFn = isTrialUser ? paymentService.createTrialUpgradeOrder : paymentService.createOrder
    const verifyFn = isTrialUser ? paymentService.verifyTrialUpgrade : paymentService.verifyPayment

    setProcessingPlanId(plan.id)

    try {
      const orderPayload = {
        plan_id: plan.id,
        amount: plan.price,
        user_id: user.id,
      }

      const orderRes = await createFn(orderPayload)
      const orderData = orderRes

      const options = {
        key: orderData.razorpay_key_id,
        amount: orderData.amount,
        currency: orderData.currency || 'USD',
        name: 'Voice Assistant Platform',
        description: `Upgrade to ${plan.name}`,
        order_id: orderData.razorpay_order_id,
        handler: async (response) => {
          const verifyPayload = {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            order_id: orderData.order_id,
          }

          try {
            const verifyRes = await verifyFn(verifyPayload)
            console.log("We got the 200 of verify response")
            console.log(verifyRes)
            if(verifyRes){
              setTimeout(() => {
                onClose()
                bootstrapAuth(setAuth)
              }, 1000)
              showSuccess(`Upgraded to ${plan.name} successfully`)
              return
            }
          } catch (err) {
            showError('Verification failed. Contact support.')
          }
        },
        prefill: {
          name: user.username || '',
          email: user.email || '',
        },
        theme: { color: '#3b82f6' },
        modal: {
          ondismiss: () => {
            showError("")
            setProcessingPlanId(null)
          },
        },
      }

      if (!window.Razorpay) {
        throw new Error('Razorpay SDK not loaded')
      }

      const razorpay = new window.Razorpay(options)
      razorpay.open()

    } catch (err) {
      showError('Payment initiation failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setProcessingPlanId(null)
    }
  }
  const filteredPlans = plans.filter((plan) => {
    if (!plan.is_active) return false
    if (plan.name === "trial") return false
    if (user?.active_subscription?.plan_id === plan.id) return false  
    return true
  })

  if (!isOpen) return null

  return (
    <div className="pricing-overlay">
      <div className="pricing-modal glass">
        <button className="pricing-close" onClick={onClose}>×</button>

        <header className="pricing-header">
          <h2>Choose Your Plan</h2>
          <p>Upgrade your account and unlock premium features</p>
        </header>

        {isLoading && (
          <div className="pricing-state loading">
            <div className="spinner"></div>
            <p>Loading plans…</p>
          </div>
        )}

        {error && (
          <p className="pricing-state error">Failed to load plans. Try again later.</p>
        )}

        {!isLoading && !error && filteredPlans.length === 0 && (
          <p className="pricing-state success">No other plans available right now 🎉</p>
        )}

        <div className="pricing-grid">
          {filteredPlans.map((plan) => (
            <div
              key={plan.id}
              className={`pricing-card glass-card ${plan.is_popular ? 'popular' : ''}`}
            >
              {plan.is_popular && <div className="popular-badge">Most Popular</div>}

              <h3 className="plan-title">{plan.name?.toUpperCase()}</h3>

              <div className="price">
                <span className="amount">
                  {plan.currency === 'INR' ? '₹' : '$'}{plan.price}
                </span>
                <span className="period">/month</span>
              </div>

              <p className="credits">{plan.credits} credits included</p>

              <ul className="features">
                {plan.features?.length ? (
                  plan.features.map((f, i) => <li key={i}>{f}</li>)
                ) : (
                  <li>All standard features included</li>
                )}
              </ul>

              <button
                className="buy-btn"
                disabled={isLoading || processingPlanId === plan.id}
                onClick={() => handleUpgrade(plan)}
              >
                {processingPlanId === plan.id ? 'Processing...' : 'Buy Plan'}
              </button>
            </div>
          ))}
        </div>

        <footer className="pricing-footer">
          Secure payment • Cancel anytime • Instant activation
        </footer>
      </div>
    </div>
  )
}

export default PlansPopup