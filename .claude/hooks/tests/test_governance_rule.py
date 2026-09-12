from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RULE = ROOT / ".cursor" / "rules" / "00-governance.mdc"


class GovernanceRuleTest(unittest.TestCase):
    def test_always_apply_rule_matches_profile_102(self) -> None:
        text = RULE.read_text(encoding="utf-8")
        self.assertIn("alwaysApply: true", text)
        self.assertNotIn("contourner les hooks", text.lower())
        self.assertIn("permissions natives", text)
        self.assertIn("AGENTS.md", text)


if __name__ == "__main__":
    unittest.main()
