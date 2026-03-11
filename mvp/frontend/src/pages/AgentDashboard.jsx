import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Zap, 
  Activity, 
  Search, 
  Bot, 
  Phone, 
  History, 
  MoreVertical, 
  Shield, 
  ArrowRight,
  Headphones,
  CheckCircle2,
  Clock,
  Sparkles,
  Mail,
  Lock,
  MessageSquare,
  LogOut,
  Download
} from 'lucide-react';
import api from '../services/api';
import config from '../config/env';
import { toast } from 'sonner';
import { useParams } from 'react-router-dom';

const AgentDashboardComponent = () => {
  const navigate = useNavigate();
  const { slug: urlSlug } = useParams();
  const [loggedIn, setLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [selectedConvo, setSelectedConvo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  
  // Login states
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [securityCode, setSecurityCode] = useState('');
  const [step, setStep] = useState('email');
  const [loginLoading, setLoginLoading] = useState(false);

  const [searchTerm, setSearchTerm] = useState('');
  const ws = useRef(null);
  const scrollRef = useRef(null);

  const filteredConversations = conversations.filter(convo => 
    convo.identifier.includes(searchTerm) || 
    (convo.summary && convo.summary.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setLoggedIn(true);
      fetchConversations();
    }
  }, []);

  useEffect(() => {
    if (loggedIn) {
      connectWebSocket();
    }
    return () => {
      if (ws.current) ws.current.close();
    };
  }, [loggedIn]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/handoff/active');
      setConversations(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setLoggedIn(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    let ownerId = 'broadcast';
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      ownerId = payload.owner_id || 'broadcast';
    } catch (e) {
      console.error("Failed to decode token", e);
    }

    const API_BASE = config?.API_BASE_URL || 'http://localhost:8081';
    const WS_URL = `${API_BASE.replace('http', 'ws')}/handoff/ws/dashboard/${ownerId}`;
    console.log(`[WS] Connecting to ${WS_URL}`);
    
    try {
      ws.current = new WebSocket(WS_URL);
    } catch (wsError) {
      console.error("[WS] Initialization error", wsError);
      return;
    }

    ws.current.onopen = () => {
      console.log('[WS] Connected');
      setWsConnected(true);
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('[WS] Received:', data);
      
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      const currentAgentId = parseInt(userData.id); // Ensure numeric comparison

      if (data.type === 'agent_assigned') {
        if (parseInt(data.agent_id) !== currentAgentId) {
          toast.info(`${data.agent_name} claimed chat +${data.whatsapp_number}`);
          setConversations(prev => prev.filter(c => c.conversation_id !== data.conversation_id));
          
          if (selectedConvo?.conversation_id === data.conversation_id) {
            setSelectedConvo(null);
            setMessages([]);
            toast.error('This chat was just claimed by another agent');
          }
        } else {
           fetchConversations();
        }
      } else if (data.type === 'handoff_alert' || data.type === 'new_handover') {
        fetchConversations();
      }
      
      if (data.type === 'new_message') {
        const incomingNum = data.whatsapp_number.replace(/^\+/, '');
        if (selectedConvo) {
           const selectedNum = selectedConvo.identifier.replace(/^\+/, '');
           if (selectedNum === incomingNum) {
             setMessages(prev => [...prev, { 
               content: data.content, 
               is_from_contact: true, 
               sender_name: "User",
               timestamp: data.timestamp || new Date().toISOString() 
             }]);
           }
        }
        setConversations(prev => prev.map(c => 
          c.identifier === incomingNum || c.identifier === data.whatsapp_number 
          ? { ...c, summary: data.content } 
          : c
        ));
      }
    };
    ws.current.onclose = () => {
      console.log('[WS] Disconnected');
      setWsConnected(false);
      setTimeout(connectWebSocket, 3000);
    };
    ws.current.onerror = (err) => {
      console.error('[WS] Error:', err);
    };
  };

  const fetchMessages = async (convoId) => {
    try {
      const response = await api.get(`/handoff/messages/${convoId}`);
      setMessages(response.data);
    } catch (err) {
      toast.error("Failed to load history");
    }
  };

  const claimConversation = (convo) => {
    if (!ws.current) return;
    if (selectedConvo?.conversation_id === convo.conversation_id) return;

    // Get current agent info for claim
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const agentId = userData.id;
    const agentName = userData.name || "Agent";

    ws.current.send(JSON.stringify({
      type: "claim",
      whatsapp_number: convo.identifier,
      agent_name: agentName,
      agent_id: agentId,
      conversation_id: convo.conversation_id
    }));
    setSelectedConvo(convo);
    fetchMessages(convo.conversation_id);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConvo || !ws.current) return;
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    ws.current.send(JSON.stringify({
      type: "message",
      to: selectedConvo.identifier,
      text: newMessage,
      conversation_id: selectedConvo.conversation_id
    }));
    setMessages(prev => [...prev, { 
      content: newMessage, 
      is_from_contact: false, 
      is_from_agent: true, 
      sender_name: userData.name || "Agent",
      timestamp: new Date().toISOString() 
    }]);
    setNewMessage('');
  };

  const releaseToAI = async () => {
    if (!selectedConvo) return;
    try {
      await api.post(`/handoff/release?conversation_id=${selectedConvo.conversation_id}`);
      setSelectedConvo(null);
      fetchConversations();
    } catch (error) {
      toast.error('Failed to release');
    }
  };

  const downloadHistory = async () => {
    if (!selectedConvo) return;
    try {
      const response = await api.get(`/handoff/download/${selectedConvo.conversation_id}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `history_${selectedConvo.identifier}_${selectedConvo.conversation_id}.txt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Failed to download log');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setLoggedIn(false);
    setSelectedConvo(null);
    setMessages([]);
    
    const slug = urlSlug || localStorage.getItem('agent_slug') || 'default';
    navigate(`/agent-login/${slug}`);
  };

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      await api.post('/human-agent/send-otp', { email, slug: urlSlug || 'default' });
      setStep('otp');
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to send OTP");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
        const res = await api.post('/human-agent/verify-otp', { 
        email, 
        otp,
        security_code: securityCode,
        slug: urlSlug || 'default'
      });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify({
        id: res.data.agent_id,
        name: res.data.agent_name,
        role: 'agent',
        owner_id: res.data.owner_id
      }));
      setLoggedIn(true);
      fetchConversations();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid OTP or Security Code");
    } finally {
      setLoginLoading(false);
    }
  };

  if (!loggedIn) {
    return (
      <div className="login-page-standalone">
        <div className="login-card-standalone">
          <div className="login-header-standalone">
             <div className="login-logo-standalone">
                <Zap size={24} color="white" />
             </div>
             <h1>Agent Console</h1>
             <p>Human Response Protocol v4</p>
          </div>

          <form className="login-form-standalone" onSubmit={step === 'email' ? handleSendOtp : handleVerifyOtp}>
            {step === 'email' ? (
              <div className="input-field-standalone">
                <label>Auth Identifier</label>
                <div className="input-row-standalone">
                  <Mail size={18} />
                  <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="agent@ldt.com" required />
                </div>
              </div>
            ) : (
              <>
                <div className="input-field-standalone">
                  <label>Secure Key (OTP)</label>
                  <div className="input-row-standalone">
                    <Lock size={18} />
                    <input type="text" value={otp} onChange={e => setOtp(e.target.value)} placeholder="6-digit key" maxLength={6} required />
                  </div>
                </div>
                <div className="input-field-standalone">
                  <label>Security Code</label>
                  <div className="input-row-standalone">
                    <Shield size={18} />
                    <input type="text" value={securityCode} onChange={e => setSecurityCode(e.target.value.toUpperCase())} placeholder="ABCDEF" maxLength={6} required />
                  </div>
                </div>
              </>
            )}
            <button type="submit" className="login-btn-standalone" disabled={loginLoading}>
              {loginLoading ? 'Authenticating...' : (step === 'email' ? 'Request Key' : 'Unlock Console')}
              {!loginLoading && <ArrowRight size={18} />}
            </button>
          </form>
          <div className="login-footer-standalone"><Shield size={14} /><span>Verified Agent Session</span></div>
        </div>
        <style dangerouslySetInnerHTML={{ __html: `
          .login-page-standalone { height: 100vh; width: 100vw; background: radial-gradient(circle at top left, #f8fafc, #f1f5f9); display: flex; align-items: center; justify-content: center; font-family: 'Outfit', sans-serif; }
          .login-card-standalone { width: 100%; max-width: 440px; background: white; padding: 48px; border-radius: 32px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }
          .login-header-standalone { text-align: center; margin-bottom: 40px; }
          .login-logo-standalone { width: 56px; height: 56px; background: #4f46e5; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 24px; box-shadow: 0 10px 15px -3px rgba(79,70,229,0.4); }
          .login-header-standalone h1 { font-size: 1.75rem; font-weight: 800; color: #0f172a; margin: 0; }
          .login-header-standalone p { font-size: 0.875rem; color: #64748b; margin-top: 8px; }
          .input-field-standalone { margin-bottom: 24px; }
          .input-field-standalone label { display: block; font-size: 0.8125rem; font-weight: 700; color: #475569; margin-bottom: 8px; text-transform: uppercase; }
          .input-row-standalone { position: relative; display: flex; align-items: center; }
          .input-row-standalone svg { position: absolute; left: 16px; color: #94a3b8; }
          .input-row-standalone input { width: 100%; padding: 14px 16px 14px 48px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 0.9375rem; outline: none; }
          .login-btn-standalone { width: 100%; padding: 14px; background: #0f172a; color: white; border: none; border-radius: 12px; font-size: 0.9375rem; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 12px; cursor: pointer; }
          .login-footer-standalone { margin-top: 40px; padding-top: 24px; border-top: 1px solid #f1f5f9; display: flex; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; font-size: 0.75rem; font-weight: 600; }
        `}} />
      </div>
    );
  }

  return (
    <div className="wa-dashboard-container">
      <aside className="wa-sidebar">
        <div className="wa-sidebar-header">
           <div className="wa-brand">
              <div className="wa-logo-bg"><Zap size={18} color="white" /></div>
              <h2>Agent Queue</h2>
           </div>
           <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
             <div className={`wa-status ${wsConnected ? 'live' : 'offline'}`}>
                <Activity size={12} className={wsConnected ? 'pulse' : ''} />
                {wsConnected ? 'LIVE' : 'DOWN'}
             </div>
             <button 
               className="wa-logout-btn" 
               onClick={handleLogout}
               title="Logout"
             >
               <LogOut size={16} />
             </button>
           </div>
        </div>
        <div className="wa-search-box"><Search size={16} /><input type="text" placeholder="Filter..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} /></div>
        <div className="wa-queue-list custom-scrollbar">
          {loading ? (
            <div className="wa-loading"><div className="wa-spinner"></div><p>Syncing...</p></div>
          ) : filteredConversations.length === 0 ? (
            <div className="wa-empty"><Bot size={32} color="#c7d2fe" /><h3>Queue Clear</h3></div>
          ) : (
            filteredConversations.map(convo => (
              <div key={convo.conversation_id} className={`wa-item ${selectedConvo?.conversation_id === convo.conversation_id ? 'active' : ''}`} onClick={() => claimConversation(convo)}>
                <div className="wa-item-header">
                  <div className="wa-avatar">{convo.identifier.slice(-2)}</div>
                  <div className="wa-meta">
                    <p className="wa-name">+{convo.identifier}</p>
                    <p className="wa-time">{new Date(convo.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                  </div>
                </div>
                <p className="wa-summary">"{convo.summary || 'Waiting...'}"</p>
              </div>
            ))
          )}
        </div>
      </aside>

      <main className="wa-chat-main">
        {selectedConvo ? (
          <div className="wa-chat-window">
             <header className="wa-chat-header">
                <div className="wa-chat-info">
                   <div className="wa-chat-avatar"><Phone size={20} /></div>
                   <div><h3>+{selectedConvo.identifier}</h3><div className="wa-chat-status"><History size={12} /><span>Human Session</span></div></div>
                </div>
                <div className="wa-chat-actions">
                   <button className="wa-download-btn" onClick={downloadHistory} title="Download .txt log">
                      <Download size={16} /> History
                   </button>
                   <button className="wa-close-btn" onClick={releaseToAI}>Transfer to AI</button>
                </div>
             </header>
             <div className="wa-chat-body custom-scrollbar" ref={scrollRef}>
                  {messages.map((m, i) => (
                    <div key={i} className={`wa-msg-row ${m?.is_from_contact ? 'in' : 'out'}`}>
                       <div className="wa-msg-bubble">
                          <div className="wa-msg-sender">{(m?.sender_name) || (m?.is_from_contact ? 'Customer' : 'Agent')}</div>
                          {m?.content}
                          <span className="wa-msg-time">{m?.timestamp ? new Date(m.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''}</span>
                       </div>
                    </div>
                  ))}
             </div>
             <footer className="wa-chat-footer">
                <form className="wa-input-row" onSubmit={handleSendMessage}>
                   <div className="wa-input-wrap"><input type="text" value={newMessage} onChange={e => setNewMessage(e.target.value)} placeholder="Type reply..." /><Sparkles size={16} /></div>
                   <button type="submit" className="wa-send-btn" disabled={!newMessage.trim()}><ArrowRight size={24} /></button>
                </form>
             </footer>
          </div>
        ) : (
          <div className="wa-welcome">
             <div className="wa-welcome-box"><Headphones size={64} color="#4f46e5" /><div className="wa-welcome-badge">Systems Ready</div></div>
             <h1>Agent Workspace</h1>
             <p>Select a waiting customer to take over. AI will stand by during your session.</p>
          </div>
        )}
      </main>
      <style dangerouslySetInnerHTML={{ __html: `
        .wa-dashboard-container { display: flex; height: 100vh; width: 100vw; background: #f8fafc; font-family: 'Outfit', sans-serif; overflow: hidden; }
        .wa-sidebar { width: 320px; background: white; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; }
        .wa-sidebar-header { padding: 24px; display: flex; justify-content: space-between; align-items: center; }
        .wa-brand { display: flex; align-items: center; gap: 12px; }
        .wa-logo-bg { background: #4f46e5; width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .wa-brand h2 { font-size: 1.125rem; font-weight: 800; color: #0f172a; margin: 0; }
        .wa-status { display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 0.6875rem; font-weight: 800; }
        .wa-status.live { background: #ecfdf5; color: #059669; }
        .wa-status.offline { background: #fef2f2; color: #dc2626; }
        .wa-logout-btn { background: #f1f5f9; color: #64748b; border: none; width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
        .wa-logout-btn:hover { background: #fee2e2; color: #dc2626; transform: scale(1.05); }
        .wa-search-box { margin: 0 24px 20px; position: relative; }
        .wa-search-box input { width: 100%; padding: 12px 14px 12px 42px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; font-size: 0.8125rem; outline: none; }
        .wa-search-box svg { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
        .wa-queue-list { flex: 1; overflow-y: auto; padding: 0 12px 12px; }
        .wa-item { padding: 16px; border-radius: 20px; cursor: pointer; transition: all 0.2s; margin-bottom: 8px; border: 1px solid transparent; }
        .wa-item:hover { background: #f8fafc; }
        .wa-item.active { background: #4f46e5; color: white; }
        .wa-item-header { display: flex; gap: 12px; margin-bottom: 8px; }
        .wa-avatar { width: 42px; height: 42px; background: #f1f5f9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.75rem; color: #64748b; }
        .wa-item.active .wa-avatar { background: rgba(255,255,255,0.2); color: white; }
        .wa-meta { flex: 1; }
        .wa-name { font-weight: 700; font-size: 0.875rem; margin: 0; }
        .wa-time { font-size: 0.6875rem; opacity: 0.5; margin-top: 2px; }
        .wa-summary { font-size: 0.75rem; font-style: italic; opacity: 0.8; margin: 0; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
        .wa-chat-main { flex: 1; background: #f8fafc; display: flex; flex-direction: column; }
        .wa-chat-window { flex: 1; margin: 16px; background: white; border-radius: 32px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; overflow: hidden; }
        .wa-chat-header { height: 80px; padding: 0 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; }
        .wa-chat-info { display: flex; align-items: center; gap: 16px; }
        .wa-chat-avatar { width: 48px; height: 48px; background: #e0e7ff; color: #4f46e5; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
        .wa-chat-info h3 { font-size: 1.125rem; font-weight: 800; margin: 0; }
        .wa-chat-status { display: flex; align-items: center; gap: 6px; font-size: 0.6875rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
        .wa-close-btn { padding: 10px 20px; background: #0f172a; color: white; border-radius: 14px; font-size: 0.75rem; font-weight: 700; border: none; cursor: pointer; }
        .wa-download-btn { padding: 10px 20px; background: #f1f5f9; color: #4f46e5; border-radius: 14px; font-size: 0.75rem; font-weight: 700; border: none; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .wa-download-btn:hover { background: #e0e7ff; }
        .wa-chat-actions { display: flex; gap: 12px; align-items: center; }
        .wa-chat-body { flex: 1; padding: 40px; overflow-y: auto; background: #fcfcfd; display: flex; flex-direction: column; gap: 16px; }
        .wa-msg-row { display: flex; width: 100%; }
        .wa-msg-row.in { justify-content: flex-start; }
        .wa-msg-row.out { justify-content: flex-end; }
        .wa-msg-bubble { max-width: 500px; padding: 12px 18px; font-size: 0.875rem; line-height: 1.6; position: relative; }
        .wa-msg-sender { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; opacity: 0.7; letter-spacing: 0.02em; }
        .in .wa-msg-sender { color: #6366f1; }
        .out .wa-msg-sender { color: rgba(255,255,255,0.8); }
        .in .wa-msg-bubble { background: white; color: #0f172a; border: 1px solid #e2e8f0; border-radius: 18px 18px 18px 0; }
        .out .wa-msg-bubble { background: #4f46e5; color: white; border-radius: 18px 18px 0 18px; }
        .wa-msg-time { display: block; font-size: 0.625rem; font-weight: 800; margin-top: 8px; text-transform: uppercase; opacity: 0.5; }
        .wa-chat-footer { padding: 32px; border-top: 1px solid #f1f5f9; }
        .wa-input-row { display: flex; gap: 16px; max-width: 900px; margin: 0 auto; }
        .wa-input-wrap { flex: 1; position: relative; }
        .wa-input-wrap input { width: 100%; padding: 16px 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 18px; font-size: 0.875rem; outline: none; }
        .wa-input-wrap svg { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); color: #4f46e5; opacity: 0.3; }
        .wa-send-btn { width: 56px; height: 56px; border-radius: 18px; background: #4f46e5; color: white; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .wa-welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; text-align: center; }
        .wa-welcome h1 { font-size: 2.5rem; font-weight: 900; color: #0f172a; margin-top: 40px; }
        .wa-spinner { width: 32px; height: 32px; border: 3px solid #4f46e5; border-top-color: transparent; border-radius: 50%; animation: wa-spin 1s linear infinite; }
        .custom-scrollbar::-webkit-scrollbar { width: 5px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
        @keyframes wa-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}} />
    </div>
  );
};

export default AgentDashboardComponent;
