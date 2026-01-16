import React from "react";
import "../styles/ViewPlan.css";

export default function ViewPlan({ plan, onBack }) {
  if (!plan) {
    return (
      <div className="plan-profile">
        <div className="error-container">
          <p>Plan not found</p>
          <button onClick={onBack} className="back-btn">← Back to Plans</button>
        </div>
      </div>
    );
  }
  return (
    <div className="plan-profile">
      <div className="profile-header">
        <button onClick={onBack} className="back-btn">← Back to Plans</button>
        <h1>Plan Details: {plan.name}</h1>
      </div>

      <div className="profile-content">
        {/* Plan Information */}
        <div className="profile-section">
          <h2>Plan Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Code</label>
              <span>{plan.code}</span>
            </div>

            <div className="info-item">
              <label>Description</label>
              <span>{plan.description || "—"}</span>
            </div>

            <div className="info-item">
              <label>Monthly Price</label>
              <span>₹{plan.price}</span>
            </div>

            <div className="info-item">
              <label>Wallet Credits</label>
              <span>{plan.credits}</span>
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