---
name: improve-codebase-architecture
description: "Évaluer puis améliorer l'architecture d'une zone du code par migration incrémentale, sans refonte big-bang."
---

# Improve Codebase Architecture

Phase 1 — diagnostic en lecture seule : responsabilités, dépendances, cycles, frontières, ownership des données, points de changement et métriques observables.

Phase 2 — décision : problème précis, options, coûts, risques, ADR proposé et état cible minimal.

Phase 3 — migration : étapes réversibles, compatibilité temporaire, tests de caractérisation, ordre des changements et suppression finale de l’ancien chemin.

Phase 4 — preuve : tests, mesures, graphe de dépendances ou inventaire avant/après et risques résiduels.

Interdire les microservices, couches génériques, event bus ou réécriture totale sans contrainte démontrée. Demander un GO CTO entre le plan et l’implémentation.
