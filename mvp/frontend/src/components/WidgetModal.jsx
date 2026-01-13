import React from 'react'

function WidgetModal({ 
  showWidgetModal, 
  selectedAgentForWidget, 
  widgetCode, 
  widgetId, 
  tab, 
  handleTabChange, 
  handleCopyWidgetCode, 
  copied, 
  onClose 
}) {
  if (!showWidgetModal || !selectedAgentForWidget) return null

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        console.log('modal-overlay clicked', e)
        // Only close if clicking directly on the overlay, not on child elements
        if (e.target === e.currentTarget) {
          onClose()
        }
      }}
    >
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>Widget Code - {selectedAgentForWidget.name}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="chrome-tabs">
            <button
              type="button"
              className={tab === "float" ? "active" : ""}
              onClick={(e) => {
                e.stopPropagation()
                handleTabChange("float")
              }}
            >
              Floating
            </button>
            <button
              type="button"
              className={tab === "static" ? "active" : ""}
              onClick={(e) => {
                e.stopPropagation()
                handleTabChange("static")
              }}
            >
              Static
            </button>
          </div>

          <div className="widget-code-section">
            <div className="code-header" onClick={(e) => e.stopPropagation()}>
              <span>
                Copy this code to integrate the widget on <strong>{selectedAgentForWidget.domain}</strong>
              </span>
              <button
                type="button"
                disabled={!widgetCode}
                onClick={(e) => {
                  e.stopPropagation()
                  e.preventDefault()
                  if (widgetCode) {
                    handleCopyWidgetCode(e)
                  }
                }}
                className="copy-btn"
                style={{
                  opacity: widgetCode ? 1 : 0.6,
                  cursor: widgetCode ? 'pointer' : 'not-allowed'
                }}
              >
                {copied ? "✓ Copied!" : "Copy Code"}
              </button>
            </div>

            <pre className="widget-code">
              <code>{widgetCode || "Loading..."}</code>
            </pre>

            <div className="widget-info">
              <p><strong>Widget ID:</strong> {widgetId || "N/A"}</p>
              <p><strong>Agent ID:</strong> {selectedAgentForWidget.id}</p>
              <p><strong>Domain:</strong> {selectedAgentForWidget.domain}</p>
              <p className="widget-note">
                <strong>Note:</strong> This widget code should only be used on <strong>{selectedAgentForWidget.domain}</strong> or its subdomains.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WidgetModal

