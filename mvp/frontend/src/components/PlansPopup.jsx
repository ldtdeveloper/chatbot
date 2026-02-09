import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { planService, paymentService } from '../services/services'
import { useAuthStore } from '../context/authStore'
import toast from 'react-hot-toast'
import '../styles/PlansPopup.css'

const PlansPopup = ({ isOpen, onClose }) => {
  const { user, updateUser } = useAuthStore()
  const [processingPlanId, setProcessingPlanId] = useState(null)

  const {
    data: plans = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['plans'],
    queryFn: planService.listPlan,
    staleTime: 5 * 60 * 1000,
  })

  const handleUpgrade = async (plan) => {
    const isTrialUser = user?.is_trial === true

    const createEndpoint = isTrialUser
      ? paymentService.createTrialUpgradeOrder
      : paymentService.createOrder

    const verifyEndpoint = isTrialUser
      ? paymentService.verifyTrialUpgrade
      : paymentService.verifyPayment

    setProcessingPlanId(plan.id)
    const toastId = toast.loading(`Initiating upgrade to ${plan.name}...`)

    try {

      const orderPayload = {
        plan_id: plan.id,
        amount: plan.price,
        user_id: user.id,
      }

      const orderRes = await createEndpoint(orderPayload)
      const orderData = orderRes


      const options = {
        key: orderData.razorpay_key_id,
        amount: orderData.amount,
        currency: orderData.currency || 'USD',
        name: 'Voice Assistant Platform',
        description: `Upgrade to ${plan.name}`,
        order_id: orderData.razorpay_order_id,
        handler: async function (response) {
          const verifyPayload = {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            order_id: orderData.order_id,
          }

          try {
            const verifyRes = await verifyEndpoint(verifyPayload)
            updateUser(verifyRes.updated_user || user) // assuming backend returns updated user
            toast.success(`Successfully upgraded to ${plan.name}! 🎉`, { id: toastId })
            onClose()
          } catch (verifyErr) {
            toast.error('Payment verification failed. Please contact support.', { id: toastId })
          }
        },
        prefill: {
          name: user.username || '',
          email: user.email || '',
        },
        theme: {
          color: '#3b82f6',
        },
        modal: {
          ondismiss: () => {
            toast.dismiss(toastId)
            setProcessingPlanId(null)
          },
        },
      }

      if (!window.Razorpay) {
        toast.error('Razorpay SDK not loaded. Please refresh the page.', { id: toastId })
        return
      }

      const razorpay = new window.Razorpay(options)
      razorpay.open()

    } catch (err) {
      toast.error('Failed to start payment: ' + (err.response?.data?.detail || err.message), { id: toastId })
    } finally {
      setProcessingPlanId(null)
    }
  }
  const filteredPlans = plans.filter((plan) => {
    if (!plan.is_active) return false
    if (user?.is_trial && plan.name?.toLowerCase() === 'trial') return false
    if (user?.plan_id === plan.id) return false
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
          <p className="pricing-state error">
            Failed to load plans. Please try again later.
          </p>
        )}

        {!isLoading && !error && filteredPlans.length === 0 && (
          <p className="pricing-state success">
            You're already on the best available plan! 🎉
          </p>
        )}

        <div className="pricing-grid">
          {filteredPlans.map((plan) => (
            <div
              key={plan.id}
              className={`pricing-card glass-card ${plan.is_popular ? 'popular' : ''}`}
            >
              {plan.is_popular && <div className="popular-badge">Most Popular</div>}

              <h3 className="plan-title">
                {plan.name?.toUpperCase()}
                {plan.is_trial && <span className="trial-tag">Trial</span>}
              </h3>

              <div className="price">
                <span className="amount">
                  {plan.currency === 'INR' ? '₹' : '$'}
                  {plan.price}
                </span>
                <span className="period">/month</span>
              </div>

              <p className="credits">{plan.credits} credits included</p>

              <ul className="features">
                {plan.features?.length ? (
                  plan.features.map((feature, idx) => <li key={idx}>{feature}</li>)
                ) : (
                  <li>All standard features included</li>
                )}
              </ul>

              <button
                className="buy-btn"
                disabled={isLoading || processingPlanId === plan.id}
                onClick={() => handleUpgrade(plan)}
              >
                {processingPlanId === plan.id
                  ? 'Processing...'
                  : plan.name?.toLowerCase() === 'trial'
                  ? 'Start Free Trial'
                  : 'Buy Plan'}
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