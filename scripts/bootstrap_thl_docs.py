#!/usr/bin/env python3
"""Bootstrap docs colonne vertébrale THE HIVE LOGISTICS."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_VERSION = "1.0.2"

DIRS = (
    "docs/prd",
    "docs/adr",
    "docs/architecture",
    "docs/backlog",
)

PRD_REDIRECT = r"""# PRD — redirection

Le modèle PRD canonique n’est **pas** maintenu dans ce fichier.

**Source de vérité :** [`PRD-TEMPLATE.md`](../PRD-TEMPLATE.md) à la racine du dépôt.

- Ne pas maintenir deux versions du gabarit PRD.
- Toute modification du modèle doit être faite uniquement dans `/PRD-TEMPLATE.md`.
- Pour rédiger le PRD produit : copier le canonique vers `docs/product/PRD.md` (voir `METHODE-BMAD.md`).
"""

BMAD_REDIRECT = r"""# BMAD — redirection

La méthode BMAD (Brief → Model → Act → Deliver) n’est plus maintenue dans ce fichier.

**Source de vérité :** [`METHODE-BMAD.md`](../METHODE-BMAD.md) à la racine du dépôt.

Ce document sert uniquement de point d’entrée historique pour les liens existants vers `docs/BMAD.md`.

- Gouvernance IDE : version **1.0.2**, profil `HOOK_PROFILE=no_runtime_hooks` — voir `AGENTS.md` et `AI-GOVERNANCE-SETUP.md`.
- Validation : `python .claude/hooks/validate_governance.py`
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def write_text_if_missing(path: Path, content: str) -> None:
    if path.is_file():
        print("SKIP (exists):", path)
        return
    write_text(path, content)
    print("OK:", path)


def main() -> int:
    print(f"Bootstrap docs THL — gouvernance {GOVERNANCE_VERSION} (sans hooks runtime)")
    for rel in DIRS:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)
    write_text_if_missing(ROOT / "docs" / "PRD-template.md", PRD_REDIRECT)
    write_text_if_missing(ROOT / "docs" / "PRD-TEMPLATE.md", PRD_REDIRECT)
    write_text_if_missing(ROOT / "docs" / "BMAD.md", BMAD_REDIRECT)
    for rel in DIRS:
        print("OK:", ROOT / rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
