import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { widgetService } from '../services/services'
import './WidgetGenerator.css'

function WidgetGenerator() {
  const [copied, setCopied] = useState(false)
  const { data: widgetData, isLoading } = useQuery({
    queryKey: ['widget-code'],
    queryFn: widgetService.generateCode,
  })

  const handleCopy = () => {
    if (widgetData?.widget_code) {
      navigator.clipboard.writeText(widgetData.widget_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="widget-generator">
      <h1>Widget Code Generator</h1>
      <p className="description">
        Copy the code below and paste it into your website to add the voice assistant widget.
      </p>

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

      <div className="widget-info">
        <h2>Widget ID: {widgetData?.widget_id}</h2>
        <p>Use this ID to track widget usage and analytics.</p>
      </div>
    </div>
  )
}

export default WidgetGenerator

