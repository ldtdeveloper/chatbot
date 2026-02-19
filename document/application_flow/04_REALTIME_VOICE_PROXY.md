# 04 | Real-time Voice Proxy Lifecycle
**Subject**: WebSocket Orchestration, Audio Pipeline, and Stream Governance  
**Version**: 1.0.0  

---

## 📑 Table of Contents
1. [Flow Overview](#flow-overview)
2. [Stage 1: The Gateway Handshake (wss://)](#stage-1-the-gateway-handshake-wss)
3. [Stage 2: The Upstream Bridge Initialization](#stage-2-the-upstream-bridge-initialization)
4. [Stage 3: The Bidirectional Audio Loop](#stage-3-the-bidirectional-audio-loop)
5. [Stage 4: Failure Mitigation & Clean Socket Close](#stage-4-failure-mitigation--clean-socket-close)

---

## 1. Flow Overview
The Real-time Voice Proxy flow is the technical center of gravity for the platform. It manages the low-latency transport of PCM16 audio blocks between the end-user's browser and the AI Provider. This flow operates entirely within the `backend/widget/` service plane.

---

## 2. Stage 1: The Gateway Handshake (wss://)

### 2.1 Connection Ingress
1.  **Protocol Upgrade**: The browser widget initiates a WebSocket handshake to `wss://api.platform.com/ws`.
2.  **Authentication Assertion**: The Proxy extracts the `UserID` and `AgentID` from the handshake headers.
3.  **The Gatekeeper Verification**: The Proxy synchronously checks the relational database:
    -   Is the Tenant's balance `> 0`?
    -   Is the Agent `is_active == True`?
4.  **Acceptance**: If valid, the Proxy returns a `101 Switching Protocols` response.

---

## 3. Stage 2: The Upstream Bridge Initialization

Once the client is connected, the Proxy must "Pipe" the connection to the AI.
1.  **AI Handshake**: The Proxy opens a secondary WebSocket to the AI Provider's Realtime endpoint.
2.  **Credential Selection**: The Proxy injects the encrypted API Key (decrypted in-memory) into the header.
3.  **Initial Configuration**: The Proxy sends a `session.update` frame containing:
    -   The Agent's `system_instructions`.
    -   Audio format (PCM16, 24kHz).
    -   VAD threshold settings.

---

## 4. Stage 3: The Bidirectional Audio Loop

This stage represents the "Active Interaction."

### 4.1 Inbound (User to AI)
-   **Chunking**: The Widget captures audio in small blocks (e.g., 100ms) and sends them as Base64 encoded strings.
-   **Forwarding**: The Proxy receives these blocks and immediately pipes them to the AI Provider's socket.

### 4.2 Outbound (AI to User)
-   **Deltas**: The AI sends audio deltas (fragments) back to the Proxy.
-   **Fan-out**: The Proxy forwards these deltas to the Browser Widget for real-time playback.
-   **Observability**: The Proxy logs the arrival of `audio_transcript.done` events to prepare for the final accounting phase.

---

## 5. Stage 4: Failure Mitigation & Clean Socket Close

### 5.1 Graceful Termination
1.  **Trigger**: The user closes the tab OR the AI finishes its final turn.
2.  **Flush**: The Proxy sends a `close` frame to the AI Provider.
3.  **Hand-off to Accounting**: The Proxy records the exact Monotonic timestamp of the closure and hands the session data to the `UsageEngine` for billing (Detailed in Section 05).

### 5.2 Resilience Patterns
-   **Timeout Governance**: If a session remains idle (no audio) for more than 5 minutes, the Proxy executes a `force_close` to prevent zombie sessions.
-   **Handshake Fail-Closed**: If the database is unreachable during the handshake, the connection is rejected to prevent unmetered usage.

---
**END OF SECTION 04**
