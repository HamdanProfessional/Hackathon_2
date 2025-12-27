"""Email Service using FastAPI-Mail."""
import os
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from fastapi_mail.errors import ConnectionErrors
from jinja2 import Template
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications."""

    def __init__(self):
        """Initialize email configuration."""
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM", "noreply@hackathon2.testservers.online"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Todo App"),
        )
        self.fastmail = FastMail(self.conf)

    async def send_email(
        self,
        subject: str,
        email: List[str],
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email.

        Args:
            subject: Email subject
            email: List of recipient emails
            body: Email body (plain text or HTML)
            html: True if body is HTML

        Returns:
            True if sent successfully
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=email,
                body=body,
                subtype=MessageType.html if html else MessageType.plain
            )

            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully to {email}")
            return True

        except ConnectionErrors as e:
            logger.error(f"Failed to send email: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
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
