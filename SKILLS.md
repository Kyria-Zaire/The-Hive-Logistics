# Catalogue des skills du projet

Les skills projet sont stockés une seule fois dans `.claude/skills/`. Claude Code les charge nativement et Cursor charge officiellement les skills compatibles présents dans ce dossier.

La gouvernance `1.0.2` s’appuie sur ces skills et sur les règles projet, **sans** hooks Python runtime obligatoires. Vérification : `python .claude/hooks/validate_governance.py`.

## Skills THE HIVE LOGISTICS

- `/constructeur-ui` : construire une section ou page responsive à partir d’une maquette validée.
- `/architecte-api` : concevoir un contrat FastAPI et ses frontières avant implémentation.
- `/senior-dev` : exécuter un ticket borné avec tests et rapport.
- `/thl-code-review` : revue de diff orientée défauts et régressions.
- `/ui-ux-pro-max` : audit UX/UI, responsive, accessibilité et finition premium.
- `/ingenieur` : diagnostic et analyse de cause racine.
- `/reviewer-securite-code` : audit de sécurité en lecture seule.
- `/createur-workflow` : concevoir ou modifier CI/CD avec moindre privilège.
- `/simplify` : simplifier le code touché sans changer son comportement.
- `/improve-codebase-architecture` : préparer puis conduire un refactor structurel incrémental.
- `/thl-shadcn` : intégrer ou adapter un primitive shadcn sans perdre la direction artistique.
- `/frontend-design-thl` : orchestrer la création frontend premium propre au projet.
- `/skill-lifecycle` : créer, évaluer, améliorer ou benchmarker un skill.

## Skills tiers déjà signalés par le développeur

- `emilkowalski/skill`
- `pbakaus/impeccable`
- `leonxlnx/taste-skill`

Ils ne sont pas copiés dans ce pack afin d’éviter les collisions, les forks silencieux et le code tiers non maîtrisé. Conserver leur lock/version d’installation et réévaluer leur contenu avant toute mise à jour.

Le plugin `frontend-design` de Claude Code peut rester namespacé par son plugin. Il ne remplace pas `/frontend-design-thl`, qui contient les contraintes spécifiques à THE HIVE LOGISTICS.
