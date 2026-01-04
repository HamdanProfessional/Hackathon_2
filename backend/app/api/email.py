"""Email API endpoints for testing and sending emails via Gmail API."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


class EmailRequest(BaseModel):
    """Request model for sending an email."""
    to: EmailStr | List[EmailStr]
    subject: str
    body: str
    is_html: bool = False


@router.post("/send-test-email")
async def send_test_email(
    email: EmailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a test email using Gmail API.

    This endpoint allows sending emails to test the Gmail API integration.
    Requires authentication.

    **IMPORTANT**: First time setup:
    1. Set GMAIL_CREDENTIALS in your .env file
    2. Run this endpoint - it will open a browser for OAuth consent
    3. Grant permission to send emails on your behalf
    4. A token.json file will be saved for future use

    Example request:
    ```json
    {
        "to": "recipient@example.com",
        "subject": "Test Email from Todo App",
        "body": "This is a test email sent via Gmail API!",
        "is_html": false
    }
    ```
    """
    try:
        from app.utils.email import send_email_async

        success = await send_email_async(
            to=email.to,
            subject=email.subject,
            body=email.body,
            is_html=email.is_html,
            from_name="Todo App"
        )

        if success:
            return {
                "success": True,
                "message": "Email sent successfully",
                "to": email.to,
                "subject": email.subject
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email. Check logs for details."
            )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gmail API libraries not installed: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {str(e)}"
        )


@router.get("/email-config-status")
async def get_email_config_status(current_user: User = Depends(get_current_user)):
    """
    Check the email configuration status.

    Returns information about whether Gmail API is properly configured.
    """
    from app.config import settings

    has_credentials = bool(settings.GMAIL_CREDENTIALS)
    from_name = settings.EMAIL_FROM_NAME

    try:
        from app.utils.email import GMAIL_AVAILABLE
    except ImportError:
        GMAIL_AVAILABLE = False

    return {
        "gmail_api_available": GMAIL_AVAILABLE,
        "credentials_configured": has_credentials,
        "from_name": from_name,
        "setup_required": not has_credentials,
        "setup_instructions": {
            "step1": "Go to Google Cloud Console",
            "step2": "Enable Gmail API",
            "step3": "Create OAuth 2.0 credentials (Desktop app)",
            "step4": "Download credentials JSON",
            "step5": "Set GMAIL_CREDENTIALS in .env file"
        }
    }
