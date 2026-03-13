import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
// socket.io-client removed in favor of raw WebSockets
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
  Bell,
  Check,
  CheckCheck,
  User,
  Trash2,
  LogOut
} from 'lucide-react';
import { showError, showSuccess } from '../utils/toast';
import config from '../config/env';
import './WhatsappDashboard.css';

// Socket URL from config with safety fallback
const SOCKET_URL = config?.API_BASE_URL || 'http://localhost:8081';

const WhatsappDashboardView = () => {
  const navigate = useNavigate();
  const { slug: urlSlug } = useParams();
  const [user, setUser] = useState(null);
  const [loggedIn, setLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [queue, setQueue] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const selectedChatRef = useRef(null); // CRITICAL for websocket closure
  
  // Sync ref with state
  useEffect(() => {
    selectedChatRef.current = selectedChat;
  }, [selectedChat]);

  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Login states
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState('email');
  const [loginLoading, setLoginLoading] = useState(false);

  const socketRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setLoggedIn(true);
      fetchQueue();
      
      const storedUser = localStorage.getItem('user');
      if (storedUser) setUser(JSON.parse(storedUser));
    }

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (loggedIn) {
      connectSocket();
    }
  }, [loggedIn]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const connectSocket = () => {
    if (socketRef.current) {
        if (socketRef.current.readyState === WebSocket.OPEN || 
            socketRef.current.readyState === WebSocket.CONNECTING) return;
        
        socketRef.current.onclose = null; // Prevent recursion
        socketRef.current.close();
        socketRef.current = null;
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    let ownerId = 'broadcast';
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      ownerId = payload.owner_id || 'broadcast';
    } catch (e) {
      console.error("Failed to decode token", e);
    }

    const WS_URL = `${SOCKET_URL.replace('http', 'ws')}/handoff/ws/dashboard/${ownerId}`;
    socketRef.current = new WebSocket(WS_URL);

    socketRef.current.onopen = () => {
      console.log('✅ Socket connected to', WS_URL);
      setWsConnected(true);
      
      // Add heartbeat (ping) every 30 seconds
      if (socketRef.current.heartbeat) clearInterval(socketRef.current.heartbeat);
      socketRef.current.heartbeat = setInterval(() => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    socketRef.current.onerror = (err) => {
      console.error('❌ Socket error:', err);
      setWsConnected(false);
      // Close will trigger onclose
      if (socketRef.current) socketRef.current.close();
    };

    socketRef.current.onclose = (event) => {
       console.log('⚠️ Socket closed:', event.code, event.reason);
       setWsConnected(false);
       if (socketRef.current?.heartbeat) clearInterval(socketRef.current.heartbeat);
       socketRef.current = null;
       setTimeout(connectSocket, 3000); // Auto-reconnect
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Socket message:', data);

      if (data.type === 'new_handover') {
        const chat = data;
        setQueue(prev => {
          const exists = prev.find(c => c.id === chat.conversation_id);
          if (exists) return prev;
          return [{
            id: chat.conversation_id,
            customer: chat.customer || chat.identifier,
            identifier: chat.identifier,
            time: 'Just now',
            status_text: 'Waiting for help'
          }, ...prev];
        });
        
        const newNotif = { 
          id: Date.now(),
          convo_id: chat.conversation_id,
          name: chat.customer || 'New Customer', 
          time: 'Just now',
          status: 'waiting' 
        };
        setNotifications(prev => [newNotif, ...prev]);
        showSuccess(`New request from ${newNotif.name}`);
      }

      if (data.type === 'agent_assigned') {
         // Only refresh if it's ANOTHER agent who claimed it
         const currentAgentId = user?.agent_id || user?.id;
         if (currentAgentId && String(data.agent_id) !== String(currentAgentId)) {
           fetchQueue(true); // silent refresh
         } else {
           // It's us, just update queue state
           setQueue(prev => prev.filter(c => c.id !== data.conversation_id));
         }
      }

      if (data.type === 'new_message') {
        const currentChat = selectedChatRef.current;
        console.log("Incoming message for convo:", data.conversation_id, "Current chat:", currentChat?.id);

        if (currentChat && String(data.conversation_id) === String(currentChat.id)) {
          const senderType = data.from === 'agent' ? 'agent' : 'customer';
          const newMsg = { 
            from: senderType, 
            text: data.content, 
            timestamp: data.timestamp || new Date().toISOString() 
          };
          
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.text === newMsg.text && lastMsg.from === newMsg.from) {
               return prev; 
            }
            return [...prev, newMsg];
          });
          
          // Also update the snippet in the queue list
          setQueue(prev => prev.map(c => 
            String(c.id) === String(data.conversation_id) 
              ? { ...c, status_text: data.content, time: 'Just now' } 
              : c
          ));

        } else if (data.from !== 'agent') {
          // Add to notifications
          const newMsgNotif = {
            id: Date.now(),
            convo_id: data.conversation_id,
            name: data.whatsapp_number || 'Customer',
            text: data.content,
            time: 'Just now',
            status: 'unread'
          };
          setNotifications(prev => [newMsgNotif, ...prev]);
          
          // Also update snippet in queue
          setQueue(prev => prev.map(c => 
            String(c.id) === String(data.conversation_id) 
              ? { ...c, status_text: data.content, time: 'Just now' } 
              : c
          ));
        }
      }
    };
  };

  const fetchQueue = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await api.get('/handoff/active');
      // Map backend fields to UI expectations
      const mappedData = res.data.map(item => ({
        ...item,
        id: item.conversation_id,
        customer: item.identifier,
        time: item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Just now',
        status_text: item.summary || 'Waiting for help'
      }));
      setQueue(mappedData);
      
      // If we have a selected chat, ensure it's updated with latest from queue
      if (selectedChatRef.current) {
        const updated = mappedData.find(c => String(c.id) === String(selectedChatRef.current.id));
        if (updated) setSelectedChat(updated);
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setLoggedIn(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (chatId) => {
    try {
      const res = await api.get(`/handoff/messages/${chatId}`);
      const history = res.data.map(m => ({
        from: m.is_from_contact ? 'customer' : 'agent',
        text: m.content,
        timestamp: m.timestamp
      }));
      setMessages(history);
    } catch (err) {
      console.error("fetchHistory Error:", err);
      showError("Failed to load history");
    }
  };

  const takeover = async (chatId) => {
    try {
      const chat = queue.find(c => c.id === chatId);
      const res = await api.post(`/handoff/takeover/${chatId}`);
      // Maintain consistent chat object structure
      const updatedChat = {
        ...chat,
        id: res.data.id || chatId,
        identifier: res.data.identifier || chat.identifier,
        assigned_agent_id: user?.agent_id || user?.id
      };
      setSelectedChat(updatedChat);
      fetchHistory(updatedChat.id);
      setNotifications(prev => prev.filter(n => n.convo_id !== chatId));
      // Refresh queue to move chat from Waiting to My Chats
      fetchQueue(true);
    } catch (err) {
      console.error("Takeover Error:", err);
      showError("Failed to takeover");
    }
  };

  const releaseToAI = async () => {
    if (!selectedChat) return;
    try {
      await api.post(`/handoff/release/${selectedChat.id}`);
      showSuccess("Handed back to AI");
      setSelectedChat(null);
      fetchQueue();
    } catch (err) {
      showError("Failed to release chat");
    }
  };

  const sendMessage = (e) => {
    if (e) e.preventDefault();
    if (!inputMsg.trim() || !selectedChat || !socketRef.current) return;

    if (socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'message',
        conversation_id: selectedChat.id,
        to: selectedChat.identifier,
        text: inputMsg
      }));
      // Manually add to view to ensure immediate feedback
      const newMsg = { from: 'agent', text: inputMsg, timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, newMsg]);
      setInputMsg('');
    } else {
      showError("Connection lost, please refresh");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setLoggedIn(false);
    const slug = urlSlug || localStorage.getItem('agent_slug') || 'default';
    navigate(`/agent-login/${slug}`);
  };

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      const slug = urlSlug || localStorage.getItem('agent_slug');
      await api.post('/human-agent/send-otp', { email, slug });
      setStep('otp');
    } catch (err) {
      showError("Failed to send OTP");
    } finally {
      setLoginLoading(false);
    }
  };

  const [securityCode, setSecurityCode] = useState('');
  const [userProfile, setUserProfile] = useState(null); // Add separate user profile state
  
  // Decoding user info on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser(payload); // payload usually has id / email
      } catch (e) {}
    }
  }, []);
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      const slug = urlSlug || localStorage.getItem('agent_slug');
      const res = await api.post('/human-agent/verify-otp', { 
        email, 
        otp, 
        slug, 
        security_code: securityCode 
      });
      localStorage.setItem('token', res.data.access_token);
      if (slug) localStorage.setItem('agent_slug', slug);
      setLoggedIn(true);
      fetchQueue();
    } catch (err) {
      showError("Invalid OTP");
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
             <h1>Agent Portal</h1>
             <p>Enterprise Handoff System</p>
          </div>

          <form className="login-form-standalone" onSubmit={step === 'email' ? handleSendOtp : handleVerifyOtp}>
            {step === 'email' && (
              <div className="input-field-standalone">
                <label>Work Email</label>
                <div className="input-row-standalone">
                  <Mail size={18} />
                  <input 
                    type="email" 
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    required
                  />
                </div>
              </div>
            )}

            {step === 'otp' && (
              <div className="login-step-otp animate-in fade-in slide-in-from-bottom-4">
                <div className="input-field-standalone">
                  <label>Verification OTP</label>
                  <div className="input-row-standalone">
                    <Shield size={18} />
                    <input 
                      type="text" 
                      placeholder="6-digit OTP" 
                      value={otp}
                      onChange={e => setOtp(e.target.value)}
                      required 
                    />
                  </div>
                </div>
                <div className="input-field-standalone">
                  <label>Security Code</label>
                  <div className="input-row-standalone">
                    <Lock size={18} />
                    <input 
                      type="text" 
                      placeholder="Security Code" 
                      value={securityCode}
                      onChange={e => setSecurityCode(e.target.value)}
                      required 
                    />
                  </div>
                </div>
                <p className="resend-text">Codes sent to <strong>{email}</strong></p>
              </div>
            )}

            <button type="submit" className="login-btn-standalone" disabled={loginLoading}>
              {loginLoading ? 'Processing...' : (step === 'email' ? 'Send Access Code' : 'Verify & Enter')}
              {!loginLoading && <ArrowRight size={18} />}
            </button>
          </form>

          <div className="login-footer-standalone">
             <Shield size={14} />
             <span>Secure Session • LDT Protocol v4</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="wa-dashboard-container">
      <aside className="wa-sidebar">
        <div className="wa-sidebar-header">
           <div className="wa-brand">
              <div className="wa-logo-bg-brand">
                 <MessageSquare size={20} color="white" />
              </div>
              <div className="wa-brand-text">
                 <h2>Support Hub</h2>
                 <p>WhatsApp Dashboard</p>
              </div>
           </div>
            <div className="wa-header-actions">
               <div className={`wa-conn-status ${wsConnected ? 'online' : 'offline'}`} title={wsConnected ? 'WebSocket Online' : 'WebSocket Reconnecting...'}>
                  <div className="wa-conn-dot"></div>
                  <span>{wsConnected ? 'Live' : 'Syncing...'}</span>
               </div>
               <div className="wa-notif-bell" onClick={() => setShowNotifications(!showNotifications)}>
                  <Bell size={20} />
                  {notifications.length > 0 && <div className="wa-notif-badge">{notifications.length}</div>}
               </div>
               <button className="wa-logout-btn-minimal" onClick={handleLogout} title="Logout">
                  <LogOut size={20} />
               </button>
            </div>
        </div>

        <div className="wa-stats-grid">
           <div className="wa-stat-card waiting active-stat">
              <div className="wa-stat-label"><Clock size={14} /> Waiting</div>
              <div className="wa-stat-value">{queue.filter(c => !c.assigned_agent_id).length}</div>
           </div>
           <div className="wa-stat-card active">
              <div className="wa-stat-label"><Check size={14} /> My Chats</div>
              <div className="wa-stat-value">{queue.filter(c => c.assigned_agent_id === (user?.agent_id || user?.id)).length}</div>
           </div>
           <div className="wa-stat-card ai">
              <div className="wa-stat-label"><Bot size={14} /> AI</div>
              <div className="wa-stat-value">Online</div>
           </div>
        </div>

        {/* --- MY ACTIVE CHATS --- */}
        <div className="wa-section-header" style={{ marginTop: '16px' }}>
           <h3><Activity size={12} /> MY ACTIVE CHATS</h3>
           <div className="wa-status-badge-green">
             {queue.filter(c => c.assigned_agent_id === (user?.agent_id || user?.id)).length}
           </div>
        </div>
        <div className="wa-queue-list compact custom-scrollbar" style={{ maxHeight: '30vh' }}>
          {queue.filter(c => c.assigned_agent_id === (user?.agent_id || user?.id)).map(chat => (
            <div 
              key={chat.id} 
              className={`wa-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
              onClick={() => {
                if (selectedChat?.id !== chat.id) {
                  setSelectedChat(chat);
                  setMessages([]);
                  fetchHistory(chat.id);
                }
              }}
            >
              <div className="wa-item-main">
                <div className="wa-avatar" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                   {chat.customer?.[0] || 'C'}
                </div>
                <div className="wa-info">
                   <div className="wa-name-row">
                      <span className="wa-name">{chat.customer || 'Customer'}</span>
                      <span className="wa-time">{chat.time}</span>
                   </div>
                   <p className="wa-status-snippet">{chat.status_text}</p>
                </div>
              </div>
              <div className="wa-item-actions">
                <div className="wa-status-badge">
                   <CheckCircle2 size={12} />
                   <span>Active</span>
                </div>
              </div>
            </div>
          ))}
          {queue.filter(c => c.assigned_agent_id === (user?.agent_id || user?.id)).length === 0 && (
            <p className="wa-empty-small">No claimed chats yet</p>
          )}
        </div>

        {/* --- WAITING QUEUE --- */}
        <div className="wa-section-header" style={{ marginTop: '16px' }}>
           <h3><Clock size={12} /> WAITING QUEUE</h3>
           <div className="wa-status-badge-orange">
             {queue.filter(c => !c.assigned_agent_id).length}
           </div>
        </div>

        <div className="wa-queue-list custom-scrollbar">
          {loading ? (
            <div className="wa-loading">
               <div className="wa-spinner"></div>
               <p>Updating...</p>
            </div>
          ) : queue.filter(c => !c.assigned_agent_id).length === 0 ? (
            <div className="wa-empty">
               <div className="wa-empty-icon">
                  <Bot size={28} />
               </div>
               <h3>All Clear</h3>
               <p>No waiting customers</p>
            </div>
          ) : (
            queue.filter(c => !c.assigned_agent_id).map(chat => (
              <div 
                key={chat.id} 
                className={`wa-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
                onClick={() => {
                  if (selectedChat?.id !== chat.id) {
                    setSelectedChat(chat);
                    setMessages([]);
                    fetchHistory(chat.id);
                  }
                }}
              >
                <div className="wa-item-main">
                  <div className="wa-avatar">
                     {chat.customer?.[0] || 'C'}
                  </div>
                  <div className="wa-info">
                     <div className="wa-name-row">
                        <span className="wa-name">{chat.customer || 'Customer'}</span>
                        <span className="wa-time">{chat.time || 'Just now'}</span>
                     </div>
                     <p className="wa-status-snippet">{chat.status_text || 'Waiting for help'}</p>
                  </div>
                </div>
                <div className="wa-item-actions">
                  <button className="wa-claim-btn-inside" onClick={(e) => {
                    e.stopPropagation();
                    takeover(chat.id);
                  }}>
                    Claim
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {user && (
          <div className="wa-sidebar-footer">
            <div className="wa-agent-profile">
               <div className="wa-agent-avatar">{user.name?.[0] || 'A'}</div>
               <div className="wa-agent-info">
                  <p className="wa-agent-name">{user.name}</p>
                  <p className="wa-agent-role">Active Session</p>
               </div>
            </div>
          </div>
        )}
      </aside>

      <main className="wa-chat-main">
        {showNotifications && (
           <div className="wa-notifications-overlay">
              <div className="wa-notifications-card border shadow-lg animate-in fade-in zoom-in duration-200">
                 <div className="wa-notif-header">
                    <div className="wa-notif-title">
                       <h3>Notifications</h3>
                    </div>
                    <button onClick={() => setNotifications([])} className="wa-clear-btn">Clear all</button>
                 </div>
                 <div className="wa-notif-list custom-scrollbar">
                    {notifications.length === 0 ? (
                       <div className="wa-notif-empty">No new notifications</div>
                    ) : (
                       notifications.map(n => (
                          <div key={n.id} className="wa-notif-item" onClick={() => {
                             const chat = queue.find(c => c.id === n.convo_id);
                             if (chat) {
                                setSelectedChat(chat);
                                fetchHistory(chat.id);
                             } else {
                                // If not in active queue, fetch it or show error
                                fetchQueue();
                             }
                             setShowNotifications(false);
                          }}>
                             <div className="wa-notif-user-icon-box">
                                <User size={20} />
                             </div>
                              <div className="wa-notif-body">
                                 <p>
                                    <strong>{n.name}</strong> 
                                    {n.status === 'unread' ? `: ${n.text?.substring(0, 40)}...` : ' is waiting for help'}
                                 </p>
                                 <span className="wa-notif-stamp">{n.time}</span>
                              </div>
                             <div className="wa-notif-indicator"></div>
                          </div>
                       ))
                    )}
                 </div>
              </div>
           </div>
        )}
        {selectedChat ? (
          <div className="wa-chat-window">
             <header className="wa-chat-header">
                <div className="wa-chat-info">
                   <div className="wa-chat-avatar">
                      CU
                   </div>
                   <div className="wa-chat-meta">
                      <h3>{selectedChat.customer}</h3>
                      <div className="wa-chat-status">
                         <div className="wa-claimed-pill">
                            <User size={12} /> Claimed session
                         </div>
                      </div>
                   </div>
                </div>
                 <div className="wa-chat-actions">
                    <button className="wa-icon-btn release-ai-btn" onClick={releaseToAI} title="Release to AI">
                       <Bot size={20} />
                       <span>To AI</span>
                    </button>
                   <button className="wa-icon-btn"><Phone size={20} /></button>
                   <button className="wa-icon-btn"><MoreVertical size={20} /></button>
                 </div>
             </header>

             <div className="wa-chat-body custom-scrollbar" ref={scrollRef}>
                {messages.length === 0 && (
                   <div className="wa-secure-badge">
                      <Shield size={24} />
                      <p>End-to-End Secure Channel</p>
                   </div>
                )}
                {messages.map((m, i) => (
                   <div key={i} className={`wa-msg-row ${m.from === 'agent' ? 'out' : 'in'}`}>
                      <div className="wa-msg-bubble">
                         {m.text}
                         <span className="wa-msg-time">
                            {new Date(m.timestamp || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                         </span>
                      </div>
                   </div>
                ))}
             </div>

             <footer className="wa-chat-footer">
                <form className="wa-input-row" onSubmit={sendMessage}>
                   <div className="wa-input-wrap">
                      <input 
                        type="text" 
                        value={inputMsg}
                        onChange={e => setInputMsg(e.target.value)}
                        placeholder="Type professional reply..." 
                      />
                      <Sparkles size={16} />
                   </div>
                   <button type="submit" className="wa-send-btn" disabled={!inputMsg.trim()}>
                      <ArrowRight size={24} />
                   </button>
                </form>
             </footer>
          </div>
        ) : (
          <div className="wa-welcome">
             <div className="wa-welcome-box">
                <Headphones size={64} color="#4f46e5" />
                <div className="wa-welcome-badge">Systems Online</div>
             </div>
             <h1>Agent Workspace</h1>
             <p>Select a customer from the queue to start a human session. The AI will pause and let you handle the interaction.</p>
             <div className="wa-welcome-stats">
                <div className="wa-pill"><Clock size={16} /> 0.2s Resp</div>
                <div className="wa-pill"><Activity size={16} /> Live SSL</div>
                <div className="wa-pill"><Shield size={16} /> Verified</div>
             </div>
          </div>
        )}
      </main>
    </div>
  );
};

const dashboardStyles = `
  .wa-logout-btn-minimal { background: transparent; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 4px; border-radius: 8px; transition: all 0.2s; color: #64748b; }
  .wa-logout-btn-minimal:hover { background: #fee2e2; color: #dc2626 !important; }
  .wa-agent-profile { margin: 12px; padding: 10px; background: #ffffff; border-radius: 14px; display: flex; align-items: center; gap: 10px; border: 1px solid #e2e8f0; }
  .wa-agent-avatar { width: 32px; height: 32px; background: #6524eb; color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8125rem; }
  .wa-agent-info { flex: 1; min-width: 0; }
  .wa-agent-name { font-weight: 700; font-size: 0.75rem; color: #0f172a; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .wa-agent-role { font-size: 0.625rem; color: #64748b; margin: 0; }
`;

export default () => (
   <>
     <style dangerouslySetInnerHTML={{ __html: dashboardStyles }} />
     <WhatsappDashboardView />
   </>
);