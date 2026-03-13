import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { whatsappService } from '../services/services';
import { MessageSquare, Loader2, Plus } from 'lucide-react';
import { useAuthStore } from '../context/authStore';
import WhatsappAgentCard from './WhatsappAgentCard';
import WhatsappAgentForm from './WhatsappAgentForm';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import { showSuccess, showError } from '../utils/toast.js';
import AppIconsCard from './mcpservercard.jsx';

const WhatsappAgentsSection = ({ onEdit: onEditParent }) => {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  // UI State
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [editingAgent, setEditingAgent] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showWidgetModal, setShowWidgetModal] = useState(false);
  const [widgetCode, setWidgetCode] = useState('');
  const [selectedAgentForWidget, setSelectedAgentForWidget] = useState(null);
  const [copied, setCopied] = useState(false);
  const [checked, setChecked] = useState(false);
  const [showMcpServerCard, setShowMcpServerCard] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    phone_number_id: '',
    startup_message: '',
    onboarding_mode: 'demo',
    instructions_details: {
      voice_behaviour: '',
      scope: '',
      contact_details: '',
      additional_instructions: ''
    }
  });

  // Fetch Agents
  const { data: agents, isLoading } = useQuery({
    queryKey: ['whatsapp-agents'],
    queryFn: () => whatsappService.list(),
    enabled: !!user?.id
  });
  console.log(agents)


  // Mutations
  const createMutation = useMutation({
    mutationFn: (data) => whatsappService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-agents'] });
      showSuccess('WhatsApp agent created successfully!');
      resetForm();
    },
    onError: () => showError('Failed to create WhatsApp agent.')
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => whatsappService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-agents'] });
      showSuccess('WhatsApp agent updated successfully!');
      resetForm();
    },
    onError: () => showError('Failed to update WhatsApp agent.')
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => whatsappService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-agents'] });
    }
  });

  // Handlers
  const resetForm = () => {
    setIsFormOpen(false);
    setEditingAgent(null);
    setFormData({
      name: '',
      phone_number: '',
      phone_number_id: '',
      startup_message: '',
      onboarding_mode: 'demo',
      instructions_details: {
        voice_behaviour: '',
        scope: '',
        contact_details: '',
        additional_instructions: ''
      }
    });
  };

  const handleInstructionsChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      instructions_details: {
        ...prev.instructions_details,
        [name]: value
      }
    }));
  };

  // Compute limit: use user.allowed_agents (same as WebAgentsSection)
  const atLimit = !!(agents && user?.allowed_agents && agents.length >= user.allowed_agents);

  const handleAddClick = () => {
    if (atLimit) return;   // guard — button should be disabled but double-check
    resetForm();
    setSelectedAgent(null);
    setIsFormOpen(true);
  };

  const handleCardClick = (agent) => {
    if (selectedAgent?.id === agent.id) {
      setSelectedAgent(null);
      setChecked(false);
      setShowMcpServerCard(false);
    } else {
      setSelectedAgent(agent);
      setIsFormOpen(false); // close form when clicking a card
      setChecked(agent.enable_mcp_server || false);
      setShowMcpServerCard(agent.enable_mcp_server || false);
    }
  };

  const handleSwitchChange = async (e) => {
    // Stop event propagation to prevent card from closing
    if (e && e.stopPropagation) {
      e.stopPropagation();
    }
    
    const newCheckedState = Boolean(e.target.checked);
    
    if (newCheckedState) {
        try {
            await updateMutation.mutateAsync({ 
                id: selectedAgent.id, 
                data: { enable_mcp_server: true } 
            });
            setChecked(true);
            setShowMcpServerCard(true);
            showSuccess('MCP server enabled');
            
            // Re-sync the selected agent with the updated data
            const updatedAgents = queryClient.getQueryData(['whatsapp-agents']);
            if (updatedAgents) {
                const updated = updatedAgents.find(a => a.id === selectedAgent.id);
                if (updated) setSelectedAgent(updated);
            }
        } catch (error) {
            showError('Failed to enable MCP server');
        }
    } else {
        try {
            await updateMutation.mutateAsync({ 
                id: selectedAgent.id, 
                data: { enable_mcp_server: false } 
            });
            setChecked(false);
            setShowMcpServerCard(false);
            setSelectedAgent(null); // Close card on disable
            showSuccess('MCP server disabled');
        } catch (error) {
            showError('Failed to disable MCP server');
        }
    }
  };

  const handleEditClick = (agent) => {
    setEditingAgent(agent);

    let instructionsDetails = {
      voice_behaviour: agent.instructions || '',
      scope: '',
      contact_details: '',
      additional_instructions: ''
    };

    try {
      if (agent.instructions && agent.instructions.startsWith('{')) {
        const parsed = JSON.parse(agent.instructions);
        if (typeof parsed === 'object') {
          instructionsDetails = { ...instructionsDetails, ...parsed };
        }
      }
    } catch (e) {
      console.log('Instructions not JSON, using as string');
    }

    setFormData({
      name: agent.name,
      phone_number: agent.phone_number || '',
      phone_number_id: agent.phone_number_id || '',
      startup_message: agent.startup_message || '',
      onboarding_mode: agent.onboarding_mode || 'demo',
      instructions_details: instructionsDetails
    });
    setIsFormOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const submittedData = {
      ...formData,
      instructions: JSON.stringify(formData.instructions_details)
    };

    if (editingAgent) {
      updateMutation.mutate({ id: editingAgent.id, data: submittedData });
    } else {
      createMutation.mutate(submittedData);
    }
  };

  // Delete Handlers are now inline in the component return below

  const handleShowWidget = async (agent) => {
    setSelectedAgentForWidget(agent);
    setShowWidgetModal(true);
    try {
      const code = await whatsappService.getWidgetCode(agent.id);
      setWidgetCode(code);
    } catch (err) {
      setWidgetCode('Error loading widget code.');
    }
  };

  const handleCopyWidget = async (agent) => {
    try {
      const code = await whatsappService.getWidgetCode(agent.id);
      navigator.clipboard.writeText(code);
      showSuccess('Widget code copied to clipboard!');
    } catch (err) {
      showError('Failed to copy widget code.');
    }
  };

  const handleSendLoginUrl = async (agentId) => {
    try {
      await whatsappService.sendLoginUrl(agentId);
      showSuccess('Dashboard Login URL has been sent to your employees!');
    } catch (err) {
      showError('Failed to send login URL. Please try again.');
    }
  };

  const handleConnectMeta = async (agentId) => {
    try {
      const resp = await whatsappService.getConnectUrl(agentId);
      if (resp.redirect_url) {
        window.location.href = resp.redirect_url;
      } else {
        showError('Could not generate connection URL.');
      }
    } catch (err) {
      showError('Failed to initiate WhatsApp connection.');
    }
  };

  // --- Inline form for Create New (renders in place of the list) ---
  if (isFormOpen && !editingAgent) {
    return (
      <div id="whatsapp-agents-section" className="web-agents-container" style={{ marginTop: '40px' }}>
        <div className="page-header">
          <h2>Create New WhatsApp Agent</h2>
        </div>
        <WhatsappAgentForm
          formData={formData}
          setFormData={setFormData}
          handleInstructionsChange={handleInstructionsChange}
          handleSubmit={handleSubmit}
          isLoading={createMutation.isLoading || updateMutation.isLoading}
          isEdit={false}
          handleCancel={resetForm}
        />
      </div>
    );
  }

  return (
    <div id="whatsapp-agents-section" className="web-agents-container" style={{ marginTop: '40px' }}>

      {/* --- Modal form for Edit (pops up over the list) --- */}
      {isFormOpen && editingAgent && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit {editingAgent.name}</h3>
              <button className="modal-close" onClick={resetForm}>×</button>
            </div>
            <div className="modal-body">
              <WhatsappAgentForm
                formData={formData}
                setFormData={setFormData}
                handleInstructionsChange={handleInstructionsChange}
                handleSubmit={handleSubmit}
                isLoading={createMutation.isLoading || updateMutation.isLoading}
                isEdit={true}
                handleCancel={resetForm}
              />
            </div>
          </div>
        </div>
      )}

      <DeleteConfirmationModal
        isOpen={!!confirmDeleteId}
        onClose={() => setConfirmDeleteId(null)}
        onConfirm={() => {
          deleteMutation.mutate(confirmDeleteId);
          showSuccess('WhatsApp agent deleted successfully.');
          setConfirmDeleteId(null);
          setSelectedAgent(null);
        }}
        title="Delete WhatsApp Agent"
      />

      {/* Widget Modal */}
      {showWidgetModal && (
        <div className="modal-overlay" onClick={() => setShowWidgetModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Widget Code - {selectedAgentForWidget?.name}</h3>
              <button className="modal-close" onClick={() => setShowWidgetModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: '14px', color: '#4b5563', marginBottom: '15px' }}>
                Copy and paste this code into your website's HTML to embed the WhatsApp chat widget.
              </p>
              <pre style={{
                background: '#f3f4f6', padding: '15px', borderRadius: '8px',
                whiteSpace: 'pre-wrap', wordBreak: 'break-all',
                fontSize: '13px', fontFamily: 'monospace'
              }}>
                <code>{widgetCode || 'Loading...'}</code>
              </pre>
              <button
                className="primary-btn"
                style={{ marginTop: '15px', width: '100%' }}
                onClick={() => {
                  navigator.clipboard.writeText(widgetCode);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2000);
                }}
              >
                {copied ? 'Copied!' : 'Copy Code'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="page-header">
        <div>
          <h2>WhatsApp Agents</h2>
          <p className="subtitle">AI agents connected to your WhatsApp Business accounts.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          
          <button
  className="create-btn"
  onClick={handleAddClick}
  disabled={atLimit}
  title={atLimit ? `Your plan allows ${user?.allowed_agents} WhatsApp agent(s). Upgrade to add more.` : 'Create a new WhatsApp agent'}
  style={{
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    opacity: atLimit ? 0.5 : 1,
    cursor: atLimit ? "not-allowed" : "pointer"
  }}
>
  <Plus size={18} />
  <span>Create Agent</span>
</button>
        </div>
      </div>

      <div className="agents-list">
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
            <Loader2 className="animate-spin" style={{ margin: '0 auto 10px' }} />
            <p>Loading WhatsApp agents...</p>
          </div>
        ) : agents?.length === 0 ? (
          <p>No WhatsApp agents created yet.</p>
        ) : (
          agents?.map((agent) => (
            <WhatsappAgentCard
              key={agent.id}
              agent={agent}
              isSelected={selectedAgent?.id === agent.id}
              onCardClick={() => handleCardClick(agent)}
              onEdit={handleEditClick}
              onDelete={(id) => setConfirmDeleteId(id)}
              onShowWidget={handleShowWidget}
              onCopyWidget={handleCopyWidget}
              onSendLoginUrl={handleSendLoginUrl}
              onConnectMeta={handleConnectMeta}
              checked={selectedAgent?.id === agent.id ? checked : false}
              onSwitchChange={handleSwitchChange}
            />
          ))
        )}
      </div>
      {showMcpServerCard && (
        <AppIconsCard 
          setShowMcpServerCard={setShowMcpServerCard} 
          setChecked={setChecked} 
          selectedAgent={selectedAgent} 
          isTextAgent={true}
        />
      )}
    </div>
  );
};

export default WhatsappAgentsSection;
