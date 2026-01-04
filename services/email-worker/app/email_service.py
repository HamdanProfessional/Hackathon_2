"""Email Service using custom email.testservers.online API."""
import os
import httpx
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using custom email API."""

    def __init__(self):
        """Initialize email client."""
        self.api_key = os.getenv("EMAIL_KEY", "emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d")
        self.api_url = os.getenv("EMAIL_API_URL", "https://email.testservers.online/api/send")
        self.from_email = os.getenv("MAIL_FROM", "noreply@hackathon2.testservers.online")

    async def send_email(
        self,
        subject: str,
        email: List[str],
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email using custom email API.

        Args:
            subject: Email subject
            email: List of recipient emails
            body: Email body (plain text or HTML)
            html: True if body is HTML

        Returns:
            True if sent successfully
        """
        try:
            # Build request payload
            payload = {
                "to": email[0] if len(email) == 1 else ", ".join(email),
                "is_html": True,
                "subject": subject,
                "body": body
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=30.0)

                if response.status_code == 200:
                    logger.info(f"Email sent successfully to {email}")
                    return True
                else:
                    logger.error(f"Email API error: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an HTML email template.

        Args:
            template_name: Name of template file
            context: Variables for template

        Returns:
            Rendered HTML string
        """
        from jinja2 import Template

        template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            template_name
        )

        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        return template.render(**context)

    async def send_template_email(
        self,
        template_name: str,
        subject: str,
        email: List[str],
        context: Dict[str, Any]
    ) -> bool:
        """
        Send an email using an HTML template.

        Args:
            template_name: Name of template file
            subject: Email subject
            email: List of recipient emails
            context: Variables for template

        Returns:
            True if sent successfully
        """
        html_body = self.render_template(template_name, context)
        return await self.send_email(subject, email, html_body, html=True)


# Global email service instance
email_service = EmailService()
