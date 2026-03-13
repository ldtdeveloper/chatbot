import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { agentAuthService } from '../services/agentAuth';
import { useAuthStore } from '../context/authStore';
import { toast } from 'sonner';
import { Mail, ShieldCheck, ArrowRight, Loader2, MessageSquare, Lock } from 'lucide-react';

const AgentLogin = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  
  const [owner, setOwner] = useState(null);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [securityCode, setSecurityCode] = useState('');
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [fetchingOwner, setFetchingOwner] = useState(true);

  useEffect(() => {
    const fetchOwner = async () => {
      try {
        const data = await agentAuthService.getOwnerInfo(slug);
        setOwner(data);
      } catch (error) {
        toast.error('Invalid login link');
        navigate('/login');
      } finally {
        setFetchingOwner(false);
      }
    };
    fetchOwner();
  }, [slug, navigate]);

  const handleSendOtp = async (e) => {
    e.preventDefault();
    if (!email) return toast.error('Please enter your email');
    
    setLoading(true);
    try {
      await agentAuthService.sendOtp(email, slug);
      setStep(2);
      toast.success('Verification codes sent to your email');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send codes');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!otp || !securityCode) return toast.error('Please fill all fields');
    
    setLoading(true);
    try {
      const data = await agentAuthService.verifyOtp({
        email,
        otp,
        security_code: securityCode
      }, slug);
      
      setAuth(data.access_token, { 
        name: data.agent_name, 
        id: data.agent_id, 
        role: 'agent',
        owner_id: data.owner_id 
      });
      // Persist slug for logout redirection
      localStorage.setItem('agent_slug', slug);
      toast.success(`Welcome back, ${data.agent_name}`);
      // Redirect to whatsapp dashboard with the specific business slug
      navigate(`/whatsapp-dashboard/${slug}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  if (fetchingOwner) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f172a]">
        <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="login-root-container">
      <div className="login-main-card">
        <div className="login-content">
          <div className="login-brand-header">
            <div className="login-icon-box">
              <MessageSquare className="login-icon" />
            </div>
            <h1 className="login-title">Agent Portal</h1>
            <p className="login-subtitle">WhatsApp Customer Support Dashboard</p>
          </div>

          <form onSubmit={step === 1 ? handleSendOtp : handleVerify} className="login-form">
            <div className="login-input-group">
              <label className="login-label">Work Email</label>
              <div className="login-input-wrapper">
                <Mail className="login-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={step === 2 || loading}
                  placeholder={`Your email registered with ${owner?.username || 'the portal'}`}
                  className="login-input"
                  required
                />
              </div>
            </div>

            {step === 2 && (
              <div className="login-step-2 fade-in">
                <div className="login-otp-row">
                  <div className="login-otp-field">
                    <label className="login-label">OTP Code</label>
                    <div className="login-input-wrapper">
                      <Lock className="login-input-icon" />
                      <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        placeholder="000000"
                        className="login-input otp-font"
                        maxLength={6}
                        required
                      />
                    </div>
                  </div>
                  <div className="login-security-field">
                    <label className="login-label">Security Code</label>
                    <input
                      type="text"
                      value={securityCode}
                      onChange={(e) => setSecurityCode(e.target.value)}
                      placeholder="CODE"
                      className="login-input otp-font uppercase"
                      maxLength={6}
                      required
                    />
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="login-primary-btn"
            >
              {loading ? (
                <Loader2 className="spinner" />
              ) : (
                <>
                  <span>{step === 1 ? 'Get Access Codes' : 'Verify & Login'}</span>
                  <ArrowRight className="btn-arrow" />
                </>
              )}
            </button>

            {step === 2 && (
              <button
                type="button"
                onClick={() => setStep(1)}
                className="login-secondary-btn"
              >
                Use a different email
              </button>
            )}
          </form>
        </div>
        
        <div className="login-footer">
          <div className="login-footer-badge">
            <ShieldCheck className="security-icon" />
            <span>ENCRYPTED SESSION • ENTERPRISE SECURITY</span>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .login-root-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #f8fafc;
          padding: 1rem;
          font-family: 'Outfit', sans-serif;
        }
        .login-main-card {
          width: 100%;
          max-width: 440px;
          background: white;
          border-radius: 32px;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
          border: 1px solid #e2e8f0;
          overflow: hidden;
        }
        .login-content {
          padding: 3rem;
        }
        .login-brand-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }
        .login-icon-box {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 56px;
          height: 56px;
          background: rgba(101, 36, 235, 0.1);
          border-radius: 16px;
          margin-bottom: 1.5rem;
          transition: transform 0.2s;
        }
        .login-icon-box:hover { transform: scale(1.05); }
        .login-icon { width: 28px; height: 28px; color: #6524eb; }
        .login-title {
          font-size: 1.75rem;
          font-weight: 800;
          color: #0f172a;
          margin-bottom: 0.5rem;
          letter-spacing: -0.025em;
        }
        .login-subtitle {
          font-size: 0.875rem;
          color: #64748b;
          font-weight: 500;
        }
        .login-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .login-label {
          display: block;
          font-size: 0.8125rem;
          font-weight: 700;
          color: #475569;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.5rem;
        }
        .login-input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }
        .login-input-icon {
          position: absolute;
          left: 1rem;
          width: 18px;
          height: 18px;
          color: #94a3b8;
        }
        .login-input {
          width: 100%;
          padding: 0.875rem 1rem 0.875rem 3rem;
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          font-size: 0.9375rem;
          color: #0f172a;
          outline: none;
          transition: all 0.2s;
        }
        .login-input:focus {
          border-color: #6524eb;
          box-shadow: 0 0 0 4px rgba(101, 36, 235, 0.1);
        }
        .login-input::placeholder { color: #94a3b8; }
        .login-otp-row { display: flex; gap: 1rem; }
        .login-otp-field { flex: 1; }
        .login-security-field { flex: 1; }
        .login-security-field .login-input { padding-left: 1rem; text-align: center; }
        .otp-font { font-family: monospace; letter-spacing: 0.15em; text-align: center; }
        .uppercase { text-transform: uppercase; }
        .login-primary-btn {
          width: 100%;
          padding: 0.875rem;
          background-color: #6524eb;
          color: white;
          font-weight: 700;
          font-size: 0.9375rem;
          border-radius: 12px;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          transition: all 0.2s;
          box-shadow: 0 4px 12px rgba(101, 36, 235, 0.2);
        }
        .login-primary-btn:hover { background-color: #521dbe; transform: translateY(-1px); }
        .login-primary-btn:active { transform: translateY(0); }
        .login-primary-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .btn-arrow { width: 18px; height: 18px; }
        .spinner { width: 20px; height: 20px; animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .login-secondary-btn {
          background: none;
          border: none;
          color: #64748b;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: color 0.2s;
        }
        .login-secondary-btn:hover { color: #6524eb; }
        .login-footer {
          background-color: #f8fafc;
          padding: 1.5rem;
          border-top: 1px solid #f1f5f9;
          text-align: center;
        }
        .login-footer-badge {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          font-size: 0.75rem;
          font-weight: 700;
          color: #94a3b8;
          letter-spacing: -0.01em;
        }
        .security-icon { width: 14px; height: 14px; color: #22c55e; }
        .fade-in { animation: fadeIn 0.4s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}} />
    </div>
  );
};

export default AgentLogin;
