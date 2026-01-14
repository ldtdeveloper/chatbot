import React from 'react'

function InstructionsModal({ selectedInstructionsAgent, convertJsonPrompt, onClose }) {
  if (!selectedInstructionsAgent) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>System Instructions - {selectedInstructionsAgent.name}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="instructions-text"
            dangerouslySetInnerHTML={{
              __html: convertJsonPrompt(selectedInstructionsAgent.instructions),
            }}
          ></div>
        </div>
      </div>
    </div>
  )
}

export default InstructionsModal

