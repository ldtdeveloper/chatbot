# Password Setup Flow After Payment Success

## Complete Flow Diagram

```
1. User Registration
   ↓
   POST /api/auth/register-with-plan
   ↓
   User created (inactive, no password)
   PaymentToken generated
   Email sent with payment link
   
2. User Clicks Payment Link
   ↓
   GET /payment/{token}
   ↓
   Shows payment page with Razorpay integration
   
3. User Completes Payment
   ↓
   Razorpay Gateway → Payment Success
   ↓
   POST /api/payments/verify-from-token
   ↓
   Payment verified → Subscription created (status: SUCCESS)
   ↓
   Redirect to: GET /payment/setup-password/{token}
   
4. Password Setup Page
   ↓
   GET /payment/setup-password/{token}
   ↓
   Validates:
   - PaymentToken exists
   - Subscription exists with SUCCESS status
   - Password not already set
   ↓
   Shows password setup form (HTML page)
   
5. User Submits Password
   ↓
   POST /api/auth/setup-password
   Body: { token: "...", password: "..." }
   ↓
   Validates:
   - PaymentToken is valid and not used
   - Token not expired
   - Subscription has SUCCESS status
   - Password not already set
   ↓
   Updates User:
   - Sets hashed_password
   - Sets password_set = True
   - Sets is_active = True
   - Marks PaymentToken as used
   ↓
   Returns: { access_token: "...", token_type: "bearer" }
   ↓
   Frontend stores token in localStorage
   Redirects to dashboard
```

## Route Details

### 1. GET `/payment/setup-password/{token}` (payment_link.py)
- **Purpose**: Display password setup form
- **Validations**:
  - PaymentToken exists
  - Subscription with SUCCESS status exists
  - Password not already set
- **Returns**: HTML page with password form

### 2. POST `/api/auth/setup-password` (auth.py) ✅ **ADDED**
- **Purpose**: Process password setup
- **Request Body**:
  ```json
  {
    "token": "payment_token_string",
    "password": "user_password"
  }
  ```
- **Validations**:
  - PaymentToken exists and not used
  - Token not expired
  - Subscription has SUCCESS status
  - Password not already set
- **Actions**:
  - Hash password and save to user
  - Set `password_set = True`
  - Set `is_active = True`
  - Mark PaymentToken as used
- **Returns**:
  ```json
  {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "message": "Password set successfully"
  }
  ```

## Why Two Routes?

1. **GET `/payment/setup-password/{token}`** (payment_link.py)
   - Serves the HTML form page
   - Validates payment status before showing form
   - Part of the payment flow (same router prefix `/payment`)

2. **POST `/api/auth/setup-password`** (auth.py)
   - Processes the password submission
   - API endpoint (returns JSON)
   - Part of authentication routes (prefix `/api/auth`)

## Security Flow

1. **Payment Token** is used to:
   - Link payment to user
   - Verify payment completion
   - Prevent password setup without payment

2. **Payment Status Check**:
   - Only allows password setup if `Subscription.payment_status == SUCCESS`
   - Prevents bypassing payment

3. **Token Expiration**:
   - PaymentToken expires after 7 days
   - Cannot set password with expired token

4. **One-Time Use**:
   - PaymentToken marked as `is_used = True` after password setup
   - Cannot reuse the same token

## Example Flow

```javascript
// After payment success in payment_link.py
window.location.href = `/payment/setup-password/${paymentToken}`;

// User sees password form, submits:
fetch(`${API_BASE}/api/auth/setup-password`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: paymentToken,
    password: userPassword
  })
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('token', data.access_token);
  window.location.href = '/dashboard';
});
```

## Database State Changes

### Before Payment:
- `User.is_active = False`
- `User.password_set = False`
- `User.hashed_password = None`
- `PaymentToken.is_used = False`
- No `Subscription` record

### After Payment Success:
- `Subscription` created with `payment_status = SUCCESS`
- `User` still inactive, no password

### After Password Setup:
- `User.is_active = True`
- `User.password_set = True`
- `User.hashed_password = <hashed>`
- `PaymentToken.is_used = True`
- `PaymentToken.used_at = <timestamp>`

