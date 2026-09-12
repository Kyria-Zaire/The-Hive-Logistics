---
paths:
  - "apps/api/**/*.py"
  - "packages/backend/**/*.py"
  - "tests/backend/**/*.py"
---

# Backend FastAPI

- Routes minces : transport HTTP seulement. Métier dans les services, persistance derrière des repositories ciblés.
- Pydantic valide toutes les entrées/sorties publiques. Ne jamais exposer directement un modèle ORM.
- SQLAlchemy 2 et migrations Alembic versionnées ; ne pas mélanger accès sync et async dans le même chemin.
- Transactions explicites au niveau du cas d’usage. Aucun commit caché dans un repository générique.
- Requêtes paramétrées uniquement ; contraintes d’intégrité également en base.
- Erreurs publiques stables et non sensibles ; détails techniques dans des logs structurés sans PII/secrets.
- Dates stockées en UTC. Identifiants non prédictibles pour les ressources publiques.
- Endpoint de devis/contact : validation serveur, normalisation, anti-spam, rate limit, idempotence utile et consentement traçable.
- Toute opération externe définit timeout, politique de retry bornée et comportement d’échec.
- OpenAPI doit refléter le contrat réel et les tests couvrent succès, validation, autorisation et panne de dépendance.
