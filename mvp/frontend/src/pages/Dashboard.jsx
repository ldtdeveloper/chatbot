import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
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
import { dashboardService } from '../services/services'
import '../assets/Dashboard.css'

function Dashboard() {
  const [dateRange, setDateRange] = useState('30d')
  const [selectedKey, setSelectedKey] = useState('all')

  // Fetch dashboard stats from API
  const { data: stats, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboardStats', dateRange, selectedKey],
    queryFn: () => dashboardService.getStats(dateRange, selectedKey),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Colors for charts
  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

  // Format date for display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  // Get dynamic gradient definitions based on available keys
  const getGradientDefs = () => {
    if (!stats?.available_keys) return null
    return stats.available_keys.map((key, index) => (
      <linearGradient key={key.id} id={`color${key.id}`} x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.8}/>
        <stop offset="95%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0}/>
      </linearGradient>
    ))
  }

  // Get dynamic Area components for interactions chart
  const getInteractionAreas = () => {
    if (!stats?.available_keys) return null
    return stats.available_keys.map((key, index) => (
      <Area 
        key={key.id}
        type="monotone" 
        dataKey={key.name} 
        stroke={COLORS[index % COLORS.length]} 
        fillOpacity={1} 
        fill={`url(#color${key.id})`} 
      />
    ))
  }

  // Get dynamic Bar components for expenses chart
  const getExpenseBars = () => {
    if (!stats?.available_keys) return null
    return stats.available_keys.map((key, index) => (
      <Bar 
        key={key.id}
        dataKey={key.name} 
        fill={COLORS[index % COLORS.length]} 
        radius={[4, 4, 0, 0]} 
      />
    ))
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
        </div>
        <div className="error-state">
          <p>Error loading dashboard: {error.message}</p>
          <button onClick={() => refetch()}>Retry</button>
        </div>
      </div>
    )
  }

  // Calculate total agents from pie chart data
  const totalAgents = stats?.agents_per_key?.reduce((sum, item) => sum + item.value, 0) || 0

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
          </select>
          <select
            className="key-selector"
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
          >
            <option value="all">All Keys</option>
            {stats?.available_keys?.map(key => (
              <option key={key.id} value={key.id}>{key.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-card-icon">📊</div>
          <div className="summary-card-content">
            <h3>Total Interactions</h3>
            <p className="summary-card-value">{stats?.total_interactions?.toLocaleString() || 0}</p>
            <span className={`summary-card-change ${stats?.interactions_change >= 0 ? 'positive' : 'negative'}`}>
              {stats?.interactions_change >= 0 ? '+' : ''}{stats?.interactions_change || 0}% from last period
            </span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">💰</div>
          <div className="summary-card-content">
            <h3>Total Expenses</h3>
            <p className="summary-card-value">${stats?.total_expenses?.toFixed(2) || '0.00'}</p>
            <span className={`summary-card-change ${stats?.expenses_change >= 0 ? 'positive' : 'negative'}`}>
              {stats?.expenses_change >= 0 ? '+' : ''}{stats?.expenses_change || 0}% from last period
            </span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">🤖</div>
          <div className="summary-card-content">
            <h3>Active Agents</h3>
            <p className="summary-card-value">{stats?.total_agents || 0}</p>
            <span className="summary-card-change neutral">Total agents configured</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">🔑</div>
          <div className="summary-card-content">
            <h3>Active Keys</h3>
            <p className="summary-card-value">{stats?.active_keys || 0}</p>
            <span className="summary-card-change neutral">API keys active</span>
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
          {stats?.interactions_chart?.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={stats.interactions_chart} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  {getGradientDefs()}
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
                {getInteractionAreas()}
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data-message">
              <p>No interaction data available for this period</p>
            </div>
          )}
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
            {stats?.expenses_chart?.length > 0 ? (
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={stats.expenses_chart} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
                    formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']}
                  />
                  <Legend />
                  {getExpenseBars()}
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="no-data-message">
                <p>No expense data available for this period</p>
              </div>
            )}
          </div>
        </div>

        {/* Active Agents Chart - 50% Width */}
        <div className="chart-card half-width">
          <div className="chart-header">
            <h2>Active Agents</h2>
            <p className="chart-subtitle">Distribution of agents per OpenAI API key</p>
          </div>
          <div className="chart-container pie-chart-wrapper">
            {stats?.agents_per_key?.length > 0 && totalAgents > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={stats.agents_per_key}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      innerRadius={60}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {stats.agents_per_key.map((entry, index) => (
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
              </>
            ) : (
              <div className="no-data-message">
                <p>No agents configured yet</p>
                <Link to="/agents" className="create-link">Create your first agent</Link>
              </div>
            )}
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
