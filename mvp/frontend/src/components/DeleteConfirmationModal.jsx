import React from 'react';

const DeleteConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = "Delete Agent", 
  message = "Are you sure you want to delete this agent? This action cannot be undone.",
  confirmText = "Yes, Delete",
  icon = "🗑️"
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '420px', padding: '0', borderRadius: '16px', overflow: 'hidden' }}
      >
        <div style={{ padding: '28px 28px 0 28px', textAlign: 'center' }}>
          <div style={{
            width: '56px', height: '56px', borderRadius: '50%',
            background: '#fef2f2', margin: '0 auto 16px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '26px'
          }}> {icon} </div>
          <h3 style={{ margin: '0 0 8px 0', color: '#111827', fontSize: '18px', fontWeight: 700 }}>
            {title}
          </h3>
          <p style={{ margin: '0 0 24px 0', color: '#6b7280', fontSize: '14px', lineHeight: '1.5' }}>
            {message}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', padding: '0 28px 28px 28px' }}>
          <button
            onClick={onClose}
            style={{
              flex: 1, padding: '10px', borderRadius: '8px',
              border: '1px solid #e5e7eb', background: 'white',
              color: '#374151', fontWeight: 600, cursor: 'pointer', fontSize: '14px'
            }}
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            style={{
              flex: 1, padding: '10px', borderRadius: '8px',
              border: 'none', background: 'linear-gradient(120deg, #f87171 0%, #ef4444 100%)',
              color: 'white', fontWeight: 600, cursor: 'pointer', fontSize: '14px',
              boxShadow: '0 4px 12px rgba(239,68,68,0.3)'
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal;
