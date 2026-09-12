from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / ".claude/hooks/validate_governance.py"
MODULE = ROOT / ".claude/hooks/validate_governance.py"


class ValidateGovernanceIntegrationTest(unittest.TestCase):
    def test_project_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("GOVERNANCE_VALIDATION = PASS", result.stdout)
        self.assertIn("GOVERNANCE_VERSION = 1.0.2", result.stdout)
        self.assertIn("HOOK_PROFILE = no_runtime_hooks", result.stdout)


class ValidateGovernanceUnitTest(unittest.TestCase):
    def test_fails_when_cursor_hooks_json_present(self) -> None:
        sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
        try:
            import validate_governance as vg

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self._write_minimal_pack(root)
                (root / ".cursor" / "hooks.json").write_text("{}", encoding="utf-8")
                errors, _ = vg.run_validation(root)
                self.assertTrue(any(".cursor/hooks.json présent" in e for e in errors))
        finally:
            sys.path.pop(0)

    def test_fails_when_cursor_hooks_json_benign_hook(self) -> None:
        sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
        try:
            import validate_governance as vg

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self._write_minimal_pack(root)
                hooks = {
                    "version": 1,
                    "hooks": {
                        "beforeShellExecution": [
                            {"command": "echo ok", "timeout": 5},
                        ]
                    },
                }
                (root / ".cursor" / "hooks.json").write_text(
                    json.dumps(hooks), encoding="utf-8"
                )
                errors, _ = vg.run_validation(root)
                self.assertTrue(any(".cursor/hooks.json présent" in e for e in errors))
        finally:
            sys.path.pop(0)

    def test_fails_when_claude_hooks_section_active(self) -> None:
        sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
        try:
            import validate_governance as vg

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self._write_minimal_pack(root)
                settings_path = root / ".claude" / "settings.json"
                settings = json.loads(settings_path.read_text(encoding="utf-8"))
                settings["hooks"] = {"PreToolUse": []}
                settings_path.write_text(json.dumps(settings), encoding="utf-8")
                errors, _ = vg.run_validation(root)
                self.assertTrue(any("hooks active" in e for e in errors))
        finally:
            sys.path.pop(0)

    def _write_minimal_pack(self, root: Path) -> None:
        for name in ("AGENTS.md", "CLAUDE.md", "CURSOR.md", "SKILLS.md"):
            (root / name).write_text("# stub\n", encoding="utf-8")
        (root / "GOVERNANCE_VERSION").write_text("1.0.2\n", encoding="utf-8")
        (root / ".claude").mkdir(parents=True)
        (root / ".cursor" / "rules").mkdir(parents=True)
        (root / ".claude" / "rules").mkdir(parents=True)
        (root / ".claude" / "skills").mkdir(parents=True)
        settings = {
            "permissions": {
                "ask": ["Bash(git commit *)"],
                "deny": ["Read(./.env)"],
            }
        }
        (root / ".claude" / "settings.json").write_text(
            json.dumps(settings), encoding="utf-8"
        )
        (root / ".cursor" / "rules" / "00-governance.mdc").write_text(
            "---\nalwaysApply: true\n---\nbody\n",
            encoding="utf-8",
        )
        for skill in (
            "constructeur-ui",
            "architecte-api",
            "senior-dev",
            "thl-code-review",
            "ui-ux-pro-max",
            "ingenieur",
            "reviewer-securite-code",
            "createur-workflow",
            "simplify",
            "improve-codebase-architecture",
            "thl-shadcn",
            "frontend-design-thl",
            "skill-lifecycle",
        ):
            skill_dir = root / ".claude" / "skills" / skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: test\n---\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main()
