# Email triage helper (Gmail + Calendar + OpenAI)

A simple Flask web app that fetches your recent Gmail messages, sends them to the OpenAI API for classification, and previews recommended actions. No email changes are made yet.

## Prerequisites
- Python 3.10+ (works well with pyenv or the system Python on macOS)
- A Google Cloud project with Gmail and Calendar APIs enabled
- `credentials.json` downloaded from Google Cloud OAuth client (Desktop app)
- An OpenAI API key

## Setup (first time)
1. Clone this repository and open a terminal in the project folder.
2. (Recommended) Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place your `credentials.json` in the project root (same folder as this README).
5. Create a `.env` file in the project root with your OpenAI key:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

## Authorize Gmail and Calendar (one time)
Run the OAuth helper. It will open a browser window and save `token.json` locally for reuse.
```bash
python authorize_gmail_and_calendar.py
```

## Run the Flask app
```bash
python app.py
```
Then open http://127.0.0.1:5000 in Safari (or any browser). You will see a preview table of your recent emails and the planned actions suggested by the AI. No emails are modified yet.

## What is new for junk-heavy inboxes
- A deterministic junk score (0-100) is now calculated for each message using keywords, sender signals, and promotional patterns.
- Emails are grouped into **high**, **medium**, and **low/junk** priorities so you can clean low-priority items in bulk.
- The preview table now explains *why* a message was flagged as junk and suggests actions like `review_for_trash` and `unsubscribe`.
- If Gmail credentials are missing or invalid, the app now shows a friendly error banner instead of crashing.

## Future automation (planned)
The following behaviors are stubbed with TODO comments in the code for later work:
- Automatically unsubscribe and delete marketing emails.
- Create Calendar tasks for action-request emails.
- Sort purchase receipts and tracking emails into a Purchases label/folder.
- Sort "save for later" informational emails into a Miscellaneous label.
- Sort travel emails into a Travel label and create calendar events with correct details and a link back to the confirmation email.
- On startup, check whether packages are delivered and trash old tracking emails.
- On startup, clean up travel emails for trips that have already passed.
