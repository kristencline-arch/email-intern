"""Helper functions for interacting with the Gmail API."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


@dataclass
class EmailContent:
    """Simple representation of an email message."""

    id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    body: str | None


class GmailClient:
    """Wrapper around the Gmail API for common actions."""

    def __init__(self, token_path: str = "token.json") -> None:
        self.token_path = token_path
        self.service = self._get_service()

    def _get_credentials(self) -> Credentials:
        creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    def _get_service(self):
        creds = self._get_credentials()
        return build("gmail", "v1", credentials=creds)

    def fetch_recent_emails(self, max_results: int = 10) -> list[EmailContent]:
        """Fetch recent inbox emails with basic details."""
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
                .execute()
            )
            messages = results.get("messages", [])
        except HttpError as error:
            print(f"An error occurred while listing messages: {error}")
            return []

        emails: list[EmailContent] = []
        for msg in messages:
            try:
                full_message = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                payload = full_message.get("payload", {})
                headers = payload.get("headers", [])
                subject = self._extract_header(headers, "Subject") or "(No subject)"
                sender = self._extract_header(headers, "From") or "(Unknown sender)"
                snippet = full_message.get("snippet", "")
                body = self._get_body_from_payload(payload)

                emails.append(
                    EmailContent(
                        id=msg["id"],
                        thread_id=full_message.get("threadId", ""),
                        subject=subject,
                        sender=sender,
                        snippet=snippet,
                        body=body,
                    )
                )
            except HttpError as error:
                print(f"Error fetching message {msg.get('id')}: {error}")
                continue
        return emails

    def apply_labels(self, message_id: str, add_labels: list[str]) -> None:
        """Apply labels to an email."""
        # TODO: automatically apply labels based on AI decisions.
        try:
            body = {"addLabelIds": add_labels}
            self.service.users().messages().modify(userId="me", id=message_id, body=body).execute()
        except HttpError as error:
            print(f"Failed to apply labels to {message_id}: {error}")

    def move_to_trash(self, message_id: str) -> None:
        """Move an email to the trash folder."""
        # TODO: use this when unsubscribing/deleting marketing emails automatically.
        try:
            self.service.users().messages().trash(userId="me", id=message_id).execute()
        except HttpError as error:
            print(f"Failed to trash message {message_id}: {error}")

    def _extract_header(self, headers: list[dict[str, str]], name: str) -> str | None:
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value")
        return None

    def _get_body_from_payload(self, payload: dict[str, Any]) -> str | None:
        """Attempt to extract a text/plain body from the email payload."""
        if "parts" in payload:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    data = part["body"].get("data")
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        if "body" in payload and "data" in payload["body"]:
            data = payload["body"].get("data")
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        return None


__all__ = ["GmailClient", "EmailContent"]
