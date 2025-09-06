import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

# Template environment
template_env = Environment(loader=FileSystemLoader("templates/email"))

class EmailService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _send_email_sync(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email synchronously."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = FROM_EMAIL
            msg["To"] = to_email
            
            # Add text version
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._send_email_sync, 
            to_email, 
            subject, 
            html_content, 
            text_content
        )
    
    async def send_verification_email(self, email: str, user_id: str):
        """Send account verification email."""
        template = template_env.get_template("verification.html")
        
        verification_link = f"http://localhost:3000/verify?token={user_id}"
        
        html_content = template.render(
            verification_link=verification_link,
            app_name="Arthachitra"
        )
        
        await self.send_email(
            to_email=email,
            subject="Verify your Arthachitra account",
            html_content=html_content
        )
    
    async def send_order_notification(self, email: str, order_data: dict):
        """Send order execution notification."""
        template = template_env.get_template("order_notification.html")
        
        html_content = template.render(
            order=order_data,
            app_name="Arthachitra"
        )
        
        subject = f"Order {order_data['status']} - {order_data['symbol']}"
        
        await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content
        )

# Global email service instance
email_service = EmailService()

# Convenience functions
async def send_verification_email(email: str, user_id: str):
    return await email_service.send_verification_email(email, user_id)

async def send_order_notification(email: str, order_data: dict):
    return await email_service.send_order_notification(email, order_data)
