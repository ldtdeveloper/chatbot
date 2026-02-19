# 02 | Domain Glossary
**Subject**: Architectural Taxonomy and Unified Service Vocabulary  
**Version**: 1.2.0  
**Confidentiality**: Level 3 (Internal Engineering & Product Only)

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [Identity & Organizational Entities](#identity--organizational-entities)
3. [Econometric & Billing Terms](#econometric--billing-terms)
4. [Interaction & Protocol Vocabulary](#interaction--protocol-vocabulary)
5. [Enforcement & Guardrail Logic](#enforcement--guardrail-logic)
6. [Audit & Compliance Terminology](#audit--compliance-terminology)

---

## 1. Introduction
To ensure seamless collaboration between Senior Engineering, Product Management, and Financial Audit teams, this Glossary establishes the canonical definitions for all components of the Voice AI SaaS Platform. Ambiguity in these terms can lead to significant logic errors in billing and infrastructure scaling.

---

## 2. Identity & Organizational Entities

### 2.1 Tenant (User/Org)
The **Tenant** is the root object in the multi-tenant hierarchy. 
*   **Technical Definition**: The unique `UUID` associated with a row in the `users` table.
*   **Business Impact**: All financial liability, agent configuration, and data retention policies are scoped to the Tenant. A Tenant is the primary billing entity for Razorpay transactions.

### 2.2 Provisioned Agent
An **Agent** is a discrete AI persona configured by a Tenant.
*   **Technical Definition**: A set of metadata (System Prompt, Voice ID, Model Temperature) stored in the `agents` table.
*   **Business Impact**: Agents act as the "Public Interface" for the Tenant. Their `is_active` status is the primary control lever for usage enforcement.

### 2.3 SuperAdmin
A specialized role within the Platform hierarchy.
*   **Technical Definition**: A User record with the `is_superuser` flag set to `True`.
*   **Business Impact**: SuperAdmins possess bypass permissions for the Gatekeeper, allowing them to manually adjust minute balances for compensation or testing purposes.

---

## 3. Econometric & Billing Terms

### 3.1 Minute Allocation
The quantity of AI talk-time purchased by a Tenant.
*   **Technical Definition**: The integer value `total_seconds` stored in the `UserMinuteBalance` model.
*   **Business Impact**: Represents the total "Purchased Inventory" of AI compute available to the Tenant.

### 3.2 Real-time Remaining Balance
The liquid quota available for immediate consumption.
*   **Technical Definition**: `UserMinuteBalance.remaining_seconds`.
*   **Business Impact**: This value is checked synchronously during the WebSocket handshake. If this value is `0`, the service is rendered unavailable.

### 3.3 COGS (Cost of Goods Sold)
The direct cost of providing the voice service.
*   **Definition**: Primarily composed of the AI Provider's token billing and the underlying server-side compute (AWS/GCP).
*   **Business Impact**: The business logic (specified in Section 03) is designed specifically to protect the spread between customer price and COGS.

### 3.4 Token Density
The ratio of Generative AI tokens consumed to the number of minutes spent on a call.
*   **Impact**: High-density interactions (long AI monologues) are more expensive for the platform than low-density interactions (short human greetings).

---

## 4. Interaction & Protocol Vocabulary

### 4.1 Interaction (Session)
A single, discrete voice conversation between an end-user and an Agent.
*   **Technical Definition**: A persistent WebSocket connection spanning from `101 Switching Protocols` to the socket `close` event.
*   **Business Impact**: The interaction is the "Billable Event." It results in a row in the `Interactions` table and a corresponding deduction from the Tenant's balance.

### 4.2 Handshake (Pre-flight)
The initial negotiation period of a connection.
*   **Technical Definition**: The HTTP upgrade request containing the JWT and the `agent_id`.
*   **Business Impact**: This is where **Rule BR-101** (The Gatekeeper) is enforced.

### 4.3 PCM16 Audio Stream
The raw audio format used for ultra-low latency.
*   **Definition**: 16-bit Pulse Code Modulation at 24kHz.
*   **Role**: This is the data being metered. The system tracks the wall-clock time that this stream is active.

---

## 5. Enforcement & Guardrail Logic

### 5.1 The Gatekeeper
The primary defensive logic of the Platform.
*   **Definition**: A service layer that intercepts every incoming request to verify that the Tenant has `remaining_seconds > 0`.
*   **Architecture Role**: It is the "Traffic Cop" of the system, preventing unmetered usage.

### 5.2 Cascade Deactivation
A systemic fail-safe for exhausted accounts.
*   **Definition**: If a Tenant's balance hits zero, all their Agents' `is_active` flags are set to `False`.
*   **Business Impact**: This ensures that even if a user has our widget embedded on 1,000 external websites, all 1,000 sites stop allowing calls simultaneously.

### 5.3 Atomic Decrement
A database update strategy to prevent race conditions.
*   **Technical Definition**: Using an SQL expression (e.g., `SET balance = balance - 10`) rather than a Python-calculated value (e.g., `balance = 90`).
*   **Impact**: Prevents "Double Spending" of seconds during concurrent calls.

---

## 6. Audit & Compliance Terminology

### 6.1 Accounting Ledger
The immutable history of balance changes.
*   **Technical Definition**: A table storing transaction IDs, delta values (minutes added/subtracted), and timestamps.
*   **Compliance Role**: This is the primary source of truth for third-party financial auditors and customer billing disputes.

### 6.2 Origin Whitelist
A security feature for widget embeds.
*   **Definition**: A list of authorized domains (e.g., `https://customer-website.com`) that are allowed to initiate handshakes for a specific agent.

### 6.3 PII (Personally Identifiable Information)
Sensitive data within a voice stream.
*   **Impact**: Transcripts generated during interactions may contain PII. The platform's Data Contracts (Section 05) must account for the retention and deletion policies for this data.

---
**END OF SECTION 02**
