"""One-time OAuth script for Gmail and Google Calendar.

This script reads `credentials.json`, runs the browser-based OAuth flow,
and saves the resulting tokens to `token.json` for later reuse.
"""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes cover Gmail modify access and Calendar events.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.events",
]


def main() -> None:
    """Run the OAuth flow and persist refreshed credentials."""
    creds: Credentials | None = None
    token_path = Path("token.json")

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # Launches a local server to complete OAuth in the browser.
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json())
    print(f"Saved tokens to {token_path.resolve()}")


if __name__ == "__main__":
    main()
