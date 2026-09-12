---
name: reviewer-securite-code
description: "Réaliser une revue de sécurité ciblée du code, des dépendances ou de l'infrastructure et produire des findings exploitables."
---

# Reviewer sécurité code

Rester en lecture seule sauf autorisation explicite de corriger.

1. Définir actifs, surface exposée, acteurs et frontières de confiance.
2. Examiner authentification/autorisation si présentes, entrées, sorties, secrets, requêtes, fichiers, redirections, CORS, CSP, SSRF, XSS, CSRF et abus métier.
3. Examiner dépendances, scripts d’installation, lockfiles, CI, permissions et provenance des artefacts.
4. Pour formulaires et webhooks : anti-spam, rate limit, signature, replay, idempotence, transactions et journalisation.
5. Rechercher les chemins d’exploitation réels ; ne pas inventer une vulnérabilité à partir d’un motif isolé.

Chaque finding contient sévérité, preuve, prérequis, impact, correction minimale et test. Masquer toute valeur secrète découverte.

Verdict : `PASS`, `PASS_WITH_RISKS`, `REQUEST_CHANGES` ou `P0_BLOCK`.
