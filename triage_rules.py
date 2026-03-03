"""Deterministic email triage helpers for junk-heavy inboxes."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

JUNK_KEYWORDS = {
    "sale",
    "deal",
    "discount",
    "promo",
    "promotion",
    "limited time",
    "clearance",
    "coupon",
    "unsubscribe",
    "newsletter",
    "offer",
    "buy now",
}

IMPORTANT_SENDER_HINTS = {
    "@bank",
    "@school",
    "@work",
    "@hospital",
    "@gov",
}


@dataclass
class TriageDecision:
    """Normalized triage result for UI rendering."""

    category: str
    actions: list[str]
    junk_score: int
    priority: str
    reason: str


def _combined_text(subject: str, body: str | None) -> str:
    return f"{subject}\n{body or ''}".lower()


def score_junk(subject: str, sender: str, body: str | None) -> tuple[int, list[str]]:
    """Return a 0-100 junk score plus reasons."""
    text = _combined_text(subject, body)
    sender_lower = sender.lower()
    reasons: list[str] = []
    score = 0

    for keyword in JUNK_KEYWORDS:
        if keyword in text:
            score += 8
            reasons.append(f"contains '{keyword}'")

    if "no-reply" in sender_lower or "noreply" in sender_lower:
        score += 10
        reasons.append("from no-reply sender")

    if re.search(r"\b\d{1,2}%\s*off\b", text):
        score += 12
        reasons.append("contains % off promotion")

    if any(hint in sender_lower for hint in IMPORTANT_SENDER_HINTS):
        score -= 15
        reasons.append("sender looks important")

    return max(0, min(100, score)), reasons


def build_triage_decision(
    subject: str,
    sender: str,
    body: str | None,
    ai_result: dict[str, Any],
) -> TriageDecision:
    """Merge AI category with deterministic anti-junk scoring."""
    junk_score, reasons = score_junk(subject, sender, body)
    category = ai_result.get("category", "other")
    actions = list(ai_result.get("actions") or [])

    if junk_score >= 35 and "trash" not in actions:
        actions.append("review_for_trash")
    if junk_score >= 35 and "unsubscribe" not in actions:
        actions.append("unsubscribe")

    if category == "action_request":
        priority = "high"
    elif junk_score >= 50 or category == "marketing":
        priority = "low"
    else:
        priority = "medium"

    reason = ", ".join(reasons[:3]) if reasons else "No junk indicators"
    return TriageDecision(
        category=category,
        actions=actions,
        junk_score=junk_score,
        priority=priority,
        reason=reason,
    )


def summarize_priorities(decisions: list[TriageDecision]) -> dict[str, int]:
    """Count decision priorities for quick inbox cleanup planning."""
    counts = Counter(item.priority for item in decisions)
    return {
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
    }


__all__ = ["TriageDecision", "build_triage_decision", "score_junk", "summarize_priorities"]
