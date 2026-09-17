# Démo locale V1 — THE HIVE LOGISTICS

> Usage : démonstration **en partage d'écran uniquement**. Aucune exposition publique : tous les services écoutent sur `127.0.0.1`, sans tunnel.
> État vérifié le 17/09/2026.

## État actuel

| Élément | État |
|---|---|
| Navigation du site (build de production) | Démontrable |
| API `/api/v1/health/live` et `/api/v1/health/ready` | 200 |
| Correctifs formulaires (champs facultatifs vides, action Turnstile) | Appliqués et testés |
| Soumission Contact et Devis avec le widget Turnstile DEV réel | **À faire manuellement** dans un navigateur habituel (voir « Démo manuelle ») |
| Vidéo `docs/demo/v1-mvp-demo.*` | Pas encore enregistrée |

## Architecture locale

| Service | Adresse | Lancement |
|---|---|---|
| Site (Next.js, build prod) | http://127.0.0.1:3100 | `next start` |
| API FastAPI | http://127.0.0.1:8001 | `uvicorn` (hôte) |
| Worker de notification | — | processus Python (hôte) |
| PostgreSQL DEV | 127.0.0.1:5433 | conteneur `thl-postgres-dev` |
| Mailpit (sink SMTP + UI) | SMTP 127.0.0.1:1025, UI http://127.0.0.1:8025 | conteneur `thl-mailpit-dev` |

Le port 8000 n'est pas utilisé : il est occupé par un autre projet sur ce poste.

## Configuration locale (fichiers ignorés par Git, ne jamais commiter)

**`apps/api/.env`** : `THL_ENV=dev`, `API_HOST=127.0.0.1`, `API_PORT=8001`, `DATABASE_URL` vers `127.0.0.1:5433/thl_dev`, trois secrets HMAC aléatoires, SMTP `127.0.0.1:1025` sans TLS (adresses `@example.com`), et :

- `TURNSTILE_SECRET_KEY` = clé secrète du **widget Turnstile DEV** (hostnames `127.0.0.1` et `localhost`) ;
- `TURNSTILE_EXPECTED_HOSTNAME=127.0.0.1`.

**`apps/web/.env.local`** : `NEXT_PUBLIC_TURNSTILE_SITE_KEY` = clé de site du widget DEV, `NEXT_PUBLIC_SITE_URL=https://thehivelogistics.fr`.

> Le widget PROD (`thehivelogistics.fr`, `www`) est distinct : ses clés ne doivent jamais se trouver sur un poste de développement.

## Relancer la stack

Depuis la racine du dépôt, en Git Bash, un terminal par processus long.

```bash
# 1. Conteneurs
cd infra/compose && docker compose -f docker-compose.dev.yml up -d --no-deps postgres mailpit && cd ../..

# 2. Migrations
uv run --directory apps/api alembic upgrade head

# 3. API (sous Windows, --reload est nécessaire : sinon psycopg async échoue et /health/ready répond 503)
uv run --directory apps/api uvicorn thl_api.main:app --host 127.0.0.1 --port 8001 --reload

# 4. Worker (sous Windows ; sous Linux ou macOS : pnpm api:worker)
uv run --directory apps/api python -c "import asyncio; asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()); from thl_api.notifications.worker import main; main([])"

# 5. Site en build de production (-H 127.0.0.1 : sinon next start écoute sur toutes les interfaces)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001 pnpm --config.engine-strict=false --filter web build
pnpm --config.engine-strict=false --filter web exec next start -p 3100 -H 127.0.0.1
```

Vérification : `curl http://127.0.0.1:8001/api/v1/health/ready` doit répondre `{"status":"ok","checks":{"database":"ok"}}`.

## Démo manuelle (navigateur habituel)

> ⚠️ Le widget Turnstile DEV **refuse les navigateurs pilotés par un outil d'automatisation** (Playwright), même si un humain coche la case : c'est son rôle anti-robots. La démo se fait donc dans Chrome ou Edge, sans automatisation.

Enregistrement vidéo : **Win + Alt + R** (Xbox Game Bar) pour démarrer et arrêter ; le fichier arrive dans `Vidéos\Captures`.

1. http://127.0.0.1:3100/ : défilement de l'accueil.
2. Vue mobile : fenêtre réduite en largeur, ouverture du menu.
3. `/services`, puis 4. `/a-propos`.
5. `/contact`, formulaire **Contact** : Prénom `Démo`, Nom `Client`, Email `demo+manuel-contact@example.com`, Sujet *Information*, Message `Message de démonstration, données fictives.`, case confidentialité, **case Turnstile**, **Envoyer le message**. Attendu : « Votre message a bien été transmis. »
6. Formulaire **Devis** : Prénom `Démo`, Nom `Client`, Email `demo+manuel-devis@example.com`, Téléphone `+33 6 00 00 00 00`, Service *Convoyage premium*, Départ `Paris` / `75008`, Arrivée `Reims` / `51100`, Période `Semaine du 15 octobre`, Catégorie *Premium / sportive*, Marque `Marque démo`, Modèle `Modèle démo`, Roulant *Oui*, case confidentialité, **case Turnstile**, **Envoyer la demande**. Attendu : « Votre demande a bien été transmise. »
7. `/mentions-legales`, puis 8. http://127.0.0.1:3100/page-inexistante-demo (404).

## Vérifier la démo côté serveur

```bash
# Leads de démo créés
docker exec thl-postgres-dev psql -U thl_dev -d thl_dev -c "select email, lead_type, public_reference, created_at from leads where email like 'demo+%@example.com' order by created_at;"

# Notifications envoyées au sink
docker exec thl-postgres-dev psql -U thl_dev -d thl_dev -c "select j.status, l.email from notification_jobs j join leads l on l.id = j.lead_id where l.email like 'demo+%@example.com';"

# Emails reçus dans Mailpit (ou UI : http://127.0.0.1:8025)
curl "http://127.0.0.1:8025/api/v1/search?query=demo%2Bmanuel"
```

## Ce qui est démontré

- Parcours des pages : `/`, `/services`, `/a-propos`, `/contact`, `/mentions-legales`, `/politique-de-confidentialite`, page 404.
- Rendu desktop et mobile (menu mobile).
- Coordonnées de l'éditeur (footer, `/contact`, mentions légales) et JSON-LD de l'organisation.
- Avec la démo manuelle : envoi Contact et Devis → API → PostgreSQL → worker → email dans Mailpit.

## Ce qui n'est PAS démontré

- **Backend hébergé** : l'API et la base ne tournent qu'en local. Hébergeur non décidé (TBD-007).
- Préproduction et production ; déploiement Vercel.
- Envoi d'emails à de vrais destinataires (DEV : sink Mailpit uniquement).
- Test E2E automatisé avec le vrai widget : impossible par conception (voir l'avertissement Turnstile). Le test `apps/web/e2e/contact-submit.spec.ts` (`@e2e-real`) exige une décision sur la stratégie de test.
- Paiement, comptes clients, réservation automatisée (hors périmètre V1).

## Avertissements

- **Pages légales incomplètes** : 11 sections gardent un placeholder `[À COMPLÉTER : …]` (4 dans les mentions légales, 7 dans la politique de confidentialité), en attente des textes de Jores et de son conseil. Ne pas les présenter comme définitives.
- **Conservation « 3 ans »** : annoncée dans la politique de confidentialité, mais aucune purge automatique n'est encore implémentée.
- **Données** : environnement DEV, **données fictives uniquement**.

## Purge des données de démo

Les tables liées référencent `leads` avec `ON DELETE RESTRICT` : suppression des enfants puis des leads, dans une transaction. **DEV uniquement.**

```bash
docker exec -i thl-postgres-dev psql -U thl_dev -d thl_dev <<'SQL'
BEGIN;
CREATE TEMP TABLE demo_leads AS SELECT id FROM leads WHERE email LIKE 'demo+%@example.com';
DELETE FROM notification_jobs       WHERE lead_id IN (SELECT id FROM demo_leads);
DELETE FROM idempotency_records     WHERE lead_id IN (SELECT id FROM demo_leads);
DELETE FROM contact_message_details WHERE lead_id IN (SELECT id FROM demo_leads);
DELETE FROM quote_request_details   WHERE lead_id IN (SELECT id FROM demo_leads);
DELETE FROM leads                   WHERE id IN (SELECT id FROM demo_leads);
SELECT count(*) AS restants FROM leads WHERE email LIKE 'demo+%@example.com';
COMMIT;
SQL
```

Emails de démo dans Mailpit : bouton « Delete all » de l'interface (sink DEV).

## Arrêt

- API, worker et site : `Ctrl+C` dans leurs terminaux.
- Mailpit : `cd infra/compose && docker compose -f docker-compose.dev.yml stop mailpit`
