import React from 'react';
import { MessageSquare, Settings, ExternalLink, Code } from 'lucide-react';

const WhatsappAgentCard = ({
  agent,
  isSelected,
  onCardClick,
  onEdit,
  onDelete,
  onShowWidget,
  onSendLoginUrl,
  onConnectMeta
}) => {
  const isConnected = agent.status === 'connected' || agent.status === 'connected_demo';

  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onClick={onCardClick}
    >
      {/* TOP: icon + name + status dot | Send URL button */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '15px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{
            width: '45px', height: '45px', borderRadius: '12px',
            background: '#f0fdf4', color: '#16a34a',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <MessageSquare size={24} />
          </div>
          <div>
            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{agent.name}</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '8px', height: '8px', borderRadius: '50%',
                background: isConnected ? '#22c55e' : '#ef4444'
              }} />
              <span style={{ fontSize: '12px', color: '#6b7280', textTransform: 'capitalize' }}>
                {agent.status.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>

        {/* Send URL always top-right */}
        <button
          onClick={(e) => { e.stopPropagation(); onSendLoginUrl(agent.id); }}
          className="secondary-btn"
          style={{ display: 'flex', width: '100px', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '8px', fontSize: '13px' }}
          title="Send Dashboard Login URL to your employees"
        >
          <ExternalLink size={14} /> Send URL
        </button>
      </div>

      {/* Number + Mode */}
      <div style={{ marginBottom: isSelected ? '20px' : '0' }}>
        <p style={{ margin: '0 0 5px 0', fontSize: '13px', color: '#6b7280' }}>
          <strong>Number:</strong> {agent.phone_number || 'Not set'}
        </p>
        <p style={{ margin: 0, fontSize: '13px', color: '#6b7280' }}>
          <strong>Mode:</strong> {agent.onboarding_mode}
        </p>
      </div>

      {/* Buttons — only when selected */}
      {isSelected && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>

          {/* Row: Edit + Delete + Widget */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '10px', gridColumn: '1 / -1' }}>
          <button
              onClick={(e) => { e.stopPropagation(); onShowWidget(agent); }}
              className="secondary-btn"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px', fontSize: '13px' }}
            >
              <Code size={10} /> Widget
            </button>

            <button
              onClick={(e) => { e.stopPropagation(); onEdit(agent); }}
              className="secondary-btn"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px', fontSize: '13px' }}
            >
              ✏️ Edit
            </button>
            
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(agent.id); }}
              className="delete-btn"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px', fontSize: '13px' }}
            >
              🗑️ Delete
            </button>

            
          </div>

          {/* Connect Meta — full width below */}
          <button
            onClick={(e) => { e.stopPropagation(); if (!isConnected) onConnectMeta(agent.id); }}
            className={isConnected ? 'verified-btn' : 'primary-btn'}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
              padding: '8px', fontSize: '13px',
              background: isConnected ? '#22c55e' : '#1877f2',
              color: 'white', border: 'none', borderRadius: '8px',
              cursor: isConnected ? 'default' : 'pointer',
              fontWeight: 600, gridColumn: '1 / -1'
            }}
            title={isConnected ? 'Meta Account Verified' : 'Connect with Meta / Google OAuth'}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {isConnected ? (
                <>
                  <div style={{
                    width: '14px', height: '14px', borderRadius: '50%',
                    background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <div style={{ width: '8px', height: '4px', borderLeft: '2px solid #22c55e', borderBottom: '2px solid #22c55e', transform: 'rotate(-45deg)', marginBottom: '2px' }} />
                  </div>
                  Meta Verified
                </>
              ) : (
                <>
                  <ExternalLink size={14} /> Connect Meta / Google
                </>
              )}
            </div>
          </button>
        </div>
      )}
    </div>
  );
};

export default WhatsappAgentCard;
