import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { userService, authService } from '../services/services';
import { useAuthStore } from '../context/authStore';
import { showError, showSuccess } from '../utils/toast';
import '../styles/ChangePassword.css';

export default function ChangePassword({ onSuccess, onCancel }) {
  const { setAuth } = useAuthStore();
  const [formData, setFormData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    if (!formData.oldPassword) {
      newErrors.oldPassword = 'Old password is required';
    }

    if (!formData.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (formData.newPassword.length < 6) {
      newErrors.newPassword = 'Password must be at least 6 characters';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const changePasswordMutation = useMutation({
    mutationFn: (data) => userService.changePassword(data),
    onSuccess: async (response) => {
      // Update token if provided
      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        try {
          const updatedUser = await authService.getMe();
          setAuth(response.access_token, updatedUser);
        } catch (error) {
          console.error("Failed to refresh user data:", error);
        }
      }
      showSuccess('Password changed successfully');
      setFormData({
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setErrors({});
      if (onSuccess) {
        onSuccess();
      }
    },
    onError: (err) => {
      const errorMessage = err.response?.data?.detail || 'Failed to change password';
      showError(errorMessage);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    changePasswordMutation.mutate({
      old_password: formData.oldPassword,
      new_password: formData.newPassword,
      confirm_password: formData.confirmPassword
    });
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <div className="change-password-wrapper">
      <h2>Change Password</h2>
      <form onSubmit={handleSubmit} className="change-password-form">
        <div className="form-group">
          <label htmlFor="oldPassword">Old Password</label>
          <input
            id="oldPassword"
            type="password"
            value={formData.oldPassword}
            onChange={(e) => handleChange('oldPassword', e.target.value)}
            autoComplete="current-password"
            className={errors.oldPassword ? 'error' : ''}
          />
          {errors.oldPassword && (
            <span className="error-message">{errors.oldPassword}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="newPassword">New Password</label>
          <input
            id="newPassword"
            type="password"
            value={formData.newPassword}
            onChange={(e) => handleChange('newPassword', e.target.value)}
            autoComplete="new-password"
            className={errors.newPassword ? 'error' : ''}
          />
          {errors.newPassword && (
            <span className="error-message">{errors.newPassword}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            autoComplete="new-password"
            className={errors.confirmPassword ? 'error' : ''}
          />
          {errors.confirmPassword && (
            <span className="error-message">{errors.confirmPassword}</span>
          )}
        </div>

        <div className="form-actions">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn-cancel"
              disabled={changePasswordMutation.isLoading}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            className="btn-submit"
            disabled={changePasswordMutation.isLoading}
          >
            {changePasswordMutation.isLoading ? 'Changing...' : 'Change Password'}
          </button>
        </div>
      </form>
    </div>
  );
}


