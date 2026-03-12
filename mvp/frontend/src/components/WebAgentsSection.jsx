import React, { useRef } from 'react'
import AgentCard from './AgentCard'
import AddAgentForm from './AddAgentForm'
import { useAuthStore } from '../context/authStore'
import DeleteConfirmationModal from './DeleteConfirmationModal'
import { useState } from 'react'

function WebAgentsSection({ 
  showAddForm,
  setShowAddForm,
  handleCancelEdit,
  formData,
  setFormData,
  Instructions,
  InstructionSet,
  activeApiKeys,
  handleSubmit,
  createMutation,
  agents,
  isLoading,
  selectedAgent,
  handleCardClick,
  handleEdit,
  deleteMutation,
  handleGenerateWidget,
  setSelectedInstructionsAgent,
  checked,
  handleChange
}) {
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)
  const cardsContainerRef = useRef(null)
  const {user} = useAuthStore()
  const hasAgent = agents && agents.length >= user.allowed_agents;
  console.log(` Has agent value is ${hasAgent}`)
  const handleCancel = () =>{
    setShowAddForm(false)
  }
  if (showAddForm) {
    return (
      <AddAgentForm
        formData={formData}
        setFormData={setFormData}
        Instructions={Instructions}
        InstructionSet={InstructionSet}
        activeApiKeys={activeApiKeys}
        handleSubmit={handleSubmit}
        isLoading={createMutation.isLoading}
        handleCancel= {handleCancel}
      />
    );
  }


  return (
    <div id="web-agents-section" className="web-agents-container">
      <div className="page-header">
        <h2>Web Agents</h2>
        {<div className="header-actions">
          <button 
          disabled={hasAgent}
          onClick={() => {
            if(hasAgent){
              return 
            }
            if (showAddForm) {
              handleCancelEdit()
            } else {
              setShowAddForm(true)
            }
          }}>
            {showAddForm ? 'Cancel' : '+ Create Web Agent'}
          </button>
        </div>}
      </div>

      <div className="agents-list" ref={cardsContainerRef}>
        {isLoading ? (
          <div>Loading agents...</div>
        ) : agents?.length === 0 ? (
          <p>No agents created yet.</p>
        ) : (
          agents?.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              isSelected={selectedAgent?.id === agent.id}
              onCardClick={() => handleCardClick(agent)}
              onEdit={handleEdit}
              onDelete={(id) => setConfirmDeleteId(id)}
              onGenerateWidget={handleGenerateWidget}
              onViewInstructions={setSelectedInstructionsAgent}
              checked={selectedAgent?.id === agent.id ? checked : false}
              onSwitchChange={handleChange}
            />
          ))
        )}
      </div>

      <DeleteConfirmationModal
        isOpen={!!confirmDeleteId}
        onClose={() => setConfirmDeleteId(null)}
        onConfirm={() => {
          deleteMutation.mutate(confirmDeleteId)
          setConfirmDeleteId(null)
        }}
        title="Delete Web Agent"
      />
      {selectedAgent && (
        <div className="selected-agent-details">
          <h4>Configuration - {selectedAgent.name}</h4>
          <div className="settings-grid">
            <div><strong>Domain:</strong> {selectedAgent.domain}</div>
            <div><strong>Voice:</strong> {selectedAgent.voice}</div>
            <div><strong>Noise Reduction:</strong> {selectedAgent.noise_reduction_mode}</div>
            <div><strong>VAD Threshold:</strong> {selectedAgent.noise_reduction_threshold}</div>
            <div><strong>Prefix Padding:</strong> {selectedAgent.noise_reduction_prefix_padding_ms}ms</div>
            <div><strong>Silence Duration:</strong> {selectedAgent.noise_reduction_silence_duration_ms}ms</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WebAgentsSection

