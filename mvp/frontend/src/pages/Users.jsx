import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '../services/services'
import '../styles/Users.css'

function Users() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    role: ''
  })

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: userService.list,
  })

  const createMutation = useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
      setShowAddForm(false)
      setFormData({ email: '', username: '', password: '', role: '' })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: userService.toggleActive,
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="users">
      <div className="page-header">
        <h1>User Management</h1>
      </div>

      <div className="users-list">
        {users?.map((user) => (
          <div key={user.id} className="user-card">
            <div className="user-info">
              <h3>{user.username}</h3>
              <span className="user-email">{user.email}</span>
              <div className="user-meta">
                <span className={`role-badge ${user.role}`}>{user.role}</span>
                <span className={`status ${user.is_active ? 'active' : 'inactive'}`}>
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
              <button
                onClick={() => toggleMutation.mutate(user.id)}
                disabled={toggleMutation.isLoading}
              >
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

