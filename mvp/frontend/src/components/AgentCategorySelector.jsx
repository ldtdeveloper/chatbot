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
      {/* WhatsApp agent card */}
      <div
        className={`agent-category-card ${activeCategory === 'whatsapp' ? 'active' : ''} whatsapp-category`}
        onClick={() => {
          setActiveCategory('whatsapp')
          const el = document.getElementById('whatsapp-agents-section')
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }}
      >
        <div className="agent-category-pill whatsapp">WhatsApp</div>
        <h3>WhatsApp Agents</h3>
        <p>AI text based assistants for WhatsApp messaging and automation.</p>
        <span className="agent-category-link">Go to WhatsApp agents →</span>
      </div>

      {/* Employees card */}
      <div
        className={`agent-category-card ${activeCategory === 'employees' ? 'active' : ''} employees-category`}
        onClick={() => {
          setActiveCategory('employees')
          const el = document.getElementById('employees-section')
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }}
      >
        <div className="agent-category-pill employees">Employees</div>
        <h3>Manage Team</h3>
        <p>Add and manage human agents in your company to handle complex support requests.</p>
        <span className="agent-category-link">Manage Employees →</span>
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


