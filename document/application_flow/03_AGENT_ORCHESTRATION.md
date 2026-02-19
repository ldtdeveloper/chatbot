# 03 | Agent Orchestration
**Subject**: Persona Definition, Instruction Injection, and UX-Driven Formation  
**Version**: 1.2.0  

---

## 📑 Table of Contents
1. [Flow Overview](#flow-overview)
2. [Stage 1: The Unified Agent Gallery (UX Entry)](#stage-1-the-unified-agent-gallery-ux-entry)
3. [Stage 2: Schema-Driven Creation & Instruction Injection](#stage-2-schema-driven-creation--instruction-injection)
4. [Stage 3: The "Formation" Sequence (Engine Binding)](#stage-3-the-formation-sequence-engine-binding)
5. [Stage 4: Runtime Orchestration & Token Control](#stage-4-runtime-orchestration--token-control)
6. [Governance & Override Patterns](#governance--override-patterns)

---

## 1. Flow Overview
Agent Orchestration is the functional bridge between a User's intent and an operational AI persona. This flow covers the end-to-end journey from clicking an "Agent Card" in the gallery to the generation of a deployable Voice Widget. It leverages the `Agent` SQLAlchemy model and the `/api/agents` FastAPI router.

---

## 2. Stage 1: The Unified Agent Gallery (UX Entry)

### 2.1 The Card-Based Interface
Upon entering the **Agents** section of the dashboard, the user is presented with the **Agent Gallery**.
1.  **Rendering**: The React frontend executes `GET /api/agents` to fetch all existing personas.
2.  **The "New Agent" Card**: A dedicated UI element (Card) acts as the trigger for the creation flow.
3.  **The Click Event**: Clicking a card (either an existing one for editing or the 'Plus' card for creation) initializes the `AgentEditor` state.

---

## 3. Stage 2: Schema-Driven Creation & Instruction Injection

### 3.1 The Instruction Input Phase
This is the core of the Agent's identity.
1.  **System Instructions**: The user fills in the "System Prompt" field (e.g., "You are an admissions counselor for University X").
2.  **Voice Identification**: The user selects a specific **Voice Profile** from the dropdown menu, which corresponds to a proprietary `voice_id` in the backend.
3.  **Parameter Tuning**: Setting noise reduction thresholds and VAD (Voice Activity Detection) parameters via the UI toggles.

### 3.2 Backend Commitment
1.  **The POST Request**: Once "Form Agent" or "Save" is clicked, the dashboard sends a JSON payload to `POST /api/agents`.
2.  **Sanitization**: The backend ensures the instructions are within token limits and the configuration JSON is valid.

---

## 4. Stage 3: The "Formation" Sequence (Engine Binding)

### 4.1 From JSON to Widget
The "Formation" of an agent is the moment the record becomes an actionable endpoint.
1.  **ID Allocation**: The database issues a unique `UUID` (e.g., `agent-550e8400`).
2.  **Widget Script Synthesis**: The system generates a specialized JavaScript snippet containing the `agent_id`.
3.  **Visualization**: The dashboard updates to show the "Agent Widget" preview, complete with the generated code block for the user to copy.

---

## 5. Stage 4: Runtime Orchestration & Token Control

### 5.1 Contextual Injection
When a voice session starts (See Section 04 for the Proxy details), the Orchestration logic performs the final hand-off:
1.  **Fetch**: The Proxy retrieves the salted instructions from the DB.
2.  **Inject**: The `session.update` frame is prepared with the `system_prompt`.
3.  **Enforcement**: The AI Provider is instructed to follow these rules exclusively, preventing "Prompt Injection" from the end-user side.

---

## 6. Governance & Override Patterns

### 6.1 Real-time Instruction Hot-Swap
The platform supports updating an agent's brain *while* the conversation is active.
-   **Trigger**: The user clicks "Save" in the dashboard during a test call.
-   **Propagation**: The Backend issues a `session.update` frame to the Proxy, which immediately forwards the new instructions to the AI Provider without dropping the WebSocket.

### 6.2 Automatic Suspension
As detailed in the Billing flow, if a user's balance drops to zero, a global governor task runs:
`UPDATE agents SET is_active = False WHERE user_id = :victim_id`. 
This is the platform’s primary mechanism for **Revenue Protection**.

---
**END OF SECTION 03**
