#!/usr/bin/env python3
"""Validate the THE HIVE LOGISTICS governance pack (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_GOVERNANCE_VERSION = "1.0.2"
DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def required_files(root: Path) -> list[Path]:
    return [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "CURSOR.md",
        root / "SKILLS.md",
        root / "GOVERNANCE_VERSION",
        root / ".claude/settings.json",
        root / ".cursor/rules/00-governance.mdc",
    ]

REQUIRED_SKILLS = {
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
}


def validate_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON invalide {path}: {exc}")
        return None


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def validate_governance_version(root: Path, errors: list[str]) -> None:
    path = root / "GOVERNANCE_VERSION"
    if not path.is_file():
        errors.append("Fichier requis manquant: GOVERNANCE_VERSION")
        return
    version = path.read_text(encoding="utf-8").strip()
    if version != EXPECTED_GOVERNANCE_VERSION:
        errors.append(
            f"GOVERNANCE_VERSION attendue {EXPECTED_GOVERNANCE_VERSION}, trouvée {version!r}"
        )


def validate_claude_settings(root: Path, errors: list[str]) -> None:
    path = root / ".claude/settings.json"
    if not path.is_file():
        errors.append("Fichier requis manquant: .claude/settings.json")
        return
    data = validate_json(path, errors)
    if data is None:
        return
    hooks = data.get("hooks")
    if hooks not in (None, {}, []):
        errors.append(
            "Section hooks active dans .claude/settings.json — profil 1.0.2 sans hooks runtime"
        )
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        errors.append(".claude/settings.json : permissions manquante ou invalide")
        return
    ask = permissions.get("ask")
    deny = permissions.get("deny")
    if not isinstance(ask, list) or len(ask) == 0:
        errors.append(".claude/settings.json : permissions.ask manquant ou vide")
    if not isinstance(deny, list) or len(deny) == 0:
        errors.append(".claude/settings.json : permissions.deny manquant ou vide")


def validate_no_active_cursor_hooks(root: Path, errors: list[str]) -> None:
    path = root / ".cursor/hooks.json"
    if not path.is_file():
        return
    errors.append(
        ".cursor/hooks.json présent : HOOK_PROFILE=no_runtime_hooks exige l'absence de ce "
        "fichier (supprimer ou renommer, ex. hooks.json.disabled). Les fichiers "
        "hooks.json.disabled, hooks.disabled.json et *.bak ne sont pas chargés par Cursor."
    )


def validate_skills_and_rules(root: Path, errors: list[str]) -> tuple[int, int]:
    skills_root = root / ".claude/skills"
    found = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    for name in sorted(REQUIRED_SKILLS - found):
        errors.append(f"Skill manquant: {name}")
    for path in skills_root.glob("*/SKILL.md"):
        meta = frontmatter(path)
        if meta.get("name") != path.parent.name:
            errors.append(f"Nom/frontmatter incohérent: {path.relative_to(root)}")
        if not meta.get("description"):
            errors.append(f"Description absente: {path.relative_to(root)}")
    rules = list((root / ".cursor/rules").glob("*.mdc"))
    for path in rules:
        meta = frontmatter(path)
        if "alwaysApply" not in meta:
            errors.append(f"alwaysApply absent: {path.relative_to(root)}")
    return len(found), len(rules)


def run_validation(root: Path | None = None) -> tuple[list[str], dict[str, int]]:
    base = root if root is not None else DEFAULT_ROOT
    errors: list[str] = []
    for path in required_files(base):
        if path.name == "GOVERNANCE_VERSION":
            continue
        if not path.is_file():
            errors.append(f"Fichier requis manquant: {path.relative_to(base)}")
    validate_governance_version(base, errors)
    validate_claude_settings(base, errors)
    validate_no_active_cursor_hooks(base, errors)
    skill_count, rule_count = validate_skills_and_rules(base, errors)
    counts = {
        "skills": skill_count,
        "cursor_rules": rule_count,
        "claude_rules": len(list((base / ".claude/rules").glob("*.md"))),
    }
    return errors, counts


def main() -> int:
    errors, counts = run_validation(None)
    if errors:
        print("GOVERNANCE_VALIDATION = FAIL")
        print(f"GOVERNANCE_VERSION = {EXPECTED_GOVERNANCE_VERSION} (attendue)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GOVERNANCE_VALIDATION = PASS")
    print(f"GOVERNANCE_VERSION = {EXPECTED_GOVERNANCE_VERSION}")
    print(f"HOOK_PROFILE = no_runtime_hooks")
    print(f"SKILLS = {counts['skills']}")
    print(f"CURSOR_RULES = {counts['cursor_rules']}")
    print(f"CLAUDE_RULES = {counts['claude_rules']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
