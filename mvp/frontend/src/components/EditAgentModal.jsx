import React from 'react'

function EditAgentModal({ 
  editingAgent, 
  formData, 
  setFormData, 
  Instructions, 
  InstructionSet, 
  handleSubmit, 
  handleCancelEdit, 
  isLoading 
}) {
  if (!editingAgent) return null

  return (
    <div className="modal-overlay" onClick={() => handleCancelEdit()}>
      <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Edit Agent: {editingAgent.name}</h3>
          <button className="modal-close" onClick={() => handleCancelEdit()}>×</button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} className="add-agent-form">
            <input
              type="text"
              placeholder="Agent Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              autoComplete="off"
              required
            />
            <input
              type="text"
              placeholder="Domain (e.g., example.com or localhost)"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              autoComplete="off"
              required
              pattern="^(localhost|127\.0\.0\.1)(:\d+)?$|^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
              title="Enter a valid domain (e.g., example.com, localhost, or 127.0.0.1)"
            />
            <label>Voice & Behavior</label>
            <textarea value={Instructions.voice_behaviour} name="voice_behaviour" autoComplete='off' rows={5} placeholder="Voice and Behavior (example: You are Maria, a personal assistant. You are a female. Answer in a soft tone. For any background noise, miswritten or understandable questions, tell the user - I didn't understand that, can you please repeat what you asked?)" onChange={InstructionSet} />
            <label>Scope/What I Can Talk About</label>
            <textarea value={Instructions.scope} name="scope" autoComplete='off' rows={5} placeholder="Scope (example: Provide information only about Demo Technologies. If user asks about other companies or unrelated topics, say: I can only provide information about Demo Technologies. How may I help you regarding our services or products?)" onChange={InstructionSet} />
            <label>Allowed Contact Details</label>
            <textarea value={Instructions.contact_details} name="contact_details" autoComplete='off' rows={5} placeholder="Contact Details (example: Email, sales (phone no), HR)" onChange={InstructionSet} />
            <label>Privacy Rules</label>
            <textarea value={Instructions.privacy_rules} name="privacy_rules" autoComplete='off' rows={5} placeholder="Privacy Rules (example: Do not share personal information)" onChange={InstructionSet} />
            <label>Top Features</label>
            <textarea value={Instructions.top_features} name="top_features" autoComplete='off' rows={5} placeholder="Top Features (example: 1. Web and Mobile Development)" onChange={InstructionSet} />
            <label>Products</label>
            <textarea value={Instructions.product} name="product" autoComplete='off' rows={5} placeholder="Products (example: Mention your products here)" onChange={InstructionSet} />
            <label>Services</label>
            <textarea value={Instructions.services} name="services" autoComplete='off' rows={5} placeholder="Services (example: Add the services you provide)" onChange={InstructionSet} />
            <label>Office Locations</label>
            <textarea value={Instructions.office_locations} name="office_locations" autoComplete='off' rows={5} placeholder="Office Locations (example: USA, India)" onChange={InstructionSet} />
            <label>Pricing Rules</label>
            <textarea value={Instructions.pricing_rules} name="pricing_rules" autoComplete="off" rows={5} placeholder="Pricing Rules (example: Do not provide specific prices)" onChange={InstructionSet} />
            <label>Restrictions</label>
            <textarea value={Instructions.restrictions} name="restrictions" autoComplete="off" rows={5} placeholder="Restrictions (example: Do not provide personal information)" onChange={InstructionSet} />
            <label>Tone Examples</label>
            <textarea value={Instructions.tone_examples} name="tone_examples" autoComplete='off' rows={5} placeholder="Tone Examples (example: 1. Greeting: Enter your type)" onChange={InstructionSet} />
            <label>Additional Instructions</label>
            <textarea value={Instructions.additional_instructions} name="additional_instructions" autoComplete="off" rows={5} placeholder="Additional Instructions (example: Add the additional instructions you want to enhance your assistant)" onChange={InstructionSet} />
            <label>
              Assistant Voice:
              <select
                value={formData.voice}
                onChange={(e) => setFormData({ ...formData, voice: e.target.value })}
                autoComplete="off"
              >
                <option value="alloy">Alloy</option>
                <option value="ash">Ash</option>
                <option value="ballad">Ballad</option>
                <option value="cedar">Cedar</option>
                <option value="coral">Coral</option>
                <option value="echo">Echo</option>
                <option value="marin">Marin</option>
                <option value="sage">Sage</option>
                <option value="shimmer">Shimmer</option>
                <option value="verse">Verse</option>
              </select>
            </label>
            <label>
              Noise Reduction:
              <select
                value={formData.noise_reduction_mode}
                onChange={(e) => setFormData({ ...formData, noise_reduction_mode: e.target.value })}
                autoComplete="off"
              >
                <option value="near_field">Near Field</option>
                <option value="far_field">Far Field</option>
              </select>
            </label>
            <label>
              VAD Threshold:
              <input
                type="text"
                value={formData.noise_reduction_threshold}
                onChange={(e) => setFormData({ ...formData, noise_reduction_threshold: e.target.value })}
                autoComplete="off"
                placeholder="0.65"
              />
            </label>
            <label>
              Prefix Padding (ms):
              <input
                type="number"
                value={formData.noise_reduction_prefix_padding_ms}
                onChange={(e) => setFormData({ ...formData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 150 })}
                autoComplete="off"
                min="0"
              />
            </label>
            <label>
              Silence Duration (ms):
              <input
                type="number"
                value={formData.noise_reduction_silence_duration_ms}
                onChange={(e) => setFormData({ ...formData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 600 })}
                autoComplete="off"
                min="0"
              />
            </label>
            <div className="form-actions">
              <button type="button" onClick={() => handleCancelEdit()} className="cancel-btn">
                Cancel
              </button>
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Updating...' : 'Update Agent'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default EditAgentModal

