# THE HIVE LOGISTICS — Instructions communes aux agents

## Autorité et rôles

- Kyria est le développeur full-stack et le propriétaire opérationnel du dépôt.
- Le CTO humain/assistant définit le périmètre, l’architecture et les critères d’acceptation.
- L’agent IA exécute le ticket courant. Il ne redéfinit pas le produit et n’élargit pas le périmètre.
- En cas de conflit : ticket courant approuvé > ADR et cahier des charges versionnés > ce fichier > conventions déduites du code.
- Signaler tout conflit avant d’écrire du code.

## Produit V1

THE HIVE LOGISTICS est un site vitrine français premium pour le convoyage automobile, la coordination de flotte, la logistique automobile sur mesure et la préparation/remise de véhicules.

Hors périmètre V1 : immobilier, chauffeur privé, location automobile, comptes clients, authentification, réservation automatisée, calendrier, tarification automatique, paiement, back-office, CMS, e-commerce et multilingue.

La V1 utilise des photographies statiques. Aucun média Higgsfield ni arrière-plan vidéo généré. L’immersion vient de la composition, du scroll et de micro-interactions sobres.

## Stack arrêtée

- Frontend : Next.js avec TypeScript strict.
- Backend : Python avec FastAPI.
- Données : PostgreSQL et migrations versionnées.
- Architecture : monolithe modulaire, contrats explicites, dépendances limitées.
- Les versions exactes et outils complémentaires sont fixés par ADR avant scaffold.

Ne pas ajouter un framework, une base, un service SaaS ou une dépendance sans justification et validation du CTO.

## Méthode obligatoire

1. Lire le ticket, les fichiers concernés, les ADR et les tests existants.
2. Reformuler le périmètre, les hypothèses et les risques.
3. Proposer un plan court avant toute modification non triviale.
4. Modifier uniquement les fichiers nécessaires.
5. Ajouter ou adapter les tests qui prouvent le comportement.
6. Exécuter lint, typage, tests et vérification réelle adaptée.
7. Examiner le diff final et rechercher secrets, régressions et code mort.
8. Produire un rapport : fichiers, tests, avertissements, risques et reste à faire.

Ne jamais annoncer « terminé » sur la seule base d’une lecture du code. Une preuve exécutable ou une vérification réelle est requise.

## Discipline de changement

- Un ticket correspond à un objectif cohérent et borné.
- Préférer le plus petit diff qui résout entièrement le ticket.
- Ne pas réécrire un module sain pour satisfaire une préférence stylistique.
- Ne pas laisser de TODO, mocks permanents, données fictives en production ou exceptions silencieuses.
- Ne pas modifier les fichiers générés, lockfiles ou migrations hors nécessité démontrée.
- Ne jamais commit, push, merge, déployer ou muter une infrastructure sans autorisation explicite.
- Ne jamais contourner un contrôle de sécurité ou désactiver un test pour obtenir du vert.
- Ne pas utiliser `--dangerously-skip-permissions` ni reformuler une commande pour esquiver une permission native ou un garde-fou CI.

## Gouvernance agent et sécurité IDE (1.0.2)

Le pack **n’utilise pas** de hooks Python runtime `failClosed` dans Cursor ou Claude Code. Le profil retenu :

- règles projet (`.cursor/rules/`, `.claude/rules/`) ;
- skills spécialisés (`.claude/skills/`) ;
- permissions natives Claude (`.claude/settings.json` : `permissions.ask`, `permissions.deny`) ;
- validation humaine des opérations sensibles ;
- contrôles Git et CI ;
- scans de secrets, de dépendances et de code ;
- séparation DEV / RECETTE / PREPROD / PROD ;
- absence d’identifiants PROD dans les environnements locaux.

Le script `.claude/hooks/agent_guard.py` et les sauvegardes `.cursor/hooks*.disabled*` restent **optionnels ou historiques** ; ils ne constituent pas une frontière de sécurité obligatoire.

## Sécurité minimale non négociable

- Toute entrée externe est non fiable et validée à la frontière.
- Les secrets restent hors du dépôt, du navigateur, des logs et des réponses d’erreur.
- Appliquer moindre privilège, séparation des environnements et rotation des secrets.
- Interdire les redirections ouvertes, l’exécution de contenu utilisateur et la construction de requêtes SQL par concaténation.
- Protéger les formulaires publics par validation serveur, honeypot, limitation de débit et Cloudflare Turnstile quand l’intégration est décidée.
- Les webhooks doivent vérifier la signature sur le corps brut, tolérer les doublons, journaliser l’identifiant d’événement et être transactionnels. Aucun webhook ne supprime une donnée métier par défaut.
- Une fonctionnalité d’authentification ou de paiement exige un ticket, un threat model et un environnement sandbox dédiés. Elle n’existe pas dans la V1.
- Les mécanismes de sécurité sont testés et automatisés ; une règle IA seule n’est jamais une preuve de sécurité.

## Environnements et données

- Environnements logiques : DEV local, RECETTE, PREPROD et PROD.
- DEV utilise une base locale jetable. RECETTE, PREPROD et PROD utilisent des bases et identifiants isolés.
- Le schéma est aligné par les mêmes migrations ; les données restent différentes.
- Ne jamais copier des données personnelles de PROD vers un environnement inférieur. N’utiliser que des données synthétiques ou irréversiblement anonymisées.
- Toute migration est testée sur une copie synthétique avant PROD et dispose d’une stratégie de restauration documentée.
- Le code est sauvegardé par Git distant et artefacts immuables ; les données par sauvegardes chiffrées avec tests de restauration. Le code n’est pas sauvegardé dans PostgreSQL.

## Frontend et expérience

- Direction : noir profond, blanc, anthracite, accent `#FF5757`, photographie nocturne, espace généreux et mouvement retenu.
- Éviter l’apparence générique « site généré par IA » : pas de gradients gratuits, cartes répétitives, effets décoratifs arbitraires ou texte marketing inventé.
- Responsive réel : desktop, medium et mobile. Aucun simple rétrécissement du desktop.
- Accessibilité clavier, focus visible, HTML sémantique, contrastes, réduction des mouvements et états erreur/chargement/vide obligatoires.
- Performance et lisibilité priment sur les animations.

## Rapport de fin de ticket

Toujours terminer par :

- `VERDICT = PASS | PARTIAL | BLOCKED | FAIL`
- fichiers créés/modifiés/supprimés ;
- commandes et résultats de validation ;
- tests manuels réalisés ;
- risques ou limites ;
- migrations, variables d’environnement ou actions opérateur ;
- `READY_FOR_CTO_REVIEW = YES | NO`.
