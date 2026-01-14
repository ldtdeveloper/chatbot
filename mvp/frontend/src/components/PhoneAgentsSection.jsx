import React from 'react'
import PhoneAgentCard from './PhoneAgentCard'
import PhoneAgentForm from './PhoneAgentForm'

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
                onDelete={deleteMutation.mutate}
              />
            )
          })
        )}
      </div>
    </div>
  )
}

export default PhoneAgentsSection

