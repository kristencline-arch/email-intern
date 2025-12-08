"""Flask app that previews AI-based email triage."""

from __future__ import annotations

from flask import Flask, render_template
from dotenv import load_dotenv

from ai_classifier import classify_email
from gmail_client import GmailClient

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    gmail_client = GmailClient()
    emails = gmail_client.fetch_recent_emails(max_results=5)

    processed = []
    for email in emails:
        ai_result = classify_email(email.subject, email.sender, email.body)
        processed.append({"email": email, "ai_result": ai_result})

    # TODO: Later, add buttons to apply unsubscribe/delete/label actions.
    # TODO: Sort receipts and tracking emails into a "Purchases" label.
    # TODO: Sort "save for later" emails into a "Miscellaneous" label.
    # TODO: Create calendar tasks for action-request emails.
    # TODO: Create travel events and add labels for travel messages.
    # TODO: On startup, check delivered packages and clean up tracking emails.
    # TODO: On startup, clean up travel emails for past trips.

    return render_template("index.html", processed=processed)


if __name__ == "__main__":
    app.run(debug=True)
