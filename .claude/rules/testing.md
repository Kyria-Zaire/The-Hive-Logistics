---
paths:
  - "apps/**/*.{py,ts,tsx}"
  - "packages/**/*.{py,ts,tsx}"
  - "tests/**/*"
  - "e2e/**/*"
---

# Tests et preuves

- Tester les comportements et invariants, pas la forme interne ni des snapshots géants.
- Chaque correction de bug ajoute d’abord ou simultanément un test de non-régression.
- Frontend : tests unitaires ciblés, composants accessibles et E2E des parcours critiques.
- Backend : services, validation, transactions, persistance et contrats HTTP.
- Sécurité : rate limit, anti-spam, validation Turnstile simulée, signatures/replay des webhooks si ces fonctions existent.
- Utiliser des données déterministes, isoler l’horloge et interdire l’accès accidentel aux services/DB de PROD.
- Un test ignoré, flaky ou dépendant du réseau est signalé ; il n’est jamais masqué pour obtenir un PASS.
- La recette visuelle couvre desktop, medium, mobile, clavier, réduction des mouvements et absence de débordement horizontal.
