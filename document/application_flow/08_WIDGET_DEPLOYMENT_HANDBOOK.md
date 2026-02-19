# 08 | Widget Deployment & Usage Handbook
**Subject**: Snippet Acquisition, Embedding Protocols, and Interaction Flow  
**Version**: 1.0.0  

---

## 📑 Table of Contents
1. [The "Last Mile" Integration](#the-last-mile-integration)
2. [Step 1: Snippet Acquisition & Copy-Logic](#step-1-snippet-acquisition--copy-logic)
3. [Step 2: External Site Attachment (Embedding)](#step-2-external-site-attachment-embedding)
4. [Step 3: Verification & Initial Handshake](#step-3-verification--initial-handshake)
5. [Step 4: Interactive Usage (The Final Voice Loop)](#step-4-interactive-usage-the-final-voice-loop)

---

## 1. The "Last Mile" Integration
Widget Deployment is the technical culmination of the platform's value chain. It represents the transition from the "Management Plane" (Dashboard) to the "Customer Ingress Plane" (Direct interaction on a client's website).

---

## 2. Step 1: Snippet Acquisition & Copy-Logic

Once an agent is "Formed" (created and configured with system instructions), the dashboard provides the Deployment Snippet.

### 2.1 The Snippet Structure
The user is provided with a standard `<script>` block and an optional `<div>` container.
- **Embedded Variable**: The script includes the `agent_id` (UUID).
- **The Loader**: It points to `https://cdn.platform.com/widget-loader.js`.
- **Copy Mechanism**: A "Copy to Clipboard" button in the Dashboard ensures the checksum of the script is maintained without manual copy-paste errors.

---

## 3. Step 2: External Site Attachment (Embedding)

### 3.1 Placement Strategy
The platform is designed to be "Drop-in Ready."
1.  **Tag Insertion**: The user pastes the snippet into the `<head>` or just before the closing `</body>` tag of their own website (WordPress, Shopify, custom HTML, etc.).
2.  **Lazy Loading**: The loader is designed to be **Asynchronous**. It does not block the host site's `LCP` (Largest Contentful Paint), ensuring the user's SEO is unaffected.

---

## 4. Step 3: Verification & Initial Handshake

### 4.1 Domain Verification
Before the widget visualizes, the Platform performs a security handshake:
1.  **Origin Check**: The Widget sends the `window.location.origin` to the backend.
2.  **Whitelist Comparison**: The backend verifies if the requesting domain is in the `Agent.authorized_domains` list.
3.  **Visualization**: If verified, the "Voice Chat Bubble" appears at the bottom right of the customer's screen.

---

## 5. Step 4: Interactive Usage (The Final Voice Loop)

### 5.1 User Engagement
1.  **The Trigger**: A customer clicks the floating "Microphone" icon.
2.  **Initialization**: The Widget requests microphone access via the browser's `navigator.mediaDevices.getUserMedia()` API.
3.  **The WebSocket Bridge**: The widget opens the `wss://` connection to the Proxy (Section 04).
4.  **Interaction**:
    -   The user speaks -> PCM16 audio chunks are streamed.
    -   The AI responds -> Audio deltas play through the customer's speakers.
    -   **Formation Feedback**: The customer sees real-time "Processing" or "Speaking" indicators, ensuring clarity of the AI's state.

### 5.2 Completion
The session ends when the customer clicks "Close" or remains silent for the duration defined in the Agent's VAD settings. The billing system immediately reconciles the seconds consumed (Section 05).

---
**END OF SECTION 08**
