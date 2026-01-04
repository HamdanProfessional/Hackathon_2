"""Generate Gmail API refresh token for email worker.

This script runs the OAuth flow to generate a refresh token that can be
used by the email worker to send emails via Gmail API.

Usage:
    python scripts/generate_gmail_token.py

The script will:
1. Open a browser for OAuth consent
2. Display the refresh token
3. Save token.json for local use
"""
import json
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: Google libraries not installed")
    print("Install: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Get credentials from environment or file
credentials_json = os.getenv("GMAIL_CREDENTIALS")
if not credentials_json:
    print("ERROR: GMAIL_CREDENTIALS environment variable not set")
    print("Please set it to your OAuth2 client credentials JSON")
    sys.exit(1)

def extract_client_config(credentials_data: dict) -> dict:
    """Extract client config from either 'web' or 'installed' type credentials."""
    if 'web' in credentials_data:
        return credentials_data['web']
    elif 'installed' in credentials_data:
        return credentials_data['installed']
    else:
        return credentials_data

def main():
    print("=" * 60)
    print("Gmail API Refresh Token Generator")
    print("=" * 60)
    print()

    # Parse credentials
    credentials_data = json.loads(credentials_json)
    client_config = extract_client_config(credentials_data)

    print(f"Client ID: {client_config.get('client_id')}")
    print(f"Project ID: {credentials_data.get('project_id', 'N/A')}")
    print()

    # Create OAuth flow
    flow = InstalledAppFlow.from_client_config(client_config, GMAIL_SCOPES)

    print("Opening browser for OAuth consent...")
    print("Please authorize the app to send emails on your behalf.")
    print()

    # Run local server for OAuth callback
    creds = flow.run_local_server(port=0)

    # Save credentials for future use
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print()
    print("=" * 60)
    print("SUCCESS! OAuth Complete")
    print("=" * 60)
    print()
    print(f"Your REFRESH TOKEN (save this!):")
    print()
    print(creds.refresh_token)
    print()
    print("=" * 60)
    print()
    print("Add this to Kubernetes secrets:")
    print(f"  kubectl patch secret -n production todo-notifications-secrets -p '{{\"data\":{{\"gmail-refresh-token\":\"{creds.refresh_token}\"}}}}'")
    print()
    print("Or set as environment variable:")
    print(f"  export GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print()

if __name__ == "__main__":
    main()
