# Dette technique — reportée en V1.1

Points connus au moment de la mise en production de la V1 (2026-09-17). Chaque entrée indique le constat, son impact et la piste retenue. Aucun de ces points ne bloque la V1 ; ils sont assumés, pas oubliés.

| # | Sujet | Gravité |
|---|---|---|
| 1 | Rétention « 3 ans » annoncée mais non appliquée | Élevée — engagement public |
| 2 | Rate limit partagé entre visiteurs | Élevée — sécurité |
| 3 | Fin de secret possible dans les logs | Élevée — sécurité |
| 4 | Sauvegarde et restauration PostgreSQL non configurées | Élevée — exploitation |
| 5 | Pas d’environnement RECETTE | Moyenne |
| 6 | Purge des données de test en PROD sans runbook | Moyenne |
| 7 | Parcours E2E non automatisable avec Turnstile réel | Moyenne |
| 8 | Messages de validation en anglais exposés aux visiteurs | Moyenne |
| 9 | Identifiants DOM dupliqués entre les deux formulaires | Faible — accessibilité |
| 10 | Référence publique du lead non affichée | Faible |
| 11 | `.env.template` cite une variable non lue | Faible |
| 12 | Pas de canonique sur la page d’accueil | Faible |
| 13 | Déploiements sans chaîne CI | Faible |
| 14 | Police display : pas de graisse sous 400 | Moyenne |
| 15 | Timeline Processus dupliquée (home et /services) | Moyenne |
| 16 | Contenu narratif /a-propos repris de la home | Moyenne |
| 17 | Token `--font-size-display-s` ajouté mais inutilisé | Faible |
| 18 | Images sources lourdes dans le dépôt | Faible |
| 19 | Cache images Next après remplacement d'un fichier | Faible — exploitation |

---

## 1. Rétention « 3 ans » annoncée mais non appliquée

La politique de confidentialité annonce une conservation de 3 ans à compter du dernier contact. Aucune purge automatique n’existe, ni en DEV ni en PROD : les leads restent indéfiniment.

**Piste :** tâche planifiée de purge des leads dépassant la durée annoncée, enfants d’abord (contraintes `ON DELETE RESTRICT`), avec journalisation du nombre de lignes supprimées et sans PII. Voir PRD TBD-010.

## 2. Rate limit partagé entre visiteurs

Les formulaires passent par des Server Actions Vercel, donc d’un serveur à l’autre : l’API ne voit que l’IP de sortie de Vercel, jamais celle du visiteur. Le compteur de `rate_limit_buckets` est de fait commun à tout le trafic. Les seuils ont été fixés hauts pour éviter de bloquer le site entier ; la protection par IP prévue par ADR-004 (étape 5) et SEC-016 est donc inopérante. Turnstile reste la barrière réelle.

**Piste :** transmettre l’IP du visiteur de la Server Action vers l’API par un en-tête signé, puis déclarer le réseau de confiance via `TRUSTED_PROXY_CIDRS` et rabaisser les seuils. Dérogation consignée dans `docs/architecture/adr/ADR-008-backend-hosting-railway.md`.

## 3. Fin de secret possible dans les logs

Reproduit avec des valeurs fictives : si une variable d’environnement est mal saisie, l’erreur de validation Pydantic affiche `input_value`, c’est-à-dire le dictionnaire des valeurs d’environnement. La fin du dernier secret apparaît alors dans les logs. Concerne `Settings` (`apps/api/src/thl_api/config.py`) et `WorkerSettings` (`apps/api/src/thl_api/notifications/contracts.py`), ce dernier via le `print(exc)` du worker.

**Piste :** `hide_input_in_errors=True` dans les deux `SettingsConfigDict`, plus un test de non-régression vérifiant l’absence de la valeur dans le message d’erreur.

## 4. Sauvegarde et restauration PostgreSQL non configurées

ENVIRONMENTS.md fait de la sauvegarde automatisée et d’une restauration testée une condition de mise en production. Rien n’est configuré côté Railway, et les RPO/RTO restent à définir (PRD §15.3).

**Piste :** activer les sauvegardes Railway, documenter la procédure de restauration et l’exercer une fois sur données synthétiques.

## 5. Pas d’environnement RECETTE

ADR-005 prévoit quatre environnements isolés. La V1 n’a que DEV local et PROD. Toute validation avant mise en ligne se fait donc en local, puis directement en production.

**Piste :** environnement RECETTE Railway avec base isolée et clés Turnstile dédiées.

## 6. Purge des données de test en PROD sans runbook

`docs/demo/README.md` documente la purge en DEV uniquement. La purge des deux leads de test en PROD a été faite à la main depuis le panneau Data de Railway. Le SQL doit toujours être borné par un `WHERE` : un `DELETE FROM leads` non borné effacerait de vrais clients.

**Piste :** runbook PROD dédié, avec requête bornée, comptage avant et après, et transaction explicite.

## 7. Parcours E2E non automatisable avec Turnstile réel

Le widget Turnstile refuse les navigateurs automatisés. Le test `@e2e-real` ne peut donc pas soumettre un formulaire en conditions réelles : la validation de bout en bout repose sur un envoi humain.

**Piste :** clés de test Cloudflare sur un environnement RECETTE, ce qui rendrait le parcours complet automatisable sans affaiblir la PROD.

## 8. Messages de validation en anglais exposés aux visiteurs

Les erreurs de validation Pydantic remontent telles quelles au front et s’affichent en anglais sous les champs, alors que tout le site est en français.

**Piste :** table de correspondance champ/message en français côté API, ou traduction à l’affichage côté front.

## 9. Identifiants DOM dupliqués entre les deux formulaires

`/contact` porte le formulaire contact et le formulaire devis sur la même page, avec des `id` identiques pour certains champs. Les associations `label`/`input` deviennent ambiguës pour les technologies d’assistance.

**Piste :** préfixer les identifiants par formulaire.

## 10. Référence publique du lead non affichée

L’API renvoie une `public_reference` à chaque lead accepté (FR-007), mais l’écran de succès ne l’affiche pas : le visiteur n’a aucun numéro à citer.

**Piste :** afficher la référence dans le message de succès.

## 11. `.env.template` cite une variable non lue

`apps/api/.env.template` mentionne `TRUSTED_PROXY_ENABLED`, que le code ne lit pas ; la variable réellement utilisée est `TRUSTED_PROXY_CIDRS`.

**Piste :** corriger le template lors du chantier n° 2.

## 12. Pas de canonique sur la page d’accueil

Toutes les pages déclarent une URL canonique sauf `/`. Antérieur au sprint de mise en production.

**Piste :** ajouter `alternates.canonical` sur la page d’accueil.

## 13. Déploiements sans chaîne CI

Front et backend sont déployés depuis le poste de développement (`vercel deploy --prod`, `railway up`). La promotion manuelle est voulue par ENVIRONMENTS.md, mais ADR-007 prévoit des artefacts issus d’une CI, et l’auto-deploy GitHub de Railway a dû être écarté faute de coupe-circuit accessible par API.

**Piste :** pipeline CI produisant l’image et déclenchant un déploiement approuvé manuellement.

---

*Entrées 14 à 19 ajoutées le 2026-09-18 à l'issue du sprint design (tickets 02 à 09).*

## 14. Police display : pas de graisse sous 400

Le design des numéros XXL de la section Processus visait une graisse 200-300. Instrument Sans est chargée en 400, 500 et 600, et une sonde de rendu confirme que 200, 300 et 400 produisent exactement la même largeur de glyphe : la famille ne descend pas plus bas et les navigateurs ne synthétisent pas les graisses fines.

**Piste :** évaluer une police display dédiée (Inter Light, ou Instrument Serif en variante light) pour les numéros et grands titres, en pesant le coût réseau d'une famille supplémentaire.

## 15. Timeline Processus dupliquée

Le balisage des 4 étapes existe deux fois : dans `method-chapter-section.tsx` (accueil, avec son `IntersectionObserver`, l'ancre `#methode-hive` et le bloc « Nos principes ») et dans `app/services/page.tsx` (version statique). Les deux doivent rester visuellement synchronisées à la main.

**Piste :** extraire un composant de présentation `ProcessSteps` consommé par les deux surfaces, dans un ticket autorisé à modifier l'accueil.

## 16. Contenu narratif /a-propos repris de la home

La section narrative de `/a-propos` réutilise mot pour mot le bloc `brandStatement` déjà publié sur l'accueil. C'est volontaire — aucun texte n'a été inventé — mais un visiteur qui enchaîne les deux pages lit deux fois la même chose.

**Piste :** demander à Jores un texte propre à `/a-propos` (histoire, origine, positionnement). Rien ne sera rédigé à sa place : gate AC-011, contenus signés Jores.

## 17. Token `--font-size-display-s` ajouté mais inutilisé

`--font-size-display-s` (clamp 28-44 px) et l'utilitaire `.text-display-s` existent depuis le ticket 09 mais ne sont appliqués nulle part. Ils comblent le trou entre `.text-heading` (32 px fixe) et `.text-display-m` (jusqu'à 56 px), qui avait aplati la hiérarchie du bloc « Nos principes ».

**Piste :** les déployer au prochain passage sur les hiérarchies de titres.

## 18. Images sources lourdes dans le dépôt

Les photos pèsent de 1,4 à 4,3 Mo l'unité, soit environ 18 Mo dans `apps/web/public`. Next les recompresse à l'affichage (20 à 60 Ko en WebP), donc aucun impact visiteur, mais le dépôt s'alourdit à chaque ajout et chaque téléversement de build.

**Piste :** passer les sources à `sharp-cli` ou Squoosh avant commit, avec une largeur maximale raisonnée.

## 19. Cache images Next après remplacement d'un fichier

Remplacer une image sans changer son nom laisse servir l'ancienne version : les variantes optimisées restent en cache dans `.next/cache/images`, et un rechargement forcé du navigateur n'y change rien.

**Piste :** renommer le fichier lors d'un remplacement, ce qui change l'URL optimisée ; sinon vider `.next/cache/images` et redémarrer le serveur.
