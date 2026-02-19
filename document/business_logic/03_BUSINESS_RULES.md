# 03 | Business Rules
**Subject**: The Enforceable Legal Code of the Platform Engine  
**Version**: 1.2.0  
**Confidentiality**: Level 3 (Internal Engineering & Product Only)

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [Category 100: Usage & Metering Rules](#category-100-usage--metering-rules)
3. [Category 200: Subscription & Plan Governance](#category-200-subscription--plan-governance)
4. [Category 300: Agent Behavioral Constraints](#category-300-agent-behavioral-constraints)
5. [Category 400: Administrative Overrides](#category-400-administrative-overrides)
6. [Rule Justifications (The "Why")](#rule-justifications-the-why)

---

## 1. Introduction
Business Rules are the foundation of the platform's stability and profitability. Unlike "Best Practices," these rules are **Binary** (either fulfilled or violated) and **Enforceable** (implemented via hard-coded checks in the Backend API and Proxy layers). 

Every engineering change MUST be validated against this rule-set. A violation of these rules is considered a "Severity 1" defect.

---

## 2. Category 100: Usage & Metering Rules

### BR-101: The Zero-Balance Gatekeeper
**Definition**: No WebSocket interaction (`Interaction`) shall proceed to the `STREAMING` state unless the associated `UserID` possesses a `UserMinuteBalance.remaining_seconds > 0`.
*   **Enforcement**: Handshake validation layer.
*   **Result of Violation**: Immediate termination of the WebSocket upgrade request with a `1008 Policy Violation` error.

### BR-102: The Minimum Billable Unit (MBU)
**Definition**: Any Interaction that successfully negotiates the `101 Switching Protocols` handshake MUST be billed a minimum of **1 second**, regardless of actual duration.
*   **Enforcement**: Post-call deduction logic.
*   **Justification**: Covers the fixed infrastructure cost of setting up the proxy and the AI processing context.

### BR-103: Atomic Deduction Guarantee
**Definition**: All balance deductions MUST be performed using atomic SQL expressions (e.g., `UPDATE ... SET balance = balance - :val`).
*   **Enforcement**: Database ORM layer.
*   **Justification**: Prevents the "Double-Usage Race Condition" where concurrent calls could potentially spend the same second of balance if recalculated in application memory.

### BR-104: The Tool Latency Tax
**Definition**: All time spent waiting for an MCP (Model Context Protocol) tool to return data is considered "Billable Interaction Time."
*   **Enforcement**: Wall-clock monitoring on the Proxy server.
*   **Justification**: The platform maintains an active, expensive socket and context during these wait periods.

---

## 3. Category 200: Subscription & Plan Governance

### BR-201: The Trial-to-Pro Conversion Bridge
**Definition**: When a user upgrades from a `TRIAL` to a `PRO` plan, their remaining trial balance is **erased**. The account starts with only the new plan's initial allocation to ensure a clean financial state for professional usage.
*   **Enforcement**: Payment Webhook Handler.

### BR-202: Plan Recharge Accumulation
**Definition**: For users already on a `PRO` plan, any subsequent successful recharge (re-payment) resulting in the same or different plan level MUST **add** the new minute allocation to the current `remaining_seconds`.
*   **Enforcement**: Payment Webhook logic.

### BR-203: Static Trial Limits
**Definition**: Users on the `TRIAL` plan are strictly limited to **exactly one (1) active Agent**. 
*   **Enforcement**: Agent Management API.
*   **Action on Violation**: The API MUST return a `403 Forbidden` if an attempt is made to create a second agent.

### BR-204: Plan Expiry Lockdown
**Definition**: Upon `Subscription.end_date`, regardless of the `remaining_seconds`, the account's ability to initiate new handshakes is **revoked**.
*   **Enforcement**: Gatekeeper layer.

---

## 4. Category 300: Agent Behavioral Constraints

### BR-301: Cascade Deactivation
**Definition**: If `UserMinuteBalance.remaining_seconds` reaches a value of `<= 0`, the system MUST immediately execute an `UPDATE agents SET is_active = False WHERE user_id = :id`.
*   **Enforcement**: Asynchronous Billing Trigger.
*   **Business Impact**: This prevents newly embedded widgets on high-traffic sites from flooding our gateway for an exhausted account.

### BR-302: Domain Origin Restriction
**Definition**: An Agent will only respond to handshakes where the `Origin` header matches a wildcard-supported domain in the `Agent.authorized_domains` list.
*   **Enforcement**: Proxy Handshake Handler.

---

## 5. Category 400: Administrative Overrides

### BR-401: Auditability of Overrides
**Definition**: No SuperAdmin may adjust a user's `UserMinuteBalance` without providing an associated `reason_code` and a corresponding `AuditLog` entry.
*   **Enforcement**: Admin Panel Controller.

### BR-402: The Manual Correction Cap
**Definition**: Manual additions of minutes by an Admin are capped at 500 minutes per transaction to prevent catastrophic accidental data entry.

---

## 6. Rule Justifications (The "Why")

### Why BR-101 (Immediate Rejection)?
If we allowed a "Grace Period" (e.g., let the call start and then check), a malicious actor could spin up 10,000 requests, talk for 2 seconds each, and kill the Platform's gross margin before the check completes.

### Why BR-103 (Atomic Deduction)?
In a high-concurrency SaaS environment, two API calls for the same user might happen at the exact same millisecond. If we calculate the balance in Python (`new_balance = old_balance - 10`), Call A and Call B might both see `old_balance = 100` and both set `new_balance = 90`. The user essentially gets 10 free seconds. SQL-level atomicity is the only way to prevent this.

### Why BR-301 (Cascade Deactivation)?
Agents are the public endpoints. If a user stops paying, we cannot rely on the Gatekeeper alone (which is reactive). We must be **proactive** and shut off the Agent switches so the system isn't even "knocked on" by the widget.

---
**END OF SECTION 03**
