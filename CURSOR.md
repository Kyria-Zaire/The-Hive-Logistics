# Instructions Cursor

Cursor charge `AGENTS.md`, les règles `.cursor/rules/*.mdc` et les skills découverts dans `.claude/skills/`.

- Commencer en mode Plan pour toute tâche non triviale.
- Utiliser un skill spécialisé seulement lorsque son périmètre correspond au ticket.
- Ne jamais activer l’exécution autonome d’un déploiement, d’une migration PROD ou d’une commande destructive.
- Appliquer le profil de sécurité IDE 1.0.2 (`AGENTS.md`) : règles, skills, permissions natives Claude, validation humaine, Git/CI et scans ; une opération refusée ou en attente d’approbation doit être remontée au CTO, pas contournée.
- Après chaque ticket, fournir le rapport imposé par `AGENTS.md`.

Note : ce fichier sert d’index humain. La règle `.cursor/rules/00-governance.mdc` le rattache explicitement au contexte Cursor. Les hooks runtime Cursor (ex. `agent_guard.py`) ne sont **pas** requis ; les fichiers `hooks*.disabled*` sont des sauvegardes historiques.
