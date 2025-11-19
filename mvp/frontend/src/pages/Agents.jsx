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
   const data1 =  JSON.parse(data)
    console.log(typeof(data1))
   
    

 
    // const data1 = cleanJson(data)
    // console.log("data"+data["pricing_rules"])
  

    return `
    VOICE & BEHAVIOUR
    ${data1.voice_behaviour}
    SCOPE
    ${data1.scope}
    CONTACT DETAILS
    ${data1.contact_details}
    PRIVACY_RULES
    ${data1.privacy_rules}
    TOP FEATURES
    ${data1.top_features}
    PRODUCT
    ${data1.product}
    SERVICES
    ${data1.services}
    OFFICE LOCATION
    ${data1.office_locations}
    PRICING RULES
    ${data1.pricing_rules}
    RESTRICTIONS
    ${data1.restrictions}
    TONE_EXAMPLES
    ${data1.tone_examples}
    ADDITONAL INSTRUCTIONS
    ${data1.additional_instructions}
    `


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

  let parsedInstructions = {
    // company_name: '',
    // company_website: '',
    // Services: '',
    // industries: '',
    // solutions: '',
    // contact_info: '',
    // careers_info: '',
    // voice_behavior: ""
  }

  try {
    parsedInstructions = JSON.parse(agent.instructions)
  } catch (error) {
    console.log("Failed to parse instructions", error)
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
      const data = await agentService.generateWidgetCode(agent.id)
      setWidgetCode(data.widget_code)
      setSelectedAgentForWidget(agent)
      setShowWidgetModal(true)
    } catch (error) {
      console.error('Error generating widget code:', error)
      alert('Failed to generate widget code: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleCopyWidgetCode = () => {
    if (widgetCode) {
      navigator.clipboard.writeText(widgetCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
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
         
          {/* <textarea
            placeholder="System Instructions *"
            value={formData.instructions}
            onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
            autoComplete="off"
            required
            rows={10}
          /> */}
         {/* <label>Basic Info</label>
                <input value ={Instructions.company_name} name="company_name"  placeholder='Company Name' onChange={InstructionSet}/>
                <input value ={Instructions.company_website} name="company_website"  placeholder='Company Website'  onChange={InstructionSet}/>
                <input value ={Instructions.company_domain} name="company_domain"  placeholder='Company Domain'  onChange={InstructionSet}/>
                <textarea value={Instructions.company_description} name="company_description"  autoComplete="off" required rows={3} placeholder='company description'  onChange={InstructionSet}/>
                 <input value ={Instructions.company_tagline} name="company_tagline"  placeholder='Company Tagline'  onChange={InstructionSet}/>
                 <label>Services/Pages</label>

                <input value={Instructions.services_page_url} name="services_page_url"  autoComplete="off" required rows={3} placeholder='Services Page Url (Enter your services page url)'  onChange={InstructionSet}/>
                <input value={Instructions.industries_page_url} name="industries_page_url"  autoComplete="off" required rows={3} placeholder='Industries Page Url (Enter your industries page url)'  onChange={InstructionSet}/>
                <input value={Instructions.solution_page_url} name="solution_page_url"  autoComplete="off" required rows={3} placeholder='Solutions Page Url (Enter your solution page url)'  onChange={InstructionSet}/>
                <input value={Instructions.insights_page_url} name="insights_page_url"  autoComplete="off" required rows={3} placeholder='Insights Page Url (Enter your insights page url)'  onChange={InstructionSet}/>
                <input value={Instructions.careers_page_url} name="careers_page_url"  autoComplete="off" required rows={3} placeholder='Careers Page Url (Enter your careers page url)'  onChange={InstructionSet}/>
                <input value={Instructions.contacts_page_url} name="contacts_page_url"  autoComplete="off" required rows={3} placeholder='Contacts Page Url (Enter your contacts page url)'  onChange={InstructionSet}/>
                <label>Leadership/Public Info</label>
                <textarea value={Instructions.leadership} name="leadership"  autoComplete="off" required rows={3} placeholder='Leadership Info'  onChange={InstructionSet}/>
                <label>Rules&Scope</label>
                <textarea value={Instructions.allowed_scope} name="allowed_scope"  autoComplete="off" required rows={3} placeholder='Allowed Scope'  onChange={InstructionSet}/>
                <textarea value={Instructions.forbidden_scope} name="forbidden_scope"  autoComplete="off" required rows={3} placeholder='Forbidden Scope'  onChange={InstructionSet}/>
                <textarea value={Instructions.strict_refusal_text} name="strict_refusal_text"  autoComplete="off" required rows={3} placeholder='Strict Refusal Text'  onChange={InstructionSet}/>
                <label>Greeting/Closure/Templates</label>
                <textarea value={Instructions.greeting_text} name="greeting_text"  autoComplete="off" required rows={3} placeholder='Greeting Text'  onChange={InstructionSet}/>
                <textarea value={Instructions.refusal_text} name="refusal_text"  autoComplete="off" required rows={3} placeholder='Refusal Text'  onChange={InstructionSet}/>
                <textarea value={Instructions.closure_text} name="closure_text"  autoComplete="off" required rows={3} placeholder='Closure Text'  onChange={InstructionSet}/>
                <label>Additonal Information</label>
                 <textarea value={Instructions.additional_information} name="additional_information"  autoComplete="off" required rows={3} placeholder='Additonal Information'  onChange={InstructionSet}/> */}
                 <label>Voice & Behavior</label>
                 <textarea value={Instructions.voice_behaviour} name="voice_behaviour" autoComplete='off' required rows={5} placeholder="Voice and Behavior (example: you are maria a personal assistant.you are a female.answer in soft tone.For any background noise, miss-written or understandable questions, tell user - I didnt understand that, can you please repeat what you asked?)" onChange={InstructionSet}/>
          <label><label>Scope/What I Can Talk About</label>
          <textarea value={Instructions.scope} name="scope" autoComplete='off' required rows={5} placeholder="Scope (example: Provide information only about Demo Technologies. If user asks about other companies or unrelated topics, say: I can only provide information about Demo Technologies. How may I help you regarding our services or products?)" onChange={InstructionSet}/>
          <label>Allowed Contact Details</label>
          <textarea value={Instructions.contact_details} name="contact_details" autoComplete='off' required rows={5} placeholder="Contact Details (example: Email,sales(phn no),HR)"  onChange={InstructionSet}/>
          <label>Privacy Rules</label>
          <textarea value={Instructions.privacy_rules} name="privacy_rules" autoComplete='off' required rows={5} placeholder="Privacy Rules (example: Do not share the personal information" onChange={InstructionSet} />
         
          <label>Top Features</label>
          <textarea value={Instructions.top_features} name="top_features" autoComplete='off' required rows={5} placeholder="Top Features (example:1.Web and Mobile Development)" onChange={InstructionSet}/>
          <label>Products</label>
          <textarea value={Instructions.product} name="product" autoComplete='off' required rows={5} placeholder="Products (example: Mention your products here)" onChange={InstructionSet}/>
          <label>Services</label>
          <textarea value={Instructions.services} name="services" autoComplete='off' required rows={5} placeholder="Services add the services you provide" onChange={InstructionSet}/>
          <label>Office Locations</label>
          <textarea value={Instructions.office_locations} name="office_locations" autocomplete='off' required rows ={5} placeholder="Office Locations (example:USA,India)" onChange={InstructionSet}/>
          <label>Pricing Rules</label>
          <textarea value={Instructions.pricing_rules} name="pricing_rules" autocomplete="off" required rows={5} placeholder="Pricing Rules (example: Do not provide specific prices)" onChange={InstructionSet}/>
          <label>Restrictions</label>
          <textarea value={Instructions.restrictions} name="restrictions" autocomplete="off" required rows={5} placeholder="Restrictions (example: Do not provide personal information)" onChange={InstructionSet}/>
          <label>Tone Examples</label>
          <textarea value={Instructions.tone_examples} name="tone_examples" autoComplete='off' required rows={5} placeholder="Tone Examples (example:1. Greeting:Enter your type)" onChange={InstructionSet}/>
          <label>Additional Instructions</label>
          <textarea value={Instructions.additional_instructions} name="additional_instructions" autocomplete="off" required rows={5} placeholder="Additonal instructions (example:Add the additonal instructions you want to enhance your assistant)" onChange={InstructionSet}/>
     
         
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
                {/* <textarea
                  placeholder="System Instructions *"
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  autoComplete="off"
                  required
                  rows={10}
                /> */}
              <label>Voice & Behavior</label>
                 <textarea value={Instructions.voice_behaviour} name="voice_behaviour" autoComplete='off' required rows={5} placeholder="Voice and Behavior (example: you are maria a personal assistant.you are a female.answer in soft tone.For any background noise, miss-written or understandable questions, tell user - I didnt understand that, can you please repeat what you asked?)" onChange={InstructionSet}/>
          <label>Scope/What I Can Talk About</label>
          <textarea value={Instructions.scope} name="scope" autoComplete='off' required rows={5} placeholder="Scope (example: Provide information only about Demo Technologies. If user asks about other companies or unrelated topics, say: I can only provide information about Demo Technologies. How may I help you regarding our services or products?)" onChange={InstructionSet}/>
          <label>Allowed Contact Details</label>
          <textarea value={Instructions.contact_details} name="contact_details" autoComplete='off' required rows={5} placeholder="Contact Details (example: Email,sales(phn no),HR)"  onChange={InstructionSet}/>
          <label>Privacy Rules</label>
          <textarea value={Instructions.privacy_rules} name="privacy_rules" autoComplete='off' required rows={5} placeholder="Privacy Rules (example: Do not share the personal information" onChange={InstructionSet} />
         
          <label>Top Features</label>
          <textarea value={Instructions.top_features} name="top_features" autoComplete='off' required rows={5} placeholder="Top Features (example:1.Web and Mobile Development)" onChange={InstructionSet}/>
          <label>Products</label>
          <textarea value={Instructions.product} name="product" autoComplete='off' required rows={5} placeholder="Products (example: Mention your products here)" onChange={InstructionSet}/>
          <label>Services</label>
          <textarea value={Instructions.services} name="services" autoComplete='off' required rows={5} placeholder="Services add the services you provide" onChange={InstructionSet}/>
          <label>Office Locations</label>
          <textarea value={Instructions.office_locations} name="office_locations" autocomplete='off' required rows ={5} placeholder="Office Locations (example:USA,India)" onChange={InstructionSet}/>
          <label>Pricing Rules</label>
          <textarea value={Instructions.pricing_rules} name="pricing_rules" autocomplete="off" required rows={5} placeholder="Pricing Rules (example: Do not provide specific prices)" onChange={InstructionSet}/>
          <label>Restrictions</label>
          <textarea value={Instructions.restrictions} name="restrictions" autocomplete="off" required rows={5} placeholder="Restrictions (example: Do not provide personal information)" onChange={InstructionSet}/>
          <label>Tone Examples</label>
          <textarea value={Instructions.tone_examples} name="tone_examples" autoComplete='off' required rows={5} placeholder="Tone Examples (example:1. Greeting:Enter your type)" onChange={InstructionSet}/>
          <label>Additional Instructions</label>
          <textarea value={Instructions.additional_instructions} name="additional_instructions" autocomplete="off" required rows={5} placeholder="Additonal instructions (example:Add the additonal instructions you want to enhance your assistant)" onChange={InstructionSet}/>
     
         
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

      {showWidgetModal && widgetCode && selectedAgentForWidget && (
        <div className="modal-overlay" onClick={() => setShowWidgetModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Widget Code - {selectedAgentForWidget.name}</h3>
              <button className="modal-close" onClick={() => setShowWidgetModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="widget-code-section">
                <div className="code-header">
                  <span>Copy this code to integrate the widget on <strong>{selectedAgentForWidget.domain}</strong></span>
                  <button onClick={handleCopyWidgetCode} className="copy-btn">
                    {copied ? '✓ Copied!' : 'Copy Code'}
                  </button>
                </div>
                <pre className="widget-code">
                  <code>{widgetCode}</code>
                </pre>
                <div className="widget-info">
                  <p><strong>Widget ID:</strong> {widgetCode.match(/widgetId\s*=\s*['"]([^'"]+)['"]/)?.[1] || 'N/A'}</p>
                  <p><strong>Agent ID:</strong> {selectedAgentForWidget.id}</p>
                  <p><strong>Domain:</strong> {selectedAgentForWidget.domain}</p>
                  <p className="widget-note"><strong>Note:</strong> This widget code should only be used on <strong>{selectedAgentForWidget.domain}</strong> or its subdomains.</p>
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
{console.log(selectedInstructionsAgent.instructions)}

              <pre className="instructions-text">{convertJsonPrompt(selectedInstructionsAgent.instructions)}</pre>
            </div>)
          </div>
        </div>
      )}
    </div>
  )
}

export default Agents

