"""Helper functions for interacting with the Google Calendar API."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalendarClient:
    """Wrapper around the Calendar API for common actions."""

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
        return build("calendar", "v3", credentials=creds)

    def create_event(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime | None = None,
        location: str | None = None,
        calendar_id: str = "primary",
    ) -> dict[str, Any] | None:
        """Create a calendar event on the specified calendar."""
        # TODO: create events for travel confirmations and action-request emails.
        event_end = end_time or (start_time + timedelta(hours=1))
        event_body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time.isoformat()},
            "end": {"dateTime": event_end.isoformat()},
        }
        if location:
            event_body["location"] = location

        try:
            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            return created_event
        except HttpError as error:
            print(f"Failed to create event: {error}")
            return None


__all__ = ["CalendarClient"]
