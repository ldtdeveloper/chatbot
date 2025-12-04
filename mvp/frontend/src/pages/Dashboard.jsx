import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './Dashboard.css'

function Dashboard() {
  const [dateRange, setDateRange] = useState('30d')
  const [selectedKey, setSelectedKey] = useState('all')

  // Dummy data for Interactions Chart (full width)
  const interactionsData = [
    { date: '2024-01-01', 'Production Key': 120, 'Development Key': 45, 'Testing Key': 20 },
    { date: '2024-01-02', 'Production Key': 135, 'Development Key': 52, 'Testing Key': 18 },
    { date: '2024-01-03', 'Production Key': 148, 'Development Key': 48, 'Testing Key': 25 },
    { date: '2024-01-04', 'Production Key': 162, 'Development Key': 55, 'Testing Key': 22 },
    { date: '2024-01-05', 'Production Key': 175, 'Development Key': 60, 'Testing Key': 28 },
    { date: '2024-01-06', 'Production Key': 190, 'Development Key': 65, 'Testing Key': 30 },
    { date: '2024-01-07', 'Production Key': 205, 'Development Key': 70, 'Testing Key': 32 },
    { date: '2024-01-08', 'Production Key': 220, 'Development Key': 75, 'Testing Key': 35 },
    { date: '2024-01-09', 'Production Key': 235, 'Development Key': 80, 'Testing Key': 38 },
    { date: '2024-01-10', 'Production Key': 250, 'Development Key': 85, 'Testing Key': 40 },
    { date: '2024-01-11', 'Production Key': 265, 'Development Key': 90, 'Testing Key': 42 },
    { date: '2024-01-12', 'Production Key': 280, 'Development Key': 95, 'Testing Key': 45 },
    { date: '2024-01-13', 'Production Key': 295, 'Development Key': 100, 'Testing Key': 48 },
    { date: '2024-01-14', 'Production Key': 310, 'Development Key': 105, 'Testing Key': 50 },
    { date: '2024-01-15', 'Production Key': 325, 'Development Key': 110, 'Testing Key': 52 },
    { date: '2024-01-16', 'Production Key': 340, 'Development Key': 115, 'Testing Key': 55 },
    { date: '2024-01-17', 'Production Key': 355, 'Development Key': 120, 'Testing Key': 58 },
    { date: '2024-01-18', 'Production Key': 370, 'Development Key': 125, 'Testing Key': 60 },
    { date: '2024-01-19', 'Production Key': 385, 'Development Key': 130, 'Testing Key': 62 },
    { date: '2024-01-20', 'Production Key': 400, 'Development Key': 135, 'Testing Key': 65 },
    { date: '2024-01-21', 'Production Key': 415, 'Development Key': 140, 'Testing Key': 68 },
    { date: '2024-01-22', 'Production Key': 430, 'Development Key': 145, 'Testing Key': 70 },
    { date: '2024-01-23', 'Production Key': 445, 'Development Key': 150, 'Testing Key': 72 },
    { date: '2024-01-24', 'Production Key': 460, 'Development Key': 155, 'Testing Key': 75 },
    { date: '2024-01-25', 'Production Key': 475, 'Development Key': 160, 'Testing Key': 78 },
    { date: '2024-01-26', 'Production Key': 490, 'Development Key': 165, 'Testing Key': 80 },
    { date: '2024-01-27', 'Production Key': 505, 'Development Key': 170, 'Testing Key': 82 },
    { date: '2024-01-28', 'Production Key': 520, 'Development Key': 175, 'Testing Key': 85 },
    { date: '2024-01-29', 'Production Key': 535, 'Development Key': 180, 'Testing Key': 88 },
    { date: '2024-01-30', 'Production Key': 550, 'Development Key': 185, 'Testing Key': 90 }
  ]

  // Dummy data for Expenses Chart (50% width)
  const expensesData = [
    { date: '2024-01-01', 'Production Key': 12.50, 'Development Key': 4.20, 'Testing Key': 1.80 },
    { date: '2024-01-02', 'Production Key': 13.75, 'Development Key': 4.60, 'Testing Key': 1.60 },
    { date: '2024-01-03', 'Production Key': 15.20, 'Development Key': 4.40, 'Testing Key': 2.00 },
    { date: '2024-01-04', 'Production Key': 16.80, 'Development Key': 5.10, 'Testing Key': 1.90 },
    { date: '2024-01-05', 'Production Key': 18.50, 'Development Key': 5.60, 'Testing Key': 2.30 },
    { date: '2024-01-06', 'Production Key': 20.20, 'Development Key': 6.10, 'Testing Key': 2.50 },
    { date: '2024-01-07', 'Production Key': 22.00, 'Development Key': 6.60, 'Testing Key': 2.70 },
    { date: '2024-01-08', 'Production Key': 23.80, 'Development Key': 7.10, 'Testing Key': 2.90 },
    { date: '2024-01-09', 'Production Key': 25.60, 'Development Key': 7.60, 'Testing Key': 3.10 },
    { date: '2024-01-10', 'Production Key': 27.40, 'Development Key': 8.10, 'Testing Key': 3.30 },
    { date: '2024-01-11', 'Production Key': 29.20, 'Development Key': 8.60, 'Testing Key': 3.50 },
    { date: '2024-01-12', 'Production Key': 31.00, 'Development Key': 9.10, 'Testing Key': 3.70 },
    { date: '2024-01-13', 'Production Key': 32.80, 'Development Key': 9.60, 'Testing Key': 3.90 },
    { date: '2024-01-14', 'Production Key': 34.60, 'Development Key': 10.10, 'Testing Key': 4.10 },
    { date: '2024-01-15', 'Production Key': 36.40, 'Development Key': 10.60, 'Testing Key': 4.30 },
    { date: '2024-01-16', 'Production Key': 38.20, 'Development Key': 11.10, 'Testing Key': 4.50 },
    { date: '2024-01-17', 'Production Key': 40.00, 'Development Key': 11.60, 'Testing Key': 4.70 },
    { date: '2024-01-18', 'Production Key': 41.80, 'Development Key': 12.10, 'Testing Key': 4.90 },
    { date: '2024-01-19', 'Production Key': 43.60, 'Development Key': 12.60, 'Testing Key': 5.10 },
    { date: '2024-01-20', 'Production Key': 45.40, 'Development Key': 13.10, 'Testing Key': 5.30 },
    { date: '2024-01-21', 'Production Key': 47.20, 'Development Key': 13.60, 'Testing Key': 5.50 },
    { date: '2024-01-22', 'Production Key': 49.00, 'Development Key': 14.10, 'Testing Key': 5.70 },
    { date: '2024-01-23', 'Production Key': 50.80, 'Development Key': 14.60, 'Testing Key': 5.90 },
    { date: '2024-01-24', 'Production Key': 52.60, 'Development Key': 15.10, 'Testing Key': 6.10 },
    { date: '2024-01-25', 'Production Key': 54.40, 'Development Key': 15.60, 'Testing Key': 6.30 },
    { date: '2024-01-26', 'Production Key': 56.20, 'Development Key': 16.10, 'Testing Key': 6.50 },
    { date: '2024-01-27', 'Production Key': 58.00, 'Development Key': 16.60, 'Testing Key': 6.70 },
    { date: '2024-01-28', 'Production Key': 59.80, 'Development Key': 17.10, 'Testing Key': 6.90 },
    { date: '2024-01-29', 'Production Key': 61.60, 'Development Key': 17.60, 'Testing Key': 7.10 },
    { date: '2024-01-30', 'Production Key': 63.40, 'Development Key': 18.10, 'Testing Key': 7.30 }
  ]

  // Dummy data for Active Agents Chart (50% width)
  const activeAgentsData = [
    { name: 'Production Key', value: 5, color: '#667eea' },
    { name: 'Development Key', value: 3, color: '#764ba2' },
    { name: 'Testing Key', value: 2, color: '#f093fb' }
  ]

  const totalAgents = activeAgentsData.reduce((sum, item) => sum + item.value, 0)

  // Colors for charts
  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

  // Format date for display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="dashboard-controls">
          <select
            className="date-range-selector"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="custom">Custom Range</option>
          </select>
          <select
            className="key-selector"
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
          >
            <option value="all">All Keys</option>
            <option value="1">Production Key</option>
            <option value="2">Development Key</option>
            <option value="3">Testing Key</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-card-icon">📊</div>
          <div className="summary-card-content">
            <h3>Total Interactions</h3>
            <p className="summary-card-value">8,250</p>
            <span className="summary-card-change positive">+12.5% from last period</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">💰</div>
          <div className="summary-card-content">
            <h3>Total Expenses</h3>
            <p className="summary-card-value">$1,234.50</p>
            <span className="summary-card-change positive">+8.3% from last period</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">🤖</div>
          <div className="summary-card-content">
            <h3>Active Agents</h3>
            <p className="summary-card-value">{totalAgents}</p>
            <span className="summary-card-change neutral">No change</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">🔑</div>
          <div className="summary-card-content">
            <h3>Active Keys</h3>
            <p className="summary-card-value">3</p>
            <span className="summary-card-change neutral">No change</span>
          </div>
        </div>
      </div>

      {/* Interactions Chart - Full Width */}
      <div className="chart-card full-width">
        <div className="chart-header">
          <h2>Interactions</h2>
          <p className="chart-subtitle">Number of interactions per OpenAI API key over time</p>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={interactionsData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorProduction" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorDevelopment" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#764ba2" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#764ba2" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorTesting" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f093fb" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#f093fb" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatDate}
                stroke="#666"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#666" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '10px'
                }}
                labelFormatter={(value) => `Date: ${formatDate(value)}`}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="Production Key" 
                stroke="#667eea" 
                fillOpacity={1} 
                fill="url(#colorProduction)" 
              />
              <Area 
                type="monotone" 
                dataKey="Development Key" 
                stroke="#764ba2" 
                fillOpacity={1} 
                fill="url(#colorDevelopment)" 
              />
              <Area 
                type="monotone" 
                dataKey="Testing Key" 
                stroke="#f093fb" 
                fillOpacity={1} 
                fill="url(#colorTesting)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row - Expenses and Active Agents */}
      <div className="charts-row">
        {/* Expenses Chart - 50% Width */}
        <div className="chart-card half-width">
          <div className="chart-header">
            <h2>Expenses</h2>
            <p className="chart-subtitle">Cost per OpenAI API key (USD)</p>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={expensesData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  stroke="#666"
                  style={{ fontSize: '11px' }}
                />
                <YAxis stroke="#666" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    padding: '10px'
                  }}
                  labelFormatter={(value) => `Date: ${formatDate(value)}`}
                  formatter={(value) => [`$${value.toFixed(2)}`, 'Cost']}
                />
                <Legend />
                <Bar dataKey="Production Key" fill="#667eea" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Development Key" fill="#764ba2" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Testing Key" fill="#f093fb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Active Agents Chart - 50% Width */}
        <div className="chart-card half-width">
          <div className="chart-header">
            <h2>Active Agents</h2>
            <p className="chart-subtitle">Distribution of agents per OpenAI API key</p>
          </div>
          <div className="chart-container pie-chart-wrapper">
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={activeAgentsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  innerRadius={60}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {activeAgentsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    padding: '10px'
                  }}
                  formatter={(value, name) => [value, 'Agents']}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
            <div className="pie-chart-center">
              <div className="pie-chart-center-value">{totalAgents}</div>
              <div className="pie-chart-center-label">Total Agents</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h2 className="quick-actions-title">Quick Actions</h2>
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
    </div>
  )
}

export default Dashboard
