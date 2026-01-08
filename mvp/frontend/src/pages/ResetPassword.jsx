import React, { useState } from 'react'
import { resetPasswordService } from '../services/services'
import { useSearchParams } from 'react-router-dom';
import { showError, showSuccess } from '../utils/toast';

function ResetPassword(){
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error,setError]  = useState('')
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        if (password !== confirmPassword) {
            showError(`Password do not match`)
            return;
        }
        try {
          const response = await resetPasswordService.resetPassword(token,password)
          console.log(`API called ${response}`)
          if(response?.message == "Password reset successful"){
            showSuccess(`Reset password successfully`)
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
          }
        } catch (err) {
          showError(`Failed to reset password`)
          setError(err.response?.data?.detail || 'Failed to reset password')}
      }

      return (
            <div className="auth-container">
            <div className="auth-card">
                <h1>Reset password</h1>
                <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>New Password</label>
                    <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    />
                </div>
                <div className="form-group">
                    <label>Confirm Password</label>
                    <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e)=> setConfirmPassword(e.target.value)}
                    required
                    />
                </div>
                <button type="submit">Set Password</button>
                </form>
            </div>
            </div>
        )
}

export default ResetPassword

