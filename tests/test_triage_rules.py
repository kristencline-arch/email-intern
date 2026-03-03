import unittest

from triage_rules import build_triage_decision, score_junk, summarize_priorities


class TriageRulesTests(unittest.TestCase):
    def test_score_junk_detects_promotions(self):
        score, reasons = score_junk(
            "Limited time sale - 50% off today",
            "noreply@shop.example",
            "Buy now and unsubscribe anytime",
        )
        self.assertGreaterEqual(score, 40)
        self.assertTrue(reasons)

    def test_score_junk_decreases_for_important_sender(self):
        score, _ = score_junk(
            "Monthly statement",
            "alerts@bank.example",
            "Your secure account notice",
        )
        self.assertEqual(score, 0)

    def test_build_triage_decision_appends_actions_for_junk(self):
        result = build_triage_decision(
            "Limited time discount offer 50% off",
            "noreply@deals.example",
            "unsubscribe and buy now",
            {"category": "marketing", "actions": ["label"]},
        )
        self.assertEqual(result.priority, "low")
        self.assertIn("unsubscribe", result.actions)

    def test_summarize_priorities_counts(self):
        decisions = [
            build_triage_decision("a", "a@work.example", "", {"category": "action_request", "actions": []}),
            build_triage_decision("sale offer", "noreply@d.example", "unsubscribe", {"category": "marketing", "actions": []}),
        ]
        summary = summarize_priorities(decisions)
        self.assertEqual(summary["high"], 1)
        self.assertEqual(summary["low"], 1)


if __name__ == "__main__":
    unittest.main()
