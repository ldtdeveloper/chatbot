import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userService, authService } from "../services/services";
import { useAuthStore } from "../context/authStore";
import '../assets/UsersUpdate.css';
import { showError, showSuccess } from "../utils/toast";

export default function EditProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user: currentUser, setAuth } = useAuthStore(); // logged-in user

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    role: "",
    password: ""
  });

  const isSelf = Number(userId) === currentUser.id;
  const canEditRole = currentUser.role === 'superadmin';

  // Fetch user data
  const { data: response, isLoading, error } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => userService.getProfile(userId),
    enabled: !!userId
  });

  const user = response?.user; // actual user object from API

  // Pre-fill form
  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || "",
        username: user.username || "",
        role: user.role || "",
        password: ""
      });
    }
  }, [user]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => userService.updateProfile(id, data),
    onSuccess: async () => {
      queryClient.invalidateQueries(["users"]);
      queryClient.invalidateQueries(["user", userId]);
      
      // If user is updating their own profile, refresh auth store
      if (isSelf) {
        try {
          const updatedUser = await authService.getMe();
          const token = localStorage.getItem('token');
          setAuth(token, updatedUser);
        } catch (error) {
          console.error("Failed to refresh user data:", error);
        }
      }
      showSuccess(`User updated successfully`)
      if (currentUser.role === 'superadmin') navigate("/users");
    },
    onError: (err) => {
      const errorMessage = err.response?.data?.detail || "Update failed!";
      showError(errorMessage)
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!user) return;

    const updateData = {};
    if (formData.email && formData.email !== user.email) updateData.email = formData.email;
    if (formData.username && formData.username !== user.username) updateData.username = formData.username;
    if (formData.role && formData.role !== user.role && canEditRole) updateData.role = formData.role;
    if (formData.password) updateData.password = formData.password;

    if (Object.keys(updateData).length === 0) {
      showSuccess(`No changes detected`)
      return;
    }

    updateMutation.mutate({ id: userId, data: updateData });
  };

  if (isLoading) return <div className="edit-profile-container"><div className="loading">Loading user data...</div></div>;
  if (error) return (
    <div className="edit-profile-container">
      <div className="error-message">{error.response?.data?.detail || error.message}</div>
      {currentUser.role === 'superadmin' && (
        <button onClick={() => navigate("/users")}>Back to Users</button>
      )}
    </div>
  );
  if (!user) return (
    <div className="edit-profile-container">
      <div className="error-message">User not found</div>
      {currentUser.role === 'superadmin' && (
        <button onClick={() => navigate("/users")}>Back to Users</button>
      )}
    </div>
  );

  return (
    <div className="edit-profile-container">
      <div className="page-header">
        <h2>Edit User Profile</h2>
        {currentUser.role === 'superadmin' && (
          <button type="button" onClick={() => navigate("/users")} className="btn-back">← Back to Users</button>
        )}
      </div>

      <form className="edit-profile-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required autoComplete="email" />
        </div>

        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input id="username" type="text" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} required autoComplete="username" />
        </div>

        <div className="form-group">
          <label htmlFor="role">Role</label>
          <select
            id="role"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            required
            disabled={!canEditRole}
          >
            <option value="">Select Role</option>
            <option value="default">Default User</option>
            <option value="superadmin">Superadmin</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="password">Password (leave blank to keep current)</label>
          <input
            id="password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            autoComplete="new-password"
            placeholder="Enter new password if you want to change"
          />
        </div>

        {updateMutation.error && <div className="error-message">{updateMutation.error.response?.data?.detail || "Failed to update user"}</div>}

        <div className="form-actions">
          {currentUser.role === 'superadmin' && (
            <button type="button" onClick={() => navigate("/users")} className="btn-cancel" disabled={updateMutation.isLoading}>Cancel</button>
          )}
          <button type="submit" className="btn-save" disabled={updateMutation.isLoading}>{updateMutation.isLoading ? 'Saving...' : 'Save Changes'}</button>
        </div>
      </form>
    </div>
  );
}
