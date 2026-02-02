"""
Email Service for BiznesAssistant
Handles email verification and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import secrets
from datetime import datetime, timedelta

from app.config import settings

class EmailService:
    """Service for sending emails and managing email verification"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@biznesassistant.uz')
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    def send_verification_email(self, to_email: str, verification_token: str, business_name: str) -> bool:
        """Send email verification to new business admin"""
        try:
            verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"
            
            subject = "Verify Your Email - BiznesAssistant"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #1f2937; text-align: center;">Welcome to BiznesAssistant!</h2>
                    
                    <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #374151;">Hi {business_name} Admin,</h3>
                        
                        <p style="color: #6b7280; line-height: 1.6;">
                            Thank you for registering your business with BiznesAssistant! 
                            Your 30-day free trial is ready to start.
                        </p>
                        
                        <p style="color: #6b7280; line-height: 1.6;">
                            Please verify your email address to activate your account and start using our platform.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" 
                               style="background-color: #3b82f6; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block;
                                      font-weight: bold;">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <p style="color: #9ca3af; font-size: 14px; text-align: center;">
                            Or copy and paste this link into your browser:<br>
                            <span style="background-color: #f3f4f6; padding: 8px; border-radius: 4px; 
                                       display: inline-block; word-break: break-all;">
                                {verification_url}
                            </span>
                        </p>
                        
                        <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                            This link will expire in 24 hours. If you didn't create this account, 
                            please ignore this email.
                        </p>
                    </div>
                    
                    <div style="text-align: center; color: #9ca3af; font-size: 12px;">
                        <p>BiznesAssistant - Your Complete Business Management Solution</p>
                        <p>Serving Uzbekistan SMEs</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_email, subject, html_body)
            
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, business_name: str, admin_name: str) -> bool:
        """Send welcome email after verification"""
        try:
            subject = "Welcome to BiznesAssistant - Let's Get Started!"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #1f2937; text-align: center;">🎉 Welcome to BiznesAssistant!</h2>
                    
                    <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #374151;">Hi {admin_name},</h3>
                        
                        <p style="color: #6b7280; line-height: 1.6;">
                            Congratulations! Your business <strong>{business_name}</strong> is now set up and ready to use.
                        </p>
                        
                        <div style="background-color: #eff6ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <h4 style="color: #1e40af; margin-top: 0;">What's Next?</h4>
                            <ul style="color: #374151; line-height: 1.6;">
                                <li>📊 <strong>Dashboard:</strong> View your business overview</li>
                                <li>👥 <strong>CRM:</strong> Manage customers and leads</li>
                                <li>💰 <strong>Accounting:</strong> Track income and expenses</li>
                                <li>📄 <strong>Invoices:</strong> Create and send invoices</li>
                                <li>✅ <strong>Tasks:</strong> Manage team activities</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{self.frontend_url}/dashboard" 
                               style="background-color: #10b981; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block;
                                      font-weight: bold;">
                                Go to Dashboard
                            </a>
                        </div>
                        
                        <p style="color: #6b7280; font-size: 14px;">
                            Your 30-day free trial has started. No credit card required.
                        </p>
                    </div>
                    
                    <div style="text-align: center; color: #9ca3af; font-size: 12px;">
                        <p>BiznesAssistant - Your Complete Business Management Solution</p>
                        <p>Serving Uzbekistan SMEs</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_email, subject, html_body)
            
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
    
    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email (if SMTP credentials are configured)
            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                return True
            else:
                # For development, just log the email
                print(f"EMAIL WOULD BE SENT TO: {to_email}")
                print(f"SUBJECT: {subject}")
                print(f"VERIFICATION URL: {html_body}")
                return True
                
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

# Global email service instance
email_service = EmailService()
