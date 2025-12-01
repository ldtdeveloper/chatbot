import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService, openAIKeyService } from '../services/services'
import './Agents.css'

function Agents() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showWidgetModal, setShowWidgetModal] = useState(false)
  const [editingAgent, setEditingAgent] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [selectedInstructionsAgent, setSelectedInstructionsAgent] = useState(null)
  const [selectedApiKeyId, setSelectedApiKeyId] = useState('')
  const [tab, setTab] = useState("float");
  const [fetchApiKeyId, setFetchApiKeyId] = useState('')
  const [Instructions, setInstructions] = useState({
  // company_name: '',
  // company_website: '',
  // industries: '',
  // solutions: '',
  // contact_info: '',
  // careers_info: '',
  // company_domain:'',
  // company_description:'',
  // company_tagline:'',
  // services_page_url:'',
  // industries_page_url:'',
  // solutions_page_url:'',
  // careers_page_url:'',
  // insights_page_url:'',
  // contact_page_url:'',
  // leadership_info:'',
  // allowed_scope:'',
  // forbidden_scope:'',
  // strict_refusal_text:'',
  // greeting_text:'',
  // refusal_text:'',
  // closure_text:'',
  voice_behaviour: "",
  scope:'',
  contact_details:'',
  privacy_rules:'',
  top_features:'',
  product:'',
  services:'',
  office_locations:'',
  pricing_rules:'',
  restrictions:'',
  tone_examples:'',
  additional_instructions:''



});

const InstructionSet = (e) => {
  
  const { name, value } = e.target;
  setInstructions((prev) => ({
    ...prev,
    [name]: value
  }));
};
const handleTabChange = async (type) => {
  setTab(type);
  if (!selectedAgentForWidget) return;

  try {
    let data;
    if (type === "float") {
      data = await agentService.generateWidgetCode(selectedAgentForWidget.id);
    } else {
      data = await agentService.generateWidgetCodeFixed(selectedAgentForWidget.id);
    }
    setWidgetCode(data.widget_code); // Set the code dynamically
    setWidgetId(data.widget_id || null); // Store widget_id from response
  } catch (error) {
    console.error("Error fetching widget code:", error);
    alert("Failed to fetch widget code");
  }
};


  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    instructions: '',
    voice: 'alloy',
    noise_reduction_mode: 'near_field',
    noise_reduction_threshold: '0.5',
    noise_reduction_prefix_padding_ms: 300,
    noise_reduction_silence_duration_ms: 500
  })
  const [selectedAgentForWidget, setSelectedAgentForWidget] = useState(null)
  const [widgetCode, setWidgetCode] = useState(null)
  const [widgetId, setWidgetId] = useState(null)
  const [copied, setCopied] = useState(false)

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents', fetchApiKeyId],
    queryFn: () => {
      if (!fetchApiKeyId) {
        return Promise.resolve([])
      }
      return agentService.list(parseInt(fetchApiKeyId))
    },
    enabled: !!fetchApiKeyId,
  })
  

  const { data: apiKeys, isLoading: keysLoading } = useQuery({
    queryKey: ['openai-keys'],
    queryFn: openAIKeyService.list,
  })

  const activeApiKeys = apiKeys?.filter(key => key.is_active) || []

  const createMutation = useMutation({
    mutationFn: agentService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setShowAddForm(false)
      handleCancelEdit()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => agentService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setEditingAgent(null)
      setShowEditModal(false)
      setSelectedAgent(null)
      handleCancelEdit()
    },
  })

///creating InstructionArray
  // const instructionsArray = Object.entries(Instructions).map(([key,value])=>({
  //   [key]:value
  // }))
  // const finalInstructions = JSON.stringify(instructionsArray)

  const deleteMutation = useMutation({
    mutationFn: agentService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setSelectedAgent(null)
    },
  })
  function convertJsonPrompt(data){
    // Handle null or undefined
    if (!data) {
      return '<div class="instruction-block"><p>No instructions available</p></div>'
    }

    let data1;
    
    // Check if data is already an object
    if (typeof data === 'object') {
      data1 = data;
    } else if (typeof data === 'string') {
      // Try to parse as JSON
      try {
        data1 = JSON.parse(data);
      } catch (e) {
        // If parsing fails, it's plain text - return it as is
        return `<div class="instruction-block"><div><h3>SYSTEM INSTRUCTIONS</h3><p>${data.replace(/\n/g, '<br>')}</p></div></div>`
      }
    } else {
      // Fallback for other types
      return '<div class="instruction-block"><p>Invalid instruction format</p></div>'
    }

    // If data1 is not an object after parsing, treat as plain text
    if (typeof data1 !== 'object' || data1 === null) {
      const textContent = typeof data1 === 'string' ? data1 : String(data);
      return `<div class="instruction-block"><div><h3>SYSTEM INSTRUCTIONS</h3><p>${textContent.replace(/\n/g, '<br>')}</p></div></div>`
    }

    // Check if it has the expected structure (has at least one of the expected properties)
    const hasStructuredData = data1.voice_behaviour || data1.scope || data1.contact_details || 
                              data1.privacy_rules || data1.top_features || data1.product || 
                              data1.services || data1.office_locations || data1.pricing_rules || 
                              data1.restrictions || data1.tone_examples || data1.additional_instructions;

    if (!hasStructuredData) {
      // If it doesn't have the expected structure, display as plain text
      const textContent = JSON.stringify(data1, null, 2);
      return `<div class="instruction-block"><div><h3>SYSTEM INSTRUCTIONS</h3><pre>${textContent}</pre></div></div>`
    }

    // Return structured format
    return `<div class="instruction-block">${data1.voice_behaviour ? `<div><h3>VOICE & BEHAVIOUR</h3><p>${data1.voice_behaviour}</p></div>` : ''}${data1.scope ? `<div><h3>SCOPE</h3><p>${data1.scope}</p></div>` : ''}${data1.contact_details ? `<div><h3>CONTACT DETAILS</h3><p>${data1.contact_details}</p></div>` : ''}${data1.privacy_rules ? `<div><h3>PRIVACY RULES</h3><p>${data1.privacy_rules}</p></div>` : ''}${data1.top_features ? `<div><h3>TOP FEATURES</h3><p>${data1.top_features}</p></div>` : ''}${data1.product ? `<div><h3>PRODUCT</h3><p>${data1.product}</p></div>` : ''}${data1.services ? `<div><h3>SERVICES</h3><p>${data1.services}</p></div>` : ''}${data1.office_locations ? `<div><h3>OFFICE LOCATION</h3><p>${data1.office_locations}</p></div>` : ''}${data1.pricing_rules ? `<div><h3>PRICING RULES</h3><p>${data1.pricing_rules}</p></div>` : ''}${data1.restrictions ? `<div><h3>RESTRICTIONS</h3><p>${data1.restrictions}</p></div>` : ''}${data1.tone_examples ? `<div><h3>TONE EXAMPLES</h3><p>${data1.tone_examples}</p></div>` : ''}${data1.additional_instructions ? `<div><h3>ADDITIONAL INSTRUCTIONS</h3><p>${data1.additional_instructions}</p></div>` : ''}</div>`
  }
  
    const handleSubmit = (e) => {
    e.preventDefault()
    const finalFormData = {
      ...formData,
      instructions: JSON.stringify(Instructions)
    }
    console.log(finalFormData)
    if (editingAgent) {
      // Update existing agent
      if (!finalFormData.instructions.trim()) {
        alert('Instructions are required')
        return
      }
      updateMutation.mutate({
        id: editingAgent.id,
        data: finalFormData
      })
    } else {
      // Create new agent
      if (!selectedApiKeyId) {
        alert('Please select an API key')
        return
      }
      if (!finalFormData.instructions.trim()) {
        alert('Instructions are required')
        return
      }
      /////sending to the backend
      createMutation.mutate({
        ...finalFormData,
        openai_key_id: parseInt(selectedApiKeyId)
      })
    }
  }

const handleEdit = (agent) => {
  setEditingAgent(agent)

  // Default structure for instructions
  const defaultInstructions = {
    voice_behaviour: "",
    scope: '',
    contact_details: '',
    privacy_rules: '',
    top_features: '',
    product: '',
    services: '',
    office_locations: '',
    pricing_rules: '',
    restrictions: '',
    tone_examples: '',
    additional_instructions: ''
  }

  let parsedInstructions = { ...defaultInstructions }

  // Handle instructions parsing
  if (agent.instructions) {
    if (typeof agent.instructions === 'object') {
      // Already an object, use it directly
      parsedInstructions = { ...defaultInstructions, ...agent.instructions }
    } else if (typeof agent.instructions === 'string') {
      try {
        // Try to parse as JSON
        const parsed = JSON.parse(agent.instructions)
        if (typeof parsed === 'object' && parsed !== null) {
          parsedInstructions = { ...defaultInstructions, ...parsed }
        } else {
          // If parsed value is not an object, treat as plain text in voice_behaviour
          parsedInstructions = { ...defaultInstructions, voice_behaviour: agent.instructions }
        }
      } catch (error) {
        // If parsing fails, it's plain text - put it in voice_behaviour
        parsedInstructions = { ...defaultInstructions, voice_behaviour: agent.instructions }
      }
    }
  }

  setInstructions(parsedInstructions)
  setFormData({
    name: agent.name,
    domain: agent.domain,
    instructions: agent.instructions, 
    voice: agent.voice,
    noise_reduction_mode: agent.noise_reduction_mode,
    noise_reduction_threshold: agent.noise_reduction_threshold,
    noise_reduction_prefix_padding_ms: agent.noise_reduction_prefix_padding_ms,
    noise_reduction_silence_duration_ms: agent.noise_reduction_silence_duration_ms
  })
  setShowEditModal(true)
}


  const handleGenerateWidget = async (agent) => {
    try {
      setTab("float") // Set initial tab to float
      const data = await agentService.generateWidgetCode(agent.id)
      setWidgetCode(data.widget_code)
      setWidgetId(data.widget_id || null)
      setSelectedAgentForWidget(agent)
      setShowWidgetModal(true)
    } catch (error) {
      console.error('Error generating widget code:', error)
      alert('Failed to generate widget code: ' + (error.response?.data?.detail || error.message))
    }
  }
  const handleGenerateWidgetFixed = async (agent) => {
    try {
      const data = await agentService.generateWidgetCodeFixed(agent.id)
      setWidgetCode(data.widget_code)
      setSelectedAgentForWidget(agent)
      setShowWidgetModal(true)
    } catch (error) {
      console.error('Error generating widget code:', error)
      alert('Failed to generate widget code: ' + (error.response?.data?.detail || error.message))
    }
  }
  

  const handleCopyWidgetCode = async () => {
    if (widgetCode) {
      try {
        // Try modern Clipboard API first (requires HTTPS or localhost)
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(widgetCode)
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        } else {
          // Fallback for browsers without Clipboard API (HTTP, older browsers)
          const textArea = document.createElement('textarea')
          textArea.value = widgetCode
          textArea.style.position = 'fixed'
          textArea.style.left = '-999999px'
          textArea.style.top = '-999999px'
          document.body.appendChild(textArea)
          textArea.focus()
          textArea.select()
          try {
            document.execCommand('copy')
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
          } catch (err) {
            console.error('Fallback copy failed:', err)
            alert('Failed to copy. Please select and copy the code manually.')
          }
          document.body.removeChild(textArea)
        }
      } catch (err) {
        console.error('Copy failed:', err)
        // Fallback method
        const textArea = document.createElement('textarea')
        textArea.value = widgetCode
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        try {
          document.execCommand('copy')
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        } catch (fallbackErr) {
          console.error('Fallback copy failed:', fallbackErr)
          alert('Failed to copy. Please select and copy the code manually.')
        }
        document.body.removeChild(textArea)
      }
    }
  }
  function convertJsonToPrompt(){
return `
voice&behaviour
${"hello"}
`
  }

  const handleCancelEdit = () => {
    setEditingAgent(null)
    setShowAddForm(false)
    setShowEditModal(false)
    setFormData({
      name: '',
      domain: '',
      instructions: '',
      voice: 'alloy',
      noise_reduction_mode: 'near_field',
      noise_reduction_threshold: '0.5',
      noise_reduction_prefix_padding_ms: 300,
      noise_reduction_silence_duration_ms: 500
    })
    setSelectedApiKeyId('')
  }


  // Auto-select first API key if none selected
  useEffect(() => {
    if (!fetchApiKeyId && activeApiKeys.length > 0){
      setFetchApiKeyId(String(activeApiKeys[0].id))
    }
  }, [activeApiKeys, fetchApiKeyId])

  if (keysLoading) return <div>Loading...</div>

  // Check if user has active API keys
  if (activeApiKeys.length === 0) {
    return (
      <div className="agents">
        <div className="page-header">
          <h1>Agents</h1>
        </div>
        <div className="no-api-keys-message">
          <p>You must create an Open AI Api Key First</p>
        </div>
      </div>
    )
  }

  return (
    <div className="agents">
      <div className="page-header">
        <h1>Agents</h1>
        <div className="header-actions">
          <select
            value={fetchApiKeyId}
            onChange={(e) => {
              setFetchApiKeyId(e.target.value)
              queryClient.invalidateQueries(['agents'])
            }}
            className="api-key-selector"
            title="Select API Key to fetch agents"
            required
          >
            <option value="">Select API Key</option>
            {activeApiKeys.map((key) => (
              <option key={key.id} value={key.id}>
                {key.key_name}
              </option>
            ))}
          </select>
          <button onClick={() => {
            if (showAddForm) {
              handleCancelEdit()
            } else {
              setShowAddForm(true)
              setShowEditModal(false)
            }
          }}>
            {showAddForm ? 'Cancel' : '+ Create Agent'}
          </button>
        </div>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="add-agent-form">
          <div className="form-info">
            <p><strong>Note:</strong> Agent configurations are stored locally and will be used when making WebRTC calls to OpenAI Realtime API.</p>
          </div>
          <select
            value={selectedApiKeyId}
            onChange={(e) => setSelectedApiKeyId(e.target.value)}
            autoComplete="off"
            required
          >
            <option value="">Select API Key</option>
            {activeApiKeys.map((key) => (
              <option key={key.id} value={key.id}>
                {key.key_name}
              </option>
            ))}
          </select>
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
                 <textarea value={Instructions.voice_behaviour} name="voice_behaviour" autoComplete='off'  rows={5} placeholder="Voice and Behavior (example: You are Maria, a personal assistant. You are a female. Answer in a soft tone. For any background noise, miswritten or understandable questions, tell the user - I didn't understand that, can you please repeat what you asked?)" onChange={InstructionSet}/>
          <label>Scope/What I Can Talk About</label>
          <textarea value={Instructions.scope} name="scope" autoComplete='off'  rows={5} placeholder="Scope (example: Provide information only about Demo Technologies. If user asks about other companies or unrelated topics, say: I can only provide information about Demo Technologies. How may I help you regarding our services or products?)" onChange={InstructionSet}/>
          <label>Allowed Contact Details</label>
          <textarea value={Instructions.contact_details} name="contact_details" autoComplete='off'  rows={5} placeholder="Contact Details (example: Email, sales (phone no), HR)"  onChange={InstructionSet}/>
          <label>Privacy Rules</label>
          <textarea value={Instructions.privacy_rules} name="privacy_rules" autoComplete='off'  rows={5} placeholder="Privacy Rules (example: Do not share personal information)" onChange={InstructionSet} />
         
          <label>Top Features</label>
          <textarea value={Instructions.top_features} name="top_features" autoComplete='off'  rows={5} placeholder="Top Features (example: 1. Web and Mobile Development)" onChange={InstructionSet}/>
          <label>Products</label>
          <textarea value={Instructions.product} name="product" autoComplete='off'  rows={5} placeholder="Products (example: Mention your products here)" onChange={InstructionSet}/>
          <label>Services</label>
          <textarea value={Instructions.services} name="services" autoComplete='off'  rows={5} placeholder="Services (example: Add the services you provide)" onChange={InstructionSet}/>
          <label>Office Locations</label>
          <textarea value={Instructions.office_locations} name="office_locations" autoComplete='off'  rows ={5} placeholder="Office Locations (example: USA, India)" onChange={InstructionSet}/>
          <label>Pricing Rules</label>
          <textarea value={Instructions.pricing_rules} name="pricing_rules" autoComplete="off"  rows={5} placeholder="Pricing Rules (example: Do not provide specific prices)" onChange={InstructionSet}/>
          <label>Restrictions</label>
          <textarea value={Instructions.restrictions} name="restrictions" autoComplete="off"  rows={5} placeholder="Restrictions (example: Do not provide personal information)" onChange={InstructionSet}/>
          <label>Tone Examples</label>
          <textarea value={Instructions.tone_examples} name="tone_examples" autoComplete='off'  rows={5} placeholder="Tone Examples (example: 1. Greeting: Enter your type)" onChange={InstructionSet}/>
          <label>Additional Instructions</label>
          <textarea value={Instructions.additional_instructions} name="additional_instructions" autoComplete="off"  rows={5} placeholder="Additional Instructions (example: Add the additional instructions you want to enhance your assistant)" onChange={InstructionSet}/>
     
         
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
              placeholder="0.5"
            />
          </label>
          <label>
            Prefix Padding (ms):
            <input
              type="number"
              value={formData.noise_reduction_prefix_padding_ms}
              onChange={(e) => setFormData({ ...formData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 300 })}
              autoComplete="off"
              min="0"
            />
          </label>
          <label>
            Silence Duration (ms):
            <input
              type="number"
              value={formData.noise_reduction_silence_duration_ms}
              onChange={(e) => setFormData({ ...formData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 500 })}
              autoComplete="off"
              min="0"
            />
          </label>
          <button type="submit" disabled={createMutation.isLoading}>
            {createMutation.isLoading ? 'Creating...' : 'Create Agent'}
          </button>
        </form>
      )}

      <div className="agents-list">
        {isLoading ? (
          <div>Loading agents...</div>
        ) : agents?.length === 0 ? (
          <p>No agents created yet.</p>
        ) : (
          agents?.map((agent) => (
            <div
              key={agent.id}
              className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
              onClick={() => setSelectedAgent(agent)}
            >
              <div className="agent-card-header">
                <h3>{agent.name}</h3>
                <button
                  className="view-instructions-btn"
                  onClick={(e) => {
                    e.stopPropagation()
               
                  
                    setSelectedInstructionsAgent(agent)
                  }}
                  title="View Instructions"
                >
                  ℹ️
                </button>
              </div>
              <div className="agent-meta">
                <span><strong>Domain:</strong> {agent.domain}</span>
                <span>Voice: {agent.voice}</span>
                <span>Noise Reduction: {agent.noise_reduction_mode}</span>
              </div>
              {selectedAgent?.id === agent.id && (
                <div className="agent-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleGenerateWidget(agent)
                    }}
                    className="widget-btn"
                  >
                    Get Widget Code
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEdit(agent)
                    }}
                    className="edit-btn"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (window.confirm('Are you sure you want to delete this agent?')) {
                        deleteMutation.mutate(agent.id)
                      }
                    }}
                    className="delete-btn"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {selectedAgent && (
        <div className="agent-details">
          <h2>{selectedAgent.name} - Configuration</h2>
          <div className="agent-info">
            <div className="info-section">
              <h3>Settings</h3>
              <div className="settings-grid">
                <div><strong>Domain:</strong> {selectedAgent.domain}</div>
                <div><strong>Voice:</strong> {selectedAgent.voice}</div>
                <div><strong>Noise Reduction:</strong> {selectedAgent.noise_reduction_mode}</div>
                <div><strong>VAD Threshold:</strong> {selectedAgent.noise_reduction_threshold}</div>
                <div><strong>Prefix Padding:</strong> {selectedAgent.noise_reduction_prefix_padding_ms}ms</div>
                <div><strong>Silence Duration:</strong> {selectedAgent.noise_reduction_silence_duration_ms}ms</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editingAgent && (
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
                 <textarea value={Instructions.voice_behaviour} name="voice_behaviour" autoComplete='off'  rows={5} placeholder="Voice and Behavior (example: You are Maria, a personal assistant. You are a female. Answer in a soft tone. For any background noise, miswritten or understandable questions, tell the user - I didn't understand that, can you please repeat what you asked?)" onChange={InstructionSet}/>
          <label>Scope/What I Can Talk About</label>
          <textarea value={Instructions.scope} name="scope" autoComplete='off'  rows={5} placeholder="Scope (example: Provide information only about Demo Technologies. If user asks about other companies or unrelated topics, say: I can only provide information about Demo Technologies. How may I help you regarding our services or products?)" onChange={InstructionSet}/>
          <label>Allowed Contact Details</label>
          <textarea value={Instructions.contact_details} name="contact_details" autoComplete='off'  rows={5} placeholder="Contact Details (example: Email, sales (phone no), HR)"  onChange={InstructionSet}/>
          <label>Privacy Rules</label>
          <textarea value={Instructions.privacy_rules} name="privacy_rules" autoComplete='off'  rows={5} placeholder="Privacy Rules (example: Do not share personal information)" onChange={InstructionSet} />
         
          <label>Top Features</label>
          <textarea value={Instructions.top_features} name="top_features" autoComplete='off'  rows={5} placeholder="Top Features (example: 1. Web and Mobile Development)" onChange={InstructionSet}/>
          <label>Products</label>
          <textarea value={Instructions.product} name="product" autoComplete='off'  rows={5} placeholder="Products (example: Mention your products here)" onChange={InstructionSet}/>
          <label>Services</label>
          <textarea value={Instructions.services} name="services" autoComplete='off'  rows={5} placeholder="Services (example: Add the services you provide)" onChange={InstructionSet}/>
          <label>Office Locations</label>
          <textarea value={Instructions.office_locations} name="office_locations" autoComplete='off'  rows ={5} placeholder="Office Locations (example: USA, India)" onChange={InstructionSet}/>
          <label>Pricing Rules</label>
          <textarea value={Instructions.pricing_rules} name="pricing_rules" autoComplete="off"  rows={5} placeholder="Pricing Rules (example: Do not provide specific prices)" onChange={InstructionSet}/>
          <label>Restrictions</label>
          <textarea value={Instructions.restrictions} name="restrictions" autoComplete="off"  rows={5} placeholder="Restrictions (example: Do not provide personal information)" onChange={InstructionSet}/>
          <label>Tone Examples</label>
          <textarea value={Instructions.tone_examples} name="tone_examples" autoComplete='off'  rows={5} placeholder="Tone Examples (example: 1. Greeting: Enter your type)" onChange={InstructionSet}/>
          <label>Additional Instructions</label>
          <textarea value={Instructions.additional_instructions} name="additional_instructions" autoComplete="off"  rows={5} placeholder="Additional Instructions (example: Add the additional instructions you want to enhance your assistant)" onChange={InstructionSet}/>
     
         
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
                    placeholder="0.5"
                  />
                </label>
                <label>
                  Prefix Padding (ms):
                  <input
                    type="number"
                    value={formData.noise_reduction_prefix_padding_ms}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_prefix_padding_ms: parseInt(e.target.value) || 300 })}
                    autoComplete="off"
                    min="0"
                  />
                </label>
                <label>
                  Silence Duration (ms):
                  <input
                    type="number"
                    value={formData.noise_reduction_silence_duration_ms}
                    onChange={(e) => setFormData({ ...formData, noise_reduction_silence_duration_ms: parseInt(e.target.value) || 500 })}
                    autoComplete="off"
                    min="0"
                  />
                </label>
                <div className="form-actions">
                  <button type="button" onClick={() => handleCancelEdit()} className="cancel-btn">
                    Cancel
                  </button>
                  <button type="submit" disabled={updateMutation.isLoading}>
                    {updateMutation.isLoading ? 'Updating...' : 'Update Agent'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

    {showWidgetModal && selectedAgentForWidget && (
  <div className="modal-overlay" onClick={() => {
    setShowWidgetModal(false)
    setWidgetCode(null)
    setWidgetId(null)
    setCopied(false)
  }}>
    <div
      className="modal-content"
      onClick={(e) => e.stopPropagation()} 
    >
      <div className="modal-header">
        <h3>Widget Code - {selectedAgentForWidget.name}</h3>
        <button className="modal-close" onClick={() => {
          setShowWidgetModal(false)
          setWidgetCode(null)
          setWidgetId(null)
          setCopied(false)
        }}>×</button>
      </div>

      <div className="modal-body">
      
        <div className="chrome-tabs">
          <button
            className={tab === "float" ? "active" : ""}
            onClick={() => handleTabChange("float")}
          >
            Floating
          </button>
          <button
            className={tab === "static" ? "active" : ""}
            onClick={() => handleTabChange("static")}
          >
            Static
          </button>
        </div>

        <div className="widget-code-section">
          <div className="code-header">
            <span>
              Copy this code to integrate the widget on <strong>{selectedAgentForWidget.domain}</strong>
            </span>
            <button onClick={handleCopyWidgetCode} className="copy-btn">
              {copied ? "✓ Copied!" : "Copy Code"}
            </button>
          </div>

          <pre className="widget-code">
            <code>{widgetCode || "Loading..."}</code>
          </pre>

          <div className="widget-info">
            <p><strong>Widget ID:</strong> {widgetId || "N/A"}</p>
            <p><strong>Agent ID:</strong> {selectedAgentForWidget.id}</p>
            <p><strong>Domain:</strong> {selectedAgentForWidget.domain}</p>
            <p className="widget-note">
              <strong>Note:</strong> This widget code should only be used on <strong>{selectedAgentForWidget.domain}</strong> or its subdomains.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
)}



      {selectedInstructionsAgent && (
        <div className="modal-overlay" onClick={() => setSelectedInstructionsAgent(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>System Instructions - {selectedInstructionsAgent.name}</h3>
              <button className="modal-close" onClick={() => setSelectedInstructionsAgent(null)}>×</button>
            </div>
            <div className="modal-body">
             <div className="instructions-text"
  dangerouslySetInnerHTML={{
    __html: convertJsonPrompt(selectedInstructionsAgent.instructions),
  }}
></div>
            </div>)
          </div>
        </div>
      )}
    </div>
  )
}

export default Agents

