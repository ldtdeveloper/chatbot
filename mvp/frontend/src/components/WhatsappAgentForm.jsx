import React from 'react'

function WhatsappAgentForm({ 
  formData, 
  setFormData, 
  handleInstructionsChange,
  handleSubmit, 
  isLoading,
  isEdit = false,
  handleCancel
}) {
  return (
    <form onSubmit={handleSubmit} className="add-agent-form">
      <div className="form-info">
        <p><strong>Note:</strong> Configure your WhatsApp agent. The <strong>Phone Number</strong> is required. <strong>Phone Number ID</strong> can be added later if you don't have it yet.</p>
      </div>
      
      <div className="form-group">
        <label>Agent Name</label>
        <input
          type="text"
          placeholder="e.g. Sales Assistant"
          value={formData.name || ''}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          autoComplete="off"
          required
        />
      </div>

      <div className="form-group">
        <label>WhatsApp Number</label>
        <input
          type="text"
          placeholder="e.g. 919876543210 (with country code, no +)"
          value={formData.phone_number || ''}
          onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
          autoComplete="off"
          required
        />
      </div>

      <div className="form-group">
        <label>Phone Number ID (Optional)</label>
        <input
          type="text"
          placeholder="From Meta Developer Portal"
          value={formData.phone_number_id || ''}
          onChange={(e) => setFormData({ ...formData, phone_number_id: e.target.value })}
          autoComplete="off"
        />
      </div>

      <div className="form-group">
        <label>Startup Message (Optional)</label>
        <input
          type="text"
          placeholder="e.g. Hi! How can I help you today?"
          value={formData.startup_message || ''}
          onChange={(e) => setFormData({ ...formData, startup_message: e.target.value })}
          autoComplete="off"
        />
      </div>

      <div className="form-group">
        <label>Onboarding Mode</label>
        <select
          value={formData.onboarding_mode || 'demo'}
          onChange={(e) => setFormData({ ...formData, onboarding_mode: e.target.value })}
        >
          <option value="demo">Demo</option>
          <option value="live">Live</option>
        </select>
      </div>

      <div className="instructions-section">
        <h3>System Instructions</h3>
        
        <div className="form-group">
          <label>Voice & Behavior</label>
          <textarea 
            value={formData.instructions_details?.voice_behaviour || ''} 
            name="voice_behaviour" 
            rows={4} 
            placeholder="How should the agent speak and act?" 
            onChange={handleInstructionsChange} 
          />
        </div>

        <div className="form-group">
          <label>Scope / Knowledge Base</label>
          <textarea 
            value={formData.instructions_details?.scope || ''} 
            name="scope" 
            rows={4} 
            placeholder="What should the agent know about?" 
            onChange={handleInstructionsChange} 
          />
        </div>

        <div className="form-group">
          <label>Contact Details to Share</label>
          <textarea 
            value={formData.instructions_details?.contact_details || ''} 
            name="contact_details" 
            rows={3} 
            placeholder="Emails, phone numbers, etc." 
            onChange={handleInstructionsChange} 
          />
        </div>

        <div className="form-group">
          <label>Additional Instructions</label>
          <textarea 
            value={formData.instructions_details?.additional_instructions || ''} 
            name="additional_instructions" 
            rows={4} 
            placeholder="Any other specific rules..." 
            onChange={handleInstructionsChange} 
          />
        </div>
      </div>

      <div className="form-actions">
        
        <button type="submit" className="submit-btn" disabled={isLoading}>
          {isLoading ? 'Saving...' : (isEdit ? 'Update WhatsApp Agent' : 'Create WhatsApp Agent')}
        </button>
        {handleCancel && (
          <button type="button" className="cancel-btn" onClick={handleCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default WhatsappAgentForm
