import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { humanAgentService } from '../services/services';
import { UserPlus, Trash2, Mail, User, Loader2 } from 'lucide-react';
import { showSuccess, showError } from '../utils/toast';

const EmployeesSection = () => {
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEmployee, setNewEmployee] = useState({ name: '', email: '' });

  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: humanAgentService.list
  });

  const createMutation = useMutation({
    mutationFn: humanAgentService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['employees']);
      setShowAddForm(false);
      setNewEmployee({ name: '', email: '' });
      showSuccess('Employee added successfully');
    },
    onError: (err) => {
      showError(err.response?.data?.detail || 'Failed to add employee');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: humanAgentService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['employees']);
      showSuccess('Employee removed successfully');
    },
    onError: () => {
      showError('Failed to remove employee');
    }
  });

  const handleAdd = (e) => {
    e.preventDefault();
    if (!newEmployee.name || !newEmployee.email) return;
    createMutation.mutate(newEmployee);
  };

  return (
    <div id="employees-section" className="web-agents-container" style={{ marginTop: '40px' }}>
      <div className="page-header">
        <div>
          <h2>Manage Team</h2>
          <p className="subtitle">Add employees who can log in to handle WhatsApp chats via OTP.</p>
        </div>
        <button 
          className="create-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : <><UserPlus size={18} style={{ marginRight: '8px' }} /> Add Employee</>}
        </button>
      </div>

      {showAddForm && (
        <div className="add-agent-form" style={{ marginBottom: '30px', padding: '20px', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h3>New Employee</h3>
          <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '15px', alignItems: 'end', marginTop: '15px' }}>
            <div className="form-group">
              <label>Full Name</label>
              <input 
                type="text" 
                placeholder="e.g. John Doe"
                value={newEmployee.name}
                onChange={(e) => setNewEmployee({...newEmployee, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Email Address</label>
              <input 
                type="email" 
                placeholder="john@example.com"
                value={newEmployee.email}
                onChange={(e) => setNewEmployee({...newEmployee, email: e.target.value})}
                required
              />
            </div>
            <button type="submit" className="submit-btn" disabled={createMutation.isLoading} style={{ height: '42px' }}>
              {createMutation.isLoading ? <Loader2 className="animate-spin" /> : 'Create'}
            </button>
          </form>
        </div>
      )}

      <div className="employees-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
            <Loader2 className="animate-spin" style={{ margin: '0 auto 10px' }} />
            <p>Loading team...</p>
          </div>
        ) : employees?.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f3f4f6', borderRadius: '12px', gridColumn: '1 / -1' }}>
            <User size={48} style={{ margin: '0 auto 15px', color: '#9ca3af' }} />
            <p style={{ color: '#4b5563', fontWeight: 500 }}>No employees added yet.</p>
            <p style={{ color: '#6b7280', fontSize: '14px' }}>Add your first team member to start handling chats manually.</p>
          </div>
        ) : (
          employees?.map((emp) => (
            <div key={emp.id} className="agent-card" style={{ padding: '20px', borderRadius: '16px', border: '1px solid #e5e7eb', background: 'white', position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <div style={{ width: '45px', height: '45px', borderRadius: '12px', background: emp.is_online ? '#ecfeff' : '#f3f4f6', color: emp.is_online ? '#0891b2' : '#6b7280', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <User size={24} />
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{emp.name}</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#6b7280', marginTop: '2px' }}>
                    <Mail size={12} />
                    {emp.email}
                  </div>
                </div>
              </div>
              
              <div style={{ marginTop: '15px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #f3f4f6', paddingTop: '15px' }}>
                <span style={{ fontSize: '12px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: emp.is_online ? '#10b981' : '#d1d5db' }}></span>
                  {emp.is_online ? 'Online' : 'Offline'}
                </span>
                
                <button 
                  onClick={() => {
                    if (window.confirm(`Are you sure you want to remove ${emp.name}?`)) {
                      deleteMutation.mutate(emp.id);
                    }
                  }}
                  style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '5px' }}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EmployeesSection;
