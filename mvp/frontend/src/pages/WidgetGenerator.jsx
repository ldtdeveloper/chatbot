import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { widgetService } from '../services/services'
import '../assets/WidgetGenerator.css'

function WidgetGenerator() {
  const [copied, setCopied] = useState(false)
  const { data: widgetData, isLoading } = useQuery({
    queryKey: ['widget-code'],
    queryFn: widgetService.generateCode,
  })

  const handleCopy = async () => {
    if (widgetData?.widget_code) {
      try {
        // Try modern Clipboard API first (requires HTTPS or localhost)
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(widgetData.widget_code)
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        } else {
          // Fallback for browsers without Clipboard API (HTTP, older browsers)
          const textArea = document.createElement('textarea')
          textArea.value = widgetData.widget_code
          textArea.style.position = 'fixed'
          textArea.style.left = '-999999px'
          textArea.style.top = '-999999px'
          document.body.appendChild(textArea)
          textArea.focus()
          textArea.select()
          try {
            document.execCommand('copy')
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
          } catch (err) {
            console.error('Fallback copy failed:', err)
            alert('Failed to copy. Please select and copy the code manually.')
          }
          document.body.removeChild(textArea)
        }
      } catch (err) {
        console.error('Copy failed:', err)
        // Fallback method
        const textArea = document.createElement('textarea')
        textArea.value = widgetData.widget_code
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        try {
          document.execCommand('copy')
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
        } catch (fallbackErr) {
          console.error('Fallback copy failed:', fallbackErr)
          alert('Failed to copy. Please select and copy the code manually.')
        }
        document.body.removeChild(textArea)
      }
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="widget-generator">
      <h1>Widget Code Generator</h1>
      <p className="description">
        Select an assistant and copy the code below to integrate it on your website.
      </p>

      {assistants && assistants.length > 0 && (
        <div className="assistant-selector">
          <label>Select Assistant:</label>
          <select
            value={selectedAssistantId || ''}
            onChange={(e) => setSelectedAssistantId(parseInt(e.target.value))}
          >
            <option value="">-- Select an Assistant --</option>
            {assistants.map((assistant) => (
              <option key={assistant.id} value={assistant.id}>
                {assistant.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {!selectedAssistantId && assistants && assistants.length > 0 && (
        <div className="info-message">
          Please select an assistant to generate widget code.
        </div>
      )}

      {assistants && assistants.length === 0 && (
        <div className="info-message">
          No assistants created yet. Go to "Assistants" to create your first chatbot.
        </div>
      )}

      {selectedAssistantId && (
        <div className="widget-code-container">
          <div className="code-header">
            <span>Widget Code</span>
            <button onClick={handleCopy} className="copy-btn">
              {copied ? '✓ Copied!' : 'Copy Code'}
            </button>
          </div>
          <pre className="widget-code">
            <code>{widgetData?.widget_code || 'No widget code available'}</code>
          </pre>
        </div>
      )}

      {selectedAssistantId && widgetData && (
        <div className="widget-info">
          <h2>Widget Information</h2>
          <p><strong>Widget ID:</strong> {widgetData.widget_id}</p>
          <p><strong>Assistant:</strong> {widgetData.assistant_name}</p>
          <p>Use this ID to track widget usage and analytics.</p>
        </div>
      )}

      {selectedAssistantId && !widgetData && !isLoading && (
        <div className="error">Failed to generate widget code. Please check your assistant configuration.</div>
      )}
    </div>
  )
}

export default WidgetGenerator

