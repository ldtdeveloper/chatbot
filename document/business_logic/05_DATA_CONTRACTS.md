# 05 | Data Contracts
**Subject**: Schema Integrity, Persistence Layer, and Field-Level Validation  
**Version**: 1.2.0  
**Confidentiality**: Level 3 (Internal Engineering & Product Only)

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [Model M-1: UserMinuteBalance (The Ledger)](#model-m-1-userminutebalance-the-ledger)
3. [Model M-2: Interaction (The Transaction)](#model-m-2-interaction-the-transaction)
4. [Model M-3: Agent (The Governance Object)](#model-m-3-agent-the-governance-object)
5. [Validation Constraints & Sanity Checks](#validation-constraints--sanity-checks)
6. [Persistence Policy & Data Retention](#persistence-policy--data-retention)

---

## 1. Introduction
Data Contracts define the "Physical Reality" of the business logic. While Section 03 defines the rules, this section defines the structure of the data that those rules act upon.

Every field in this document is derived from the core application models (found in `backend/app/models/`). Discrepancies between this document and the ORM implementation are considered critical bugs.

---

## 2. Model M-1: UserMinuteBalance (The Ledger)
This model is the "Single Source of Truth" for a Tenant's financial standing.

| Field Name | Data Type | Constraint | Business Logic Role |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Unique identifier for the balance record. |
| `user_id` | `UUID` | FK (Users) | The link to the Tenant. Indexing is mandatory. |
| `total_seconds`| `BIGINT` | `min=0` | Cumulative lifetime allotment. Only increases. |
| `used_seconds` | `BIGINT` | `min=0` | Cumulative lifetime usage. Only increases. |
| `remaining_seconds`| `BIGINT` | `signed` | The active "Spent" balance. Ceiling logic: `total - used`. |
| `last_deduction_at`| `DateTime`| `auto_now` | Audit field for the last billable event. |

**Critical Architectural Constraint**: No logic outside the `UsageService` may perform a direct `WRITE` to this model. All updates must flow through approved service methods to ensure logging.

---

## 3. Model M-2: Interaction (The Transaction)
The Interaction model records the "Proof of Usage."

| Field Name | Data Type | Constraint | Business Logic Role |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Unique transaction ID. |
| `agent_id` | `UUID` | FK (Agents) | Identifies which AI persona was consumed. |
| `started_at` | `DateTime`| Non-Null | ISO-8601 timestamp of Handshake completion. |
| `ended_at` | `DateTime`| Nullable | ISO-8601 timestamp of Socket closure. |
| `duration_seconds`| `INT` | `min=1` | Calculated as `ceil(ended_at - started_at)`. |
| `status` | `Enum` | [1..5] | Maps to Interaction States in Section 04. |
| `provider_session_id`| `STRING` | Unique | Mapping to the upstream AI provider's ID. |

**Audit Requirement**: Every interaction MUST be referencable back to a specific `user_id` to prevent "Ghost Usage" leakage.

---

## 4. Model M-3: Agent (The Governance Object)
The Agent model is the mechanism by which the platform enables or disables the user's ability to trigger the Metering Engine.

| Field Name | Data Type | Constraint | Business Logic Role |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | The public Agent identifier. |
| `user_id` | `UUID` | FK (Users) | Owner of the agent. |
| `is_active` | `BOOLEAN` | Default: `True`| The primary shut-off valve for the Gatekeeper. |
| `authorized_domains`| `ARRAY` | Non-Empty | Whitelist of origins for the handshake check. |
| `name` | `STRING` | 255 chars | User-facing identifier. |

---

## 5. Validation Constraints & Sanity Checks

### 5.1 The Monotonicity Guarantee
*   `used_seconds` MUST NEVER decrease. In the event of a refund, the `total_seconds` is adjusted upward (adding "Credit"), rather than subtracting from `used_seconds`.

### 5.2 The Negative Balance Ceiling
*   While `remaining_seconds` can technically go negative (as specified in Section 03), the system MUST set a "Safe Floor" (e.g., `-3600`). This prevents an unlimited-overage attack where a single call runs for days.

### 5.3 Handshake Delta Limit
*   The `started_at` timestamp must not exist more than 5 minutes in the past relative to the server clock during handshake processing. This prevents replay attacks on recycled JWTs.

---

## 6. Persistence Policy & Data Retention

### 6.1 Transactional Integrity
All updates to `UserMinuteBalance` and the creation of an `Interaction` record MUST be wrapped in a single **Database Transaction**. 
*   If the interaction creation fails, the balance must not be deducted.
*   If the balance deduction fails, the interaction must be marked as `FAILED_ACCOUNTING`.

### 6.2 Archival Strategy
*   **Active Data**: 12 months in the primary SQL database.
*   **Archival Data**: Interactions older than 1 year are moved to cold storage (e.g., S3 Parquet) for long-term audit compliance.
*   **Lead Ledger**: The `UserMinuteBalance` record is NEVER deleted as long as the Tenant account exists.

---
**END OF SECTION 05**
