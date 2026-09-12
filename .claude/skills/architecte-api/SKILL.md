---
name: architecte-api
description: "Concevoir ou faire évoluer une API FastAPI, ses contrats, données, menaces et migrations avant implémentation."
---

# Architecte API

Lire `AGENTS.md`, `.claude/rules/backend.md`, `.claude/rules/security.md` et, si nécessaire, `.claude/rules/environments-data.md`.

Produire d’abord :

- cas d’usage et non-objectifs ;
- acteurs, frontières de confiance et scénarios d’abus ;
- contrat HTTP, schémas d’entrée/sortie et erreurs ;
- modèle de données, contraintes et ownership transactionnel ;
- idempotence, concurrence, timeouts et panne de dépendances ;
- stratégie de migration et compatibilité ;
- tests d’acceptation et observabilité sans PII.

Favoriser un monolithe modulaire. Ne proposer microservice, event bus, cache ou abstraction générique que si une contrainte mesurée l’exige.

Ne pas implémenter avant validation du plan quand le changement touche schéma, sécurité, intégration externe ou contrat public.
