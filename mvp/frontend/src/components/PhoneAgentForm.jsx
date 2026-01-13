import React from 'react'

function PhoneAgentForm({ 
  phoneFormData, 
  setPhoneFormData, 
  Instructions, 
  InstructionSet, 
  activeApiKeys,
  handlePhoneSubmit, 
  isLoading 
}) {
  return (
    <form onSubmit={handlePhoneSubmit} className="add-agent-form">
      <div className="form-info">
        <p><strong>Note:</strong> Configure your phone agent with SIP settings. Only <strong>Phone Number</strong> and <strong>SIP Server</strong> are required. Username, Password, and Domain are optional and only needed if your SIP server requires authentication.</p>
      </div>
      <input
        type="text"
        value={activeApiKeys.length > 0 ? activeApiKeys[0].key_name : ''}
        readOnly     
        autoComplete="off"
      />
      <input
        type="text"
        placeholder="Agent Name"
        value={phoneFormData.name}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, name: e.target.value })}
        autoComplete="off"
        required
      />
      <input
        type="text"
        placeholder="Phone Number (e.g., +1234567890)"
        value={phoneFormData.phone_number}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, phone_number: e.target.value })}
        autoComplete="off"
        required
      />
      <input
        type="text"
        placeholder="SIP Server (e.g., sip.example.com)"
        value={phoneFormData.sip_server}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, sip_server: e.target.value })}
        autoComplete="off"
        required
      />
      <input
        type="text"
        placeholder="SIP Username (optional - for SIP server authentication)"
        value={phoneFormData.sip_username}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, sip_username: e.target.value })}
        autoComplete="off"
      />
      <input
        type="password"
        placeholder="SIP Password (optional - for SIP server authentication)"
        value={phoneFormData.sip_password}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, sip_password: e.target.value })}
        autoComplete="off"
      />
      <input
        type="text"
        placeholder="SIP Domain/Realm (optional - e.g., sip.example.com)"
        value={phoneFormData.sip_domain}
        onChange={(e) => setPhoneFormData({ ...phoneFormData, sip_domain: e.target.value })}
        autoComplete="off"
      />
      <div className="form-info" style={{ marginTop: '10px', padding: '10px', background: '#f0f9ff', borderRadius: '6px', fontSize: '14px' }}>
        <p><strong>💡 SIP Configuration Help:</strong></p>
        <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
          <li><strong>SIP Server:</strong> Required - Your SIP server address (e.g., sip.provider.com or 192.168.1.100)</li>
          <li><strong>Username/Password:</strong> Only needed if your SIP server requires authentication</li>
          <li><strong>SIP Domain:</strong> Usually optional - Some SIP providers require a realm/domain for authentication</li>
        </ul>
      </div>
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
          value={phoneFormData.voice}
          onChange={(e) => setPhoneFormData({ ...phoneFormData, voice: e.target.value })}
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
          value={phoneFormData.noise_reduction_mode}
          onChange={(e) => setPhoneFormData({ ...phoneFormData, noise_reduction_mode: e.target.value })}
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
          value={phoneFormData.noise_reduction_threshold}
          onChange={(e) => setPhoneFormData({ ...phoneFormData, noise_reduction_threshold: e.target.value })}
          autoComplete="off"
          placeholder="0.65"
        />
      </label>
      <label>
        Prefix Padding (ms):
        <input
          type="number"
          value={phoneFormData.noise_reduction_prefix_padding_ms}
          onChange={(e) => setPhoneFormData({ ...phoneFormData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 150 })}
          autoComplete="off"
          min="0"
        />
      </label>
      <label>
        Silence Duration (ms):
        <input
          type="number"
          value={phoneFormData.noise_reduction_silence_duration_ms}
          onChange={(e) => setPhoneFormData({ ...phoneFormData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 600 })}
          autoComplete="off"
          min="0"
        />
      </label>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Phone Agent'}
      </button>
    </form>
  )
}

export default PhoneAgentForm

