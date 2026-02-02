import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userCreate, userService, planService } from '../services/services';
import { showError, showSuccess } from '../utils/toast';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FaEye, FaEdit, FaToggleOn, FaToggleOff, FaTimes } from 'react-icons/fa';
import '../styles/Users.css';

function Users() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [showAddForm, setShowAddForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    role: '',
    planId: '', // renamed from plan_id to planId for consistency
  });

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const token = localStorage.getItem('token');

  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: userService.list,
  });

  const { data: plans = [], isLoading: plansLoading } = useQuery({
    queryKey: ['plans'],
    queryFn: planService.listPlan,
    enabled: currentUser.role === 'superadmin' && showAddForm,
    staleTime: 5 * 60 * 1000,
  });

  const createUserMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await userCreate.createUser(payload, token);
      return res.data;
    },
    onSuccess: () => {
      showSuccess('Payment link sent to registered email');
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowAddForm(false);
      resetForm();
    },
    onError: (err) => {
      console.error(err);
      showError(err?.response?.data?.detail || 'Failed to create user');
    },
  });

  const toggleMutation = useMutation({
    mutationFn: userService.toggleActive,
    onMutate: async (userId) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previousUsers = queryClient.getQueryData(['users']);

      queryClient.setQueryData(['users'], (old) =>
        old?.map((user) =>
          user.id === userId ? { ...user, is_active: !user.is_active } : user
        )
      );

      return { previousUsers };
    },
    onSuccess: (data) => {
      showSuccess(data.is_active ? 'User activated successfully' : 'User deactivated successfully');
    },
    onError: (_, __, context) => {
      queryClient.setQueryData(['users'], context.previousUsers);
      showError('Failed to update user status');
    },
  });

  const resetForm = () => {
    setFormData({
      email: '',
      username: '',
      role: '',
      planId: '',
    });
    setIsSubmitting(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    if (!formData.email || !formData.username || !formData.role) {
      showError('Please fill in all required fields');
      setIsSubmitting(false);
      return;
    }

    if (currentUser.role === 'superadmin' && !formData.planId) {
      showError('Please select a plan for the new user');
      setIsSubmitting(false);
      return;
    }

    const payload = {
      email: formData.email,
      username: formData.username,
      role: formData.role,
      ...(currentUser.role === 'superadmin' && {
        plan_id: formData.planId, // backend expects plan_id
      }),
    };

    try {
      await createUserMutation.mutateAsync(payload);
    } catch {
      // error handled in onError
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLoading = usersLoading || (currentUser.role === 'superadmin' && showAddForm && plansLoading);

  if (isLoading && !showAddForm) {
    return <div className="loading">Loading users...</div>;
  }

  return (
    <div className="users">
      <div className="page-header">
        <h1>User Management</h1>
        <button 
          className="create-btn" 
          onClick={() => setShowAddForm(true)}
          disabled={isSubmitting}
        >
          + Create User
        </button>
      </div>

      {/* Modal Popup */}
      {showAddForm && (
        <div className="modal-overlay" onClick={() => setShowAddForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New User</h2>
              {/* <button 
                className="modal-close-btn" 
                onClick={() => setShowAddForm(false)}
                disabled={isSubmitting}
              >
                <FaTimes />
              </button> */}
            </div>

            <form className="add-user-form" onSubmit={handleSubmit}>
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />

              <input
                type="text"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />

              <select 
                name="role" 
                value={formData.role} 
                onChange={handleChange} 
                required
                disabled={isSubmitting}
              >
                <option value="">Select Role</option>
                <option value="default">Default User</option>
                <option value="superadmin">Superadmin</option>
              </select>

              {currentUser.role === 'superadmin' && (
                <select
                  name="planId"
                  value={formData.planId}
                  onChange={handleChange}
                  required
                  disabled={plansLoading || plans.length === 0 || isSubmitting}
                >
                  <option value="">
                    {plansLoading 
                      ? 'Loading plans...' 
                      : plans.length === 0 
                        ? 'No plans available' 
                        : 'Select Plan'}
                  </option>

                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                      {plan.price && ` - ${plan.price}`}
                      {plan.interval && ` / ${plan.interval}`}
                    </option>
                  ))}
                </select>
              )}

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setShowAddForm(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="submit-btn"
                  disabled={isSubmitting || createUserMutation.isPending}
                >
                  {isSubmitting ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="users-list">
        {users?.length === 0 && <p>No users found.</p>}

        {users?.map((user) => (
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
                title="View Profile"
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

              {user.role.toUpperCase() !== 'SUPERADMIN' && (
                <button
                  className="action-btn toggle-btn"
                  onClick={() => toggleMutation.mutate(user.id)}
                  disabled={toggleMutation.isPending}
                  title={user.is_active ? 'Deactivate' : 'Activate'}
                >
                  {user.is_active ? <FaToggleOn /> : <FaToggleOff />}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Users;