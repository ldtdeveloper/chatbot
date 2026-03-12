import React from 'react'
import PhoneAgentCard from './PhoneAgentCard'
import PhoneAgentForm from './PhoneAgentForm'
import DeleteConfirmationModal from './DeleteConfirmationModal'
import { useState } from 'react'

function PhoneAgentsSection({ 
  showPhoneAddForm,
  setShowPhoneAddForm,
  phoneFormData,
  setPhoneFormData,
  Instructions,
  InstructionSet,
  activeApiKeys,
  handlePhoneSubmit,
  createPhoneMutation,
  phoneAgents,
  phoneAgentsLoading,
  selectedPhoneAgentId,
  handlePhoneCardClick,
  handleEdit,
  deleteMutation,
  phoneCardsRef
}) {
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)

  return (
    <div id="phone-agents-section" className="phone-agents-container">
      <div className="page-header">
        <h2>Phone Agents</h2>
        <div className="header-actions">
          <button
            onClick={() => setShowPhoneAddForm((prev) => !prev)}
          >
            {showPhoneAddForm ? 'Cancel' : '+ Create Phone Agent'}
          </button>
        </div>
      </div>
      {showPhoneAddForm && (
        <PhoneAgentForm
          phoneFormData={phoneFormData}
          setPhoneFormData={setPhoneFormData}
          Instructions={Instructions}
          InstructionSet={InstructionSet}
          activeApiKeys={activeApiKeys}
          handlePhoneSubmit={handlePhoneSubmit}
          isLoading={createPhoneMutation.isLoading}
        />
      )}
      <div className="agents-list" ref={phoneCardsRef}>
        {phoneAgentsLoading ? (
          <div>Loading phone agents...</div>
        ) : phoneAgents?.length === 0 ? (
          <p>No phone agents created yet.</p>
        ) : (
          phoneAgents?.map((agent) => {
            const isSelected = selectedPhoneAgentId === agent.id
            return (
              <PhoneAgentCard
                key={`phone-agent-${agent.id}`}
                agent={agent}
                isSelected={isSelected}
                onCardClick={(e) => {
                  e.stopPropagation()
                  e.preventDefault()
                  handlePhoneCardClick(agent, e)
                }}
                onEdit={handleEdit}
                onDelete={(id) => setConfirmDeleteId(id)}
              />
            )
          })
        )}
      </div>

      <DeleteConfirmationModal
        isOpen={!!confirmDeleteId}
        onClose={() => setConfirmDeleteId(null)}
        onConfirm={() => {
          deleteMutation.mutate(confirmDeleteId)
          showSuccess('Phone agent deleted successfully.')
          setConfirmDeleteId(null)
          setSelectedPhoneAgentId(null)
        }}
        title="Delete Phone Agent"
      />
    </div>
  )
}

export default PhoneAgentsSection

