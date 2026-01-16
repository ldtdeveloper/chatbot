from datetime import datetime, timezone

def generate_email_html(user,payment_link,plan,amount):
    return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15); max-width: 600px;">
                            <!-- Header with Gradient -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 50px 40px; text-align: center; position: relative; overflow: hidden;">
                                    <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255, 255, 255, 0.1); border-radius: 50%;"></div>
                                    <div style="position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
                                    <div style="position: relative; z-index: 1;">
                                        <div style="width: 80px; height: 80px; background: rgba(255, 255, 255, 0.2); border-radius: 20px; margin: 0 auto 20px; display: inline-block; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                                            <div style="color: #ffffff; font-size: 40px; line-height: 80px;">🎙️</div>
                                        </div>
                                        <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">Welcome to VoiceAI!</h1>
                                        <p style="margin: 10px 0 0; color: rgba(255, 255, 255, 0.95); font-size: 16px; font-weight: 400;">Your journey begins here</p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <p style="margin: 0 0 20px; color: #1a202c; font-size: 18px; font-weight: 500; line-height: 1.6;">
                                        Hello <strong style="color: #667eea; font-weight: 600;">{user.username}</strong>,
                                    </p>
                                    
                                    <p style="margin: 0 0 30px; color: #4a5568; font-size: 16px; line-height: 1.8;">
                                        Thank you for registering with <strong style="color: #667eea;">VoiceAI Platform</strong>! We're excited to have you on board. To complete your registration and activate your account, please complete the payment for your selected plan.
                                    </p>
                                    
                                    <!-- Plan Details Card -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fdf4ff 0%, #f0f9ff 100%); border-radius: 16px; padding: 30px; margin: 30px 0; border: 2px solid rgba(102, 126, 234, 0.1);">
                                        <tr>
                                            <td>
                                                <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 8px 16px; margin-bottom: 20px;">
                                                    <span style="color: #ffffff; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Plan Details</span>
                                                </div>
                                                <table width="100%" cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                            <span style="color: #718096; font-size: 14px; font-weight: 500;">Plan:</span>
                                                            <span style="color: #1a202c; font-size: 16px; font-weight: 700; float: right; text-transform: uppercase; letter-spacing: 0.5px;">{plan.name.upper()}</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                            <span style="color: #718096; font-size: 14px; font-weight: 500;">Amount:</span>
                                                            <span style="color: #667eea; font-size: 20px; font-weight: 700; float: right;">${amount:.2f}<span style="font-size: 14px; color: #a0aec0;">/month</span></span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                            <span style="color: #718096; font-size: 14px; font-weight: 500;">Username:</span>
                                                            <span style="color: #1a202c; font-size: 16px; font-weight: 600; float: right;">{user.username}</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 12px 0;">
                                                            <span style="color: #718096; font-size: 14px; font-weight: 500;">Email:</span>
                                                            <span style="color: #1a202c; font-size: 16px; font-weight: 600; float: right; word-break: break-all;">{user.email}</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 25px; color: #4a5568; font-size: 16px; line-height: 1.8; text-align: center;">
                                        Click the button below to proceed with payment:
                                    </p>
                                    
                                    <!-- CTA Button -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" style="padding: 10px 0 30px;">
                                                <a href="{payment_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 18px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); transition: all 0.3s ease; letter-spacing: 0.3px;">
                                                    💳 Complete Payment
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Alternative Link -->
                                    <div style="background: #f7fafc; border-radius: 12px; padding: 20px; margin: 30px 0; border: 1px solid #e2e8f0;">
                                        <p style="margin: 0 0 12px; color: #718096; font-size: 13px; font-weight: 500; text-align: center;">
                                            Or copy and paste this link into your browser:
                                        </p>
                                        <p style="margin: 0; text-align: center; word-break: break-all;">
                                            <a href="{payment_link}" style="color: #667eea; font-size: 13px; text-decoration: none; font-weight: 500; border-bottom: 1px dashed #667eea; padding-bottom: 2px;">{payment_link}</a>
                                        </p>
                                    </div>
                                    
                                    <!-- Note -->
                                    <div style="background: #fff5e6; border-left: 4px solid #f6ad55; border-radius: 8px; padding: 16px 20px; margin: 30px 0;">
                                        <p style="margin: 0; color: #744210; font-size: 13px; line-height: 1.6;">
                                            <strong style="color: #c05621;">⏰ Important:</strong> This payment link will expire in <strong>7 days</strong>. After successful payment, you'll be able to set your password and access your dashboard.
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background: #f7fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                    <p style="margin: 0 0 10px; color: #718096; font-size: 13px; line-height: 1.6;">
                                        © 2025 VoiceAI Platform. Built with ❤️ by <strong style="color: #667eea;">LDT Technologies</strong>.
                                    </p>
                                    <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                                        If you didn't register for this account, please ignore this email.
                                    </p>
                                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Privacy Policy</a>
                                        <span style="color: #cbd5e0;">•</span>
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Terms of Service</a>
                                        <span style="color: #cbd5e0;">•</span>
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Support</a>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
  
def generate_email_html_reset_password(db_user,reset_password_link):
    '''Email html for reset password '''

    return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15); max-width: 600px;">
                            <!-- Header with Gradient -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 50px 40px; text-align: center; position: relative; overflow: hidden;">
                                    <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255, 255, 255, 0.1); border-radius: 50%;"></div>
                                    <div style="position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
                                    <div style="position: relative; z-index: 1;">
                                        <div style="width: 80px; height: 80px; background: rgba(255, 255, 255, 0.2); border-radius: 20px; margin: 0 auto 20px; display: inline-block; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                                            <div style="color: #ffffff; font-size: 40px; line-height: 80px;">🎙️</div>
                                        </div>
                                        <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">Welcome to <strong style="color: #667eea; font-weight: 600;">VoiceAI!</strong></h1>
                                        <p style="margin: 10px 0 0; color: rgba(255, 255, 255, 0.95); font-size: 16px; font-weight: 400;">Your journey begins here</p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <p style="margin: 0 0 20px; color: #1a202c; font-size: 18px; font-weight: 500; line-height: 1.6;">
                                        Hello <strong style="color: #667eea; font-weight: 600;">{db_user.username}</strong>,
                                    </p>
                                    
                                    <p style="margin: 0 0 30px; color: #4a5568; font-size: 16px; line-height: 1.8;">
                                            We received a request to reset your password for your <strong style="color: #667eea;">VoiceAI Platform</strong> account.
                                    </p>
                                    
                                    <p style="margin: 30px 0 25px; color: #4a5568; font-size: 16px; line-height: 1.8; text-align: center;">
                                        Click the button below to proceed with reset password. This link is valid for <strong>15 minutes</strong>.
                                    </p>
                                    
                                    <!-- Alternative Link -->
                                    <div style="background: #f7fafc; border-radius: 12px; padding: 20px; margin: 30px 0; border: 1px solid #e2e8f0;">
                                        <p style="margin: 0 0 12px; color: #718096; font-size: 13px; font-weight: 500; text-align: center;">
                                            Or copy and paste this link into your browser:
                                        </p>
                                        <p style="margin: 0; text-align: center; word-break: break-all;">
                                            <a href="{reset_password_link}" style="color: #667eea; font-size: 13px; text-decoration: none; font-weight: 500; border-bottom: 1px dashed #667eea; padding-bottom: 2px;">{reset_password_link}</a>
                                        </p>
                                    </div>
                                    
                                    <!-- Note -->
                                    <div style="background: #fff5e6; border-left: 4px solid #f6ad55; border-radius: 8px; padding: 16px 20px; margin: 30px 0;">
                                        <p style="margin: 0; color: #744210; font-size: 13px; line-height: 1.6;">
                                            <strong style="color: #c05621;">⏰ Important:</strong> This reset password link will expire within <strong>15 min</strong>
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background: #f7fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                    <p style="margin: 0 0 10px; color: #718096; font-size: 13px; line-height: 1.6;">
                                        © 2025 VoiceAI Platform. Built with ❤️ by <strong style="color: #667eea;">LDT Technologies</strong>.
                                    </p>
                                    <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                                        If you didn't register for this account, please ignore this email.
                                    </p>
                                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Privacy Policy</a>
                                        <span style="color: #cbd5e0;">•</span>
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Terms of Service</a>
                                        <span style="color: #cbd5e0;">•</span>
                                        <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Support</a>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
    """

def expense_report_html(period_label,expenses_list,table_rows,grand_total):
    ''' Report HTML for sending expenses per user report 
    via email to superadmin (Superadmin only)'''

    return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    @media only screen and (max-width: 600px) {{
                        .email-container {{
                            padding: 10px !important;
                        }}
                        .summary-cards {{
                            flex-direction: column !important;
                        }}
                        .summary-card {{
                            min-width: 100% !important;
                        }}
                        table {{
                            font-size: 12px !important;
                        }}
                        th, td {{
                            padding: 8px 6px !important;
                        }}
                    }}
                </style>
            </head>
            <body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                <div style="max-width:800px;margin:0 auto;padding:20px;" class="email-container">
                    <!-- Header -->
                    <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:16px 16px 0 0;padding:30px 25px;text-align:center;box-shadow:0 4px 12px rgba(102,126,234,0.2);">
                        <h1 style="margin:0 0 8px 0;color:white;font-size:24px;font-weight:600;letter-spacing:-0.5px;">📊 Per User Expenses Report</h1>
                        <p style="margin:0;color:rgba(255,255,255,0.95);font-size:14px;font-weight:400;">Detailed breakdown of expenses by user</p>
                        <div style="margin-top:12px;padding:8px 16px;background:rgba(255,255,255,0.15);border-radius:8px;display:inline-block;">
                            <span style="color:white;font-size:13px;font-weight:500;">Period: {period_label}</span>
                        </div>
                    </div>
                    
                    <!-- Content -->
                    <div style="background:white;padding:30px 25px;border-radius:0 0 16px 16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <!-- Summary Cards -->
                        <div style="display:flex;gap:15px;margin-bottom:30px;flex-wrap:wrap;" class="summary-cards">
                            <div style="flex:1;min-width:180px;background:#f9fafb;padding:20px;border-radius:12px;border-left:4px solid #667eea;box-shadow:0 2px 6px rgba(0,0,0,0.06);" class="summary-card">
                                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                                    <div style="width:40px;height:40px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">👥</div>
                                    <div>
                                        <p style="margin:0;color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;font-weight:500;">Total Users</p>
                                        <p style="margin:4px 0 0 0;font-size:28px;font-weight:700;color:#333;line-height:1;">{len(expenses_list)}</p>
                                    </div>
                                </div>
                            </div>
                            <div style="flex:1;min-width:180px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:20px;border-radius:12px;box-shadow:0 4px 12px rgba(102,126,234,0.3);color:white;" class="summary-card">
                                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                                    <div style="width:40px;height:40px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">💰</div>
                                    <div>
                                        <p style="margin:0;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;font-weight:500;opacity:0.95;">Grand Total</p>
                                        <p style="margin:4px 0 0 0;font-size:28px;font-weight:700;line-height:1;">${grand_total:.2f}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- User Breakdown Section -->
                        <div style="margin-top:25px;">
                            <h3 style="color:#333;font-size:18px;font-weight:600;margin:0 0 20px 0;padding-bottom:12px;border-bottom:2px solid #e5e7eb;">User Breakdown</h3>
                            <div style="background:#f9fafb;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
                                <table style="width:100%;border-collapse:collapse;background:white;">
                                    <thead>
                                        <tr style="background:linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);">
                                            <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Rank</th>
                                            <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Username</th>
                                            <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Email</th>
                                            <th style="padding:14px 16px;text-align:center;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Interactions</th>
                                            <th style="padding:14px 16px;text-align:right;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Expenses</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {table_rows if table_rows else '<tr><td colspan="5" style="padding:40px 20px;text-align:center;color:#6b7280;font-size:14px;">No expenses data available for this period</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Footer -->
                        <div style="border-top:1px solid #e5e7eb;padding-top:20px;margin-top:30px;text-align:center;">
                            <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;">
                                Generated on <strong>{datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M:%S UTC')}</strong>
                            </p>
                            <p style="margin:8px 0 0 0;color:#cbd5e1;font-size:11px;">
                                Voice Assistant Platform - Expenses Report
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
                    """

def payment_page_html(user,plan_name,settings,db_token,token,amount_cents):
    '''Display payment page with Razorpay integration'''

    return f"""
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
            const plan = '{db_token.plan}';
            const userId = {user.id};
            const plan_name = '{plan_name}';
            console.log(plan)
            async function initiatePayment() {{
                const button = document.getElementById('payButton');
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                console.log("Intiated Payment ............")
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
                    
                    console.log('Order created : ', orderData,plan_name,plan);
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
                        description: `${{plan_name.toUpperCase()}} Plan Subscription - ${{(orderData.amount / 100).toFixed(2)}}`,
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

def setup_password_page_html(settings,token):
    ''' Display password setup page '''

    return f"""
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