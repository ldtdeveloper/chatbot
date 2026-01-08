import { useState, useEffect } from 'react';
import '../styles/mcpserver.css';
import {integrationConfigService} from '../services/services'
import { IoCloseOutline } from "react-icons/io5";
import { showSuccess,showError } from '../utils/toast';


export default function HubSpotForm({ setShowHubSpotForm,setCheckedLocal,selectedAgent,hubspotformdata,onSuccess }) {
  const [formData, setFormData] = useState({
    instructions: '',
    client_id: '',
    client_secret: ''
  });
  const [isConnecting, setIsConnecting] = useState(false);
  const [oauthStatus, setOauthStatus] = useState(null); // 'connected', 'not_connected', 'checking'

  // Update form data when hubspotformdata changes or when form opens
  useEffect(() => {
    console.log("HubSpotForm useEffect triggered, hubspotformdata:", hubspotformdata);
    if (hubspotformdata && hubspotformdata.length > 0) {
      console.log("Setting form data with:", {
        instructions: hubspotformdata[0].instructions
      });
      setFormData({
        instructions: hubspotformdata[0].instructions || '',
        client_id: hubspotformdata[0].oauth_client_id || '',
        client_secret: '' // Never show client_secret, user must re-enter if needed
      });
      
      // Check OAuth status - if oauth_client_id exists, OAuth is connected
      // Note: Backend doesn't return OAuth status in current response, so we'll check via API
      checkOAuthStatus();
    } else {
      console.log("No hubspotformdata, setting empty form");
      setFormData({
        instructions: '',
        client_id: '',
        client_secret: ''
      });
      setOauthStatus('not_connected');
    }
  }, [hubspotformdata, selectedAgent]);

  // Check OAuth connection status
  const checkOAuthStatus = async () => {
    if (!selectedAgent?.id) return;
    
    setOauthStatus('checking');
    try {
      const response = await integrationConfigService.list(selectedAgent.id);
      if (response && response.length > 0) {
        const config = response[0];
        // Check if OAuth is connected (backend now returns oauth_connected field)
        if (config.oauth_connected) {
          setOauthStatus('connected');
        } else {
          setOauthStatus('not_connected');
        }
      } else {
        setOauthStatus('not_connected');
      }
    } catch (error) {
      console.error("Error checking OAuth status:", error);
      setOauthStatus('not_connected');
    }
  };

  // Check for OAuth callback success/error in URL params
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const oauthSuccess = urlParams.get('oauth_success');
    const oauthError = urlParams.get('oauth_error');
    const agentId = urlParams.get('agent_id');
    
    if (oauthSuccess === 'true' && agentId) {
      showSuccess("HubSpot OAuth connection successful!");
      // Refresh data to show updated status
      if (onSuccess) {
        onSuccess();
      }
      // Check OAuth status after a short delay to ensure backend has saved the token
      setTimeout(() => {
        checkOAuthStatus();
      }, 500);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (oauthError) {
      showError(`Oauth error : ${oauthError}`);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []); // Run once on mount to check for OAuth callback

  // Don't render if no agent is selected - check after all hooks
  if (!selectedAgent || !selectedAgent.id) {
    return null;
  }

  const handleChange = (e) => {
    console.log(e.target.value);
    const name = e.target.name;
    const value = e.target.value;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle HubSpot OAuth connection
  const handleConnectHubSpot = async () => {
    if (!selectedAgent?.id) {
      showError(`No agent selected`)
      return;
    }

    // Validate that client_id and client_secret are provided
    if (!formData.client_id || !formData.client_secret) {
      showError(`Please provide HubSpot Client ID and Client Secret before connecting`)
      return;
    }

    // First save the credentials
    try {
      const payload = {
        instructions: formData.instructions || '',
        oauth_client_id: formData.client_id,
        oauth_client_secret: formData.client_secret
      };
      
      if (hubspotformdata && hubspotformdata.length > 0) {
        await integrationConfigService.update(hubspotformdata[0].id, payload);
      } else {
        payload.agent_id = selectedAgent.id;
        payload.provider = "hubspot";
        await integrationConfigService.create(payload);
      }
      showSuccess(`Hubspot credentials saved`)
    } catch (error) {
      showError(`Failed to save credentials: ${error.message || error})`)
      return;
    }

    setIsConnecting(true);
    try {
      // Get OAuth installation URL from backend
      const response = await integrationConfigService.getHubSpotOAuthUrl(selectedAgent.id);
      const installUrl = response.install_url;
      
      // Open OAuth URL in new window/tab
      window.location.href = installUrl;
      
      // Note: After OAuth callback, user will be redirected back
      // The callback endpoint will save the token automatically
      showSuccess(`Redirecting to hubspot for authorization`)
    } catch (error) {
      setIsConnecting(false);
      showError(`Failed to get OAuth URL: ${error.message || error})`);
    }
  };

  const handleDisconnectHubSpot = async () => {
    if (!selectedAgent?.id) {
      showError(`No agent selected`);
      return;
    }

    if (!window.confirm("Are you sure you want to disconnect HubSpot OAuth? MCP tools will no longer work until you reconnect.")) {
      return;
    }

    setIsConnecting(true);
    try {
      await integrationConfigService.disconnectHubSpotOAuth(selectedAgent.id);
      showSuccess(`Hubspot OAuth disconnected successfully`)
      setOauthStatus('not_connected');
      
      // Refresh data to show updated status
      if (onSuccess) {
        onSuccess();
      }
      
      // Re-check OAuth status after a short delay
      setTimeout(() => {
        checkOAuthStatus();
      }, 500);
    } catch (error) {
      setIsConnecting(false);
      showError(`Failed to disconnect OAuth ${error.message || error}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try{
      if (!selectedAgent || !selectedAgent.id) {
      showError(`No agent selected`);
        return;
      }
      
      // Save instructions and HubSpot app credentials
      const payload = {
        instructions: formData.instructions,
        oauth_client_id: formData.client_id,
        oauth_client_secret: formData.client_secret // Will be encrypted on backend
      }
      
      let response;
      if(hubspotformdata && hubspotformdata.length > 0){
        response = await integrationConfigService.update(hubspotformdata[0].id, payload);
      }
      else{
        // Create config with just instructions (OAuth will be added via OAuth flow)
        payload.agent_id = selectedAgent.id;
        payload.provider = "hubspot";
        response = await integrationConfigService.create(payload);
      }
      
      console.log(response.success)
      showSuccess(`Configuration saved successfully`)
      setShowHubSpotForm(false);
      setCheckedLocal(true);
      // Refetch data to get updated configId and data
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
        setShowHubSpotForm(false);
        setCheckedLocal(false);
        showError(`Something went wrong ${error.message || error}`);
       }
  };

  const handleCancel = () => {
    setShowHubSpotForm(false);
  }

  return (
    <div className="container" onClick={(e) => e.stopPropagation()}>
      <div className="form-card" onClick={(e) => e.stopPropagation()}>
        <h2 className="form-title">Configuration</h2>
        
        <div className="form-content">
            <div className="modal-box">
            <IoCloseOutline className="close-icon" onClick={handleCancel} />
            </div>
          <div className="form-group">
            <label htmlFor="instructions" className="form-label">
              Instructions
            </label>
            <textarea
              id="instructions"
              name="instructions"
              value={formData.instructions}
              onChange={handleChange}
              rows="4"
              className="form-textarea"
              placeholder="Enter your instructions here..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              HubSpot Authentication
            </label>
            <div style={{ marginBottom: '10px' }}>
              {oauthStatus === 'checking' && (
                <p style={{ color: '#666', fontSize: '14px' }}>Checking connection status...</p>
              )}
              {oauthStatus === 'not_connected' && (
                <div>
                  <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#fff3cd', borderRadius: '4px', border: '1px solid #ffc107' }}>
                    <p style={{ color: '#856404', fontSize: '13px', margin: '0 0 8px 0', fontWeight: '500' }}>
                      ⚠️ MCP Server Requirement
                    </p>
                    <p style={{ color: '#856404', fontSize: '12px', margin: '0' }}>
                      HubSpot MCP server requires <strong>OAuth authentication</strong>. Please provide your HubSpot app credentials below.
                    </p>
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label htmlFor="client_id" className="form-label" style={{ fontSize: '13px', marginBottom: '5px', display: 'block' }}>
                      HubSpot Client ID
                    </label>
                    <input
                      id="client_id"
                      name="client_id"
                      type="text"
                      value={formData.client_id}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Enter your HubSpot app Client ID"
                      style={{ width: '100%', padding: '8px', fontSize: '13px' }}
                    />
                  </div>
                  
                  <div style={{ marginBottom: '15px' }}>
                    <label htmlFor="client_secret" className="form-label" style={{ fontSize: '13px', marginBottom: '5px', display: 'block' }}>
                      HubSpot Client Secret
                    </label>
                    <input
                      id="client_secret"
                      name="client_secret"
                      type="password"
                      value={formData.client_secret}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Enter your HubSpot app Client Secret"
                      style={{ width: '100%', padding: '8px', fontSize: '13px' }}
                    />
                    <p style={{ color: '#666', fontSize: '11px', marginTop: '5px', fontStyle: 'italic' }}>
                      Get these from your HubSpot app settings. They will be encrypted and stored securely.
                    </p>
                  </div>
                  
                  <button 
                    type="button"
                    onClick={handleConnectHubSpot}
                    disabled={isConnecting}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#ff7a59',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: isConnecting ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      width: '100%'
                    }}
                  >
                    {isConnecting ? 'Connecting...' : '🔗 Connect HubSpot (OAuth)'}
                  </button>
                </div>
              )}
              {oauthStatus === 'connected' && (
                <div>
                  <p style={{ color: '#2e7d32', fontSize: '14px', marginBottom: '10px' }}>
                    ✅ HubSpot connected via OAuth
                  </p>
                  {formData.client_id && (
                    <p style={{ color: '#666', fontSize: '12px', marginBottom: '10px' }}>
                      Client ID: <code style={{ fontSize: '11px', backgroundColor: '#f5f5f5', padding: '2px 4px', borderRadius: '3px' }}>{formData.client_id}</code>
                    </p>
                  )}
                  <p style={{ color: '#666', fontSize: '12px', marginBottom: '10px' }}>
                    Token will be automatically refreshed when needed. MCP tools are enabled.
                  </p>
                  <button 
                    type="button"
                    onClick={handleDisconnectHubSpot}
                    disabled={isConnecting}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#d32f2f',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: isConnecting ? 'not-allowed' : 'pointer',
                      fontSize: '13px',
                      fontWeight: '500',
                      width: '100%'
                    }}
                  >
                    {isConnecting ? 'Disconnecting...' : '🔌 Disconnect HubSpot'}
                  </button>
                </div>
              )}
            </div>
          </div>
          
          <div className='button-row'>
          <button onClick={handleSubmit} className="submit-button">
            Save Instructions
          </button>
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
          </div>
        </div>
      </div>
    </div>
  );
}