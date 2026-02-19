# 09 | User Profile & Security Workflow
**Subject**: Identity Modification, Gmail-Linked Security, and Password Hardening  
**Version**: 1.0.0  

---

## 📑 Table of Contents
1. [Flow Overview](#flow-overview)
2. [Stage 1: Profile Attribute Modification](#stage-1-profile-attribute-modification)
3. [Stage 2: The Secure Password Change Protocol](#stage-2-the-secure-password-change-protocol)
4. [Stage 3: Gmail-Linked Verification Loop](#stage-3-gmail-linked-verification-loop)
5. [Stage 4: Identity Re-Commitment](#stage-4-identity-re-commitment)

---

## 1. Flow Overview
The User Profile & Security workflow manages the self-service lifecycle of a tenant's identity credentials. This flow ensures that sensitive modifications (like password changes) are verified via an out-of-band communication channel (Gmail) to prevent unauthorized account takeovers.

---

## 2. Stage 1: Profile Attribute Modification

### 2.1 Edit Profile Interaction
Within the Dashboard, users can access their profile settings via the user dropdown.
1.  **Retrieval**: The dashboard fetches current attributes via `GET /api/users/me`.
2.  **Modification**: The user updates fields such as `Display Name` or `Timezone`.
3.  **Commitment**: A `PATCH /api/users/me` request updates the SQLAlchemy `User` model. This is an immediate, authenticated action that does not require secondary verification.

---

## 3. Stage 2: The Secure Password Change Protocol

Changing a password is a high-sensitivity event that triggers a multi-stage security loop.

### 3.1 Initiation
1.  **Trigger**: The user clicks "Change Password" in the Security section.
2.  **Intent Verification**: The system requests a "Password Reset Intent" from the backend.
3.  **Token Generation**: The backend generates a cryptographically secure, one-time-use **Reset Token** pinned to the user's UUID.

---

## 4. Stage 3: Gmail-Linked Verification Loop

### 4.1 The Secure Link Dispatch
The platform does not allow in-situ password changes without email confirmation.
1.  **SMTP Handshake**: The `EmailService` sends a transactional email to the user's registered Gmail address.
2.  **The Magical Link**: The email contains a link: `https://app.platform.com/reset-password?token=XYZ`.
3.  **TTL Enforcement**: The link is valid for exactly **15 minutes**.

---

## 5. Stage 4: Identity Re-Commitment

### 5.1 Setting the New Password
1.  **Entry**: Clicking the Gmail link redirects the user back to the platform's secure reset page.
2.  **Validation**: The client-side dashboard verifies the token's validity against the backend.
3.  **Bcrypt Hardening**: 
    - The user submits the new password.
    - The backend hashes it using **Bcrypt**.
    - The `hashed_password` field in the DB is updated.
4.  **Session Invalidation**: Once the password is changed, all existing **JWT tokens** for that user are invalidated, forcing a re-login on all devices to ensure a clean security state.

---
**END OF SECTION 09**
