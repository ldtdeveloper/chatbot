"""
Payment Link routes - for handling payment via email link
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.payment_token import PaymentToken
from app.models.user import User
from app.models.subscription import Subscription, PlanType, PaymentStatus
from app.routes.payments import TEST_MODE, razorpay_client
from app.core.config import settings
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib

router = APIRouter(prefix="/payment", tags=["payment-link"])

# Templates directory (create if needed)
try:
    templates = Jinja2Templates(directory="templates")
except:
    templates = None




@router.get("/{token}")
async def payment_page(token: str, request: Request, db: Session = Depends(get_db)):
    """Display payment page with Razorpay integration"""
    # Get payment token
    db_token = db.query(PaymentToken).filter(
        PaymentToken.token == token,
        PaymentToken.is_used == False
    ).first()

    print("this is db token",db_token)
    if not db_token:
      
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invalid Payment Link</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #ef4444; }
            </style>
        </head>
        <body>
            <h1 class="error">Invalid or Expired Payment Link</h1>
            <p>This payment link is invalid or has already been used.</p>
            <p>Please contact support if you need assistance.</p>
        </body>
        </html>
        """, status_code=404)
    
    # Check if token expired
    
    expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)  
    if datetime.now(timezone.utc) > expires_at:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Expired Payment Link</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #ef4444; }
            </style>
        </head>
        <body>
            <h1 class="error">Payment Link Expired</h1>
            <p>This payment link has expired. Please request a new payment link.</p>
        </body>
        </html>
        """, status_code=410)
    
    # Get user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already paid
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS,
        Subscription.is_active == True
    ).first()
    
    if active_subscription:
        # Already paid, redirect to password setup
        return RedirectResponse(url=f"/setup-password/{token}", status_code=302)
    
    # Generate payment page HTML
    plan_name = db_token.plan_type.upper()
    amount_cents = int(db_token.amount * 100)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complete Payment - VoiceAI Platform</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Outfit', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                padding: 20px; 
            }}
            .container {{ 
                background: white; 
                border-radius: 24px; 
                box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
                max-width: 500px; 
                width: 100%; 
                padding: 40px; 
                animation: scaleIn 0.3s ease-out;
            }}
            @keyframes scaleIn {{
                from {{ transform: scale(0.95); opacity: 0; }}
                to {{ transform: scale(1); opacity: 1; }}
            }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ 
                color: #667eea; 
                margin-bottom: 10px; 
                font-size: 28px;
                font-weight: 700;
            }}
            .header p {{ color: #718096; font-size: 14px; }}
            .info-box {{ 
                background: linear-gradient(135deg, #fdf4ff 0%, #f0f9ff 100%); 
                border: 2px solid rgba(102, 126, 234, 0.1);
                border-left: 4px solid #667eea; 
                padding: 24px; 
                border-radius: 16px; 
                margin: 20px 0; 
            }}
            .info-box h3 {{ 
                color: #667eea; 
                margin-bottom: 16px; 
                font-size: 16px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .info-box p {{ 
                margin: 8px 0; 
                color: #1a202c; 
                font-size: 15px;
            }}
            .info-box strong {{
                color: #4a5568;
                font-weight: 500;
            }}
            .amount {{ 
                text-align: center; 
                font-size: 56px; 
                font-weight: 700; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 30px 0; 
            }}
            .amount-label {{
                text-align: center;
                color: #718096;
                font-size: 14px;
                margin-top: -10px;
                margin-bottom: 20px;
            }}
            .button {{ 
                width: 100%; 
                padding: 18px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                border: none; 
                border-radius: 12px; 
                font-size: 18px; 
                font-weight: 600; 
                cursor: pointer; 
                margin-top: 20px; 
                transition: all 0.3s ease;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                letter-spacing: 0.3px;
            }}
            .button:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
            }}
            .button:active {{
                transform: translateY(0);
            }}
            .button:disabled {{ 
                opacity: 0.6; 
                cursor: not-allowed; 
                transform: none;
            }}
            .loading {{ 
                text-align: center; 
                color: #667eea; 
                margin-top: 20px; 
                font-weight: 500;
            }}
            .error {{
                display: none; 
                color: #ef4444; 
                text-align: center; 
                margin-top: 20px;
                padding: 12px;
                background: #fee;
                border-radius: 8px;
                border: 1px solid #fcc;
            }}
            .secure-badge {{
                text-align: center;
                margin-top: 15px;
                color: #718096;
                font-size: 12px;
            }}
            .secure-badge::before {{
                content: "🔒 ";
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Complete Your Payment</h1>
                <p>VoiceAI Platform</p>
            </div>
            
            <div class="info-box">
                <h3>Account Details</h3>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Plan:</strong> {plan_name}</p>
            </div>
            
            <div class="amount">${db_token.amount:.2f}</div>
            <div class="amount-label">One-time payment</div>
            
            <button id="payButton" class="button" onclick="initiatePayment()">
                💳 Pay Now with Razorpay
            </button>
            <div class="secure-badge">Secure payment powered by Razorpay</div>
            
            <div id="loading" class="loading" style="display: none;">⏳ Processing payment...</div>
            <div id="error" class="error"></div>
        </div>
        
        <script>
            const API_BASE = '{settings.api_base_url}';
            const paymentToken = '{token}';
            const amount = {amount_cents};
            const plan = '{db_token.plan_type}';
            const userId = {user.id};
            
            async function initiatePayment() {{
                const button = document.getElementById('payButton');
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                
                button.disabled = true;
                loading.style.display = 'block';
                error.style.display = 'none';
                
                try {{
                    // Create payment order
                    const orderResponse = await fetch(`${{API_BASE}}/api/payments/create-order-from-token`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            token: paymentToken,
                            user_id: userId
                        }})
                    }});
                    
                    if (!orderResponse.ok) {{
                        const errorData = await orderResponse.json();
                        throw new Error(errorData.detail || 'Failed to create payment order');
                    }}
                    
                    const orderData = await orderResponse.json();
                    
                    console.log('Order created:', orderData);
                    
                    // Check if Razorpay SDK is loaded
                    if (typeof Razorpay === 'undefined') {{
                        throw new Error('Razorpay SDK not loaded. Please refresh the page.');
                    }}
                    
                    // Always open Razorpay gateway (even in test mode, let user interact with it)
                    // Validate that we have a valid Razorpay key
                    if (!orderData.razorpay_key_id || orderData.razorpay_key_id === 'rzp_test_MOCK_KEY' || orderData.razorpay_key_id === 'test_key_id') {{
                        throw new Error('Razorpay is not properly configured. Please contact support.');
                    }}
                    
                    // Initialize Razorpay - ALWAYS open the gateway
                    const options = {{
                        key: orderData.razorpay_key_id,
                        amount: orderData.amount,
                        currency: orderData.currency || 'USD',
                        name: 'VoiceAI Platform',
                        description: `${{plan.toUpperCase()}} Plan Subscription - ${{(orderData.amount / 100).toFixed(2)}}`,
                        order_id: orderData.razorpay_order_id,
                        handler: async function(response) {{
                            console.log('Razorpay payment successful:', response);
                            // Hide loading and show success message
                            loading.style.display = 'none';
                            loading.textContent = 'Payment successful! Verifying...';
                            loading.style.display = 'block';
                            await verifyPayment(response, orderData.order_id);
                        }},
                        prefill: {{
                            email: '{user.email}',
                            name: '{user.username}',
                            contact: ''
                        }},
                        theme: {{
                            color: '#667eea'
                        }},
                        modal: {{
                            ondismiss: function() {{
                                console.log('Razorpay modal closed by user');
                                button.disabled = false;
                                loading.style.display = 'none';
                            }}
                        }},
                        // Enable all payment methods
                        method: {{
                            netbanking: true,
                            card: true,
                            wallet: true,
                            upi: true,
                            emi: true
                        }}
                    }};
                    
                    console.log('Opening Razorpay checkout with options:', options);
                    
                    const razorpay = new Razorpay(options);
                    
                    // Handle payment failure
                    razorpay.on('payment.failed', function(response) {{
                        console.error('Payment failed:', response);
                        error.textContent = 'Payment failed: ' + (response.error?.description || response.error?.reason || 'Unknown error');
                        error.style.display = 'block';
                        button.disabled = false;
                        loading.style.display = 'none';
                    }});
                    
                    // Open Razorpay payment gateway - THIS IS THE KEY LINE
                    console.log('Calling razorpay.open()...');
                    razorpay.open();
                    console.log('Razorpay modal should be open now');
                    
                    // Re-enable button and hide loading since modal handles its own UI
                    button.disabled = false;
                    loading.style.display = 'none';
                    
                }} catch (err) {{
                    console.error('Payment error:', err);
                    error.textContent = err.message || 'Payment initialization failed';
                    error.style.display = 'block';
                    button.disabled = false;
                    loading.style.display = 'none';
                }}
            }}
            
            async function verifyPayment(razorpayResponse, orderId) {{
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                const button = document.getElementById('payButton');
                
                loading.textContent = 'Verifying payment...';
                loading.style.display = 'block';
                error.style.display = 'none';
                button.disabled = true;
                
                try {{
                    console.log('Verifying payment with:', {{
                        token: paymentToken,
                        razorpay_order_id: razorpayResponse.razorpay_order_id,
                        razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                        razorpay_signature: razorpayResponse.razorpay_signature,
                        order_id: orderId
                    }});
                    
                    const verifyResponse = await fetch(`${{API_BASE}}/api/payments/verify-from-token`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            token: paymentToken,
                            razorpay_order_id: razorpayResponse.razorpay_order_id,
                            razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                            razorpay_signature: razorpayResponse.razorpay_signature,
                            order_id: orderId
                        }})
                    }});
                    
                    const verifyData = await verifyResponse.json();
                    console.log('Verification response:', verifyData);
                    
                    if (!verifyResponse.ok) {{
                        const errorMsg = verifyData.detail || verifyData.message || 'Payment verification failed';
                        throw new Error(errorMsg);
                    }}
                    
                    if (verifyData.success) {{
                    
                        // Payment successful - redirect to password setup
                        
                        loading.textContent = '✅ Payment successful! Redirecting to password setup...';
                        loading.style.color = '#10b981';
                        
                        setTimeout(() => {{
                            window.location.href = `/payment/setup-password/${{paymentToken}}`;
                        }}, 1500);
                    }} else {{
                        throw new Error(verifyData.message || 'Payment verification failed');
                    }}
                }} catch (err) {{
                    console.error('Verification error:', err);
                    error.textContent = err.message || 'Payment verification failed. Please contact support.';
                    error.style.display = 'block';
                    loading.style.display = 'none';
                    button.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/setup-password/{token}")
async def setup_password_page(token: str, request: Request, db: Session = Depends(get_db)):
    """Display password setup page"""
    # Verify token and check payment status
    db_token = db.query(PaymentToken).filter(PaymentToken.token == token).first()
    
    if not db_token:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Invalid Link</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #ef4444;">Invalid Link</h1>
            <p>This link is invalid.</p>
        </body>
        </html>
        """, status_code=404)
    
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if payment completed
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS
    ).first()
    
    if not subscription:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Payment Required</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #ef4444;">Payment Required</h1>
            <p>Please complete payment first.</p>
            <a href="/payment/{}" style="color: #667eea;">Go to Payment</a>
        </body>
        </html>
        """.format(token), status_code=400)
    
    # Check if password already set
    if user.password_set:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Password Already Set</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>Password Already Set</h1>
            <p>Your password has already been set. You can now login.</p>
            <a href="/login" style="color: #667eea;">Go to Login</a>
        </body>
        </html>
        """)
    
    # Password setup form
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Setup Password - VoiceAI Platform</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
            .container {{ background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 450px; width: 100%; padding: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #667eea; margin-bottom: 10px; }}
            .header p {{ color: #666; }}
            .form-group {{ margin-bottom: 20px; }}
            .form-group label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 600; }}
            .form-group input {{ width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.3s; }}
            .form-group input:focus {{ outline: none; border-color: #667eea; }}
            .button {{ width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            .button:hover {{ transform: translateY(-2px); }}
            .button:disabled {{ opacity: 0.6; cursor: not-allowed; }}
            .error {{ color: #ef4444; text-align: center; margin-top: 15px; display: none; }}
            .success {{ color: #10b981; text-align: center; margin-top: 15px; display: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Setup Your Password</h1>
                <p>Complete your account setup</p>
            </div>
            
            <form id="passwordForm" onsubmit="setupPassword(event)">
                <div class="form-group">
                    <label>New Password</label>
                    <input type="password" id="password" required minlength="6" placeholder="Enter your password (min 6 characters)">
                </div>
                
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" id="confirmPassword" required minlength="6" placeholder="Confirm your password">
                </div>
                
                <button type="submit" class="button" id="submitBtn">Set Password</button>
                
                <div id="error" class="error"></div>
                <div id="success" class="success"></div>
            </form>
        </div>
        
        <script>
            const API_BASE = '{settings.api_base_url}';
            const token = '{token}';
            
            async function setupPassword(e) {{
                e.preventDefault();
                
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const errorDiv = document.getElementById('error');
                const successDiv = document.getElementById('success');
                const submitBtn = document.getElementById('submitBtn');
                
                // Clear previous messages
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                
                // Validate passwords match
                if (password !== confirmPassword) {{
                    errorDiv.textContent = 'Passwords do not match';
                    errorDiv.style.display = 'block';
                    return;
                }}
                
                if (password.length < 6) {{
                    errorDiv.textContent = 'Password must be at least 6 characters';
                    errorDiv.style.display = 'block';
                    return;
                }}
                
                submitBtn.disabled = true;
                submitBtn.textContent = 'Setting up...';
                
                try {{
                    const response = await fetch(`${{API_BASE}}/api/auth/setup-password`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            token: token,
                            password: password
                        }})
                    }});
                    
                    if (!response.ok) {{
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Failed to setup password');
                    }}
                    
                    const data = await response.json();
                    
                    successDiv.textContent = 'Password set successfully! Redirecting to dashboard...';
                    successDiv.style.display = 'block';
                    
                    // Store token for auto-login
                    localStorage.setItem('token', data.access_token);
                    
                    // Redirect to dashboard (adjust URL based on your frontend)
                    setTimeout(() => {{
                        // If frontend is on different port, adjust this
                        window.location.href = 'http://localhost:3000/';
                    }}, 2000);
                    
                }} catch (err) {{
                    errorDiv.textContent = err.message || 'Failed to setup password';
                    errorDiv.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Set Password';
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)



