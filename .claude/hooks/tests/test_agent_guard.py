from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "agent_guard.py"


def invoke(payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    output = json.loads(result.stdout or "{}")
    return result.returncode, output


class AgentGuardTest(unittest.TestCase):
    def test_allows_safe_command(self) -> None:
        code, output = invoke({"hook_event_name": "beforeShellExecution", "command": "pnpm test"})
        self.assertEqual(code, 0)
        self.assertEqual(output, {"permission": "allow"})

    def test_denies_destructive_cursor_command(self) -> None:
        code, output = invoke({"hook_event_name": "beforeShellExecution", "command": "git reset --hard HEAD"})
        self.assertEqual(code, 0)
        self.assertEqual(output["permission"], "deny")

    def test_requests_approval_for_production_write(self) -> None:
        code, output = invoke({"hook_event_name": "beforeShellExecution", "command": "deploy production"})
        self.assertEqual(code, 0)
        self.assertEqual(output["permission"], "ask")

    def test_denies_secret_read_for_claude(self) -> None:
        code, output = invoke(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Read",
                "tool_input": {"file_path": "C:\\project\\.env.production"},
            }
        )
        self.assertEqual(code, 0)
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")

    def test_allows_env_template(self) -> None:
        code, output = invoke({"hook_event_name": "beforeReadFile", "file_path": "/project/.env.example"})
        self.assertEqual(code, 0)
        self.assertEqual(output, {"permission": "allow"})

    def test_claude_safe_command_uses_native_no_decision(self) -> None:
        code, output = invoke(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python -m pytest"},
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(output, {})

    def test_denies_agent_delete_tool(self) -> None:
        code, output = invoke({"hook_event_name": "preToolUse", "tool_name": "Delete", "tool_input": {}})
        self.assertEqual(code, 0)
        self.assertEqual(output["permission"], "deny")

    def test_denies_secret_write_for_claude(self) -> None:
        code, output = invoke(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": "/project/.env.local", "content": "SECRET=value"},
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
