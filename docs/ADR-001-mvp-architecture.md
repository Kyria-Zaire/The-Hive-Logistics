# ADR-001 — Architecture MVP vitrine

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-15 |
| Périmètre | MVP vitrine THE HIVE LOGISTICS |

## Contexte

Le dépôt est un monorepo pnpm composé d'une application Next.js et d'une API FastAPI. Le backend possède déjà les contrats OpenAPI, la validation métier, l'idempotence, la protection Turnstile, la persistance PostgreSQL et le worker de notifications.

Le MVP doit ajouter une façade d'intégration côté web sans déplacer la responsabilité métier vers Next.js. Le choix de version Next.js doit également rester compatible avec le socle existant et ses tests.

## Décisions

### 1. Conserver Next.js 16.3.5

Next.js `16.3.5` est conservé. Aucun downgrade vers Next.js 15 ne sera réalisé pour ce MVP.

**Raison :** le dépôt, le lockfile, la configuration App Router et les validations existantes sont déjà alignés sur Next.js 16. Un downgrade introduirait un risque de régression sans valeur métier pour le MVP.

### 2. FastAPI est l'autorité métier

Le flux public est :

```text
Formulaire -> Server Action -> POST /api/v1/{endpoint} -> FastAPI
```

Les Server Actions Next.js sont des façades minces. Elles extraient les champs du `FormData`, vérifient uniquement leur présence, leur type et l'état vide du honeypot, puis délèguent au client HTTP typé.

La validation métier, les règles de domaine, l'idempotence, Turnstile, le rate limiting, la persistance et les notifications restent exclusivement dans FastAPI.

Il est interdit de dupliquer ces responsabilités dans Next.js.

### 3. Resend est géré par le worker backend

Resend n'est jamais appelé depuis Next.js. Les notifications sont produites et envoyées par le worker backend selon le pipeline transactionnel existant.

Conséquences : aucune clé Resend ne doit apparaître dans `apps/web`, dans le navigateur ou dans les variables `NEXT_PUBLIC_*`.

### 4. Mapbox est hors scope V1

Mapbox GL est retiré du périmètre du MVP V1. Aucun package, token, composant cartographique ou appel Mapbox ne sera ajouté dans ce ticket ou dans le MVP défini ci-dessous.

### 5. Scope MVP figé

Le MVP comprend uniquement :

- accueil ;
- formulaire de contact ;
- formulaire de demande de devis ;
- mentions légales ;
- politique de confidentialité ;
- SEO technique de base ;
- page 404 personnalisée.

Sont explicitement hors scope : blog, authentification, réservation, paiement et Mapbox.

## Conséquences

### Positives

- Une seule autorité pour les règles métier et la sécurité des leads.
- Contrat HTTP typé et aligné sur `contracts/openapi/openapi.yaml`.
- Aucun secret métier dans le bundle web.
- Les notifications restent durables et découplées du cycle HTTP public.
- Le périmètre est suffisamment borné pour le MVP.

### Négatives

- Les Server Actions dépendent de la disponibilité de l'API FastAPI.
- L'URL API doit être configurée par environnement via `NEXT_PUBLIC_API_URL`.
- Les erreurs d'intégration doivent être présentées sans exposer de détails techniques.
- Le formulaire ne peut pas confirmer une demande tant que FastAPI n'a pas répondu avec succès.

## Validation

- Le client web utilise exclusivement `fetch` et les formes du contrat OpenAPI.
- Les actions ne possèdent aucun accès base de données, appel Resend ou règle métier.
- Les validations `lint` et `typecheck` doivent réussir avant revue CTO.