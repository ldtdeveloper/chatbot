import React, { useState, useEffect } from "react";
import { FaPlus, FaTimes } from 'react-icons/fa';
import '../styles/PlanForm.css'; // optional, for styling

export default function PlanForm({ initialData, onSubmit, onBack }) {
  // Handle both prop names (initialData and initialdata) for compatibility
  const data = initialData || {};  
  const [formData, setFormData] = useState({
    name: data.name || "",
    description: data.description || "",
    currency: data.currency || "USD",
    // wallet_credits: data.wallet_credits || data.credits || 0, // Support old 'credits' field for backward compatibility
    plan_type: data.plan_type || "monthly",
    price: data.price || 0,
    minutes:data.minutes||0,
    features: Array.isArray(data.features) ? data.features : [],
    is_active: data.is_active ?? true,
  });
  const [currentFeature, setCurrentFeature] = useState("");

  // Currency options
  const currencies = [
    { value: "USD", label: "US Dollar ($)" },
    { value: "INR", label: "Indian Rupee (₹)" },
    { value: "BHD", label: "Bahraini Dinar (BD)" },
    { value: "KWD", label: "Kuwaiti Dinar (KD)" },
    { value: "OMR", label: "Omani Rial (OMR)" },
    { value: "SAR", label: "Saudi Riyal (SAR)" },
    { value: "AED", label: "UAE Dirham (AED)" },
    { value: "EUR", label: "Euro (€)" },
    { value: "GBP", label: "British Pound (£)" },
  ];

  // Plan type options
  const planTypes = [
    { value: "monthly", label: "Monthly" },
    { value: "yearly", label: "Yearly" },
  ];

  // Update form data when initialData changes
  useEffect(() => {
    const currentData = initialData || {};
    setFormData({
      name: currentData.name || "",
      description: currentData.description || "",
      currency: currentData.currency || "USD",
      // wallet_credits: currentData.wallet_credits || currentData.credits || 0,
      plan_type: currentData.plan_type || "monthly",
      price: currentData.price || 0,
      minutes:currentData.minutes||0,
      features: Array.isArray(currentData.features) ? currentData.features : [],
      is_active: currentData.is_active ?? true,
    });
    setCurrentFeature("");
  }, [initialData]);

  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleAddFeature = () => {
    const trimmedFeature = currentFeature.trim();
    if (trimmedFeature) {
      setFormData((prev) => ({
        ...prev,
        features: [...prev.features, trimmedFeature],
      }));
      setCurrentFeature("");
      setError("");
    }
  };

  const handleRemoveFeature = (index) => {
    setFormData((prev) => ({
      ...prev,
      features: prev.features.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.features.length === 0) {
      setError("Please add at least one feature.");
      return;
    }

    const submitData = {
      ...formData,
      // wallet_credits: Number(formData.wallet_credits),
      price: Number(formData.price),
      minutes:Number(formData.minutes),
      features: formData.features,
    };
    
    // Remove old 'credits' field if it exists
    // delete submitData.credits;
    // delete submitData.minutes
    delete submitData.code; // Remove code field if it exists
    
    // If editing, include the id
    if (data.id) {
      submitData.id = data.id;
    }

    // Call onSubmit if it's a function, otherwise just call onBack
    if (typeof onSubmit === 'function') {
      onSubmit(submitData,initialData);
    } else if (onBack) {
      onBack();
    }
  };

  const handleBack = () => {
    if (typeof onBack === 'function') {
      onBack();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleBack}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <form className="plan-form" onSubmit={handleSubmit}>
          <div className="plan-form-header">
            <h2>{data.id ? "Edit Plan" : "Create Plan"}</h2>
            <button type="button" onClick={handleBack} className="back-btn">← Back</button>
          </div>
          <div className="plan-form-content">
            {error && <p className="form-error">{error}</p>}
          <label>
            Name
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Description
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter plan description"
            />
          </label>

          <label>
            Currency
            <select
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              required
            >
              {currencies.map((currency) => (
                <option key={currency.value} value={currency.value}>
                  {currency.label}
                </option>
              ))}
            </select>
          </label>

          {/* <label> 
            Wallet Credits
            <input
              type="number"
              name="wallet_credits"
              inputMode="numeric"
              pattern="[0-9]*"
              value={formData.wallet_credits}
              onChange={handleChange}
              min={0}
              required
              placeholder="Credits user gets when purchasing this plan"
            />
          </label>*/}
           <label> 
            Total Minutes
            <input
              type="number"
              name="minutes"
              inputMode="numeric"
              pattern="[0-9]*"
              value={formData.minutes}
              onChange={handleChange}
              min={0}
              required
              placeholder="Minutes User Get on this plan"
            />
          </label>

          <label>
            Plan Type
            <select
              name="plan_type"
              value={formData.plan_type}
              onChange={handleChange}
              required
            >
              {planTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Plan Price ({formData.currency})
            <input
              type="number"
              name="price"
              inputMode="numeric"
              pattern="[0-9]*"
              value={formData.price}
              onChange={handleChange}
              min={0}
              step="0.01"
              required
              placeholder="Enter plan price"
            />
          </label>

          <label>
            Plan Features (Add one at a time)
            <div className="features-input-container" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="text"
                value={currentFeature}
                onChange={(e) => setCurrentFeature(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddFeature();
                  }
                }}
                placeholder="Enter a feature"
                style={{ flex: 1 }}
              />
              <button
                type="button"
                onClick={handleAddFeature}
                className="add-feature-btn"
                style={{ padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', minWidth: '32px', width: '32px', height: '32px' }}
                title="Add feature"
              >
                <FaPlus size={14} />
              </button>
            </div>
            {formData.features.length > 0 && (
              <ul className="features-list" style={{ listStyle: 'none', padding: 0, marginTop: '8px' }}>
                {formData.features.map((feature, index) => (
                  <li key={index} className="feature-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ flex: 1 }}>{feature}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveFeature(index)}
                      className="remove-feature-btn"
                      style={{ padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', minWidth: '32px', width: '32px', height: '32px' }}
                      title="Remove feature"
                    >
                      <FaTimes size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </label>
          </div>
          <div className="form-actions">
            <button type="button" onClick={onBack} className="cancel-btn">
              Cancel
            </button>
            <button type="submit">
              {data.id ? "Update Plan" : "Create Plan"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
