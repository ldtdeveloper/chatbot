import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '../services/services'
import { FaEye, FaEdit, FaToggleOn, FaToggleOff } from 'react-icons/fa'
import axios from 'axios'
import '../styles/Users.css'
import { showSuccess,showError } from '../utils/toast'

function Users() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [showAddForm, setShowAddForm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    role: '',
    plan: ''
  })

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  const token = localStorage.getItem('token')

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: userService.list
  })

  const createUserMutation = useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })

  const toggleMutation = useMutation({
    mutationFn: userService.toggleActive,
    onMutate: async (userId) => {
      await queryClient.cancelQueries({ queryKey: ['users'] })
      const previousUsers = queryClient.getQueryData(['users'])
      
      queryClient.setQueryData(['users'], (old) => {
        return old?.map(user => 
          user.id === userId 
            ? { ...user, is_active: !user.is_active }
            : user
        )
      })
      
      return { previousUsers }
    },
    onSuccess: (data) => {
      if (data.is_active) {
        showSuccess("User activated successfully");
      } else {
        showSuccess("User deactivated successfully");
      }
    },
    onError: (err, userId, context) => {
      queryClient.setQueryData(['users'], context.previousUsers)
      showError("Failed to update user status");
    }
  })

  const resetForm = () => {
    setShowAddForm(false)
    setIsSubmitting(false)
    setFormData({
      email: '',
      username: '',
      password: '',
      role: '',
      plan: ''
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    if (currentUser.role === 'superadmin') {
      if (!formData.plan) {
        alert('Please select a plan')
        setIsSubmitting(false)
        return
      }

      try {
        const createdUser = await createUserMutation.mutateAsync({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          role: formData.role
        })

        await axios.post(
          '/api/auth/register-with-plan',
          {
            user_id: createdUser.id,
            email: createdUser.email,
            username: createdUser.username,
            plan: formData.plan
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )

        alert('User created & payment link sent')
        resetForm()
      } catch (err) {
        alert(err?.response?.data?.detail || 'Failed')
        setIsSubmitting(false)
      }
      return
    }

    try {
      await createUserMutation.mutateAsync(formData)
      alert('User created')
      resetForm()
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed')
      setIsSubmitting(false)
    }
  }

  if (isLoading) return <div className="loading">Loading users...</div>

  return (
    <div className="users">
      <div className="page-header">
        <h1>User Management</h1>
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

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

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
        {users?.length === 0 && <p>No users found.</p>}

        {users?.map(user => (
          <div key={user.id} className="user-card">
            <div className="user-info">
              <h3>{user.username}</h3>
              <p className="user-email">{user.email}</p>
              <div className="user-meta">
                <span className={`role-badge ${user.role}`}>
                  {user.role.toUpperCase()}
                </span>
                <span className={`status ${user.is_active ? 'active' : 'inactive'}`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="user-actions">
              <button
                className="action-btn view-btn"
                onClick={() => navigate(`/users/${user.id}/profile`)}
                title="View User"
              >
                <FaEye />
              </button>
              <button
                className="action-btn edit-btn"
                onClick={() => navigate(`/users/${user.id}/profile-update`)}
                title="Edit User"
              >
                <FaEdit />
              </button>
              {user.role.toUpperCase() != 'SUPERADMIN' && (
                <button
                className="action-btn edit-btn"
                onClick={() => toggleMutation.mutate(user.id)}
                disabled={toggleMutation.isPending}
                title={user.is_active ? "Deactivate User" : "Activate User"}
              >
                {user.is_active ? <FaToggleOn /> : <FaToggleOff />}
              </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Users
