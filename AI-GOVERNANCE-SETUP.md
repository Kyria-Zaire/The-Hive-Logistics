# Installation et vérification

Version du pack : `1.0.2` (profil **sans hooks runtime**).

1. Extraire le contenu de ce pack à la racine du projet `logistics`, en fusionnant `.claude` et `.cursor` sans supprimer les skills tiers existants.
2. Vérifier qu’aucun fichier existant n’a été écrasé sans revue.
3. Ouvrir le dossier comme workspace de confiance après inspection de :
   - `.claude/settings.json` (`permissions.ask` et `permissions.deny`, **sans** section `hooks` active) ;
   - `.cursor/rules/` et `.claude/skills/` ;
   - absence de `.cursor/hooks.json` actif (les fichiers `hooks.json.disabled` / `hooks.disabled.json` sont des sauvegardes historiques v1.0.1, non obligatoires).
4. Dans Claude Code, lancer `/context` et `/skills` ; ne pas activer de hooks Claude Code pour ce pack.
5. Dans Cursor, ouvrir Customize → Rules/Skills et vérifier la découverte du pack (pas de hooks runtime requis).
6. Exécuter : `python .claude/hooks/validate_governance.py` (doit annoncer la version `1.0.2` et `GOVERNANCE_VALIDATION = PASS`).
7. Exécuter : `python -m unittest discover -s .claude/hooks/tests -v`.
8. Initialiser Git seulement après validation du contenu et créer le premier commit sous contrôle du CTO.

## Profil de sécurité IDE (1.0.2)

- Règles projet et skills spécialisés.
- Permissions natives Claude (`ask` / `deny`).
- Validation humaine des opérations sensibles.
- Contrôles Git et CI, scans secrets/dépendances/code.
- Séparation DEV / RECETTE / PREPROD / PROD ; pas d’identifiants PROD en local.

`agent_guard.py` reste disponible à titre **optionnel ou expérimental** ; il n’est pas une frontière de sécurité obligatoire.

## Modèle d’environnements retenu

- DEV : application et PostgreSQL locaux, données jetables/synthétiques.
- RECETTE : première base hébergée isolée, tests métier et acceptation.
- PREPROD : deuxième base hébergée isolée, configuration proche de PROD.
- PROD : troisième base hébergée isolée, vraies données et accès restreints.

Cela correspond à trois bases distantes plus une base DEV locale. Il n’y a jamais de rabattage brut de PROD. Les migrations sont identiques ; les jeux de données sont synthétiques, anonymisés ou propres à chaque environnement.

## Fonctionnalités différées

Magic link, OTP, OAuth Google, cartes de test, paiements à 0 €, 3-D Secure et webhooks de paiement sont des exigences conditionnelles. Elles seront activées seulement si le produit ajoute comptes ou paiements, après choix du fournisseur, threat model et ADR. Elles ne doivent pas apparaître dans la V1 actuelle.

## Sauvegardes

- Frontend/backend : dépôt Git distant protégé, tags de release et artefacts immuables.
- PostgreSQL PROD : sauvegardes chiffrées, rétention documentée, restauration testée.
- Médias : stockage objet versionné si un stockage externe est introduit.
- Variables et secrets : gestionnaire de secrets, jamais Git ni sauvegarde SQL applicative.
