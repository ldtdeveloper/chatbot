# 07 | User Dashboard UI & Analytics
**Subject**: Information Architecture, Visual Observability, and Tenant Navigation  
**Version**: 1.1.0  

---

## 📑 Table of Contents
1. [The High-Fidelity Navigation Framework](#the-high-fidelity-navigation-framework)
2. [Level 1: Executive KPI Cards & Balance Logic](#level-1-executive-kpi-cards--balance-logic)
3. [Level 2: Multidimensional Analysis (The Engagement Graph)](#level-2-multidimensional-analysis-the-engagement-graph)
4. [Level 3: The Agent Workspace (Gallery & Creation)](#level-3-the-agent-workspace-gallery--creation)
5. [The User Profile Horizon](#the-user-profile-horizon)

---

## 1. The High-Fidelity Navigation Framework
The Tenant Dashboard utilizes a persistent sidebar/navbar framework designed for one-click access to core resources.

### 1.1 Navigation Elements
- **Dashboard**: The central analytics view containing KPI cards and primary engagement graphs.
- **Agents**: Direct access to the Agent Gallery. Here, users can view, edit, and initiate the "Formation" of new voice personas.
- **User Profile Icon**: Located at the top-right, this triggers the dropdown for account management, security settings, and session termination (Logout).

### 1.2 Dashboard Navigation Flow
```mermaid
graph TD
    D[Dashboard Home] --> K[KPI Summary Cards]
    D --> G[Usage Trends (Recharts)]
    D --> A[Agent Management]
    
    A --> AE[Edit Persona]
    A --> AW[Generate Widget Code]
    A --> AH[Connect HubSpot MCP]
    
    D --> U[User Profile]
    U --> US[Security Settings]
    U --> UB[Billing & Wallet]
```

---

## 2. Level 1: Executive KPI Cards & Balance Logic

The dashboard provides a real-time "Snapshot" of the tenant's operational state.

### 2.1 The Dashboard KPI Cards
- **Total Interactions**: Cumulative count of voice sessions successfully processed.
- **Total Minutes**: Aggregated duration of all calls, formatted for human readability (H:M:S).
- **Total Active Keys**: Number of authorized API keys currently in circulation for the tenant.
- **Total Agents**: Discrete count of AI personas defined in the workspace.

### 2.2 The "Minutes Balance" Visibility
A specialized card or layout element displays the **Live Minute Balance**.
- **Real-time Deduction**: As calls occur (Section 05), the balance is visibly decremented.
- **Visual Cues**: 
    - **Green**: Healthy balance (> 20%).
    - **Yellow/Red**: Low balance warning indicating a need for replenishment via the Billing flow (Section 02).

---

## 3. Level 2: Multidimensional Analysis (The Engagement Graph)

The Engagement Graph provides a time-series view of platform performance metrics.
- **X-Axis**: Time intervals (Hourly during peaks, Daily for trends).
- **Y-Axis (Bars)**: Interaction volume.
- **Y-Axis (Line)**: Unique Agent utilization counts.
- **UX**: Hovering over data points triggers a **Zustand-powered Tooltip** that reveals precise minute-burn for that specific interval.

---

## 4. Level 3: The Agent Workspace (Gallery & Creation)

### 4.1 Managing Your Personas
The **Agents Section** is a dedicated environment for lifecycle management.
- **Active Grid**: Users see their existing agents as clickable cards (See Section 03 for creation details).
- **The "Create New Agent" Trigger**: A prominent card allows users to launch the System Instruction editor. Once instructions are filled and "Formed," the new agent immediately appears in this grid.

---

## 5. The User Profile Horizon

### 5.1 The Profile Dropdown
Clicking the profile icon reveals specialized actions:
1.  **Edit Profile**: Transitions the user to a secure form to update their `Display Name` and `Contact Email`.
2.  **Security Center**: Direct access to the Password Modification workflow.
    - **Logic**: Changing a password initiates a Gmail-linked verification loop (Detailed in Section 09).

---
**END OF SECTION 07**
