# HubSpot OAuth Automation Guide

## Overview
The OAuth flow is now **fully automated** for end users. They only need to click "Connect HubSpot" once, and the system handles everything automatically.

## What End Users See

### 1. When Configuring HubSpot MCP Server

**Information Collected:**
- ✅ **Instructions** (optional) - Custom instructions for HubSpot integration
- ❌ **NO API Key Required** - OAuth handles authentication automatically

**UI Flow:**
1. User enables MCP server toggle for an agent
2. User clicks "Configure" to open HubSpot settings
3. Form shows:
   - Instructions textarea
   - **"Connect HubSpot" button** (if not connected)
   - **Connection status** (if connected: ✅ HubSpot connected via OAuth)

### 2. OAuth Connection Process

**Step 1: Click "Connect HubSpot"**
- Frontend calls: `GET /api/integration-config/hubspot/oauth/install-url?agent_id={id}`
- Backend returns OAuth installation URL
- User is redirected to HubSpot authorization page

**Step 2: Authorize in HubSpot**
- User authorizes the app in HubSpot
- HubSpot redirects back to: `/api/integration-config/hubspot/oauth/callback?code={auth_code}&agent_id={id}`

**Step 3: Automatic Token Storage**
- Backend exchanges authorization code for tokens
- Tokens are automatically saved to database:
  - `oauth_access_token` - Used for API calls
  - `oauth_refresh_token` - Used to refresh expired tokens
  - `oauth_token_expires_at` - Token expiration timestamp
- User is redirected back to frontend with success message

### 3. Automatic Token Management

**Token Usage:**
- Every widget connection automatically uses OAuth token (if available)
- System prioritizes OAuth tokens over legacy Private App tokens
- No manual intervention needed

**Token Refresh:**
- System automatically checks token expiration before each use
- If token expires within 5 minutes, system automatically refreshes it
- Uses refresh token to get new access token
- Updates database with new token
- **Completely transparent to end user**

## Backend Endpoints

### 1. Get OAuth Install URL
```
GET /api/integration-config/hubspot/oauth/install-url?agent_id={id}
```
**Response:**
```json
{
  "install_url": "https://app.hubspot.com/oauth/authorize?...",
  "agent_id": 1
}
```

### 2. OAuth Callback (Handled Automatically)
```
GET /api/integration-config/hubspot/oauth/callback?code={code}&agent_id={id}
```
**Action:**
- Exchanges code for tokens
- Saves tokens to database
- Redirects to frontend with success/error

### 3. Manual Token Refresh (Optional)
```
POST /api/integration-config/hubspot/oauth/refresh?agent_id={id}
```
**Use Case:** Manual refresh if needed (usually not required)

## Frontend Integration

### Service Methods Added
```javascript
integrationConfigService.getHubSpotOAuthUrl(agentId)
integrationConfigService.refreshHubSpotToken(agentId)
```

### Response Schema Updated
```typescript
{
  id: number;
  provider: string;
  instructions: string;
  oauth_connected: boolean;  // NEW: OAuth connection status
  oauth_expires_at: datetime; // NEW: Token expiration
  // ... other fields
}
```

## User Experience

### First Time Setup
1. User enables MCP server
2. User clicks "Configure HubSpot"
3. User sees "Connect HubSpot" button
4. User clicks button → Redirected to HubSpot
5. User authorizes → Redirected back with success
6. ✅ **Done!** OAuth is now connected

### Subsequent Uses
- User sees: "✅ HubSpot connected via OAuth"
- System automatically uses OAuth token
- System automatically refreshes expired tokens
- **No user action required**

## Summary

✅ **One-time setup:** User clicks "Connect HubSpot" once  
✅ **Automatic token usage:** System uses OAuth token for all calls  
✅ **Automatic token refresh:** System refreshes expired tokens automatically  
✅ **No manual work:** After initial setup, everything is automated  

The end user never needs to:
- Enter API keys manually
- Manage tokens
- Refresh tokens manually
- Re-authenticate (unless they revoke access in HubSpot)

