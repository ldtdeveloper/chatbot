import React from "react";
import { FaTimes } from "react-icons/fa";
import "../styles/ViewPlan.css";

// Currency symbols mapping
const getCurrencySymbol = (currency) => {
  const currencyMap = {
    'USD': '$',
    'INR': '₹',
    'BHD': 'BD',
    'KWD': 'KD',
    'OMR': 'OMR',
    'SAR': 'SAR',
    'AED': 'AED',
    'EUR': '€',
    'GBP': '£',
  };
  return currencyMap[currency] || currency || '$';
};

export default function ViewPlan({ plan, onBack }) {
  if (!plan) {
    return (
      <div className="plan-profile">
        <div className="error-container">
          <p>Plan not found</p>
          <button onClick={onBack} className="close-btn" title="Close">
            <FaTimes />
          </button>
        </div>
      </div>
    );
  }

  const currency = plan.currency || 'USD';
  const currencySymbol = getCurrencySymbol(currency);
  // const walletCredits = plan.wallet_credits || plan.credits || 0;
  const minutesCredit = plan.minutes||0;
  const agents = plan.number_of_agents||0;
  const planType = plan.plan_type || 'monthly';

  return (
    <div className="plan-profile">
      <div className="profile-header">
        <h1>{plan.name}</h1>
        <button onClick={onBack} className="close-btn" title="Close">
          <FaTimes />
        </button>
      </div>

      <div className="profile-content">
        {/* Plan Information */}
        <div className="profile-section">
          <h2>Plan Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Description</label>
              <span>{plan.description || "—"}</span>
            </div>

            <div className="info-item">
              <label>Price</label>
              <span className="price-value">
                <span className="currency-symbol">{currencySymbol}</span>
                {plan.price}
                <span className="plan-type-badge">{planType}</span>
              </span>
            </div>

            <div className="info-item">
              <label>Currency</label>
              <span className="currency-badge">{currency}</span>
            </div>

            {/* <div className="info-item">
              <label>Wallet Credits</label>
              <span className="credits-value">{walletCredits} credits</span>
            </div> */}
            <div className="info-item">
              <label>Total Minutes</label>
              <span className="credits-value">{minutesCredit} Minutes</span>
            </div>
            <div className="info-item">
              <label>Total Agents</label>
              <span className="credits-value">{agents} Agents</span>
            </div>

            <div className="info-item">
              <label>Plan Type</label>
              <span className="plan-type-value">{planType}</span>
            </div>

            <div className="info-item">
              <label>Status</label>
              <span className={plan.is_active ? "status active" : "status inactive"}>
                {plan.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            <div className="info-item">
              <label>Created</label>
              <span>
                {plan.created_at
                  ? new Date(plan.created_at).toLocaleDateString()
                  : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="profile-section">
          <h2>Plan Features</h2>

          {plan.features && Object.keys(plan.features).length > 0 ? (
            <div className="features-list">
              {Object.entries(plan.features).map(([key, value]) => (
                <div key={key} className="feature-item">
                  <span className="feature-icon">✓</span>
                  <span>{String(value)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-data">No features defined for this plan.</p>
          )}
        </div>
      </div>
    </div>
  );
}