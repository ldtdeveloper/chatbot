import React from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="dashboard-grid">
        <Link to="/openai-keys" className="dashboard-card">
          <h2>🔑 OpenAI Keys</h2>
          <p>Manage your OpenAI API keys</p>
        </Link>
        <Link to="/prompts" className="dashboard-card">
          <h2>📝 Prompts</h2>
          <p>Create and manage audio prompts</p>
        </Link>
        <Link to="/assistant-config" className="dashboard-card">
          <h2>⚙️ Settings</h2>
          <p>Configure voice and noise reduction</p>
        </Link>
        <Link to="/widget-generator" className="dashboard-card">
          <h2>🎨 Widget Generator</h2>
          <p>Generate code for your voice assistant widget</p>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard

