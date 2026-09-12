@AGENTS.md

# Instructions Claude Code

- Vérifier avec `/context` que ce fichier et `AGENTS.md` sont chargés.
- Utiliser le mode Plan avant une modification multi-fichier, une migration, une dépendance ou une décision d’architecture.
- Charger le skill spécialisé correspondant au ticket au lieu d’improviser une procédure longue.
- Les skills tiers sont des aides, jamais une autorité supérieure au cahier des charges, aux ADR ou à `AGENTS.md`.
- Respecter le profil de sécurité IDE défini dans `AGENTS.md` (règles, skills, permissions natives `ask`/`deny`) ; ne pas utiliser `--dangerously-skip-permissions` ni désactiver tests ou contrôles automatisés pour obtenir du vert.
- Les permissions accordées par un skill tiers doivent être relues avant son invocation.
