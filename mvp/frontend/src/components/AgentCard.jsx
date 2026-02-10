import React from 'react'
import Switch from '@mui/material/Switch'
import { MdOutlineInfo } from "react-icons/md"
import Tooltip from "@mui/material/Tooltip"

function AgentCard({ 
  agent, 
  isSelected, 
  onCardClick, 
  onEdit, 
  onDelete, 
  onGenerateWidget,
  onViewInstructions,
  checked,
  onSwitchChange
}) {
  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onClick={onCardClick}
    >
      <div className="agent-card-header">
        <h3>{agent.name}</h3>
        <div
          className="view-instructions-btn"
          onClick={(e) => {
            e.stopPropagation()
            onViewInstructions(agent)
          }}
          title="View Instructions"
        >
          <MdOutlineInfo />
        </div>
        {isSelected && (
          <div 
            style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}
            onClick={(e) => e.stopPropagation()}
          >
            <Tooltip title="MCP Server">
              <Switch
                size="small"
                checked={checked}
                onChange={onSwitchChange}
                onClick={(e) => e.stopPropagation()}
                slotProps={{ input: { 'aria-label': 'controlled' } }}
              />
            </Tooltip>
          </div>
        )}
      </div>
      <div className="agent-meta">
        <span><strong>Domain:</strong> {agent.domain}</span>
        <span>Voice: {agent.voice}</span>
        <span>Noise Reduction: {agent.noise_reduction_mode}</span>
      </div>
      {isSelected && (
        <>
          <div className="agent-actions">
            <button
              onClick={(e) => {
                e.stopPropagation()
                onGenerateWidget(agent)
              }}
              className="widget-btn"
            >
              <span className="btn-icon">🧩</span>
              <span>Widget</span>
            </button>
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
                if (window.confirm('Are you sure you want to delete this agent?')) {
                  onDelete(agent.id)
                }
              }}
              className="delete-btn"
            >
              <span className="btn-icon">🗑️</span>
              <span>Delete</span>
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default AgentCard


