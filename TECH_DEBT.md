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

---

# Dette introduite par la V3 immersive (tickets 16 à 27)

| # | Sujet | Gravité |
|---|---|---|
| ~~20~~ | ~~Vidéos du hero non créditées~~ | **Résolue au ticket 28-BIS** |
| ~~21~~ | ~~Débordement horizontal de 17 px sur `/contact` à 320 px~~ | **Résolue au ticket 28-BIS** |
| 22 | L'accordéon Services anime `flex-grow` | Faible — performance |
| 23 | Liste blanche `images.qualities` à maintenir | Faible — piège silencieux |
| 24 | Voitures de la section Méthode en PNG non optimisé | Faible |
| 25 | Photo Engagements : 966 Ko en desktop | Moyenne — performance |
| 26 | Distances d'animation figées sur un changement de hauteur seul | Faible |
| 27 | Neuf classes CSS orphelines dans `globals.css` | Faible — reportée en V3.1 |

## 20. Vidéos du hero non créditées

`hero-desktop.mp4` (1,61 Mo) et `hero-mobile.mp4` (636 Ko) sont en ligne sans mention de leur source. Aucune occurrence de « Pexels » dans le dépôt, ni dans les mentions légales.

**Résolue au ticket 28-BIS.** Crédit ajouté sous le copyright du pied de page : « Vidéo d'accueil : Pexels (30843746), licence gratuite commerciale. » Le texte vit dans `homeContent.footer.mediaCredit`.

## 21. Débordement horizontal de 17 px sur `/contact` à 320 px

Diagnostiqué par élimination : le conteneur du widget Turnstile. À 320 px la boîte disponible fait 248 px (320 − 40 de conteneur − 32 de carte) pour un widget qui en exige environ 300. Les deux formulaires sont concernés. Absent à 360 px et au-delà depuis le correctif `min-w-0` du ticket 23.

320 px n'est pas une largeur de validation du projet (`frontend.md` liste 1440, 1024, 768 et 390), et le correctif toucherait le rendu d'un contrôle anti-spam qui ne s'affiche pas en environnement de test — d'où le report.

**Résolue au ticket 28-BIS.** `transform: scale(0.8)` sur `.thl-turnstile` sous 360 px, origine à gauche, avec une marge négative qui reprend la hauteur laissée par la transformation. Mesuré à 0 px de débordement de 320 à 390 px. Le widget est réduit, jamais rogné : un captcha amputé de son bord droit ne peut pas être validé.

## 22. L'accordéon Services anime `flex-grow`

Mesuré à 55 i/s desktop et mobile sur la traversée avec survol des trois panneaux, contre 60 ailleurs. Animer une largeur déclenche un calcul de mise en page à chaque image, là où le reste du site n'anime que `transform` et `opacity`.

**Piste :** rendre l'ouverture par `transform: scaleX()` compensé sur le contenu, ou accepter les 55 i/s — c'est fluide à l'œil.

**[MAJ TICKET 34]** La traversée complète de l'accueil en desktop 1440 mesure **42 i/s de médiane** (5 relevés : 37,3 · 41 · 42 · 44,4 · 44,9). Cette dette n'en explique qu'une part : le parcours cumule l'accordéon, le dépliage des Engagements, la voiture épinglée de la Méthode et le comptage des chiffres clés. Le retrait du ScrollReveal de la Vision au TICKET 34 ne l'a pas fait bouger — la mesure d'avant, 43,2 i/s, tombe dans l'étendue d'après. Mobile 390 reste à 60 i/s.

**Piste V3.1 :** profiler le parcours section par section avant de toucher à quoi que ce soit ; l'accordéon est un suspect, pas une cause établie.

## 23. Liste blanche `images.qualities` à maintenir

`next.config.ts` déclare `images: { qualities: [60, 75, 80] }`. Toute valeur absente de cette liste est **silencieusement ramenée à 75** : au ticket 22-TER, un `quality={80}` est resté sans effet jusqu'à ce que la mesure le révèle. Rien dans la sortie du build ne le signale.

**Piste :** ajouter la valeur à la liste en même temps qu'on l'utilise, et vérifier le paramètre `q=` servi plutôt que de supposer.

## 24. Voitures de la section Méthode en PNG non optimisé

`car-method-red.png` (1,53 Mo) et `car-principles-911.png` (1,50 Mo) sont détourées mais restent des PNG bruts. Next les sert en WebP à l'affichage, donc l'impact visiteur est nul ; c'est le dépôt qui s'alourdit de 3 Mo.

**Piste :** les convertir en WebP à la source, comme la dette 18 le prévoit pour les photos.

## 25. Photo Engagements : 966 Ko en desktop

La source est un portrait 3648 × 5472. Avec `sizes="100vw"`, Next sert du 1920 de large, donc **1920 × 2880** — dont `object-cover` n'affiche que 31 % de la hauteur sur un écran 1440 × 900. On télécharge 2880 px de haut pour en montrer 900. Mobile et tablette restent à 124 et 193 Ko.

**Piste :** recadrage paysage dédié au desktop, servi en art direction comme les affiches du hero. Estimation 350 à 450 Ko.

## 26. Distances d'animation figées sur un changement de hauteur seul

Les sections Méthode, Engagements et Vision mesurent leurs distances au montage et se reconstruisent sur un vrai redimensionnement. Le garde ignore un changement de **hauteur seule inférieur à 200 px**, pour ne pas reconstruire à chaque repli de la barre d'adresse mobile. Traîner le bord bas d'une fenêtre desktop sur une courte distance laisse donc des distances légèrement périmées.

**Piste :** distinguer le redimensionnement de fenêtre du repli de barre d'adresse via `visualViewport`, plutôt que par un seuil en pixels.

## 27. Neuf classes CSS orphelines dans `globals.css`

`.thl-chapter-enter`, `.thl-hero-actions`, `.thl-hero-block`, `.thl-hero-content`, `.thl-hero-grid-bg`, `.thl-hero-h1`, `.thl-hero-reveal`, `.thl-hero-serif-accent`, `.thl-hero-title` ne sont référencées nulle part depuis les refontes du hero. Environ 160 lignes sur 834, plus les keyframes `thl-hero-fade` et `thl-chapter-enter` qui ne servaient qu'à elles.

**Arbitrage du ticket 28-BIS : reportée en V3.1.** Aucun gain de performance à la clé, et toucher 160 lignes de feuille de style la veille d'une mise en production ne se justifie pas. Suppression en un seul passage une fois la V3 en ligne et stable.

## 28. Pas de Content-Security-Policy en production

Le ticket 31-BIS a posé `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` et `Cross-Origin-Opener-Policy` dans `next.config.ts`. La CSP en a été délibérément exclue : la poser correctement demande de composer avec les scripts inline de Next (JSON-LD, bootstrap du runtime), GSAP et l'iframe Turnstile — donc un `nonce` propagé depuis un middleware, ou `strict-dynamic`, et une recette complète sur les six routes. Fait à la hâte, on obtient soit une CSP en `unsafe-inline` qui ne protège de rien, soit un site cassé en production.

**Sévérité : Medium.** Défense en profondeur absente ; aucune vulnérabilité active connue — l'audit SAST du ticket 31 n'a relevé aucun XSS ni injection sur 483 règles.

**Piste :** ticket V3.1 dédié. Commencer en `Content-Security-Policy-Report-Only` pour mesurer les violations réelles avant de bloquer.

## 29. HSTS sans `includeSubDomains`

La production renvoie `Strict-Transport-Security: max-age=63072000`, sans `includeSubDomains` ni `preload`. L'en-tête est injecté par Vercel, pas par notre code : il n'est donc **pas modifiable depuis `next.config.ts`** — il faut passer par la configuration du projet Vercel.

**Sévérité : Low.** `api.thehivelogistics.fr` est aujourd'hui servi par Railway en HTTPS ; l'absence de `includeSubDomains` laisse théoriquement un sous-domaine futur accessible en clair au premier contact.

**Piste :** activer `includeSubDomains` côté Vercel, puis `preload` seulement après avoir vérifié que **tous** les sous-domaines, `api.` compris, sont en HTTPS — le preload est difficile à révoquer.

## 30. Semgrep installé dans le Python global — résolu

L'audit du ticket 31 a installé Semgrep via `pip` dans le Python 3.13 global faute de `pipx`, ce qui a modifié des paquets partagés. Semgrep a été désinstallé au ticket 31-BIS, mais `pip uninstall` ne retire pas les dépendances transitives : `click` 8.4.2, `jsonschema` 4.25.1 et `opentelemetry-semantic-conventions` 0.58b0 restent en place et violent les contraintes de `gtts`, `openapi-spec-validator` et `mistralai`. Le projet n'est pas affecté — `apps/api` a son propre `.venv` et la CI installe Semgrep sur un runner jetable.

**Sévérité : Low**, hors dépôt.

**Piste :** à l'avenir `pipx run semgrep` plutôt que `pip install`. Commandes de remise en état de l'environnement global dans le rapport du ticket 31-BIS.

## 31. `opentelemetry-semantic-conventions` bloqué en 0.58b0 — environnement global

Suite de la dette 30. Le nettoyage du ticket 31-TER a restauré `click` en 8.1.8 et `jsonschema` en 4.26.0, ce qui rétablit `gtts` et `openapi-spec-validator` (import et points d'entrée vérifiés). `opentelemetry-semantic-conventions` reste en 0.58b0 et viole la contrainte de `mistralai` (`>=0.60b1`).

C'est volontaire : `opentelemetry-sdk`, `-instrumentation` et `-instrumentation-requests` l'épinglent à `==0.58b0`. Ces trois paquets sont arrivés avec Semgrep, mais rien ne dit lesquels préexistaient — monter la version casserait les trois, les retirer casserait peut-être autre chose.

**Sévérité : Low**, hors dépôt. Aucun impact projet : `apps/api` a son propre `.venv`, la CI installe Semgrep par `uv tool run` sur un runner jetable.

**Piste :** ne rien toucher sans un inventaire de l'état antérieur. À défaut, recréer l'environnement Python global depuis un `requirements` reconstruit.

## 32. Conflits `httpx` préexistants — environnement global

`pip check` signale `postgrest`, `storage3`, `supabase` et `supafunc` qui demandent `httpx<0.28` alors que 0.28.1 est installé. **Antérieurs à Semgrep et sans rapport avec ce projet** : Semgrep ne dépend pas de `httpx` (seulement de `httpx-sse`). Documenté ici pour qu'on ne les impute pas à tort aux tickets 31 / 31-BIS / 31-TER lors d'un prochain `pip check`.

**Sévérité : Low**, hors dépôt, hors périmètre THE HIVE LOGISTICS.

## 33. « RÉSERVATION » rognée de 9 px à 320 px dans la timeline Méthode

La première étape de la section Méthode (`h3` en `text-[20px] font-medium uppercase tracking-[0.12em]`) mesure 162 px de texte dans une colonne de 153 px. Le conteneur `.thl-method-steps` étant en `overflow-x: hidden`, la fin du mot est coupée sur un écran de 320 px.

**Préexistant, et non introduit par le TICKET 33** : mesuré à l'identique sur la production servant le code antérieur (débord de 9 px des deux côtés, `font-size` 20 px et `letter-spacing` 2,4 px inchangés). Les titres de section passés en capitales à ce ticket n'y sont pour rien — ce `h3` portait déjà son propre `uppercase`.

**Sévérité : Low.** Un seul mot, une seule largeur, texte partiellement lisible ; les trois autres étapes passent.

**Piste V3.1 :** réduire le `tracking` sous 360 px, ou autoriser le retour à la ligne dans la colonne plutôt que de compter sur `overflow-x: hidden`.

## 34. Réserve de 280 px au-dessus d'un dossier Vision ouvert

La fiche d'un dossier est en position absolue, donc hors flux : la grille ne fait pas de place toute seule. Depuis le TICKET 34-QUATER la fiche sort **vers le haut**, et la réserve dépend de la forme de la grille — les deux stratégies simples échouent chacune de leur côté, mesuré sur 20 ouvertures × 5 largeurs :

- réserver sur le **conteneur** ne protège que la première rangée : à 320, 390 et 768 px, les dossiers 1 à 3 recouvraient leur voisin du dessus ;
- réserver sur **tous les éléments** tient partout, mais insère 1120 px de vide sur mobile — 280 px au-dessus de chacun des trois dossiers fermés ;
- réserver sur **l'élément ouvert seul** tient en une colonne, mais dès deux colonnes le dossier ouvert descend seul sous son voisin de rangée.

D'où la règle en place : élément ouvert seul en une colonne, tous les éléments dès 640 px.

La valeur de 280 px est calée sur la plus haute des quatre fiches, mesurée à la largeur la plus étroite. **Une description sensiblement plus longue la ferait déborder à nouveau**, et il y a désormais deux endroits à corriger plutôt qu'un.

**Sévérité : Low**, tant que les quatre textes ne bougent pas.

**Piste :** faire participer la fiche au flux (`grid-template-rows: 0fr → 1fr`) plutôt que de réserver une hauteur en dur — l'animation reste possible, la valeur magique et la distinction par point de rupture disparaissent toutes les deux.
