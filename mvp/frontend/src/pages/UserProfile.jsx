import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { userService } from '../services/services'
import './UserProfile.css'

function UserProfile() {
  const { userId } = useParams()
  const navigate = useNavigate()
  
  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['user-profile', userId],
    queryFn: () => userService.getProfile(userId),
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="user-profile">
        <div className="loading-container">
          <div>Loading user profile...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="user-profile">
        <div className="error-container">
          <p>Error loading user profile: {error.response?.data?.detail || error.message || 'Unknown error'}</p>
          <button onClick={() => navigate('/users')} className="back-btn">← Back to Users</button>
        </div>
      </div>
    )
  }

  if (!profile || !profile.user) {
    return (
      <div className="user-profile">
        <div className="error-container">
          <p>User not found</p>
          <button onClick={() => navigate('/users')} className="back-btn">← Back to Users</button>
        </div>
      </div>
    )
  }

  return (
    <div className="user-profile">
      <div className="profile-header">
        <button onClick={() => navigate('/users')} className="back-btn">← Back to Users</button>
        <h1>User Profile: {profile.user.username}</h1>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h2>User Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Email:</label>
              <span>{profile.user.email}</span>
            </div>
            <div className="info-item">
              <label>Username:</label>
              <span>{profile.user.username}</span>
            </div>
            <div className="info-item">
              <label>Role:</label>
              <span className={`role-badge ${profile.user.role}`}>{profile.user.role}</span>
            </div>
            <div className="info-item">
              <label>Status:</label>
              <span className={profile.user.is_active ? 'status active' : 'status inactive'}>
                {profile.user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="info-item">
              <label>Created:</label>
              <span>{new Date(profile.user.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>Chatbot Assistants</h2>
          {!profile.assistants || profile.assistants.length === 0 ? (
            <p className="no-data">No chatbot assistants created yet.</p>
          ) : (
            <div className="assistants-list">
              {profile.assistants.map((assistant) => (
                <div key={assistant.id} className="assistant-card">
                  <h3>{assistant.name}</h3>
                  <div className="assistant-meta">
                    <span>Voice: {assistant.voice}</span>
                    <span>Created: {new Date(assistant.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserProfile

