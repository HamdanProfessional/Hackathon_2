"""Direct email notification utility."""
import os
import httpx
import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

EMAIL_API_URL = os.getenv("EMAIL_API_URL", "https://email.testservers.online/api/send")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d")

async def send_task_email(
    email: str,
    subject: str,
    task_title: str,
    task_description: Optional[str] = None,
    task_status: str = "created"
) -> bool:
    """
    Send task notification email directly via email API.

    Args:
        email: User email address
        subject: Email subject
        task_title: Task title
        task_description: Task description
        task_status: Task status (created, updated, completed, deleted)

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Build HTML email body
        description_html = f"<p>{task_description or 'No description'}</p>" if task_description else ""

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .task-title {{ font-size: 24px; font-weight: bold; margin: 0 0 10px 0; }}
                .task-status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
                .status-created {{ background: #d4edda; color: #155724; }}
                .status-updated {{ background: #fff3cd; color: #856404; }}
                .status-completed {{ background: #d3f8d7; color: #155724; }}
                .status-deleted {{ background: #f8d7da; color: #721c24; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Todo Task Notification</h2>
                </div>
                <div class="content">
                    <h3 class="task-title">{task_title}</h3>
                    <p><span class="task-status status-{task_status}">Status: {task_status.upper()}</span></p>
                    {description_html}
                    <p><strong>View your tasks:</strong> <a href="https://hackathon2.testservers.online">hackathon2.testservers.online</a></p>
                </div>
                <div class="footer">
                    <p>You're receiving this email because you subscribed to task notifications for the Todo App.</p>
                </div>
            </div>
        </body>
        </html>
        """

        payload = {
            "to": email,
            "is_html": True,
            "subject": subject,
            "body": html_body
        }

        headers = {
            "Authorization": f"Bearer {EMAIL_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                EMAIL_API_URL,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                logger.info(f"Email sent successfully to {email} for task '{task_title}'")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


async def send_task_created_email(email: str, task_data: Dict[str, Any]) -> bool:
    """Send task created notification."""
    return await send_task_email(
        email=email,
        subject=f"Task Created: {task_data.get('title', 'New Task')}",
        task_title=task_data.get('title', 'New Task'),
        task_description=task_data.get('description'),
        task_status="created"
    )


async def send_task_updated_email(email: str, task_data: Dict[str, Any]) -> bool:
    """Send task updated notification."""
    return await send_task_email(
        email=email,
        subject=f"Task Updated: {task_data.get('title', 'Task')}",
        task_title=task_data.get('title', 'Task'),
        task_description=task_data.get('description'),
        task_status="updated"
    )


async def send_task_completed_email(email: str, task_data: Dict[str, Any]) -> bool:
    """Send task completed notification."""
    return await send_task_email(
        email=email,
        subject=f"Task Completed: {task_data.get('title', 'Task')}",
        task_title=task_data.get('title', 'Task'),
        task_description=task_data.get('description'),
        task_status="completed"
    )


async def send_task_deleted_email(email: str, task_data: Dict[str, Any]) -> bool:
    """Send task deleted notification."""
    return await send_task_email(
        email=email,
        subject=f"Task Deleted: {task_data.get('title', 'Task')}",
        task_title=task_data.get('title', 'Task'),
        task_description=task_data.get('description'),
        task_status="deleted"
    )
