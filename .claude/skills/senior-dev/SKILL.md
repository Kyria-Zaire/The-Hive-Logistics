---
name: senior-dev
description: "Exécuter un ticket de développement borné avec discipline senior, diff minimal, tests, vérification réelle et rapport CTO."
---

# Senior Dev

1. Lire le ticket et établir les critères d’acceptation observables.
2. Inspecter les appelants, types, tests et conventions avant de modifier.
3. Signaler les ambiguïtés qui changent le produit ; décider localement seulement pour les détails réversibles.
4. Implémenter le chemin le plus simple qui respecte l’architecture.
5. Traiter erreurs, concurrence, états vides, accessibilité et sécurité concernés.
6. Ajouter des tests proportionnés au risque.
7. Lancer les validations pertinentes et tester le comportement réel.
8. Relire le diff comme reviewer hostile aux régressions.
9. Produire le rapport de `AGENTS.md`.

Ne pas commit, push, déployer, modifier PROD ou étendre le périmètre sans GO explicite.
