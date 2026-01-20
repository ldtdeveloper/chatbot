import React, { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService, openAIKeyService } from '../services/services'
import '../styles/Agents.css'
import AppIconsCard from '../components/mcpservercard.jsx';
import { showSuccess,showError } from '../utils/toast.js';
import AgentCategorySelector from '../components/AgentCategorySelector';
import WebAgentsSection from '../components/WebAgentsSection';
import PhoneAgentsSection from '../components/PhoneAgentsSection';
import EditAgentModal from '../components/EditAgentModal';
import WidgetModal from '../components/WidgetModal';
import InstructionsModal from '../components/InstructionsModal';
import WalletModal from '../components/WalletModal';
import { useAuthStore } from '../context/authStore';
import { authService } from '../services/services';

function Agents() {
  console.log("compnoent re renderd ----------------")
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
  const [activeCategory, setActiveCategory] = useState('web')
  const [phoneApiKeyId, setPhoneApiKeyId] = useState('')
  const [showPhoneAddForm, setShowPhoneAddForm] = useState(false)
  const [checked, setChecked] = useState(false);
  const [showMcpServerCard, setShowMcpServerCard] = useState(false);
  const [Instructions, setInstructions] = useState({
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
  });

  useEffect(() => {
    if (selectedAgent) {
      console.log("Selected Agent changed:", selectedAgent.enable_mcp_server);
          setChecked(selectedAgent.enable_mcp_server);
          setShowMcpServerCard(selectedAgent.enable_mcp_server || false)
        }
      }, [selectedAgent]);
      
  const handleChange = async (e) => {
    // Stop event propagation to prevent card from closing
    if (e && e.stopPropagation) {
      e.stopPropagation();
    }
    
    if(e.target.checked){
      try{
        const response = await agentService.update(
        selectedAgent.id,
        { enable_mcp_server: true});
        // Update the query cache directly to keep state in sync
        queryClient.setQueryData(['agents', fetchApiKeyId, 'WEB'], (oldData) => {
          if (!oldData) return oldData;
          return oldData.map(agent => 
            agent.id === selectedAgent.id 
              ? { ...agent, enable_mcp_server: true }
              : agent
          );
        });
        // Update selectedAgent with the response data to keep state in sync
        // agentService.update returns the full response, so access response.data
        const updatedAgent = response?.data || { ...selectedAgent, enable_mcp_server: true };
        setSelectedAgent(updatedAgent);
        setChecked(true);
        setShowMcpServerCard(true);
        // Also invalidate to refetch and ensure consistency
        queryClient.invalidateQueries(['agents']);
        // Keep the card open when enabling
        setTimeout(() => {
        document.getElementById("mcpservercard").scrollIntoView({
        behavior: "smooth",
      });
        }, 200);
        showSuccess(`MCP server enabled`);
      }
      catch(error){
        showError(`Something went wrong while enabling the MCP server`)
      }
    }
    else{
      try{
        const response = await agentService.update(
        selectedAgent.id,
        { enable_mcp_server: false }
        );
        // Update the query cache directly to keep state in sync
        queryClient.setQueryData(['agents', fetchApiKeyId, 'WEB'], (oldData) => {
          if (!oldData) return oldData;
          return oldData.map(agent => 
            agent.id === selectedAgent.id 
              ? { ...agent, enable_mcp_server: false }
              : agent
          );
        });
        // Also invalidate to refetch and ensure consistency
        queryClient.invalidateQueries(['agents']);
        // Always trust backend - update state immediately
        setChecked(false);
        setShowMcpServerCard(false);
        // Close the agent card when disabling
        setSelectedAgent(null);
        setSelectedAgentForWidget(null);
        setShowWidgetModal(false);
        showSuccess(`MCP server disabled`);
        } catch(error){
          showError(`Something went wrong while disabling the MCP server`)
        }
      }
  }

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
    noise_reduction_threshold: '0.65',  // Optimized: higher = fewer false starts = lower cost
    noise_reduction_prefix_padding_ms: 150,  // Optimized: reduced from 300 = faster responses
    noise_reduction_silence_duration_ms: 600,  // Optimized: balanced for speed and quality
    startup_message: ''  // Startup message that bot sends automatically when chat starts
  })

  const [phoneFormData, setPhoneFormData] = useState({
    name: '',
    phone_number: '',
    sip_server: '',
    sip_username: '',
    sip_password: '',
    sip_domain: '',
    instructions: '',
    voice: 'alloy',
    noise_reduction_mode: 'near_field',
    noise_reduction_threshold: '0.65',  // Optimized: higher = fewer false starts = lower cost
    noise_reduction_prefix_padding_ms: 150,  // Optimized: reduced from 300 = faster responses
    noise_reduction_silence_duration_ms: 600  // Optimized: balanced for speed and quality
  })
  const [selectedAgentForWidget, setSelectedAgentForWidget] = useState(null)
  const [widgetCode, setWidgetCode] = useState(null)
  const [widgetId, setWidgetId] = useState(null)
  const [copied, setCopied] = useState(false)
  const cardsContainerRef = useRef(null)
  const phoneCardsRef = useRef(null)
  const [selectedPhoneAgentId, setSelectedPhoneAgentId] = useState(null)
  const [showWalletModal, setShowWalletModal] = useState(false)
  const { user, setAuth } = useAuthStore()

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents', fetchApiKeyId, 'WEB'],
    queryFn: () => {
      if (!fetchApiKeyId) {
        return Promise.resolve([])
      }
      return agentService.list(parseInt(fetchApiKeyId), 'WEB')
    },
    enabled: !!fetchApiKeyId,
  })

  const { data: phoneAgents, isLoading: phoneAgentsLoading } = useQuery({
    queryKey: ['agents', phoneApiKeyId, 'PHONE'],
    queryFn: () => {
      if (!phoneApiKeyId) {
        return Promise.resolve([])
      }
      return agentService.list(parseInt(phoneApiKeyId), 'PHONE')
    },
    enabled: !!phoneApiKeyId,
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
      showSuccess(`Agent created successfully`);
    },
    onError: (error) => {
      // Check if it's a payment required error (402 - insufficient wallet balance)
      if (error?.response?.status === 402) {
        setShowWalletModal(true)
      } else {
        showError(error?.response?.data?.detail || 'Failed to create agent. Please try again.')
      }
    },
  })

  const createPhoneMutation = useMutation({
    mutationFn: agentService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setShowPhoneAddForm(false)
      handleCancelPhoneEdit()
      showSuccess(`Phone agent created successfully`);
    },
    onError: (error) => {
      // Check if it's a payment required error (402 - insufficient wallet balance)
      if (error?.response?.status === 402) {
        setShowWalletModal(true)
      } else {
        showError(error?.response?.data?.detail || 'Failed to create phone agent. Please try again.')
      }
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
      showSuccess(`Agent updated successfully`)
    },
    onError: (error) =>{
      showError(error)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: agentService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setSelectedAgent(null)
      showSuccess(`Agent deleted successfully`)
    },
  })
  function convertJsonPrompt(data) {
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
      noise_reduction_silence_duration_ms: agent.noise_reduction_silence_duration_ms,
      startup_message: agent.startup_message || ''
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


  const handleCopyWidgetCode = async (e) => {
    // CRITICAL: Stop event propagation immediately to prevent modal from closing
    if (e) {
      e.stopPropagation()
      e.preventDefault()
    }

    console.log('Copy button clicked, widgetCode:', widgetCode ? 'exists' : 'null', 'Length:', widgetCode?.length)

    if (!widgetCode) {
      console.warn('No widget code to copy')
      alert('No widget code available to copy. Please wait for it to load.')
      return
    }

    // Method 1: Try modern Clipboard API (works on HTTPS and localhost)
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(widgetCode)
        console.log('✅ Copied using Clipboard API')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
        return
      } catch (clipboardErr) {
        console.warn('Clipboard API failed:', clipboardErr)
        // Continue to fallback
      }
    }

    // Method 2: Fallback using textarea (works everywhere)
    try {
      const textArea = document.createElement('textarea')
      textArea.value = widgetCode
      textArea.style.position = 'fixed'
      textArea.style.top = '0'
      textArea.style.left = '0'
      textArea.style.width = '2em'
      textArea.style.height = '2em'
      textArea.style.padding = '0'
      textArea.style.border = 'none'
      textArea.style.outline = 'none'
      textArea.style.boxShadow = 'none'
      textArea.style.background = 'transparent'
      textArea.style.opacity = '0'
      textArea.setAttribute('readonly', '')
      textArea.setAttribute('aria-hidden', 'true')

      document.body.appendChild(textArea)

      // For iOS devices
      if (navigator.userAgent.match(/ipad|iphone/i)) {
        const range = document.createRange()
        range.selectNodeContents(textArea)
        const selection = window.getSelection()
        selection.removeAllRanges()
        selection.addRange(range)
        textArea.setSelectionRange(0, 999999)
      } else {
        textArea.select()
        textArea.setSelectionRange(0, widgetCode.length)
      }

      const successful = document.execCommand('copy')
      document.body.removeChild(textArea)

      if (successful) {
        console.log('✅ Copied using execCommand')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } else {
        throw new Error('execCommand returned false')
      }
    } catch (err) {
      console.error('All copy methods failed:', err)
      // Last resort: Show the code in an alert or prompt
      const userConfirmed = confirm(
        'Automatic copy failed. Would you like to see the code to copy it manually?'
      )
      if (userConfirmed) {
        prompt('Copy this code:', widgetCode)
      }
    }
  }

  const handleCardClick = (agent) => {
    if (selectedAgent?.id === agent.id) {
      setSelectedAgent(null)
      setSelectedAgentForWidget(null)
      setShowWidgetModal(false)
    } else {
      setSelectedAgent(agent)
      setSelectedPhoneAgentId(null)
    }
  }

  const handlePhoneCardClick = (agent, e) => {
    e.stopPropagation()
    e.preventDefault()
    // Toggle: if this card is already selected, deselect it
    const willBeSelected = selectedPhoneAgentId !== agent.id
    if (willBeSelected) {
      // Select only this card - clear web agent selection
      setSelectedAgent(null)
      setSelectedAgentForWidget(null)
      setShowWidgetModal(false)
    }
    // Update phone agent selection
    setSelectedPhoneAgentId(willBeSelected ? agent.id : null)
  }

  const handleCancel = () =>{
    setShowAddForm(false);
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
      noise_reduction_threshold: '0.65',  // Optimized: higher = fewer false starts = lower cost
      noise_reduction_prefix_padding_ms: 150,  // Optimized: reduced from 300 = faster responses
      noise_reduction_silence_duration_ms: 600  // Optimized: balanced for speed and quality
    })
    setSelectedApiKeyId('')
    setInstructions({
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
    })
  }

  const handleCancelPhoneEdit = () => {
    setShowPhoneAddForm(false)
    setPhoneFormData({
      name: '',
      phone_number: '',
      sip_server: '',
      sip_username: '',
      sip_password: '',
      sip_domain: '',
      instructions: '',
      voice: 'alloy',
      noise_reduction_mode: 'near_field',
      noise_reduction_threshold: '0.65',  // Optimized: higher = fewer false starts = lower cost
      noise_reduction_prefix_padding_ms: 150,  // Optimized: reduced from 300 = faster responses
      noise_reduction_silence_duration_ms: 600  // Optimized: balanced for speed and quality
    })
    setInstructions({
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
    })
  }

  const handlePhoneSubmit = (e) => {
    e.preventDefault()
    const finalFormData = {
      ...phoneFormData,
      agent_type: 'PHONE',
      instructions: JSON.stringify(Instructions)
    }
    if (!phoneApiKeyId) {
      alert('Please select an API key')
      return
    }
    if (!finalFormData.instructions.trim()) {
      alert('Instructions are required')
      return
    }
    if (!finalFormData.phone_number) {
      alert('Phone number is required')
      return
    }
    if (!finalFormData.sip_server) {
      alert('SIP server is required')
      return
    }
    createPhoneMutation.mutate({
      ...finalFormData,
      openai_key_id: parseInt(phoneApiKeyId)
    })
  }


  // Auto-select first API key if none selected
  useEffect(() => {
    if (!fetchApiKeyId && activeApiKeys.length > 0) {
      setFetchApiKeyId(String(activeApiKeys[0].id))
    }
  }, [activeApiKeys, fetchApiKeyId])

  // Auto-select first API key for phone agents if none selected
  useEffect(() => {
    if (!phoneApiKeyId && activeApiKeys.length > 0) {
      setPhoneApiKeyId(String(activeApiKeys[0].id))
    }
  }, [activeApiKeys, phoneApiKeyId])

  // Close selected phone card on outside click
  useEffect(() => {
  if (activeApiKeys.length > 0) {
    setSelectedApiKeyId(activeApiKeys[0].id);
    setFetchApiKeyId(activeApiKeys[0].id); // for fetch dropdown
  }
}, [activeApiKeys]);

  useEffect(() => {
    function handleOutsideClickPhone(e) {
      if (!selectedPhoneAgentId) return

      const target = e.target

      // Don't close if clicking inside any modal
      const clickedModal = target.closest('.modal-overlay') || target.closest('.modal-content')
      if (clickedModal) {
        return // Don't close when clicking inside modals
      }

      // Don't close if clicking on buttons or interactive elements (including Switch)
      if (target.closest('button') || target.closest('input') || target.closest('select') || target.closest('textarea') || target.closest('[role="switch"]') || target.closest('.MuiSwitch-root')) {
        return
      }

      const container = phoneCardsRef.current
      if (!container) return

      const selectedCard = container.querySelector('.agent-card.selected')
      if (selectedCard && selectedCard.contains(target)) return

      // Close when click is outside the selected card (anywhere else, but not in modals)
      setSelectedPhoneAgentId(null)
    }
    document.addEventListener('mousedown', handleOutsideClickPhone)
    return () => document.removeEventListener('mousedown', handleOutsideClickPhone)
  }, [selectedPhoneAgentId])

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
      </div>

      <AgentCategorySelector 
        activeCategory={activeCategory}
        setActiveCategory={setActiveCategory}
      />

      {activeCategory === 'phone' && (
        <PhoneAgentsSection
          showPhoneAddForm={showPhoneAddForm}
          setShowPhoneAddForm={setShowPhoneAddForm}
          phoneFormData={phoneFormData}
          setPhoneFormData={setPhoneFormData}
          Instructions={Instructions}
          InstructionSet={InstructionSet}
          activeApiKeys={activeApiKeys}
          handlePhoneSubmit={handlePhoneSubmit}
          createPhoneMutation={createPhoneMutation}
          phoneAgents={phoneAgents}
          phoneAgentsLoading={phoneAgentsLoading}
          selectedPhoneAgentId={selectedPhoneAgentId}
          handlePhoneCardClick={handlePhoneCardClick}
          handleEdit={handleEdit}
          deleteMutation={deleteMutation}
          phoneCardsRef={phoneCardsRef}
        />
      )}

      {activeCategory === 'web' && (
        <WebAgentsSection
          showAddForm={showAddForm}
          setShowAddForm={setShowAddForm}
          handleCancelEdit={handleCancelEdit}
          formData={formData}
          setFormData={setFormData}
          Instructions={Instructions}
          InstructionSet={InstructionSet}
          activeApiKeys={activeApiKeys}
          handleSubmit={handleSubmit}
          createMutation={createMutation}
          agents={agents}
          isLoading={isLoading}
          selectedAgent={selectedAgent}
          handleCardClick={handleCardClick}
          handleEdit={handleEdit}
          deleteMutation={deleteMutation}
          handleGenerateWidget={handleGenerateWidget}
          setSelectedInstructionsAgent={setSelectedInstructionsAgent}
          checked={checked}
          handleChange={handleChange}
          handleCancel={handleCancel}
        />
      )}
      {showMcpServerCard && <AppIconsCard setShowMcpServerCard={setShowMcpServerCard} setChecked = {setChecked} selectedAgent = {selectedAgent}/>}
      <EditAgentModal
        editingAgent={editingAgent}
        formData={formData}
        setFormData={setFormData}
        Instructions={Instructions}
        InstructionSet={InstructionSet}
        handleSubmit={handleSubmit}
        handleCancelEdit={handleCancelEdit}
        isLoading={updateMutation.isLoading}
      />
      <WidgetModal
        showWidgetModal={showWidgetModal}
        selectedAgentForWidget={selectedAgentForWidget}
        widgetCode={widgetCode}
        widgetId={widgetId}
        tab={tab}
        handleTabChange={handleTabChange}
        handleCopyWidgetCode={handleCopyWidgetCode}
        copied={copied}
        onClose={() => {
          setShowWidgetModal(false)
          setWidgetCode(null)
          setWidgetId(null)
          setCopied(false)
        }}
      />
      <InstructionsModal
        selectedInstructionsAgent={selectedInstructionsAgent}
        convertJsonPrompt={convertJsonPrompt}
        onClose={() => setSelectedInstructionsAgent(null)}
      />
      <WalletModal
        isOpen={showWalletModal}
        onClose={() => setShowWalletModal(false)}
        onWalletUpdate={async (newBalance) => {
          // Refresh user data after wallet update
          const userInfo = await authService.getMe()
          setAuth(null, userInfo)
        }}
      />
    </div>
  )
}

export default Agents

