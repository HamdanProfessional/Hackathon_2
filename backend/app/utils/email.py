"""Gmail API email utility for sending emails without SMTP.

This module uses Gmail API instead of SMTP to send emails.
This bypasses Digital Ocean's SMTP port blocking (25, 465, 587).

Uses OAuth2 credentials or service account for authentication.
"""
import base64
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import asyncio
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

from app.config import settings

# OAuth2 scopes for Gmail API
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Token file for storing OAuth credentials
TOKEN_FILE = "token.json"


def _extract_client_config(credentials_data: dict) -> dict:
    """
    Extract client config from either 'web' or 'installed' type credentials.

    Args:
        credentials_data: Parsed JSON credentials from Google Cloud Console

    Returns:
        Normalized client config dictionary
    """
    # Handle both 'web' and 'installed' credential types
    if 'web' in credentials_data:
        return credentials_data['web']
    elif 'installed' in credentials_data:
        return credentials_data['installed']
    else:
        # Assume it's already the client config
        return credentials_data


class GmailEmailClient:
    """Gmail API client for sending emails."""

    def __init__(self, credentials_json: Optional[str] = None):
        """
        Initialize Gmail API client.

        Args:
            credentials_json: JSON string containing OAuth2 credentials.
                             If not provided, uses GMAIL_CREDENTIALS from config.
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Google API libraries not installed. "
                "Install: pip install google-api-python-client google-auth-oauthlib"
            )

        self.credentials_json = credentials_json or settings.GMAIL_CREDENTIALS
        self.credentials = None
        self.service = None
        self._authenticated = False

    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.

        Supports:
        1. Pre-generated refresh token from GMAIL_REFRESH_TOKEN env var
        2. Saved token.json file
        3. Interactive OAuth flow (for local dev only)

        Returns:
            True if authentication successful, False otherwise.
        """
        creds = None

        # Option 1: Use refresh token from environment (production)
        refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
        if refresh_token and self.credentials_json:
            try:
                credentials_data = json.loads(self.credentials_json)
                client_config = _extract_client_config(credentials_data)

                creds = Credentials(
                    token=None,  # Will be refreshed
                    refresh_token=refresh_token,
                    token_uri=client_config.get('token_uri'),
                    client_id=client_config.get('client_id'),
                    client_secret=client_config.get('client_secret'),
                    scopes=GMAIL_SCOPES
                )

                # Refresh the token
                creds.refresh(Request())
                print("[EMAIL] Authenticated using refresh token from environment")

            except Exception as e:
                print(f"[EMAIL] Error using refresh token: {e}")
                creds = None

        # Option 2: Load from saved token file
        if not creds or not creds.valid:
            token_path = Path(TOKEN_FILE)
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(TOKEN_FILE, GMAIL_SCOPES)
                    print("[EMAIL] Loaded credentials from token.json")
                except Exception as e:
                    print(f"[EMAIL] Error loading token: {e}")

        # Option 3: Refresh existing credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("[EMAIL] Refreshed expired token")
                except Exception as e:
                    print(f"[EMAIL] Error refreshing token: {e}")
                    creds = None

        # Option 4: Interactive OAuth flow (local dev only)
        if not creds and self.credentials_json:
            try:
                # Parse credentials JSON
                credentials_data = json.loads(self.credentials_json)
                client_config = _extract_client_config(credentials_data)

                # Create flow from credentials
                flow = InstalledAppFlow.from_client_config(
                    client_config, GMAIL_SCOPES
                )

                # Run local server for OAuth callback
                print("[EMAIL] Starting OAuth flow - browser will open...")
                creds = flow.run_local_server(port=0)

                # Save credentials for future use
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())

                print(f"[EMAIL] OAuth complete! Token saved to {TOKEN_FILE}")
                print(f"[EMAIL] REFRESH_TOKEN (save to GMAIL_REFRESH_TOKEN env var):")
                print(f"[EMAIL] {creds.refresh_token}")

            except Exception as e:
                print(f"[EMAIL] Error getting new credentials: {e}")
                return False

        self.credentials = creds
        if creds and creds.valid:
            try:
                self.service = build('gmail', 'v1', credentials=creds)
                self._authenticated = True
                return True
            except Exception as e:
                print(f"[EMAIL] Error building Gmail service: {e}")
                return False

        return False

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send an email using Gmail API.

        Args:
            to: Recipient email address or list of addresses
            subject: Email subject
            body: Email body content
            is_html: True if body is HTML, False for plain text
            from_name: Optional sender name (defaults to account name)

        Returns:
            True if email sent successfully, False otherwise.

        Example:
            >>> client = GmailEmailClient()
            >>> client.send_email(
            ...     to="user@example.com",
            ...     subject="Test Email",
            ...     body="Hello from Gmail API!"
            ... )
        """
        if not self._authenticated:
            if not self._authenticate():
                print("[EMAIL] Authentication failed")
                return False

        try:
            # Create message
            if is_html:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'html'))
            else:
                message = MIMEText(body)

            # Set headers
            message['to'] = ', '.join([to] if isinstance(to, str) else to)
            message['subject'] = subject
            if from_name:
                message['from'] = from_name

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send via Gmail API
            send_message = (
                self.service.users()
                .messages()
                .send(userId='me', body={'raw': raw_message})
                .execute()
            )

            print(f"[EMAIL] Message sent! ID: {send_message.get('id')}")
            return True

        except HttpError as e:
            print(f"[EMAIL] Gmail API error: {e}")
            return False
        except Exception as e:
            print(f"[EMAIL] Error sending email: {e}")
            return False


async def send_email_async(
    to: str | List[str],
    subject: str,
    body: str,
    is_html: bool = False,
    from_name: Optional[str] = None
) -> bool:
    """
    Async wrapper for sending email via Gmail API.

    Args:
        to: Recipient email address or list of addresses
        subject: Email subject
        body: Email body content
        is_html: True if body is HTML, False for plain text
        from_name: Optional sender name

    Returns:
        True if email sent successfully, False otherwise.

    Example:
        >>> await send_email_async(
        ...     to="user@example.com",
        ...     subject="Welcome!",
        ...     body="<h1>Hello!</h1><p>Welcome to our app.</p>",
        ...     is_html=True
        ... )
    """
    loop = asyncio.get_event_loop()
    client = GmailEmailClient()

    # Run send_email in thread pool to avoid blocking
    result = await loop.run_in_executor(
        None,
        lambda: client.send_email(to, subject, body, is_html, from_name)
    )

    return result


# Simple sync wrapper for convenience
def send_email(
    to: str | List[str],
    subject: str,
    body: str,
    is_html: bool = False,
    from_name: Optional[str] = None
) -> bool:
    """
    Send email using Gmail API (sync wrapper).

    Args:
        to: Recipient email address or list of addresses
        subject: Email subject
        body: Email body content
        is_html: True if body is HTML, False for plain text
        from_name: Optional sender name

    Returns:
        True if email sent successfully, False otherwise.
    """
    client = GmailEmailClient()
    return client.send_email(to, subject, body, is_html, from_name)


# Test function
if __name__ == "__main__":
    print("[EMAIL] Gmail API Email Module")
    print(f"[EMAIL] Gmail API Available: {GMAIL_AVAILABLE}")
    print(f"[EMAIL] Credentials configured: {bool(settings.GMAIL_CREDENTIALS)}")
