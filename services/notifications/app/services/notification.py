"""Notification service for sending email and push notifications."""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications to users.

    Supports email notifications (SMTP) and can be extended for push notifications.
    """

    def __init__(self):
        """Initialize notification service."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        self.email_enabled = settings.EMAIL_ENABLED and all([
            self.smtp_user,
            self.smtp_password
        ])

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (fallback)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.email_enabled:
            logger.info(f"Email notifications disabled. Would have sent: {subject}")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.smtp_from
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text version
            if text_body:
                message.attach(MIMEText(text_body, "plain", "utf-8"))

            # Add HTML version
            message.attach(MIMEText(html_body, "html", "utf-8"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_task_due_notification(
        self,
        user_email: str,
        user_name: str,
        task_title: str,
        task_description: str,
        due_date: date,
        hours_until_due: int,
        task_id: int
    ) -> bool:
        """
        Send notification for task due soon.

        Args:
            user_email: User's email address
            user_name: User's name
            task_title: Task title
            task_description: Task description
            due_date: Task due date
            hours_until_due: Hours until task is due
            task_id: Task ID for link

        Returns:
            True if sent successfully, False otherwise
        """
        subject = f"Task Due Soon: {task_title}"

        # Calculate due time
        if hours_until_due <= 24:
            due_text = f"due {hours_until_due} hours"
        else:
            due_text = f"due on {due_date.strftime('%B %d, %Y')}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .task-title {{ font-size: 20px; font-weight: bold; color: #667eea; margin: 15px 0; }}
                .task-meta {{ color: #666; font-size: 14px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Task Due Soon</h2>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>You have a task that is {due_text}:</p>
                    <div class="task-title">{task_title}</div>
                    <div class="task-meta">
                        <p><strong>Description:</strong> {task_description or 'No description'}</p>
                        <p><strong>Due Date:</strong> {due_date.strftime('%B %d, %Y')}</p>
                    </div>
                    <p style="margin-top: 20px;">Please complete your task on time!</p>
                </div>
                <div class="footer">
                    <p>Todo App - Stay organized, get things done</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hi {user_name},

        You have a task that is {due_text}:

        Task: {task_title}
        Description: {task_description or 'No description'}
        Due Date: {due_date.strftime('%B %d, %Y')}

        Please complete your task on time!

        --
        Todo App - Stay organized, get things done
        """

        return await self.send_email(user_email, subject, html_body, text_body)

    async def send_recurring_task_notification(
        self,
        user_email: str,
        user_name: str,
        task_title: str,
        recurrence_pattern: str,
        next_due_date: date
    ) -> bool:
        """
        Send notification for recurring task created.

        Args:
            user_email: User's email address
            user_name: User's name
            task_title: Task title
            recurrence_pattern: Recurrence pattern (daily, weekly, monthly, yearly)
            next_due_date: Next due date

        Returns:
            True if sent successfully, False otherwise
        """
        subject = f"New Recurring Task: {task_title}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .task-title {{ font-size: 20px; font-weight: bold; color: #667eea; margin: 15px 0; }}
                .badge {{ display: inline-block; background: #667eea; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Recurring Task Created</h2>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>A new instance of your recurring task has been created:</p>
                    <div class="task-title">{task_title}</div>
                    <div>
                        <span class="badge">{recurrence_pattern.capitalize()}</span>
                    </div>
                    <p style="margin-top: 15px;"><strong>Next Due:</strong> {next_due_date.strftime('%B %d, %Y')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hi {user_name},

        A new instance of your recurring task has been created:

        Task: {task_title}
        Pattern: {recurrence_pattern}
        Next Due: {next_due_date.strftime('%B %d, %Y')}

        --
        Todo App - Stay organized, get things done
        """

        return await self.send_email(user_email, subject, html_body, text_body)

    async def log_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Log event to database (for audit trail).

        Args:
            event_data: Event data to log

        Returns:
            True if logged successfully, False otherwise
        """
        # This will be implemented in the subscription handlers
        # to create TaskEventLog entries
        logger.info(f"Event logged: {event_data}")
        return True


# Global singleton instance
notification_service = NotificationService()
