import React from 'react'

function AgentCategorySelector({ activeCategory, setActiveCategory }) {
  return (
    <div className="agent-category-grid">
      <div
        className={`agent-category-card ${activeCategory === 'web' ? 'active' : ''}`}
        onClick={() => {
          setActiveCategory('web')
          const el = document.getElementById('web-agents-section')
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }}
      >
        <div className="agent-category-pill">Web</div>
        <h3>Web Agents</h3>
        <p>Embed on sites and apps, manage widgets, and edit instructions.</p>
        <span className="agent-category-link">Go to web agents →</span>
      </div>
      <div
        className={`agent-category-card ${activeCategory === 'phone' ? 'active' : ''} phone-category-disabled`}
        style={{ pointerEvents: 'none', cursor: 'not-allowed' }}
      >
        <div className="agent-category-pill phone">Phone</div>
        <div className="coming-soon-badge">Coming Soon</div>
        <h3>Phone Agents</h3>
        <p>IVR-style assistants for calls. Configure routing and voice flows.</p>
        <span className="agent-category-link">Go to phone agents →</span>
      </div>
    </div>
  )
}

export default AgentCategorySelector


