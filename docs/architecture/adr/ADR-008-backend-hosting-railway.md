# ADR-008 — Hébergement backend PROD (Railway)

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-17 |
| Ticket | BACKEND-01 / **BACKEND-01 v2** |

## Contexte

ADR-007 laissait le choix d’hébergeur ouvert (TBD-007) et prévoyait « addendum ou ADR-008 » une fois tranché. Le front est en PROD sur Vercel depuis le 2026-09-17 ; l’API, le worker et PostgreSQL restaient à héberger. TBD-009 (email) et TBD-021 (domaine canonique) étaient également ouverts.

## Décision

- **Hébergeur backend : Railway** (plan Pro, requis car le SMTP sortant est désactivé sous Free, Trial et Hobby), workspace personnel `kyria-zaire`, projet `prolific-integrity`.
- **Base : PostgreSQL managé Railway**, atteint par le réseau privé du projet. `DATABASE_URL` est composée au schéma **`postgresql+psycopg://`**, exigé par `create_async_engine` ; la variable `DATABASE_URL` fournie par Railway (`postgresql://`) ne convient pas telle quelle.
- **Email : Resend en SMTP** (`smtp.resend.com:587`, STARTTLS), expéditeur `noreply@thehivelogistics.fr`, destinataire `contact@thehivelogistics.fr`. L’adaptateur SMTP existant est conservé ; l’API HTTP Resend reste l’option de repli prévue par ADR-007.
- **Artefact : image Docker unique** (`apps/api/Dockerfile`) pour l’API et le worker, base épinglée par digest, dépendances installées depuis `uv.lock` (`uv sync --frozen --no-dev`), exécution sous l’utilisateur non root `app` (uid 1000).
- **Deux services** partagent cette image : `api` (Uvicorn, healthcheck `GET /api/v1/health/ready`) et `worker` (`python -m thl_api.notifications.worker`). Le worker ne reçoit **ni** secret Turnstile **ni** secret HMAC : moindre privilège.
- **Migrations** : `alembic upgrade head` en commande de pré-déploiement, dans le conteneur. Aucun identifiant PROD n’atterrit sur un poste local, conformément à ENVIRONMENTS.md.
- **Déploiement manuel** par `railway up`, sans déclencheur GitHub : ENVIRONMENTS.md impose une promotion PROD manuelle et approuvée.
- **Domaine API : `api.thehivelogistics.fr`** (CNAME chez IONOS vers la cible Railway).
- **TBD levés** : TBD-007 (hébergement), TBD-009 (email), TBD-021 (domaine canonique `thehivelogistics.fr`).

## Dérogations assumées

| Règle | Dérogation | Raison et conséquence |
|---|---|---|
| ENVIRONMENTS.md « Same-origin PROD : ingress `/api/v1/*` → FastAPI » | API sur le sous-domaine `api.thehivelogistics.fr` | Front et backend sont chez deux fournisseurs. Les formulaires passent par des Server Actions Vercel, donc d’un serveur à l’autre : **pas de CORS navigateur**, mais **l’IP du visiteur n’est pas transmise**. |
| ADR-004 étape 5 + SEC-016 (rate limit par IP) | Seuils hauts au démarrage | Le compteur est de fait partagé par tous les visiteurs : un seuil bas bloquerait le site entier. Turnstile reste la barrière principale. Ticket V1.1 pour transmettre l’IP du visiteur de façon fiable. |
| ADR-005 (quatre bases isolées) | Un seul environnement PROD | RECETTE reportée à la V1.1. Aucune donnée de PROD ne descend vers un environnement inférieur ; DEV reste sur base locale jetable. |

## Alternatives

| Alternative | Rejet |
|---|---|
| Reverse proxy Vercel `/api/v1/*` vers Railway | Conserverait le same-origin, mais ajoute un saut réseau et ne restitue pas l’IP du visiteur sans travail supplémentaire ; à réévaluer en V1.1 |
| Backend chez Vercel (fonctions) | FastAPI durable, worker et verrous consultatifs PostgreSQL s’y prêtent mal |
| Resend via API HTTP | Demande un adaptateur de code ; inutile puisque le plan Pro autorise le SMTP |

## Réévaluation

- Transmission fiable de l’IP du visiteur, puis abaissement des seuils de rate limit.
- `www.thehivelogistics.fr` sert encore le site sans redirection : un jeton Turnstile émis sur `www` est rejeté (hostname attendu `thehivelogistics.fr`). Redirection à mettre en place côté Vercel.
- Sauvegardes et PITR PostgreSQL, restauration testée : gate PROD ENVIRONMENTS.md, à confirmer sur Railway.
- Ouverture d’un environnement RECETTE (ADR-005) en V1.1.
