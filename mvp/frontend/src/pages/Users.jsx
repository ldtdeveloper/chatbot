import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { userCreate, userService } from '../services/services'
import { showError,showSuccess } from '../utils/toast'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import '../styles/Users.css'

function Users() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    // password: '',
    role: '',
    plan: '',
    schedule: '',
  })

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  const token = localStorage.getItem('token')

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.list(),
    enabled: !!token,
  })

  const createUserMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await userCreate.createUser(payload, token)
      return res.data
    },
    onSuccess: () => {
      showSuccess(`User created successfully. Payment link sent (if applicable).`)
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setShowAddForm(false)
      setFormData({
        email: '',
        username: '',
        // password: '',
        role: '',
        plan: '',
        schedule: '',
      })
    },
    onError: (err) => {
      console.error(err)
      showError(err?.response?.data?.detail || 'Failed to create user')
     
    },
  })

 
  const isSubmitting = createUserMutation.isPending

  const toggleMutation = useMutation({
    mutationFn: (userId) => userService.toggleActive(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!token) {
      showError("Not authenticated")
     
      return
    }

    if (currentUser.role === 'SUPERADMIN') {
      if (!formData.plan || !formData.schedule) {
        showError("Please select plan and billing schedule")
        return
      }
    }

    createUserMutation.mutate(formData)
  }

  if (isLoading) return <div className="loading">Loading users...</div>

  return (
    <div className="users">
      <div className="page-header">
        <h1>User Management</h1>
        <button onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : '+ Create User'}
        </button>
      </div>

      {showAddForm && (
        <form className="add-user-form" onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />

          {/* <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          /> */}

          <select name="role" value={formData.role} onChange={handleChange} required>
            <option value="">Select Role</option>
            <option value="default">Default User</option>
            <option value="superadmin">Superadmin</option>
          </select>

          {currentUser.role === 'superadmin' && (
            <select name="plan" value={formData.plan} onChange={handleChange}>
              <option value="">Select Plan</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          )}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Processing...' : 'Create User'}
          </button>
        </form>
      )}

      <div className="users-list">
        {users.length === 0 && <p>No users found.</p>}

        {users.map(user => (
          <div key={user.id} className="user-card">
            <div className="user-info">
              <h3>{user.username}</h3>
              <span>{user.email}</span>
              <div className="user-meta">
                <span className={`role-badge ${user.role}`}>{user.role}</span>
                <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                  <span className="status-dot" />
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="user-actions">
              <button
                onClick={() => navigate(`/users/${user.id}/profile`)}
                className="view-btn"
                title={`View profile for ${user.username} (${user.role})`}
              >
                View Profile
              </button>
              <button
                onClick={() => navigate(`/users/${user.id}/profile-update`)}
                className="view-btn"
                title={`View profile for ${user.username} (${user.role})`}
              >
                Edit Profile
              </button>
              <button onClick={() => toggleMutation.mutate(user.id)}>
                {user.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        ))}
        {users?.length === 0 && <p>No users found.</p>}
      </div>
    </div>
  )
}

export default Users