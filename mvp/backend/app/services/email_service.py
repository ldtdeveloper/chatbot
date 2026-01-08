"""
Email Service for sending reports
Supports SMTP and can be extended for SendGrid/AWS SES
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from app.config import settings


class EmailService:
    """Email service for sending HTML reports"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.frontend_url = settings.frontend_url
    
    def generate_report_html(self, report_data: Dict[str, Any]) -> str:
        """Generate beautiful HTML email from report data"""
        dashboard_url = f"{self.frontend_url}/dashboard"
        unsubscribe_url = f"{self.frontend_url}/reports/unsubscribe"
        user = report_data['user']
        summary = report_data['summary']
        period = report_data['report_period']
        daily = report_data.get('daily_breakdown', [])
        keys = report_data.get('key_breakdown', [])
        top_agents = report_data.get('top_agents', [])
        
        start_date = period['start'][:10]
        end_date = period['end'][:10]
        frequency = period['frequency'].title()
        
        int_arrow = "+" if summary['interactions_change'] >= 0 else ""
        exp_arrow = "+" if summary['expenses_change'] >= 0 else ""
        int_color = "#10b981" if summary['interactions_change'] >= 0 else "#ef4444"
        exp_color = "#ef4444" if summary['expenses_change'] >= 0 else "#10b981"
        
        keys_html = ""
        for key in keys:
            status = "Active" if key['is_active'] else "Inactive"
            keys_html += f"""
            <tr>
                <td style="padding:12px;border-bottom:1px solid #e2e8f0;">{key['key_name']}</td>
                <td style="padding:12px;text-align:center;border-bottom:1px solid #e2e8f0;">{status}</td>
                <td style="padding:12px;text-align:center;border-bottom:1px solid #e2e8f0;">{key['interactions']}</td>
                <td style="padding:12px;text-align:center;border-bottom:1px solid #e2e8f0;">${key['expenses']:.2f}</td>
            </tr>
            """
        
        agents_html = ""
        for agent in top_agents[:5]:
            agents_html += f"""
            <div style="padding:8px 0;border-bottom:1px solid #f1f5f9;">
                <strong>{agent['name']}</strong> - {agent['interactions']} calls, ${agent['expenses']:.2f}
            </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
    <div style="max-width:600px;margin:0 auto;padding:20px;">
        
        <div style="background:#1e293b;border-radius:12px 12px 0 0;padding:25px;text-align:center;">
            <h1 style="margin:0;color:white;font-size:22px;">Voice Assistant</h1>
            <p style="margin:8px 0 0;color:#94a3b8;">{frequency} Report</p>
        </div>
        
        <div style="background:white;padding:25px;border-radius:0 0 12px 12px;">
            
            <p style="color:#334155;font-size:15px;">Hi {user['username']},</p>
            <p style="color:#64748b;font-size:14px;">
                Report period: <strong>{start_date}</strong> to <strong>{end_date}</strong>
            </p>
            
            <table style="width:100%;margin:20px 0;">
                <tr>
                    <td style="background:#f8fafc;border-radius:8px;padding:15px;width:50%;border-left:3px solid #6366f1;">
                        <p style="margin:0;color:#64748b;font-size:11px;">INTERACTIONS</p>
                        <p style="margin:5px 0;font-size:24px;font-weight:bold;color:#1e293b;">{summary['total_interactions']}</p>
                        <p style="margin:0;font-size:11px;color:{int_color};">{int_arrow}{summary['interactions_change']:.1f}%</p>
                    </td>
                    <td style="width:10px;"></td>
                    <td style="background:#f8fafc;border-radius:8px;padding:15px;width:50%;border-left:3px solid #10b981;">
                        <p style="margin:0;color:#64748b;font-size:11px;">EXPENSES</p>
                        <p style="margin:5px 0;font-size:24px;font-weight:bold;color:#1e293b;">${summary['total_expenses']:.2f}</p>
                        <p style="margin:0;font-size:11px;color:{exp_color};">{exp_arrow}{summary['expenses_change']:.1f}%</p>
                    </td>
                </tr>
            </table>
            
            <table style="width:100%;margin:20px 0;">
                <tr>
                    <td style="background:#f8fafc;border-radius:8px;padding:15px;width:50%;border-left:3px solid #f59e0b;">
                        <p style="margin:0;color:#64748b;font-size:11px;">DURATION</p>
                        <p style="margin:5px 0;font-size:24px;font-weight:bold;color:#1e293b;">{summary['total_duration_minutes']:.0f}m</p>
                    </td>
                    <td style="width:10px;"></td>
                    <td style="background:#f8fafc;border-radius:8px;padding:15px;width:50%;border-left:3px solid #ec4899;">
                        <p style="margin:0;color:#64748b;font-size:11px;">AGENTS</p>
                        <p style="margin:5px 0;font-size:24px;font-weight:bold;color:#1e293b;">{summary['total_agents']}</p>
                    </td>
                </tr>
            </table>
            
            {f'''
            <h3 style="color:#1e293b;font-size:14px;margin:25px 0 10px;">Top Agents</h3>
            <div style="background:#f8fafc;border-radius:8px;padding:10px 15px;">
                {agents_html if agents_html else "<p style='color:#64748b;'>No activity</p>"}
            </div>
            ''' if top_agents else ''}
          
            <div style="text-align:center;margin:25px 0 15px;">
             
                <a href="{dashboard_url}" style="display:inline-block;background:#6366f1;color:white;text-decoration:none;padding:12px 24px;border-radius:6px;font-size:13px;">
                    View Dashboard
                </a>
            </div>
            
            <div style="border-top:1px solid #e2e8f0;padding-top:15px;margin-top:15px;">
                <p style="margin:0;color:#94a3b8;font-size:11px;text-align:center;">
                    Automated {frequency.lower()} report | <a href="{unsubscribe_url}" style="color:#6366f1;">Unsubscribe</a>
                </p>
            </div>
        </div>
        
        <p style="text-align:center;color:#94a3b8;font-size:11px;margin:15px 0;">
            Voice Assistant Platform 2025
        </p>
    </div>
</body>
</html>
        """
        return html
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an email via SMTP"""
        if not self.smtp_user or not self.smtp_password:
            print(f"[Email] SMTP not configured - would send to {to_email}")
            print(f"[Email] Subject: {subject}")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"[Email] Sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[Email] Failed to send to {to_email}: {e}")
            raise
    
    def send_report(self, report_data: Dict[str, Any]) -> bool:
        """Generate and send a report email"""
        user = report_data['user']
        frequency = report_data['report_period']['frequency'].title()
        
        subject = f"Your {frequency} Voice Assistant Report"
        print(report_data)
        html_content = self.generate_report_html(report_data)
        
        return self.send_email(to_email=user['email'], subject=subject, html_content=html_content)

