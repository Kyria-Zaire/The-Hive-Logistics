# Sécurité applicative et supply chain

- Commencer toute surface publique sensible par ses actifs, acteurs, frontières de confiance et scénarios d’abus.
- Refuser par défaut : secrets dans Git, SQL concaténé, HTML brut non assaini, `eval`, désérialisation non sûre, redirection non allowlistée et CORS wildcard avec credentials.
- Configurer en production CSP stricte, HSTS, `nosniff`, politique de referrer, permissions policy et cookies sécurisés si des cookies apparaissent.
- Protéger les formulaires par honeypot, rate limiting serveur et Turnstile vérifié côté serveur ; prévoir un comportement accessible en cas d’échec.
- Pinner les dépendances et lockfiles. Examiner nom, provenance, mainteneur, scripts d’installation et vulnérabilités avant ajout.
- Pinner les actions CI tierces par SHA complet. Permissions CI en lecture seule par défaut ; OIDC plutôt que secrets longue durée.
- Interdire les secrets ou données clients dans logs, traces, analytics, fixtures, captures et rapports d’agent.
- Aucun webhook ne fait confiance au payload avant vérification cryptographique sur le corps brut. Déduplication et machine d’état empêchent replay et transitions invalides.
- Aucun mécanisme auth/paiement n’est implémenté hors ticket dédié. S’il est ajouté : sandbox réelle, clés isolées, 3-D Secure testé, magic link/OTP à usage unique et OAuth avec `state`, PKCE et URI strictes.
- Une revue IA ne remplace jamais SAST, audit de dépendances, secret scanning, DAST ciblé et revue humaine.
