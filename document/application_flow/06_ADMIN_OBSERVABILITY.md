# 06 | Administrative Observability & Control
**Subject**: SuperAdmin Command Center, Multi-Tenant Governance, and Financial Telemetry  
**Version**: 1.1.0  

---

## 📑 Table of Contents
1. [The SuperAdmin Command Architecture](#the-superadmin-command-architecture)
2. [Level 1: The Platform Profitability Cards](#level-1-the-platform-profitability-cards)
3. [Level 2: The Infrastructure API Key Manager](#level-2-the-infrastructure-api-key-manager)
4. [Level 3: Global Plan Orchestration](#level-3-global-plan-orchestration)
5. [Level 4: Multi-Tenant User Governance](#level-4-multi-tenant-user-governance)

---

## 1. The SuperAdmin Command Architecture
The SuperAdmin experience is a separate, highly-privileged plane of the platform. Unlike the Tenant dashboard, the SuperAdmin dashboard focuses on **COGS (Cost of Goods Sold)**, platform-wide resource usage, and global management.

---

## 2. Level 1: The Platform Profitability Cards

The SuperAdmin top-row provide an "Economic Snapshot" of the entire system.

### 2.1 The Financial Monitoring Cards
- **Total Cost**: Aggregated external provider costs (inferred from token-burn across all tenants).
- **Total Expenses**: Maintenance, infrastructure, and fixed-cost overheads.
- **Total Active Keys**: Platform-wide count of active session-authority tokens.
- **Total Active Agents**: Sum of all `is_active == True` agents across the global database.

### 2.2 Platform Graphs
The SuperAdmin graphs overlay **Revenue (from Payments)** against **Cost (from AI usage)**, allowing real-time monitoring of platform margins.

---

## 3. Level 2: The Infrastructure API Key Manager

Accessible via the **API Keys** item in the SuperAdmin Navbar.
- **Identity Cards**: Admins see a grid of "Key Cards" representing every user's infrastructure credentials.
- **Audit Details**: Each card shows the `UserID`, `Creation Date`, and `Last Used` timestamp.
- **Administrative Actions**:
    - **View**: Inspect key metadata (excluding raw secrets).
    - **Inactivate**: Forcefully revoke a user's API keys to stop service or mitigate abuse.

---

## 4. Level 3: Global Plan Orchestration

### 4.1 Managing Plans
The **Manage Plans** section allows SuperAdmins to define the platform's commercial offerings.
1.  **The Plan Form**: A specialized UI to input `Plan Name`, `Minute Allocation`, `Price`, and `Trial Period`.
2.  **Formation**: Clicking "Create Plan" persists the record to the `plans` table.
3.  **Frontend Synchronicity**: New plans immediately appear on the public-facing landing page and the user's upgrade dashboard, driven by the `GET /api/plans` endpoint.

---

## 5. Level 4: Multi-Tenant User Governance

### 5.1 The Master User Inventory
The **Manage Users** table is the source of truth for all platform entities.
- **CRUD Capabilities**:
    - **View**: Deep dive into a specific user's interaction logs and balance history.
    - **Edit**: Adjust user names or manually replenish minute balances.
    - **Inactive/Ban**: Set `is_active = False` to prevent any system usage.
    - **Delete**: Execute a cascading purge of a tenant's data (Subject to audit retention rules).

---
**END OF SECTION 06**
