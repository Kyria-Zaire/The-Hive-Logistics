# PRD produit — THE HIVE LOGISTICS

> **PRODUCT_ID** = THL-PRODUCT-001
> **VERSION** = 0.1.4
> **STATUS** = DRAFT_FOR_HUMAN_APPROVAL
> **Document** = `docs/product/THL-PRD.md`
> **Modèle** = [`PRD-TEMPLATE.md`](../../PRD-TEMPLATE.md) (structure canonique, non modifiée)
> **Méthode** = [`METHODE-BMAD.md`](../../METHODE-BMAD.md)

---

## 0. Contrat d’utilisation du document

**Numérotation :** section **0** = contrat documentaire ; sections principales **1 à 28** ; **29 sections numérotées au total** (0 inclus). L’Annexe A est hors numérotation du template.

Ce PRD est la source de vérité du **quoi** et du **pourquoi** pour la V1 vitrine THE HIVE LOGISTICS. Il ne remplace pas les ADR, l’architecture spine ni les `SPEC.md` d’epic.

### Règles pour humains et agents IA

1. Ne pas inventer chiffres, témoignages, partenaires, certifications, zones d’intervention ni médias.
2. Conserver les identifiants stables (`OBJ-`, `CAP-`, `FR-`, `NFR-`, `SEC-`, `DATA-`, `SEO-`, `AC-`, `RISK-`, `TBD-`, `BR-`, `JRN-`).
3. Marquer `[HYPOTHÈSE]`, `[À CONFIRMER]`, `[BLOQUANT]` selon le template.
4. Le PRD n’autorise aucun commit, déploiement PROD ni mutation d’infrastructure.
5. Les maquettes Figma/Bolt de Jores sont des références de départ, pas la source de vérité ni du code.

### Responsabilités humaines et rôle de l’IA

| Rôle | Porteur | Périmètre |
|---|---|---|
| Sponsor métier | **Jores** | Vision contenu, validation publique, arbitrages métier |
| Product Owner | **Jores** | Priorisation, contenu, critères métier |
| Responsable contenu | **Jores** | Textes, médias, coordonnées affichées |
| Tech Lead | **Kyria** | Architecture, sécurité, delivery, gates techniques |
| Assistance IA | **IA** | Analyse, rédaction et exécution **sous contrôle humain** ; jamais responsable, approbateur ni autorité de mise en production |

### Ordre d’autorité

Instruction humaine actuelle → décisions registre → PRD approuvé → architecture/ADR → spec epic → story → conventions implicites.

---

## 1. Contrôle documentaire

| Champ | Valeur |
|---|---|
| Produit | THE HIVE LOGISTICS — site vitrine V1 |
| Référence | THL-PRODUCT-001 |
| Version | 0.1.4 |
| Statut | DRAFT_FOR_HUMAN_APPROVAL |
| Gate architecture API | `READY_FOR_API_ARCHITECTURE = YES` (THL-PRODUCT-002, 2026-09-12) |
| Gate production | `READY_FOR_PRODUCTION = NO` |
| Sponsor métier | Jores |
| Product Owner | Jores |
| Responsable contenu | Jores |
| Tech Lead | Kyria |
| UX/UI Lead | [À CONFIRMER] |
| Security Reviewer | Kyria |
| Date de création | 2026-09-12 |
| Dernière révision | 2026-09-12 |
| Horizon couvert | V1 (vitrine + leads) ; V1.1 / V2+ distingués §19 |
| Documents sources | THL-PRODUCT-001 / 001A / 001B / **002** / **002A** ; `AGENTS.md` ; gouvernance 1.0.2 |

### Historique des versions

| Version | Date | Auteur | Nature du changement | Décision associée |
|---|---|---|---|---|
| 0.1.0 | 2026-09-12 | Agent + Kyria | Première rédaction produit à partir du template | THL-PRODUCT-001 |
| 0.1.1 | 2026-09-12 | Agent + Kyria | Corrections post-revue CTO (rôles, portfolio, leads, Turnstile, vie privée, CWV, TBD/gates) | THL-PRODUCT-001A |
| 0.1.2 | 2026-09-12 | Agent + Kyria | Closeout intégrité Markdown, budgets perf/a11y, DEC/TBD, gates médias | THL-PRODUCT-001B |
| 0.1.3 | 2026-09-12 | Agent + Kyria | Fermeture gates architecture API : champs devis, Contact/Devis, référence publique, catégories véhicules (DEC-005–008) | THL-PRODUCT-002 |
| 0.1.4 | 2026-09-12 | Agent + Kyria | Workflow transactionnel leads, idempotence/Turnstile, référence non-auth, rate limit Contact, traçabilité FR-025, alignement Hero mobile, NFR 19 | THL-PRODUCT-002A |

### Approbations

| Rôle | Nom | Verdict | Date | Réserves |
|---|---|---|---|---|
| Sponsor métier | Jores | EN ATTENTE | — | — |
| Product Owner | Jores | EN ATTENTE | — | — |
| Tech Lead | Kyria | EN ATTENTE | — | — |

---

## 2. Résumé exécutif

### 2.1 Produit en une phrase

Pour les prospects particuliers et professionnels de la mobilité automobile premium, THE HIVE LOGISTICS est un site vitrine français qui présente convoyage, coordination de flotte, logistique et préparation automobile, rassure sur la maîtrise opérationnelle et convertit l’intérêt en demandes de devis ou contacts qualifiés — sans réservation ni paiement en ligne en V1.

### 2.2 Problème à résoudre

Les prospects peinent à comprendre rapidement l’étendue des services, le niveau de professionnalisme et le mode de prise en charge ; l’absence de présence digitale premium limite la génération de leads qualifiés et la crédibilité perçue.

### 2.3 Réponse proposée

Site vitrine Next.js + API FastAPI + PostgreSQL : pages éditoriales, parcours devis structuré, contact, réalisations vérifiables, SEO et conformité de base, sécurité des formulaires publics, design premium noir / anthracite / accent `#FF5757`.

### 2.4 Valeur attendue

- Visiteurs : clarté, confiance, parcours mobile fluide vers une demande humaine.
- Entreprise : leads qualifiés traçables (référence demande), image de marque cohérente.
- Partenaires : canal de prise de contact sans promesse d’investissement public non validée.

### 2.5 Résultat attendu à la fin de la release V1

Site public en français, responsive, **cible de conformité WCAG 2.2 niveau AA** (sans certification revendiquée sans audit), indexable selon SEO défini, capable de recevoir des demandes qualifiées sécurisées avec persistance, référence, notification interne fiable et confirmation utilisateur, sans contenu inventé ni services hors périmètre publiés comme disponibles.

---

## 3. Contexte et preuves

### 3.1 Situation actuelle

Marque en structuration ; reconstruction depuis zéro (pas reprise code maquettes) ; stack et gouvernance déjà validées ; contenus légaux et médias en cours de collecte (TBD).

### 3.2 Opportunité

Formaliser l’offre premium, préparer évolutions futures (location premium, couverture nationale) sans les livrer en V1, et industrialiser la capture de demandes.

### 3.3 Éléments probants

| Référence | Type | Fait établi | Source | Date | Confiance |
|---|---|---|---|---|---|
| EVD-001 | Décision produit | Périmètre V1 vitrine sans auth/paiement/booking | AGENTS.md + ticket | 2026-09-12 | Fort |
| EVD-002 | Décision stack | Next.js TS, FastAPI, PostgreSQL monolithe modulaire | AGENTS.md / PRD template §7.4 | 2026-09-12 | Fort |
| EVD-003 | Brief Sponsor | Positionnement convoyage, flotte, logistique, préparation | THL-PRODUCT-001 | 2026-09-12 | Fort |
| EVD-004 | Validation ciblée | Champs devis, séparation Contact/Devis, catégories véhicules (Jores) ; format référence publique (Kyria) | THL-PRODUCT-002 | 2026-09-12 | Fort |

Validation du 2026-09-12 : arbitrages métier Jores et format référence Kyria pour l’architecture API — **sans** approbation intégrale du PRD ni autorisation PROD.

### 3.4 Contraintes héritées

- Gouvernance 1.0.2, profil sans hooks runtime.
- Photographies statiques V1 ; pas de vidéo obligatoire au lancement.
- Quatre environnements DEV / RECETTE / PREPROD / PROD isolés.
- Prix de développement (300 €) **hors** PRD — relation commerciale prestataire/client.

---

## 4. Vision, principes et positionnement

### 4.1 Vision produit

THE HIVE LOGISTICS devient la référence perçue de la mobilité automobile premium B2B/B2C, avec une base digitale extensible vers location et services nationaux **après** validation métier, juridique et technique.

### 4.2 Promesse principale

**« Nous déplaçons plus que des véhicules. »** — slogan Hero accueil (FR-037).

### 4.3 Principes produit

| ID | Principe | Conséquence concrète |
|---|---|---|
| PP-001 | Prestige sobre | Pas de stats/témoignages inventés ; espace négatif, photo pro |
| PP-002 | Confiance par transparence | Processus de prise en charge expliqué ; pas fausse instantanéité |
| PP-003 | Mobile d’abord | Parcours devis validé sur la matrice responsive §10.3 |
| PP-004 | Sécurité by design | Validation serveur, anti-abus, secrets hors dépôt |
| PP-005 | Vérité contenu | TBD plutôt que placeholder trompeur |

### 4.4 Positionnement

- Segment : convoyage et logistique automobile premium (particuliers exigeants, flottes, partenaires).
- Différenciation : maîtrise, discipline, rapidité, modernité — **à prouver** par processus et réalisations réelles, pas par slogans vides.
- Perception recherchée : prestige, confiance, excellence, professionnalisme.
- À éviter : personal branding Jores non validé ; esthétique « site IA générique » ; copie de marques inspirantes (Ardian, Porsche, etc.) — **inspiration de principes uniquement**.

---

## 5. Utilisateurs et parties prenantes

### 5.1 Segments utilisateurs

| ID | Segment | Besoin principal | Contexte | Priorité |
|---|---|---|---|---|
| USR-001 | Particulier premium | Convoyer un véhicule en confiance | Mobile, urgence modérée | P0 |
| USR-002 | Professionnel flotte | Coordination / logistique multi-véhicules | Desktop + mobile | P0 |
| USR-003 | Visiteur rassurance | Comprendre le processus | SEO, recommandation | P0 |
| USR-004 | Partenaire potentiel | Contacter pour partenariat | Formulaire contact | P1 |
| USR-005 | Équipe interne | Traiter demandes entrantes | Notification, back-office futur V1.1 | P1 |

### 5.2 Persona de référence

**Nom :** Alex (fictif)
**Profil :** Responsable flotte PME
**Objectif :** Qualifier un prestataire pour convoyage récurrent
**Freins :** Peur de l’amateurisme, délais flous
**Confiance :** Processus clair, coordonnées vérifiables, réponse humaine
**Contexte :** Mobile en déplacement

### 5.3 Parties prenantes

| Partie | Responsabilité | Décisions | Consultation |
|---|---|---|---|
| Jores | Sponsor, PO, contenu, validation publique | Textes, médias, coordonnées, arbitrages métier | Hebdo |
| Kyria | Tech Lead, sécurité, delivery | Stack, infra, gates techniques, go-live technique | Continue |
| IA | Assistance | Aucune approbation | Sur demande humaine |

### 5.4 RACI simplifié

| Activité | R | A | C | I |
|---|---|---|---|---|
| Validation métier contenu | Jores | Jores | Kyria | — |
| Architecture & sécurité | Kyria | Kyria | Jores | — |
| Mise en production PROD | Kyria | Jores | — | — |

---

## 6. Objectifs et signaux de succès

### 6.1 Objectifs

| ID | Objectif | Indicateur | Baseline | Cible | Échéance | Mesure |
|---|---|---|---|---|---|---|
| OBJ-001 | Générer des demandes qualifiées | Demandes valides acceptées / mois | 0 | [À CONFIRMER] | M+3 post-lancement | PostgreSQL |
| OBJ-002 | Qualité entonnoir devis | Taux d’erreur formulaire (validation + 5xx) | — | [À CONFIRMER] | PREPROD puis PROD | Logs / tests |
| OBJ-003 | Exploitabilité commerciale | Ratio demandes exploitables / demandes acceptées ; délai de traitement (après règles métier Jores) | — | [À CONFIRMER] | M+1 | Process Jores + DB |
| OBJ-004 | Qualité technique | CWV §11 : lab PREPROD (Lighthouse mobile, médiane ≥3 runs) ; terrain post-lancement si données CrUX/Search Console ou RUM autorisé | — | Seuils §11 | PREPROD / post-lancement | Lighthouse ; CrUX/Search Console ; RUM si TBD-006 |
| OBJ-005 | Conformité contenu | 0 contenu inventé en PROD | — | 0 | Go-live | Audit Jores |

### 6.2 Garde-fous

| ID | Signal | Seuil | Action |
|---|---|---|---|
| GRD-001 | Spam / abus formulaire | > [À CONFIRMER] % soumissions bloquées/jour | Ajuster rate limit, revue Turnstile |
| GRD-002 | Taux échec soumission 5xx (devis/contact public) | ≥ 0,5 % sur fenêtre PREPROD | Bloquer promotion environnement (aligné NFR-REL-002) |
| GRD-003 | Promotion bloquée si a11y parcours critiques non conforme | ≥1 violation **critique** non résolue, ≥1 **sérieuse** non résolue (automatisé), ou blocage clavier | Dérogation écrite approuvée par Kyria uniquement |

### 6.3 Anti-métriques

Volume de code, nombre d’animations, pages créées sans parcours validé, trafic non qualifié seul.

---

## 7. Périmètre

### 7.1 Inclus dans la release V1

| ID | Capacité | Valeur | Priorité |
|---|---|---|---|
| CAP-001 | Accueil `/` + navigation + footer | Compréhension marque et conversion | MUST |
| CAP-002 | Services `/services` (3 prestations) | Éducation offre | MUST |
| CAP-003 | Demande de devis `/demande-de-devis` | Lead qualifié + référence | MUST |
| CAP-004 | À propos `/a-propos` | Confiance, vision mobilité auto | MUST |
| CAP-005 | Réalisations `/realisations` (conditionnel) | Preuves réelles publiées si contenu validé | SHOULD_CONDITIONAL |
| CAP-006 | Contact `/contact` | Multicanal validé | MUST |
| CAP-007 | Pages légales | Conformité | MUST |
| CAP-008 | API FastAPI publiques Contact et Devis (contrats distincts) + validation | Backend autoritaire | MUST |
| CAP-009 | Persistance PostgreSQL + migrations | Traçabilité demandes | MUST |
| CAP-010 | Médias photo optimisés | Performance et crédibilité | MUST |
| CAP-011 | Notifications internes fiables + reprise opérationnelle | Aucune perte de demande acceptée | MUST |
| CAP-012 | SEO technique de base | Découvrabilité | MUST |

### 7.2 Explicitement hors périmètre V1

| ID | Exclusion | Motif |
|---|---|---|
| OUT-001 | Immobilier | Décision métier |
| OUT-002 | Chauffeur privé | Décision métier |
| OUT-003 | Réservation automatisée temps réel | V2+ |
| OUT-004 | Paiement en ligne | V2+ |
| OUT-005 | Compte client / auth (magic link, OTP, OAuth) | V2+ |
| OUT-006 | Espace administrateur / CMS complet | V1.1+ / V2+ |
| OUT-007 | Pièces jointes formulaire | V1 interdit sauf CR |
| OUT-008 | Vidéo obligatoire au lancement | Médias V1 = photos |
| OUT-009 | Microservices, K8s, event bus, CRM sur mesure, IA, moteur investissement | Anti-surarchitecture |
| OUT-010 | Appel public à investir sans validation juridique | Risque légal |

### 7.3 Périmètre différé

| ID | Futur | Déclencheur |
|---|---|---|
| FUT-001 | Location véhicules premium | PRD + validation métier/juridique |
| FUT-002 | Développement national (zones) | Contenu + capacité ops |
| FUT-003 | Réservation / paiement / compte | V2+ gates |
| FUT-004 | Suivi demandes, analytics avancés | V1.1 |

### 7.4 Garde-fous validés pour THE HIVE LOGISTICS

Reprise du bloc canonique template §7.4, confirmé pour ce PRD : vitrine convoyage/flotte/logistique/préparation ; exclusions immobilier/chauffeur ; photos statiques ; pas auth/paiement/booking V1 ; témoignages/chiffres/partenaires uniquement validés ; stack Next.js/FastAPI/PostgreSQL ; pas Redis/microservices/CMS/paiement sans ADR ; évolutions via demande de changement.

---

## 8. Parcours utilisateurs

### JRN-001 — Particulier → devis

**Acteur :** USR-001 | **Déclencheur :** Besoin convoyage | **Résultat :** Demande enregistrée + référence

| Étape | Action | Réponse produit | Donnée | Échec | Récupération |
|---|---|---|---|---|---|
| 1 | Arrive sur `/` | Hero, slogan, CTA devis | — | Lenteur | Contenu prioritaire |
| 2 | Consulte `/services` | 4 services | — | — | Nav |
| 3 | Ouvre `/demande-de-devis` | Formulaire structuré (DEC-006) | Champs obligatoires §9.2 | Validation | Messages a11y |
| 4 | Soumet | Turnstile + validation | DATA-* | Rate limit | Message neutre |
| 5 | Succès | Référence + confirmation | Référence | 5xx | Retry + contact |

### JRN-002 — Professionnel flotte → demande qualifiée

**Acteur :** USR-002 | **Déclencheur :** Recherche prestataire flotte | **Résultat :** Demande entreprise qualifiée

Parcours : accueil → services (coordination flotte) → devis avec entreprise facultative → confirmation.

### JRN-003 — Visiteur rassurance → contact

**Acteur :** USR-003 | **Déclencheur :** Doute sur processus | **Résultat :** Message ou appel canal validé

Parcours : `/a-propos` ou processus accueil → `/contact` (sujets : information, devis, partenariat, autre).

### JRN-004 — Partenaire → contact

**Acteur :** USR-004 | **Résultat :** Demande partenariat enregistrée (sans CTA investir public)

Formulaire contact, sujet partenariat ; pas de collecte d’investissement sans cadre juridique.

### JRN-005 — Mobile → devis

**Acteur :** USR-001 mobile | **Résultat :** Soumission réussie sur matrice §10.3

Même JRN-001 ; structure mono-page ou multi-étapes : **[À produire — spécification UX dédiée du formulaire Devis]**, avec conservation des données entre étapes si multi-étapes.

### JRN-006 — Spam / invalide → rejet

**Acteur :** Bot ou données invalides | **Résultat :** Aucune **demande métier** créée

Honeypot, Turnstile, rate limit, validation schéma ; réponse non divulgative. Les **métadonnées anti-abus minimales** (ex. compteur, hash IP tronquée) peuvent être journalisées séparément selon DATA-005 et BR-009, sans créer de fiche lead.

### JRN-007 — Erreur backend → récupération

**Acteur :** Tout visiteur | **Résultat :** Message non technique + possibilité réessayer ou contact

FR-029, pas de stack trace ; lien contact.

### États transverses

Chargement, succès, erreur validation, erreur technique, réseau lent, clavier, `prefers-reduced-motion`, bannière cookies **uniquement** si traceurs non essentiels activés (décision TBD-006).

---

## 9. Exigences fonctionnelles

[MAJ 18/09/2026] Confirmé par Jores : 3 services, préparation retirée. CAP-002 et FR-002 mis à jour en conséquence.

| ID | Capacité | Exigence | Priorité | Critère d’acceptation | Source |
|---|---|---|---|---|---|
| FR-001 | CAP-001 | Page `/` avec Hero photo, marque THE HIVE LOGISTICS, synthèse services, confiance, processus, CTA final | MUST | Les 2 CTA présents et accessibles sur mobile ; **390×844** : H1, paragraphe et CTA primaire sans défilement ; **320×568** : H1 et CTA primaire sans défilement (CTA secondaire peut être immédiatement sous le premier viewport) | Ticket, docs/ux |
| FR-002 | CAP-002 | `/services` : convoyage premium, flotte, logistique | MUST | 3 blocs distincts | Ticket |
| FR-003 | CAP-003 | `/demande-de-devis` formulaire qualifié métier structuré (non réservation instantanée) | MUST | Champs obligatoires §9.2 persistés ; optionnels §9.2 acceptés ou absents | DEC-006 |
| FR-004 | CAP-003 | Devis : identité (nom, prénom), email, téléphone, service demandé, villes/CP départ et arrivée, date ou période, catégorie véhicule (§9.4), marque/modèle, roulant/non roulant, **prise de connaissance** politique confidentialité (pas consentement marketing) ; optionnels : entreprise, contraintes, message complémentaire, préférence de contact | MUST | Persistance champs validés ; case/info non ambiguë ; catégorie « Autre » → précision obligatoire | DEC-006 |
| FR-005 | CAP-003 | Honeypot anti-bot | MUST | Bot → pas de demande | SEC-002 |
| FR-006 | CAP-003, CAP-006 | Cloudflare Turnstile **obligatoire** pour toute **nouvelle** opération lead (Contact et Devis) ; validation **serveur** (widget seul insuffisant) ; jeton valide 5 min ; **pas** de revalidation Turnstile sur replay idempotent d’une opération déjà commitée (§9.1.1) ; jeton rejoué pour nouvelle opération → rejet ; expiré/invalide → nouveau jeton côté client ; idempotency key métier **distincte** du jeton et de tout `idempotency_key` Siteverify | MUST | Tests §9.1.1 ; siteverify sur premier accept ; cf. DEC-003 | SEC-003 |
| FR-007 | CAP-003 | Référence publique `THL-YYYYMMDD-XXXXXXXX` affichée au succès (§9.3) ; identifiant séquentiel interne jamais exposé | MUST | Format DEC-007 ; même valeur UI, DB et notification | DEC-007, SEC-005 |
| FR-008 | CAP-003 | Confirmation réception + référence | MUST | Cohérence UI/DB | TBD-012 |
| FR-009 | CAP-003 | Erreurs validation accessibles | MUST | Focus/messages par champ | NFR-A11Y-001 |
| FR-010 | CAP-004 | `/a-propos` mission, méthode, engagements, vision mobilité auto | MUST | Pas immobilier/chauffeur | Ticket |
| FR-011 | CAP-005 | `/realisations` publiée **uniquement** si ≥1 réalisation validée (texte + photos + droits + autorisation client) | SHOULD_CONDITIONAL | Sans contenu : route absente nav/sitemap ; pas de page vide publique | TBD-015, TBD-016 |
| FR-012 | CAP-006 | `/contact` formulaire + coordonnées validées | MUST | ≥1 canal validé | TBD-001 |
| FR-013 | CAP-007 | Mentions légales, confidentialité, cookies si besoin, CGU si besoin | MUST | Liens footer | TBD-020 |
| FR-014 | CAP-001 | Header nav vers routes V1 + légal | MUST | Clavier OK | Ticket |
| FR-015 | CAP-001 | Footer cohérent | MUST | Liens légaux stables | FR-013 |
| FR-016 | CAP-008 | API publique création demande devis **et** API publique contact (contrats distincts) ; pipeline interne de traitement des leads partageable | MUST | OpenAPI séparés ; contact sans champs logistiques devis | DEC-005 |
| FR-017 | CAP-008 | Validation autoritaire entrées API | MUST | 4xx payload invalide | SEC-001 |
| FR-018 | CAP-008 | Rate limiting | MUST | Seuil configurable | SEC-004 |
| FR-019 | CAP-009 | Persistance PostgreSQL + migrations | MUST | Enregistrement RECETTE | Stack |
| FR-020 | CAP-009 | Isolation données par environnement | MUST | Pas PROD en DEV | AGENTS.md |
| FR-021 | CAP-010 | Pages statiques lisibles sans JS (hors contrainte Turnstile documentée) | SHOULD | `/services` lisible | NFR-COMP |
| FR-022 | CAP-010 | Photos statiques avec `alt` | MUST | Alt présent | Ticket médias |
| FR-023 | CAP-002 | Deep-link sections services | COULD | Ancre visible | TBD-011 |
| FR-024 | CAP-003 | Pas calendrier réservation, paiement, compte | MUST | DOM inspecté | OUT-* |
| FR-025 | CAP-006 | `/contact` : formulaire simple (§9.2) ; contrat API contact distinct du devis ; validation serveur, honeypot, Turnstile serveur, rate limiting, idempotence, persistance avant notification, erreurs non révélatrices ; **jamais** de champs logistiques devis obligatoires | MUST | Parcours contact conforme DEC-005 | DEC-005 |
| FR-026 | CAP-011 | Notification interne **obligatoire** après persistance transactionnelle ; états `pending` / `sent` / `failed` ; retries durables ; alerte ops si échec final ; demande **jamais perdue** si email échoue | MUST | Preuve RECETTE E2E ; TBD-009 clos | TBD-009 |
| FR-027 | CAP-001 | Contenu validé, pas génération non relue | MUST | Traçabilité Jores | Gouvernance |
| FR-028 | CAP-012 | 404 marque + retour accueil | MUST | HTTP 404 | NFR-REL |
| FR-029 | CAP-012 | 500 générique sans fuite technique | MUST | Pas stack client | SEC-010 |
| FR-030 | CAP-001 | Interface FR, `lang=fr` | MUST | html lang fr | AGENTS.md |
| FR-031 | CAP-005 | Droits image + autorisation client avant publication réalisation | SHOULD_CONDITIONAL | Check-list CNT-005 | TBD-016 |
| FR-032 | CAP-003 | Lien politique confidentialité depuis devis | MUST | Clavier | DATA-001 |
| FR-033 | CAP-008 | Health check sans secrets | MUST | Pas env list | NFR-OBS |
| FR-034 | CAP-001 | `prefers-reduced-motion` | MUST | Animations off | §10.4 |
| FR-035 | CAP-002 | Pas location/immobilier/chauffeur commandables | MUST | Crawl V1 | §7.4 |
| FR-036 | CAP-001 | Nav : Accueil, Services, À propos, Contact + CTA Demander un devis ; **Réalisations** uniquement si FR-011 actif | MUST | Pas de lien `/realisations` sans contenu validé | Ticket |
| FR-037 | CAP-001 | Slogan Hero : « Nous déplaçons plus que des véhicules. » | MUST | Texte exact | Ticket |
| FR-038 | CAP-001 | CTA Hero devis + découvrir services | MUST | 2 CTA | Ticket |
| FR-039 | CAP-003 | Aucune pièce jointe V1 | MUST | Pas input file | OUT-007 |
| FR-040 | CAP-010 | Médias : droits validés, AVIF/WebP si possible, responsive, dimensions, lazy load hors Hero, priorité Hero, pas faux logos/témoignages/chiffres | MUST | Check-list média | Ticket |
| FR-041 | CAP-006 | WhatsApp / Instagram / LinkedIn seulement si URLs/numéros approuvés | MUST | Absent si TBD | TBD-001 |
| FR-042 | CAP-001 | Pas libellé « Réservations » sans booking ; CTA « réserver » → prise en charge humaine uniquement | MUST | Pas instantanéité | Ticket |
| FR-043 | CAP-008 | Idempotence soumission Contact **et** Devis via clé métier à entropie suffisante (format/durée = ADR/OpenAPI) ; replay même clé + même payload normalisé → même référence, pas de second lead ; même clé + payload différent → **409** sans mutation | MUST | Tests replay, conflit 409, un seul enregistrement | SEC-017, §9.1.1 |
| FR-044 | CAP-006 | Sujets contact : information, devis, partenariat, autre | MUST | Liste sélection | Ticket |
| FR-045 | CAP-001 | Pas d’appel public investir sans validation juridique | MUST | Absence CTA invest | OUT-010 |
| FR-046 | CAP-011 | Reprise **exceptionnelle** d’une demande déjà enregistrée : procédure lecture seule, auditée, réservée à Kyria (pas usage commercial courant ; **pas d’export CSV applicatif V1** — TBD-024 en V1.1) | MUST | Runbook exception documenté | Kyria |

### 9.1 Workflow opérationnel des leads (CAP-011)

Ordre impératif pour chaque soumission **nouvelle** acceptée (replay idempotent : §9.1.1, sans recréation ni email avant commit) :

1. Validation de l’enveloppe HTTP, du schéma et des tailles.
2. Contrôles honeypot et rate limiting.
3. Résolution de l’idempotency key métier (replay → réponse sans repasser par les étapes 4–7).
4. Pour une **nouvelle** opération : validation Turnstile **serveur**.
5. Génération de la référence publique `THL-YYYYMMDD-XXXXXXXX` (DEC-007, §9.3) ; en cas de collision UNIQUE, **nouvelle génération** sans lead partiel.
6. Transaction PostgreSQL **atomique** enregistrant : le lead ; sa référence publique ; l’idempotency key et l’empreinte normalisée de la requête ; l’état ou intention durable de notification **`pending`**.
7. **Commit** de la transaction.
8. Traitement asynchrone de la notification avec retries durables (implémentation = ADR ; **pas** Redis/Celery imposés ici).
9. Passage de la notification à `sent` ou `failed`.
10. Alerte opérationnelle après échec final de notification, **sans suppression** du lead.

**Aucun email** (ni notification externe équivalente) **avant** le commit PostgreSQL (étape 7).

Réponse succès au client après commit : référence publique + libellé honnête si notification encore `pending` (TBD-012).

États observables notification : `pending`, `sent`, `failed`.

**TBD-009** bloque RECETTE E2E et PROD.

### 9.1.1 Idempotence, Turnstile et replay (Contact et Devis)

Règles communes aux deux contrats API publics :

| Situation | Comportement |
|---|---|
| Même idempotency key métier + **même** payload normalisé, opération déjà commitée | Retourner le résultat précédent et la **même** référence ; **aucun** second lead ; **ne pas** revalider le jeton Turnstile déjà consommé pour cette opération |
| Même idempotency key + payload **différent** | Réponse **409 Conflict** ; **aucune** mutation en base |
| Opération jamais acceptée (pas de commit antérieur) | Turnstile **obligatoire** (FR-006) |
| Jeton Turnstile **rejoué** pour une **nouvelle** opération | Rejet ; pas de lead |
| Jeton Turnstile expiré ou invalide | Rejet ; l’utilisateur doit obtenir un **nouveau** jeton widget |

L’idempotency key métier reste **distincte** de tout paramètre `idempotency_key` éventuellement transmis à Siteverify pour les retries Cloudflare. Durée de conservation et format technique de la clé : **ADR / contrat OpenAPI** ; entropie suffisante exigée.

### 9.2 Contrats des formulaires publics V1 (DEC-005, DEC-006)

**Demande de devis** (`/demande-de-devis`, API dédiée) — champs **obligatoires** : nom et prénom ; email ; téléphone ; service demandé ; ville et code postal de départ ; ville et code postal d’arrivée ; date précise ou période souhaitée ; catégorie du véhicule (§9.4) ; marque et modèle ; état roulant ou non roulant ; prise de connaissance de la politique de confidentialité (**pas** consentement marketing).

**Devis — champs optionnels** : entreprise ; contraintes particulières ; message complémentaire ; préférence de contact.

**Contact** (`/contact`, API dédiée) — champs **obligatoires** : nom et prénom ; email ; sujet ; message ; prise de connaissance de la politique de confidentialité (**pas** consentement marketing).

**Contact — champs optionnels** : téléphone ; entreprise.

Les deux parcours partagent : validation serveur, honeypot, Turnstile serveur, rate limiting, idempotence, persistance avant notification, messages d’erreur non révélateurs (DEC-003, FR-005–006, FR-018, FR-043). Le formulaire Contact **ne demande jamais** les informations logistiques du devis.

### 9.3 Référence publique demande (DEC-007)

Format : `THL-YYYYMMDD-XXXXXXXX` (exemple syntaxique uniquement : `THL-20260912-7K3M9Q2X` — **ne pas** utiliser comme fixture fixe PROD).

- `YYYYMMDD` : date dérivée de `created_at` **UTC** ;
- `XXXXXXXX` : huit caractères **Crockford Base32 en majuscules**, aléa cryptographiquement sûr côté serveur ;
- regex normative : `^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$` ;
- contrainte **UNIQUE** en base ; nouvelle génération en cas de collision (sans lead partiel) ;
- référence **immuable** après attribution ;
- identifiant séquentiel interne **jamais** exposé publiquement ;
- même référence affichée à l’utilisateur, persistée et incluse dans la notification interne ;
- la référence est un **identifiant d’échange**, **jamais** un secret ; elle **ne doit pas** servir seule à authentifier un utilisateur ni permettre l’accès à des données personnelles ;
- **aucun** endpoint public de consultation par simple référence en V1.

### 9.4 Catégories véhicule V1 (DEC-008)

1. Citadine / berline
2. SUV / 4×4
3. Véhicule premium ou sportif
4. Utilitaire léger
5. Véhicule ancien ou de collection
6. Autre — **précision textuelle obligatoire**

L’état roulant / non roulant reste un **champ distinct** de la catégorie. Les identifiants techniques définitifs sont fixés dans le contrat API OpenAPI, sans modifier ces libellés métier.

### Règles métier

| ID | Règle | Cas limites | Propriétaire |
|---|---|---|---|
| BR-001 | Devis chiffré uniquement par humain | Demande incomplète → qualification | Jores |
| BR-002 | Référence publique unique par demande (`THL-YYYYMMDD-XXXXXXXX`) | Collision → régénération CSPRNG | Kyria |
| BR-003 | Champs devis/contact conformes DEC-006 / DEC-005 | Extension → CR + DEC | Jores |
| BR-004 | Honeypot rempli → rejet silencieux | Faux positif a11y → revue | Kyria |
| BR-005 | Turnstile obligatoire pour nouvelle opération ; invalide/expiré/rejoué (nouvelle op.) → pas de lead ; replay idempotent commité → pas de revalidation Turnstile (§9.1.1) | Panne Cloudflare : **pas de contournement silencieux** ; dégradation = ADR uniquement | Kyria |
| BR-006 | Pas témoignage/logo/chiffre sans preuve | Accord écrit | Jores |
| BR-007 | Services limités aux 4 familles V1 | Extension → CR | Jores |
| BR-008 | Rétention selon DATA-* et TBD-010 | Exception légale documentée | Jores + Kyria |
| BR-009 | Abus : pas de demande métier ; journal anti-abus minimal séparé autorisé | Pas de « quarantaine lead » ambiguë | Kyria |
| BR-010 | Sans réalisation validée : pas de route `/realisations` publique | Publication = FR-011 | Jores |
| BR-011 | Coordonnées = canaux surveillés | Horaires indicatifs | Jores |
| BR-012 | Auth/paiement/booking → PRD dédié | Piste V2+ sans UI | Kyria |

### Contenus et preuves métier

| ID | Contenu | Fournisseur | Statut | Preuve | Fallback |
|---|---|---|---|---|---|
| CNT-001 | Accueil / Hero | Jores | [À CONFIRMER] | Validation | Pas PROD |
| CNT-002 | 4 services | Jores | [À CONFIRMER] | Relecture | Structure seule |
| CNT-003 | Coordonnées | Jores | [À CONFIRMER] | Justificatif | TBD-001 |
| CNT-004 | Photographies | Jores | [À CONFIRMER] | Licences | RECETTE only |
| CNT-005 | Réalisations | Jores | MANQUANT | Autorisations | Route non publiée (FR-011) |
| CNT-006 | Légal | Jores + conseil | [À CONFIRMER] | Juridique | Noindex |
| CNT-007 | Logo / wordmark | Jores | [À CONFIRMER] | TBD-027 | Wordmark texte temp |
| CNT-008 | Meta SEO | Jores | [À CONFIRMER] | Check SEO | PREPROD block |

---

## 10. Exigences UX, UI et marque

### 10.1 Intentions d’expérience

Confiance → parcours devis + légal accessible ; Clarté → 4 services en ≤2 clics ; Premium sobre → palette #FF5757, espacement, FR-034 ; Mobile first → devis validé mobile QA.

### 10.2 Architecture de l’information

| Route | Objectif | CTA principal | Condition de publication |
|---|---|---|---|
| `/` | Conversion | Demander un devis | V1 MUST |
| `/services` | Éducation | Demander un devis | V1 MUST |
| `/demande-de-devis` | Capture lead | Soumettre | V1 MUST |
| `/a-propos` | Confiance | Devis / contact | V1 MUST |
| `/realisations` | Preuve | Devis | **Uniquement** si FR-011 active (≥1 réalisation validée) ; absent nav/sitemap sinon |
| `/contact` | Joindre | Devis ou message | V1 MUST |
| Légal | Conformité | Accueil | V1 MUST (textes TBD-020) |

### 10.3 Responsive — matrice de validation

| Viewport | Largeur CSS px | Exigences |
|---|---|---|
| Minimum supporté | 320 | Pas de débordement horizontal ; formulaires utilisables |
| Mobile référence | 390 | Parcours devis complet clavier + tactile |
| Medium / tablette | 768 | Parité capacités métier |
| Medium large | 1024 | Parité capacités métier |
| Desktop | 1440 | Mise en page premium ; contenu max-width maîtrisé |
| Grand écran | 1920 | Pas d’étirement illimité du contenu |

Mêmes capacités métier V1 à chaque taille. Structure du formulaire Devis (mono/multi-étapes) : **[À produire — spécification UX dédiée du formulaire Devis]**, avec conservation des données entre étapes si applicable.

### 10.4 Accessibilité

**Cible de conformité WCAG 2.2 niveau AA** — aucune certification formelle revendiquée sans audit dédié.

Automatisé (NFR-A11Y-001, aligné GRD-003) : zéro violation **critique** non résolue ; zéro violation **sérieuse** non résolue sur parcours critiques ; aucun blocage clavier ; toute dérogation justifiée et approuvée par Kyria.

Manuel obligatoire : navigation clavier ; ordre/focus visible ; formulaires/erreurs ; zoom/reflow ; smoke lecteur d’écran ; `prefers-reduced-motion`.

Cibles : minimum WCAG 2.2 **24×24 CSS px** (ou exception applicable) ; objectif UX contrôles principaux **44×44 CSS px**.

Contrastes : texte normal **4,5:1** ; grand texte **3:1** ; composants/UI **3:1** ; vérifier accent `#FF5757` sur noir/anthracite.

Références : [Target Size Minimum (WCAG 2.2)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

### 10.5 Direction artistique THE HIVE LOGISTICS

Noir profond, blanc, anthracite, `#FF5757`, photo auto premium nocturne, minimalisme, lignes fines, micro-interactions maîtrisées ; inspirations Ardian, One Concierge, Apple, Porsche, Maybach, Rolls-Royce **sans copie** ; pas esthétique IA générique ; pas vidéo V1.

---

## 11. Exigences non fonctionnelles

| ID | Domaine | Exigence | Vérification | Seuil blocage |
|---|---|---|---|---|
| NFR-PERF-001 | Perf (lab PREPROD) | LCP `/` ≤ **2,5 s** ; profil Lighthouse **mobile** documenté ; **médiane** d’au moins **3** exécutions | Lighthouse CI / PREPROD | LCP > 2,5 s sans dérogation Kyria |
| NFR-PERF-002 | Perf (lab PREPROD) | **TBT** ≤ **200 ms** (proxy lab interactivité ; pas INP Lighthouse) ; même profil et médiane ≥3 runs | Lighthouse | TBT > 200 ms sans dérogation Kyria |
| NFR-PERF-003 | Perf (lab PREPROD) | **CLS** ≤ **0,1** ; même profil et médiane ≥3 runs | Lighthouse | CLS > 0,1 sans dérogation Kyria |
| NFR-PERF-004 | Perf | Budget poids images Hero (Ko) | Audit | TBD-014 dépassé de >20 % |
| NFR-PERF-005 | Perf (terrain) | LCP p75 ≤ 2,5 s **mobile et desktop** séparés, lorsque volume de données suffisant | CrUX / Search Console ; ou RUM vie privée si TBD-006 autorisé | > 2,5 s p75 soutenu |
| NFR-PERF-006 | Perf (terrain) | INP p75 ≤ 200 ms mobile et desktop séparés, données suffisantes | Idem §NFR-PERF-005 | > 200 ms p75 soutenu |
| NFR-PERF-007 | Perf (terrain) | CLS p75 ≤ 0,1, données suffisantes | Idem §NFR-PERF-005 | > 0,1 p75 soutenu |
| NFR-REL-001 | Fiabilité | SLO disponibilité ≥ 99,5 %/mois **après** activation monitoring (objectif interne, pas garantie contractuelle client final) | Monitoring | Revue Tech Lead si SLO non mesurable |
| NFR-REL-002 | Fiabilité | Taux échec soumission 5xx endpoints publics lead < **0,5 %** (aligné GRD-002) | Logs agrégés PREPROD/PROD | ≥ 0,5 % |
| NFR-SEC-001 | Sécurité | Pas secret en client/dépôt/logs | Scan CI | Hit confirmé |
| NFR-SEC-002 | Sécurité | CSP, HSTS PROD, en-têtes | DAST | CSP absente PROD |
| NFR-SEC-003 | Sécurité | Rate limit des **deux** endpoints publics de leads : Contact et Devis | Tests RECETTE sur les deux contrats | Absent PROD sur l’un ou l’autre |
| NFR-PRIV-001 | Vie privée | DATA-* à jour | Audit | Écart non doc |
| NFR-A11Y-001 | A11y | 0 violation **critique** non résolue ; 0 violation **sérieuse** non résolue sur parcours critiques ; pas de blocage clavier ; dérogation = Kyria | axe + checklist §10.4 | Gate GRD-003 |
| NFR-A11Y-002 | A11y | Contrastes §10.4 dont `#FF5757` | Checker | Seuils non atteints |
| NFR-SEO-001 | SEO | Title + description uniques | Crawl | Vide/doublon PROD |
| NFR-OBS-001 | Obs | Logs structurés sans PII claire | Revue | PII PROD |
| NFR-COMP-001 | Compat | Chrome/Firefox/Safari/Edge + mobile | Matrice QA | Devis bloqué |
| NFR-MAINT-001 | Maint | TS strict, lint vert CI | Pipeline | Fail main |

**Web Vitals — lab :** budgets PREPROD ci-dessus ; dépassement bloque promotion sauf dérogation documentée par Kyria. **Terrain :** [web.dev/vitals](https://web.dev/articles/vitals) ; mesure via CrUX/Search Console lorsque disponible ; RUM respectueux de la vie privée **uniquement** après décision TBD-006 — **RUM non obligatoire** si analytics V1 désactivés.

Baseline : validation serveur, rate limit, honeypot, Turnstile, moindre privilège, deps lock, CSP, logs redacted.

---

## 12. Données, vie privée et rétention

| ID | Donnée | Finalité | Base légale | Rétention | Accès |
|---|---|---|---|---|---|
| DATA-001 | Identité contact | Traiter devis | Précontractuel [À CONFIRMER] | TBD-010 | Commercial |
| DATA-002 | Email / téléphone | Reprise | Idem | TBD-010 | Commercial |
| DATA-003 | Besoin, lieux, dates | Qualification | Idem | TBD-010 | Commercial |
| DATA-004 | Référence publique demande (`THL-YYYYMMDD-XXXXXXXX`, DEC-007) | Support utilisateur | Intérêt légitime | TBD-010 | Ops |
| DATA-005 | IP tronquée/pseudonymisée, horodatage ; **User-Agent non persisté** sauf justification ADR | Anti-abus | Sécurité | Durée minimale liée TBD-010 | Ops |
| DATA-006 | Jeton Turnstile (transit) | Anti-bot | Sécurité | Non persisté | Backend |
| DATA-007 | Logs opérationnels (request id, codes) — **sans contenu formulaire** | Exploitation | Intérêt légitime | 30–90 j, TBD-010 | Kyria |
| DATA-008 | Consentement traceurs **non essentiels** uniquement | Preuve si activé | Consentement | TBD-010 | Contact vie privée TBD-022 |

Principes : minimisation ; pas PROD en DEV ; sauvegardes chiffrées testées ; droits personnes via **TBD-022** (pas de DPO désigné tant que non officialisé) ; séparation logs opérationnels / analytics produit.

### 12.2 Modèle de données conceptuel (leads V1)

| Entité logique | Distinction | Identifiants |
|---|---|---|
| Demande de devis | Formulaire métier `/demande-de-devis`, contrat API devis | Référence publique DEC-007 ; clé interne séquentielle non exposée |
| Message contact | Formulaire simple `/contact`, contrat API contact | Référence publique DEC-007 ; clé interne séquentielle non exposée ; **sans** champs logistiques devis |
| Pipeline notification | Partagé possible (CAP-011) | États `pending` / `sent` / `failed` ; indépendant du contrat HTTP public |

Persistance transactionnelle avant notification ; idempotency key métier distincte du jeton Turnstile.

### 12.3 Traceurs et consentement

**Décision V1 :** aucun analytics **non essentiel** par défaut ; aucun tracker publicitaire ; **pas de CMP** si seuls mécanismes strictement nécessaires (ex. Turnstile selon qualification juridique [À CONFIRMER]).

Activation ultérieure analytics (TBD-006) = décision documentée + mise à jour pages légales.

Formulaires : **prise de connaissance** politique confidentialité ; consentement explicite **uniquement** pour finalités facultatives qui l’exigent — formulation non avis juridique définitif.

---

## 13. SEO, partage et découvrabilité

| ID | Exigence |
|---|---|
| SEO-001 | Title/description uniques par route indexable (Jores) |
| SEO-002 | Canoniques domaine PROD TBD-021 |
| SEO-003 | Index routes vitrine ; noindex succès formulaire ; `/realisations` indexée **seulement** si publiée ; devis TBD-013 |
| SEO-004 | Schema Organization/WebSite ; LocalBusiness si adresse validée |
| SEO-005 | Open Graph + image 1200×630 licenciée |
| SEO-006 | sitemap.xml + robots.txt |
| SEO-007 | NAP aligné si publié ; pas zone inventée |
| SEO-008 | Search Console post-lancement |

---

## 14. Intégrations et dépendances externes

| ID | Service | Finalité | Dégradé | Propriétaire |
|---|---|---|---|---|
| INT-001 | Cloudflare Turnstile | Anti-bot formulaires publics ; validation serveur siteverify obligatoire V1 | Panne : politique dégradation **ADR** (pas contournement silencieux) | Kyria |
| INT-002 | Email transactionnel TBD-009 | Notification leads MUST | Retries + alerte | Kyria |
| INT-003 | Hébergement frontend TBD-007 | Next.js | Cache statique | Kyria |
| INT-004 | Backend + PostgreSQL TBD-007 | API/DB | Page maintenance | Kyria |
| INT-005 | DNS/CDN | TLS/WAF | Runbook DNS | Kyria |
| INT-006 | Analytics non essentiels | **Désactivé V1 par défaut** | N/A | Jores |

---

## 15. Environnements, mise en service et exploitation

### 15.1 Environnements

DEV, RECETTE, PREPROD, PROD — configs, secrets, bases isolés (§ ticket).

### 15.2 Promotion

DEV → RECETTE → PREPROD → PROD traçable ; pas promotion implicite agent.

### 15.3 Sauvegarde

**Code** versionné Git (pas dans PostgreSQL). **PostgreSQL** backups dédiés. **Médias** stockage objet versionné si externe. Restauration testée = backup valide.

| Élément | RPO | RTO | Fréquence | Test restore |
|---|---|---|---|---|
| PostgreSQL PROD | 24 h [À CONFIRMER] | 4 h [À CONFIRMER] | Quotidien | Trimestriel |
| Médias optimisés versionnés (web) | 7 j | 24 h | Par release Git | Restauration depuis tag/release |
| Originaux photo + preuves licence | — | — | Archive contrôlée / stockage objet (ADR) | Test restauration archive, **pas Git seul** |
| Secrets | — | — | Rotation TBD-019 | Procédure |

---

## 16. Sécurité et abus

### 16.1 Surface

Formulaire, API, frontend, DB, logs, CI/CD — contrôles SEC-*.

### 16.2 Règles impératives

Validation serveur ; honeypot ; Turnstile ; rate limit ; en-têtes ; CSP étudiée ; CORS restrictif ; CSRF si requis ; SQL paramétré ORM ; secrets hors dépôt ; logs PII masqués ; deps auditées ; SAST/secrets CI ; backups testés ; moindre privilège ; pas cred PROD local ; webhooks futurs signés/idempotents/non-destructifs ; pas auth/paiement V1.

### 16.3 SEC-* (contrôles et résultats attendus)

| ID | Contrôle | Résultat attendu |
|---|---|---|
| SEC-001 | Schéma strict API | Rejet 4xx ; tailles max requête/champs documentées |
| SEC-002 | Honeypot | Pas de lead ; pas de fuite règle |
| SEC-003 | Turnstile serveur | siteverify sur nouvelle opération ; jeton 5 min ; pas de re-siteverify sur replay idempotent commité ; rejoué/expiré/invalide selon §9.1.1 ; cf. [validation serveur Turnstile](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/) |
| SEC-004 | Rate limit | Seuils TBD-018 ; 429 documenté |
| SEC-005 | Références CSPRNG | Regex `^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$` ; Crockford majuscules ; identifiant d’échange, **pas** secret/auth ; pas d’endpoint consultation publique par référence V1 ; collision sans lead partiel |
| SEC-006 | Erreurs génériques client | Pas stack |
| SEC-007 | Secrets hors dépôt | Scan CI vert |
| SEC-008 | TLS PROD | HTTPS forcé |
| SEC-009 | CSP + headers | Politique documentée PREPROD |
| SEC-010 | Logs | Pas contenu formulaire ; PII redacted |
| SEC-011 | CVE | Haute/critique traitées avant PROD |
| SEC-012 | CORS restrictif | Origines allowlist |
| SEC-013 | HTTP/formes | Méthodes et Content-Type allowlist |
| SEC-014 | Email injection | En-têtes sanitizés notification |
| SEC-015 | Timeouts externes | Turnstile/email bornés |
| SEC-016 | IP de confiance | Config proxy documentée |
| SEC-017 | Idempotence | Replay même clé+payload → même référence ; clé+payload différent → 409 ; pas double lead ; cf. §9.1.1 |
| SEC-018 | PostgreSQL | Moindre privilège compte app |

### 16.4 Menaces

Alignées RISK-* ; réponse incident documentée.

---

## 17. Observabilité et analytique produit

| Événement | Finalité | Interdit | Conservation |
|---|---|---|---|
| page_view (si analytics activé) | Trafic | PII | TBD-006 |
| quote_submit_ok / quote_submit_fail | Entonnoir devis | **Contenu champs formulaire** | Agrégats sans PII ; TBD-010 |
| api_error_5xx | Fiabilité | Payload corps requête | 30 j |
| rate_limit_hit | Abus | IP en clair dans analytics produit | 30 j |

Signaux actionnables V1 : demandes valides reçues, taux d’erreur formulaire, ratio exploitables/acceptées, délai de traitement (process Jores), uptime, latence API, CWV, alertes CVE. **Aucun analytics non essentiel par défaut** (§12.3).

---

## 18. Risques, hypothèses et dépendances

### 18.1 Risques

| ID | Risque | P | I | Réduction | Owner |
|---|---|---|---|---|---|
| RISK-001 | Contenu/légal pas prêt | 4 | 4 | Plan Jores | Jores |
| RISK-002 | ADR Turnstile/email retard | 3 | 5 | Spike early | Kyria |
| RISK-003 | Spam notifications | 3 | 3 | SEC-004 | Kyria |
| RISK-004 | RGPD (durées, traceurs) | 2 | 5 | DATA + TBD-006/020/022 | Jores + Kyria |
| RISK-005 | Perf images mobile | 3 | 3 | NFR-PERF-004 | Kyria |
| RISK-006 | A11y clavier | 2 | 4 | Tests PREPROD | Kyria |
| RISK-007 | Fuite secret deploy | 2 | 5 | SEC-007 | Kyria |
| RISK-008 | Portfolio publié sans droits | 3 | 4 | FR-011, BR-010 | Jores |
| RISK-009 | Panne hébergeur J0 | 2 | 4 | PREPROD drill | Kyria |
| RISK-010 | Scope creep | 3 | 4 | §7.4 CR | Jores |

### 18.2 Hypothèses

| ID | Hypothèse | Validation | Si fausse |
|---|---|---|---|
| ASM-001 | Conversion principale = devis | Nombre de demandes **valides** en PostgreSQL (M+1 post-lancement) ; entonnoir analytics **seulement** si mécanisme autorisé (TBD-006) | Renforcer contact |
| ASM-002 | Turnstile acceptable a11y | Test users | ADR alt |
| ASM-003 | Monolithe suffit trafic V1 | Load light | Cache |
| ASM-004 | Photos suffisent sans vidéo | Sponsor | Brief média |
| ASM-005 | Traitement demandes < 48 h ouvrés | Process Jores | Ajuster copy |

### 18.3 Dépendances

| ID | Dépendance | Owner | Date |
|---|---|---|---|
| DEP-001 | Textes/coordonnées | Jores | PREPROD |
| DEP-002 | ADR + threat model (post-gate API THL-PRODUCT-002) | Kyria | Avant RECETTE E2E |
| DEP-003 | Compte Turnstile | Kyria | RECETTE E2E |
| DEP-004 | Domaine + TLS | Kyria | PROD |
| DEP-005 | Licences images | Jores | PROD |
| DEP-006 | Mentions légales | Jores | PROD |

---

## 19. Découpage de haut niveau

**Qualité transversale :** SEC-*, NFR-* (perf, fiabilité, a11y) et DATA-* s’appliquent **dans chaque epic** (Definition of Done de l’epic), pas uniquement en fin de projet.

| Epic | Résultat | CAP | Ordre |
|---|---|---|---|
| EPIC-FOUNDATION | CI, envs, health, API socle | CAP-008, CAP-009 (socle) | 1 |
| EPIC-CONTENT-SHELL | Layout, nav, footer, légal, shell accueil | CAP-001 (structure), CAP-007 | 2 |
| EPIC-PAGES-MARKETING | Contenu accueil, services, à propos, contact, médias | CAP-001 (contenu), CAP-002, CAP-004, CAP-006, CAP-010 | 3 |
| EPIC-QUOTE | Devis + leads E2E (persistance, notification, reprise) | CAP-003, CAP-008, CAP-009, CAP-011 | 4 |
| EPIC-PORTFOLIO | `/realisations` **si** FR-011 active | CAP-005 | 5 (conditionnel) |
| EPIC-SEO-OBS | SEO technique, erreurs, observabilité | CAP-012 | 6 |
| EPIC-HARDENING | **Vérification finale** cross-env (sec/perf/a11y/backup), pas première implémentation | Revue SEC/NFR | 7 |

### Roadmap

| Release | Contenu |
|---|---|
| **V1** | Vitrine complète, devis sécurisé, notifications MUST, SEO base, cible WCAG 2.2 AA ; `/realisations` **uniquement** si contenu validé (sinon absent nav/sitemap) |
| **V1.1** | Export/suivi demandes (TBD-024), analytics non essentiels si décidé (TBD-006), contenu éditorial enrichi |
| **V2+** | Booking, compte, paiement, location — PRD + threat model chacun |

---

## 20. Stratégie de validation

### 20.1 Produit

Revue Jores ; pas contenu inventé ; recette mobile/tablette/desktop.

### 20.2 Technique

Lint, types, tests API/e2e, scans deps, smoke envs, migrations synthétiques.

### 20.3 Matrice de traçabilité — FR MUST

| FR | CAP | Epic | Preuve attendue |
|---|---|---|---|
| FR-001 | CAP-001 | EPIC-PAGES-MARKETING | Recette Hero + sections ; 390×844 et 320×568 : critères viewport FR-001 (CTA primaire sans scroll ; secondaire admis sous fold 320) |
| FR-002 | CAP-002 | EPIC-PAGES-MARKETING | 4 blocs services visibles ; crawl V1 |
| FR-003 | CAP-003 | EPIC-QUOTE | e2e soumission devis RECETTE |
| FR-004 | CAP-003 | EPIC-QUOTE | Test champs + prise de connaissance politique |
| FR-005 | CAP-003 | EPIC-QUOTE | Test honeypot → 0 enregistrement |
| FR-006 | CAP-003 / CAP-006 | EPIC-QUOTE | siteverify nouvelle op. ; replay idempotent sans re-siteverify ; jeton expiré/rejoué rejeté (Devis + Contact) |
| FR-007 | CAP-003 | EPIC-QUOTE | Audit format `THL-YYYYMMDD-XXXXXXXX` (DEC-007) |
| FR-008 | CAP-003 | EPIC-QUOTE | UI référence = DB |
| FR-009 | CAP-003 | EPIC-QUOTE | axe + clavier erreurs champs |
| FR-010 | CAP-004 | EPIC-PAGES-MARKETING | Relecture contenu Jores |
| FR-012 | CAP-006 | EPIC-PAGES-MARKETING | Formulaire contact + canal validé |
| FR-013 | CAP-007 | EPIC-CONTENT-SHELL | Liens footer PREPROD |
| FR-014 | CAP-001 | EPIC-CONTENT-SHELL | Test nav clavier |
| FR-015 | CAP-001 | EPIC-CONTENT-SHELL | Liens footer stables |
| FR-016 | CAP-008 | EPIC-FOUNDATION / QUOTE | Contrats OpenAPI devis **et** contact + tests création |
| FR-017 | CAP-008 | EPIC-QUOTE | Tests payload invalides 4xx |
| FR-018 | CAP-008 | EPIC-QUOTE | Test rate limit 429 endpoints publics **Devis et Contact** (NFR-SEC-003) |
| FR-019 | CAP-009 | EPIC-FOUNDATION | Migration + insert RECETTE |
| FR-020 | CAP-009 | EPIC-FOUNDATION | Config env isolée |
| FR-022 | CAP-010 | EPIC-PAGES-MARKETING | Audit `alt` médias |
| FR-024 | CAP-003 | EPIC-QUOTE | Inspection DOM : pas booking/paiement |
| FR-025 | CAP-006 | **EPIC-PAGES-MARKETING** (UI `/contact`) **+ EPIC-QUOTE** (API contact, persistance, idempotence, anti-abus, notification) | Formulaire sans champs logistiques ; OpenAPI Contact distinct ; honeypot, Turnstile, rate limit, idempotence, persistance, notification durable (DEC-005, §9.1) |
| FR-026 | CAP-011 | EPIC-QUOTE | e2e notification + états pending/sent/failed |
| FR-027 | CAP-001 | EPIC-PAGES-MARKETING | Trace validation Jores |
| FR-028 | CAP-012 | EPIC-SEO-OBS | HTTP 404 custom |
| FR-029 | CAP-012 | EPIC-SEO-OBS | 500 sans stack client |
| FR-030 | CAP-001 | EPIC-CONTENT-SHELL | `lang=fr` |
| FR-032 | CAP-003 | EPIC-QUOTE | Lien politique accessible clavier |
| FR-033 | CAP-008 | EPIC-FOUNDATION | Health sans secrets |
| FR-034 | CAP-001 | EPIC-PAGES-MARKETING | Test reduced-motion |
| FR-035 | CAP-002 | EPIC-PAGES-MARKETING | Crawl : pas services hors périmètre |
| FR-036 | CAP-001 | EPIC-CONTENT-SHELL | Nav sans `/realisations` si CAP-005 inactive |
| FR-037 | CAP-001 | EPIC-PAGES-MARKETING | Texte Hero exact |
| FR-038 | CAP-001 | EPIC-PAGES-MARKETING | 2 CTA Hero présents et accessibles (visibilité viewport : FR-001) |
| FR-039 | CAP-003 | EPIC-QUOTE | Pas input file |
| FR-040 | CAP-010 | EPIC-PAGES-MARKETING | Check-list médias + perf |
| FR-041 | CAP-006 | EPIC-PAGES-MARKETING | Liens sociaux absents si non validés |
| FR-042 | CAP-001 | EPIC-PAGES-MARKETING | Pas CTA réservation instantanée |
| FR-043 | CAP-008 | EPIC-QUOTE | Replay même clé+payload → même référence ; clé+payload différent → 409 ; Devis + Contact |
| FR-044 | CAP-006 | EPIC-PAGES-MARKETING | Liste sujets contact |
| FR-045 | CAP-001 | EPIC-PAGES-MARKETING | Absence CTA investissement |
| FR-046 | CAP-011 | EPIC-QUOTE | Runbook reprise **exceptionnelle** lecture seule (Kyria) ; pas export CSV V1 |

*FR MUST hors matrice obligatoire : aucun — FR-011/031 = SHOULD_CONDITIONAL ; FR-021 = SHOULD ; FR-023 = COULD.*

### 20.4 AC-* (acceptation release V1)

| ID | Critère |
|---|---|
| AC-001 | Chaque FR MUST de §20.3 prouvé (pas seulement « tous MUST faits » sans preuve) |
| AC-002 | Devis succès + erreurs RECETTE |
| AC-003 | Honeypot + rate limit prouvés (endpoints publics Devis **et** Contact) |
| AC-004 | Turnstile : validation **serveur** siteverify obligatoire V1 ; ADR = dégradation contrôlée uniquement |
| AC-005 | Scan secrets CI vert |
| AC-006 | Pages légales liées |
| AC-007 | SEO-001–006 PROD (sitemap sans `/realisations` si inactive) |
| AC-008 | Gate a11y GRD-003 / NFR-A11Y-001 : 0 critique non résolue, 0 sérieuse non résolue (parcours critiques), 0 blocage clavier ; checklist §10.4 |
| AC-009 | NFR-PERF-001–003 lab PREPROD (LCP ≤2,5 s, TBT ≤200 ms, CLS ≤0,1, médiane ≥3 runs) ; NFR-PERF-005–007 terrain quand CrUX/Search Console ou RUM autorisé (données suffisantes) |
| AC-010 | Restore backup PostgreSQL synthétique |
| AC-011 | Contenu PROD signé Jores |
| AC-012 | RISK-001/004 mitigations ou acceptées |
| AC-013 | Smoke PROD post-deploy |
| AC-014 | Rollback testé |
| AC-015 | Validation Tech Lead (Kyria) + Sponsor (Jores) enregistrée |

---

## 21. Definition of Ready du PRD

Problème/utilisateurs/objectifs clairs ; périmètre in/out ; FR/NFR/SEC identifiés ; TBD owned ; risques owned ; stack cohérente ; verdicts §1 ; pas contradiction bloquante architecture.

---

## 22. Definition of Done produit V1

MUST validés ; AC-001–015 ; parcours mobile/desktop ; contenus licenciés (TBD-016/TBD-027 pour tout média publié) ; sécurité ; pas vulnérabilité critique ouverte ; gate a11y GRD-003 ; budgets lab NFR-PERF-001–003 ; obs/backups ; écarts documentés ; validation livraison humaine.

---

## 23. Questions ouvertes (TBD-*)

| ID | Décision | Owner humain | Statut | Gate au plus tard | Impact si non résolu | Valeur / référence |
|---|---|---|---|---|---|---|
| TBD-001 | Coordonnées officielles affichées | Jores | Ouvert | PREPROD | PROD bloquée ; FR-012/041 | — |
| TBD-002 | Adresse + zone de service | Jores | Ouvert | PREPROD | SEO/local trompeur | — |
| TBD-003 | Champs obligatoires devis | Jores | **Clos** | Architecture API (levée 2026-09-12) | — | DEC-006 |
| TBD-004 | Contact séparé vs demande commune catégorisée | Jores (+ UX) | **Clos** | Architecture API (levée 2026-09-12) | — | DEC-005 |
| TBD-005 | Horaires / délais affichés | Jores | Ouvert | PREPROD | Copy imprécis | — |
| TBD-006 | Analytics non essentiels + consentement | Jores | Ouvert | Avant activation | CMP/pages si activé | **Défaut V1 : aucun** — ne bloque pas PROD |
| TBD-007 | Hébergeurs PROD | Jores + Kyria | Ouvert | PREPROD | Pas de déploiement | — |
| TBD-008 | Format référence demande | Kyria | **Clos** | Architecture API (levée 2026-09-12) | — | DEC-007 |
| TBD-009 | Fournisseur email + destinataires leads | Kyria + Jores | Ouvert | **RECETTE E2E** ; **PROD** | Pas de notification fiable | — |
| TBD-010 | Durées rétention DATA-* | Jores (+ conseil) | Ouvert | PREPROD ; **PROD** | Non-conformité | — |
| TBD-011 | Structure page services | Jores (+ UX) | Ouvert | **Avant approbation de la spécification UX de /services** | UX services | — |
| TBD-012 | Message post-soumission utilisateur | Jores | Ouvert | **RECETTE E2E** | UX incohérente | — |
| TBD-013 | Indexation `/demande-de-devis` | Jores | Ouvert | PROD | SEO | — |
| TBD-014 | Budget Ko images Hero | Kyria | Ouvert | **Avant implémentation frontend** | NFR-PERF-004 | — |
| TBD-015 | Date 1ère réalisation portfolio | Jores | Ouvert | Avant publication CAP-005 | Route inactive OK | — |
| TBD-016 | Droits de **toutes** photos, illustrations, logos et médias publics ; preuve licence/autorisation avant PROD ; autorisation client **en plus** pour réalisations ; média non couvert = **non publié** | Jores | Ouvert | PREPROD ; **PROD** (chaque média publié) | Publication illégale | — |
| TBD-017 | Carte interactive contact | Jores + Kyria | Ouvert | Optionnel V1 | UX contact | **Défaut V1 : aucune carte** — ne bloque pas PREPROD |
| TBD-018 | Seuils rate limit PROD | Kyria | Ouvert | **RECETTE E2E** | Abus ou faux positifs | — |
| TBD-019 | Rotation secrets | Kyria | Ouvert | PREPROD | Fuite prolongée | — |
| TBD-020 | Textes légaux finaux | Jores | Ouvert | PREPROD ; **PROD** | Conformité | — |
| TBD-021 | Domaine canonique | Jores + Kyria | Ouvert | PREPROD ; **PROD** | SEO/TLS | — |
| TBD-022 | Contact vie privée / exercice droits | Jores | Ouvert | PREPROD ; **PROD** | Droits personnes | — |
| TBD-023 | Typologie véhicules formulaire | Jores | **Clos** | Architecture API (levée 2026-09-12) | — | DEC-008 |
| TBD-024 | Export CSV demandes (fonctionnel) | Jores + Kyria | Ouvert | **V1.1** (sauf justification métier) | Reprise via notification + FR-046 exceptionnel | — |
| TBD-025 | Date go-live V1 | Jores + Kyria | Ouvert | PROD | Planning | — |
| TBD-026 | Budget exploitation mensuel + approbation coûts fournisseurs | Jores + Kyria | Ouvert | **Avant souscription ou provisioning payant** | Surcoût infra/email | Hors prix dev commercial |
| TBD-027 | Logo / wordmark définitif approuvé pour PROD | Jores | Ouvert | PREPROD ; **PROD** si logo graphique affiché | Marque incohérente | Wordmark texte temporaire possible si non revendiqué comme final |

**Gate architecture API :** TBD-003, TBD-004, TBD-008, TBD-023 **clos** (2026-09-12, DEC-005–008) → **`READY_FOR_API_ARCHITECTURE = YES`**. Cela **n’équivaut pas** à **`READY_FOR_PRODUCTION = YES`**.

**Gates PROD (résolus ou N/A documenté) :** coordonnées (TBD-001), identité/mentions (TBD-020), domaine (TBD-021), hébergement (TBD-007), destinataires leads (TBD-009), rétention (TBD-010), canal droits (TBD-022), **droits de chaque média publié** (TBD-016), **logo/wordmark si affiché** (TBD-027), sauvegarde/restauration (§15.3 + ADR), contenus signés Jores (AC-011).

---

## 24. Registre des décisions

| ID | Date | Décision | Décideur |
|---|---|---|---|
| DEC-001 | 2026-09-12 | V1 vitrine sans auth/paiement/booking | Jores + Kyria |
| DEC-002 | 2026-09-12 | Next.js + FastAPI + PostgreSQL | Kyria |
| DEC-003 | 2026-09-12 | V1 : Turnstile formulaires publics + honeypot + rate limit ; **validation serveur obligatoire** ; jeton 5 min usage unique ; idempotency key métier distincte ; ADR = dégradation contrôlée seulement | Kyria |
| DEC-004 | 2026-09-12 | Pas preuve sociale inventée | Jores |
| DEC-005 | 2026-09-12 | `/contact` formulaire simple et `/demande-de-devis` formulaire métier structuré ; **contrats API publics distincts** ; pipeline interne de traitement des leads partageable ; Contact sans champs logistiques devis | Jores (métier) ; Kyria (architecture interne) |
| DEC-006 | 2026-09-12 | Champs obligatoires et optionnels devis et contact (§9.2) ; prise de connaissance politique confidentialité **sans** consentement marketing | Jores |
| DEC-007 | 2026-09-12 | Référence publique `THL-YYYYMMDD-XXXXXXXX` (Crockford Base32 **majuscules**, UTC, UNIQUE, immuable, regex §9.3) ; identifiant d’échange, pas secret ni auth ; pas de consultation publique par référence V1 | Kyria |
| DEC-008 | 2026-09-12 | Typologie véhicules V1 §9.4 ; « Autre » avec précision obligatoire ; roulant/non roulant distinct | Jores |

*Décisions ouvertes liées au déploiement : TBD-007 (hébergement), TBD-009 (email), etc. §23. À l’acceptation, ajouter une nouvelle entrée DEC datée — ne pas laisser de DEC « à confirmer ».*

---

## 25. Demandes de changement

| ID | Statut |
|---|---|
| CR-001 | Aucune demande enregistrée |

Procédure : enregistrer → impact → verdict → versionner PRD → specs/stories.

---

## 26. Handoff

**État actuel :** PRD en `DRAFT_FOR_HUMAN_APPROVAL` — **aucune** approbation globale Jores/Kyria du document entier n’est acquise pour la livraison V1.

**Autorisé sans approbation globale :** la validation ciblée DEC-005–008 (THL-PRODUCT-002) lève la gate **architecture API** → `READY_FOR_API_ARCHITECTURE = YES` pour entamer `ARCHITECTURE-SPINE.md`, contrats OpenAPI et ADR techniques (workflow §9.1, idempotence §9.1.1).

**Toujours obligatoire avant livraison PROD :** approbation globale enregistrée §1 ; gates PROD §23 (coordonnées, légal, hébergement, email, rétention, médias, etc.) ; `READY_FOR_PRODUCTION = NO` tant que non levé.

Enchaînement cible une fois gates satisfaits : UX produit (`docs/ux/*`, specs formulaire Devis à produire) → spine + ADR → SPEC/epics → stories → gates BMAD (METHODE-BMAD §29).

---

## 27. Checklist rédacteur

- [ ] 29 sections numérotées (0–28) présentes
- [ ] TBD avec owner humain et gate (§23)
- [ ] Pas PRIMiE / immobilier / chauffeur services
- [ ] Pas chiffres/témoignages inventés
- [ ] FR MUST testables
- [ ] V1 vs V1.1 vs V2+ distincts
- [ ] Annexe BMAD à jour

---

## 28. Glossaire

| Terme | Définition |
|---|---|
| Demande de devis | Lead qualifié, traitement humain, pas tarif auto |
| THE HIVE LOGISTICS | Marque principale du site |
| TBD-* | Décision ouverte tracée |
| Site vitrine V1 | Marketing + leads, pas transaction |

---

## Annexe A — Synthèse passes BMAD (THL-PRODUCT-001 / 001A / 001B / **002** / **002A**)

Passes exécutées sur **un seul** PRD (`docs/product/THL-PRD.md`), sans documents séparés.

| Passe | Focus | Verdict | Objections / décisions clés |
|---|---|---|---|
| **Analyste métier** | Périmètre services, exclusions, parcours JRN-* | PARTIAL | OK exclusions ; TBD coordonnées et zones |
| **Product Manager** | CAP/FR/BR, roadmap V1/V1.1/V2+ | PARTIAL | Portfolio conditionnel ; notification MUST |
| **UX/UI** | §10, IA routes, DA #FF5757, matrice responsive | PARTIAL | THL-UX-001 = Home ; spec formulaire Devis **[À produire]** ; Hero mobile aligné FR-001 |
| **Architecte** | Stack, monolithe, sauvegardes Git vs archive médias | **READY_FOR_API_ARCHITECTURE** | TBD-003/004/008/023 clos (DEC-005–008) ; TBD-007 PREPROD ; **pas** READY_FOR_PRODUCTION |
| **Sécurité** | SEC-001–018, Turnstile serveur V1, BR-009 | PARTIAL | Threat model avant PROD ; TBD-018 RECETTE |
| **QA** | Matrice FR MUST §20.3, AC lab/terrain CWV | PARTIAL | WCAG cible AA ; pas certification sans audit |
| **Relecture Tech Lead** | Cohérence 29 sections (0–28), tableaux, DEC acceptées seules | EN ATTENTE | v0.1.4 post-002A — DRAFT_FOR_HUMAN_APPROVAL |

**Synthèse identifiants :** FR 46 ; BR 12 ; NFR **19** ; SEC 18 ; DATA 8 ; SEO 8 ; AC 15 ; RISK 10 ; DEC **8** acceptées ; TBD 27 (**4 clos**, owner + gate §23).

**Gate architecture API :** `READY_FOR_API_ARCHITECTURE = YES` (THL-PRODUCT-002, cohérence transactionnelle 002A).

**Bloquant PROD :** voir §23 (TBD-006 **exclu** si décision « aucun analytics non essentiel V1 ») ; **`READY_FOR_PRODUCTION = NO`**.
