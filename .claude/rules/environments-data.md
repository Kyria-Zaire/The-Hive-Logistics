---
paths:
  - "infra/**/*"
  - "deploy/**/*"
  - ".github/workflows/**/*"
  - "**/alembic/**/*"
  - "**/migrations/**/*"
  - "**/*docker*"
  - "**/*.sql"
---

# Environnements, migrations et données

- DEV local, RECETTE, PREPROD et PROD sont isolés en réseau, secrets et données.
- Trois bases distantes : RECETTE, PREPROD, PROD. DEV dispose de sa base locale jetable.
- Même historique de migrations dans tous les environnements ; données volontairement différentes.
- Jamais de dump PROD brut hors PROD. Un refresh inférieur passe par anonymisation irréversible documentée, sinon données synthétiques.
- Migration : compatibilité progressive, sauvegarde vérifiée, dry-run, observabilité, fenêtre de déploiement et stratégie de restauration.
- Ne jamais lancer une migration ou commande d’écriture PROD depuis un poste agent sans autorisation humaine explicite.
- PROD exige approbation manuelle, environnement protégé, identité courte durée et séparation build/deploy.
- Sauvegardes DB chiffrées avec RPO/RTO documentés et exercice de restauration périodique.
- Le code est restauré depuis Git et les artefacts de release, jamais depuis PostgreSQL.
