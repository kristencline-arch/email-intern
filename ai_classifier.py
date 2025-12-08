"""Email classification using the OpenAI API."""

from __future__ import annotations

import json
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

CATEGORIES = [
    "marketing",
    "action_request",
    "purchase_receipt",
    "tracking_info",
    "travel",
    "save_for_later",
    "other",
]


def classify_email(subject: str, sender: str, body: str | None) -> dict[str, Any]:
    """Send email content to OpenAI and return structured decisions."""
    prompt = (
        "You are a helpful email triage assistant."
        " Categorize the email and propose safe actions."
        " Return JSON with keys: category (one of the allowed values),"
        " actions (list), optional task info (title, description, due_date),"
        " optional travel info (event_summary, start_time, end_time, location),"
        " optional tracking info (carrier, tracking_number)."
    )
    instructions = {
        "subject": subject,
        "sender": sender,
        "body": body or "",
    }
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(instructions)},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        category = result.get("category", "other")
        if category not in CATEGORIES:
            result["category"] = "other"
        return result
    except (json.JSONDecodeError, KeyError) as parse_error:
        print(f"Failed to parse AI response: {parse_error}")
        return {"category": "other", "actions": ["label"], "notes": "Parse error"}
    except Exception as api_error:  # noqa: BLE001
        print(f"OpenAI API error: {api_error}")
        return {"category": "other", "actions": ["label"], "notes": "API error"}


__all__ = ["classify_email", "CATEGORIES"]
