import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { whatsappService } from '../services/services';
import { MessageSquare, Loader2, Plus } from 'lucide-react';
import { useAuthStore } from '../context/authStore';
import WhatsappAgentCard from './WhatsappAgentCard';
import WhatsappAgentForm from './WhatsappAgentForm';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import { showSuccess, showError } from '../utils/toast.js';

const WhatsappAgentsSection = () => {
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

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data) => whatsappService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-agents'] });
      showSuccess('WhatsApp agent connected successfully!');
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

  const handleAddClick = () => {
    resetForm();
    setSelectedAgent(null);
    setIsFormOpen(true);
  };

  const handleCardClick = (agent) => {
    if (selectedAgent?.id === agent.id) {
      setSelectedAgent(null);
    } else {
      setSelectedAgent(agent);
      setIsFormOpen(false); // close form when clicking a card
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
        <button className="create-btn" onClick={handleAddClick}>
          <Plus size={18} /> Create Agent
        </button>
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
            />
          ))
        )}
      </div>
    </div>
  );
};

export default WhatsappAgentsSection;
