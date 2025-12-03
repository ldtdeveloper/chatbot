import React from 'react'
import { Link } from 'react-router-dom'
import '../assets/Dashboard.css'

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="dashboard-grid">
        <Link to="/openai-keys" className="dashboard-card">
          <h2>🔑 OpenAI Keys</h2>
          <p>Manage your OpenAI API keys</p>
        </Link>
        <Link to="/agents" className="dashboard-card">
          <h2>🤖 Agents</h2>
          <p>Create and manage agent configurations</p>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard

