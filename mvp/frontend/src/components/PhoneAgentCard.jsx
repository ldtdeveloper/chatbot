import React from 'react'

function PhoneAgentCard({ 
  agent, 
  isSelected, 
  onCardClick, 
  onEdit, 
  onDelete
}) {
  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onClick={onCardClick}
    >
      <div className="agent-card-header">
        <h3>{agent.name}</h3>
      </div>
      <div className="agent-meta">
        <span><strong>Phone:</strong> {agent.phone_number || 'N/A'}</span>
        <span>Voice: {agent.voice}</span>
        <span>Noise Reduction: {agent.noise_reduction_mode}</span>
      </div>
      {isSelected && (
        <>
          <div className="agent-actions">
            <button
              onClick={(e) => {
                e.stopPropagation()
                onEdit(agent)
              }}
              className="edit-btn"
            >
              <span className="btn-icon">✏️</span>
              <span>Edit</span>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                if (window.confirm('Are you sure you want to delete this phone agent?')) {
                  onDelete(agent.id)
                }
              }}
              className="delete-btn"
            >
              <span className="btn-icon">🗑️</span>
              <span>Delete</span>
            </button>
          </div>
          <div className="selected-agent-details">
            <h4>Configuration</h4>
            <div className="settings-grid">
              <div><strong>Phone Number:</strong> {agent.phone_number || 'N/A'}</div>
              <div><strong>SIP Server:</strong> {agent.sip_server || 'N/A'}</div>
              <div><strong>SIP Username:</strong> {agent.sip_username || 'N/A'}</div>
              <div><strong>SIP Domain:</strong> {agent.sip_domain || 'N/A'}</div>
              <div><strong>Voice:</strong> {agent.voice}</div>
              <div><strong>Noise Reduction:</strong> {agent.noise_reduction_mode}</div>
              <div><strong>VAD Threshold:</strong> {agent.noise_reduction_threshold}</div>
              <div><strong>Prefix Padding:</strong> {agent.noise_reduction_prefix_padding_ms}ms</div>
              <div><strong>Silence Duration:</strong> {agent.noise_reduction_silence_duration_ms}ms</div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default PhoneAgentCard


