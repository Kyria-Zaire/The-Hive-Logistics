#!/usr/bin/env python3
"""Optional experimental safety gate for Cursor/Claude hooks (not required in governance 1.0.2)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePath
from typing import Any


SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.production.local",
    ".env.preprod",
    ".env.recette",
    "credentials.json",
    "service-account.json",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks"}

DENY_COMMANDS = (
    (r"\brm\s+-[^\n]*r[^\n]*f\b|\brm\s+-[^\n]*f[^\n]*r\b", "suppression récursive forcée"),
    (r"\bremove-item\b[^\n]*\b-recurse\b", "suppression PowerShell récursive"),
    (r"\b(?:rmdir|rd)\s+/s\b|\bdel\s+/s\b", "suppression Windows récursive"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+clean\s+-[^\s]*[fdx]", "nettoyage Git destructif"),
    (r"\bgit\s+push\b[^\n]*(?:--force|-f)\b", "push Git forcé"),
    (r"\bdocker\s+system\s+prune\b", "prune Docker global"),
    (r"\bterraform\s+destroy\b", "destruction Terraform"),
    (r"\bkubectl\s+delete\b", "suppression Kubernetes"),
    (r"\b(?:drop\s+(?:database|schema|table)|truncate\s+(?:table\s+)?)\b", "DDL destructif"),
    (r"\bdelete\s+from\s+[\w.]+\s*(?:;|$)", "DELETE SQL sans filtre apparent"),
    (r"(?:curl|wget)[^\n|]*\|\s*(?:sh|bash|zsh)\b", "téléchargement exécuté directement dans un shell"),
    (r"\b(?:invoke-expression|iex)\b", "exécution PowerShell dynamique"),
)

PRODUCTION_WRITE = re.compile(
    r"(?is)(?:prod(?:uction)?).*(?:deploy|migrate|upgrade|apply|destroy|delete|write|seed)"
    r"|(?:deploy|migrate|upgrade|apply|destroy|delete|write|seed).*(?:prod(?:uction)?)"
)


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def command_from(payload: dict[str, Any]) -> str:
    direct = payload.get("command")
    if isinstance(direct, str):
        return direct
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        return command if isinstance(command, str) else ""
    return ""


def path_from(payload: dict[str, Any]) -> str:
    direct = payload.get("file_path")
    if isinstance(direct, str):
        return direct
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        path = tool_input.get("file_path")
        return path if isinstance(path, str) else ""
    return ""


def secret_path_reason(path_value: str) -> str | None:
    if not path_value:
        return None
    normalized = path_value.replace("\\", "/").lower()
    path = PurePath(normalized)
    name = path.name
    if name in {".env.example", ".env.sample", ".env.template"}:
        return None
    if name in SECRET_NAMES or any(name.endswith(suffix) for suffix in SECRET_SUFFIXES):
        return f"lecture d’un fichier secret interdite : {name}"
    if "/secrets/" in f"/{normalized.strip('/')}/":
        return "lecture du répertoire secrets interdite"
    return None


def command_decision(command: str) -> tuple[str, str] | None:
    if not command:
        return None
    for pattern, reason in DENY_COMMANDS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            return "deny", f"Commande bloquée : {reason}. Exécution humaine requise."
    if PRODUCTION_WRITE.search(command):
        return "ask", "Commande susceptible de modifier PROD : approbation humaine explicite requise."
    return None


def emit(payload: dict[str, Any], decision: str, reason: str) -> None:
    is_claude = payload.get("hook_event_name") == "PreToolUse"
    if is_claude:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason,
            }
        }
    else:
        output = {
            "permission": decision,
            "user_message": reason,
            "agent_message": reason,
        }
    print(json.dumps(output, ensure_ascii=False))


def emit_allow(payload: dict[str, Any]) -> None:
    """Claude accepts no decision; Cursor requires an explicit allow response."""
    if payload.get("hook_event_name") == "PreToolUse":
        print("{}")
    else:
        print(json.dumps({"permission": "allow"}))


def main() -> int:
    try:
        payload = read_payload()
        if payload.get("tool_name") == "Delete":
            emit(payload, "deny", "Suppression via outil agent bloquée : exécution humaine explicite requise.")
            return 0
        path_reason = secret_path_reason(path_from(payload))
        if path_reason:
            emit(payload, "deny", path_reason)
            return 0
        command_result = command_decision(command_from(payload))
        if command_result:
            emit(payload, *command_result)
            return 0
        emit_allow(payload)
        return 0
    except Exception as exc:  # fail closed is configured by Cursor; Claude has deny rules too.
        print(f"agent_guard failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
