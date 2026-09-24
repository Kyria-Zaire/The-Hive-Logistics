# THL-EXPERIENCE — Fondations d’expérience THE HIVE LOGISTICS

[MAJ 20/09/2026] Accent rouge changé sur décision client (Jores) : #FF5757 → #DC2626.

> **Ticket** = THL-UX-001 / **001A** / **001B** / **THL-UX-001C**
> **Version** = 0.1.3
> **Statut** = DRAFT_FOR_HUMAN_APPROVAL
> **PRD** = `docs/product/THL-PRD.md` v0.1.2
> **Concept directeur** = **PRÉCISION EN MOUVEMENT**

Ce document définit parcours, navigation, contenu et comportements V1. Il ne remplace pas le PRD et n’autorise ni commit applicatif ni fermeture de TBD PRD sans validation humaine.

---

## 1. Promesse d’expérience

THE HIVE LOGISTICS doit faire ressentir, en quelques secondes :

- une **maîtrise opérationnelle** du déplacement automobile premium ;
- une **clarté** sur ce qui est proposé et comment entrer en contact ;
- une **discipline visuelle** (noir, anthracite, photographie nocturne, accent `#DC2626` mesuré) ;
- l’absence de promesses instantanées ou automatisées non livrées en V1.

**Formulation directrice :** *De la demande à la prise en charge humaine, chaque interaction est nette, lisible et digne de confiance.*

---

## 2. Perception recherchée

| Dimension | Cible | Anti-patterns |
|---|---|---|
| Prestige | Sobre, éditorial, espace généreux | Cartes SaaS répétitives, glow néon |
| Confiance | Processus explicite, coordonnées honnêtes | Faux chiffres, témoignages, logos partenaires |
| Modernité | Typographie forte, photo recadrée, mouvement discret | Esthétique « site IA générique » |
| Précision | Grille architecturale, alignements, hiérarchie nette | Dégradés décoratifs, glassmorphism |
| Mouvement | Révélations courtes, jamais bloquantes | Scroll hijack, parallaxe agressive mobile |

Inspirations de **principe** uniquement (rythme, retenue, qualité photo) — pas de copie de marques tierces.

---

## 3. Principes UX

| ID | Principe | Application |
|---|---|---|
| UX-001 | Vérité contenu | TBD ou retrait plutôt qu’invention (aligné PP-005 PRD) |
| UX-002 | Devis ≠ réservation | CTA « Demander un devis » ; pas « Réserver » sans booking V1 |
| UX-003 | Mobile d’abord | Parcours devis et accueil validés 390 px puis 320 px |
| UX-004 | Parité capacités | Mêmes actions métier à 320–1920 px (PRD §10.3) |
| UX-005 | Confiance sans preuve sociale inventée | Engagements qualitatifs, pas stats non sourcées |
| UX-006 | Progressive enhancement | Contenu et navigation utilisables sans JS (hors contraintes documentées Turnstile sur formulaires) |
| UX-007 | Focus visible | Ordre tab logique header → contenu → footer |
| UX-008 | Mouvement optionnel | Respect `prefers-reduced-motion` (FR-034) |
| UX-009 | Portfolio conditionnel | Pas de section Réalisations vide (CAP-005, FR-011) |
| UX-010 | Accessibilité continue | Cible WCAG 2.2 AA ; contrôles principaux 44×44 px objectif |

---

## 4. Utilisateurs prioritaires

Aligné PRD §5 :

| ID | Segment | Besoin sur le site | Priorité page d’accueil |
|---|---|---|---|
| USR-001 | Particulier premium | Comprendre convoyage / confiance | Hero + méthode + CTA devis |
| USR-002 | Pro flotte | Voir étendue services + sérieux | Services + manifeste |
| USR-003 | Visiteur rassurance | Processus clair | HOME-05 Méthode |
| USR-004 | Partenaire | Contact sans tunnel devis forcé | Footer + lien contact |

Persona de référence : **Alex** (fictif, PRD) — responsable flotte, mobile, besoin de processus clair.

---

## 5. Navigation principale

### 5.1 Routes V1 (PRD §10.2)

| Lien | Route | Nav header | Condition |
|---|---|---|---|
| Accueil | `/` | Oui | Toujours |
| Services | `/services` | Oui | Toujours |
| À propos | `/a-propos` | Oui | Toujours |
| Contact | `/contact` | Oui | Toujours |
| Réalisations | `/realisations` | **Non** tant que CAP-005 inactive | FR-036 |
| Demander un devis | `/demande-de-devis` | CTA distinct (pas libellé « Réservations ») | Toujours |

Pages légales : footer uniquement (mentions, confidentialité, cookies si besoin).

### 5.2 Header (comportement global — verrouillé)

| Plage (px) | Navigation dans la barre | CTA « Demander un devis » dans la barre |
|---|---|---|
| **320–1279** | Wordmark + **menu drawer** uniquement | **Absent** — accès via **Hero** (P0 rouge) et entrée du menu |
| **1280+** | Wordmark + **navigation inline** + **CTA compact** (outline blanc, **pas** bouton primaire rouge) | Présent — variante `btn-header-compact` §6.2 `THL-DESIGN.md` |

- Menu drawer : focus trap, Échap, retour focus, focus visible §7 `THL-DESIGN.md` ;
- Scroll accueil : transparent → `color-bg-anthracite` + bordure basse (250 ms).
- **Un seul bouton primaire rouge `#DC2626` visible dans le Hero** (pas de second P0 rouge dans le header).

### 5.3 Fil d’Ariane

Non requis V1 sur vitrine plate ; titres de page et `<h1>` uniques par route.

---

## 6. Hiérarchie des CTA

| Niveau | Libellé type | Destination | Règle |
|---|---|---|---|
| P0 | Demander un devis | `/demande-de-devis` | Bouton **rouge** `#DC2626` / texte `#0A0A0A` — **Hero** (et blocs conversion dédiés, ex. fin chapitre méthode, HOME-09) |
| P0-header | Demander un devis | `/demande-de-devis` | **≥1280 px uniquement** : CTA **compact outline** (fond transparent, texte blanc, bordure blanche) — **ne pas** qualifier de primaire rouge |
| P1 | Découvrir nos services | `#services` | Secondaire outline dans le Hero |
| P2 | Nous contacter | `/contact` | Tertiaire texte ou outline discret |
| Interdit V1 | Réserver / Payer / Créer un compte | — | FR-024, FR-042 |

Ordre de lecture accueil (aligné ordre DOM) : **Hero** → **Déclaration de marque** → **Services** → **Méthode / Engagements** → **Réalisations** (si actives) → **Vision** → **Conversion finale**.

---

## 7. Architecture globale des pages V1

| Page | Rôle | Sections clés | Spec détaillée |
|---|---|---|---|
| `/` | Conversion + éducation synthétique | HOME-01…09 | `pages/HOME.md` |
| `/services` | Éducation 4 prestations | Voir §15 ci-dessous | [À produire THL-UX-002] |
| `/demande-de-devis` | Capture lead | Formulaire | [THL-UX formulaire] |
| `/a-propos` | Confiance longue | Mission, vision | [À produire] |
| `/contact` | Multicanal | Formulaire + coordonnées TBD-001 | [À produire] |
| `/realisations` | Preuve | Liste cas validés | **Absente** si pas de contenu |
| Légal | Conformité | Textes TBD-020 | [À produire] |

Aucune route hors PRD §10.2.

---

## 8. Stratégie responsive

Matrice PRD §10.3 + grand écran 1920 px :

| Viewport | Rôle design | Comportement layout |
|---|---|---|
| 320 px | Minimum | Une colonne ; padding réduit ; pas de scroll horizontal |
| 390 px | Mobile référence | Hero full-bleed ; texte bas-gauche ; H1 + CTA primaire sans scroll (390×844) |
| 768 px | Tablette | Hero plein écran ; composition recentrée |
| 1024 px | Medium large | Hero immersif plein écran ; services alternés à partir de **1024 px** |
| 1280 px | Nav desktop | Navigation inline + CTA header |
| 1440 px | Desktop référence | Hero **min-height 92svh** ; contenu max 1280 px |
| 1920 px | Grand écran | Hero **min-height 92svh** ; marges latérales ; image recadrée, pas d’étirement |

Hero : **full-bleed photographique unique** — spec `pages/HOME.md` HOME-02. Trois recadrages sources (desktop / tablette / mobile). `[À CONFIRMER — Owner: Jores — Gate: PROD]` médias CNT-004 + droits TBD-016.

---

## 9. Règles d’accessibilité

Aligné PRD §10.4, NFR-A11Y-001, GRD-003 :

- HTML sémantique (`header`, `nav`, `main`, `section`, `footer`) ;
- un `<h1>` par page ; hiérarchie titres sans saut ;
- contrastes 4,5:1 texte normal, 3:1 grand texte et UI ;
- `#DC2626` : **jamais** seul vecteur d’information ; tester chaque usage sur fond noir/anthracite ;
- focus visible 2 px minimum, couleur distincte de l’accent si besoin ;
- cibles interactives ≥ 24×24 px (WCAG) ; boutons nav/CTA ≥ 44×44 px objectif ;
- images décoratives `alt=""` ; images porteuses de sens : `alt` descriptif validé Jores ;
- motion : voir §12 ; désactivation via `prefers-reduced-motion` ;
- tests : axe parcours critiques + checklist clavier, zoom 200 %, smoke lecteur d’écran.

---

## 10. Règles de contenu

1. Tout texte public marqué **DRAFT_CONTENT — À VALIDER PAR JORES** jusqu’à validation explicite.
2. Interdit d’inventer : volumes, délais, zones, assurances, certifications, partenaires, témoignages, disponibilité 7j/7.
3. Coordonnées, réseaux, horaires : afficher **uniquement** si TBD-001 / TBD-005 clos.
4. Pas de logo constructeur automobile en promotion.
5. FAQ : uniquement si réponses validées métier (proposition services §15).
6. Langue : français ; `lang="fr"`.

---

## 11. États globaux

Pages marketing V1 : rendu serveur — **pas de skeleton global**.

| État | DEV / RECETTE | PROD |
|---|---|---|
| Chargement | HTML + CSS immédiat ; réservation ratio média (`aspect-ratio`, width/height) | Idem |
| Hero sans asset | Placeholder interne marqué RECETTE (non publiable) | **Blocage gate** — pas de déploiement |
| Image service absente | Placeholder interne identifié | Fallback graphique premium **sans texte** ou bloc sans image |
| Coordonnées non validées | Section contact test avec données fictives isolées env | **Omise** — gate PRD TBD-001 ; jamais de copy « à confirmer » |
| 404 / 500 | FR-028 / FR-029 | Idem |
| CAP-005 inactive | HOME-07 absente ; pas de lien Réalisations | Idem |

Textes **interdits en PROD** : « Visuel en cours de validation », « Coordonnées à confirmer », « Contenu à venir », mentions de placeholders internes.

---

## 12. Principes de mouvement

**Autorisé :** entrée **initiale Hero uniquement** (400 ms) ; micro-interactions hover/focus ; transition header 250 ms ; **au plus une** transition légère entre grands chapitres si elle améliore la hiérarchie ; progression discrète timeline méthode (HOME-05).

**Interdit :** fade-in systématique sur chaque bloc ; scroll bloqué ; animation retardant CTA ; parallaxe agressive mobile ; GSAP obligatoire ; layout shift ; contenu masqué si JS off ; effets **non désactivables** sous `prefers-reduced-motion`.

**Reduced motion :** durées 0 ms ; pas de translate/scale ; contenu entièrement lisible au chargement.

---

## 13. Progressive enhancement

1. Contenu textuel et liens fonctionnent sans JS.
2. Navigation mobile dégrade en `<details>` / lien ancre si JS off [HYPOTHÈSE technique à confirmer en implémentation].
3. Formulaires : enhancement validation client **après** validation serveur autoritaire (PRD).
4. Animations : couche CSS/JS légère ; pas de contenu critique uniquement en JS.

---

## 14. Confiance sans preuve sociale inventée

Substituts autorisés :

- **Méthode** en 4 étapes (demande → qualification → prise en charge → livraison) ;
- **Engagements** qualitatifs (communication, structure, respect véhicule, suivi humain) — promesses opérationnelles `[À CONFIRMER]` Jores ;
- **Services** décrits par besoin réel, sans superlatifs chiffrés ;
- **Réalisations** uniquement avec cas validés (CAP-005).

Interdit : bandeau « +500 clients », logos presse, notes stars, certifications non prouvées.

---

## 15. Structure proposée pour `/services` (TBD-011)

> **Statut TBD-011 :** **PROPOSITION UX** — ne ferme **pas** le TBD dans le PRD tant que Jores n’a pas validé (gate PRD : avant validation THL-UX-001).

### 15.1 Objectif page

Éduquer sur les quatre familles de prestation et amener vers devis ou contact qualifié.

### 15.2 Structure recommandée

1. **Introduction courte** — une colonne, titre + 2–3 phrases DRAFT_CONTENT.
2. **Sommaire / navigation intra-page** — ancres vers SVC-01…04 (liste liens clavier, focus visible).
3. **Quatre chapitres éditoriaux** (composition asymétrique, photo + texte alternés) :
   - **SVC-01** Convoyage automobile premium ;
   - **SVC-02** Gestion et coordination de flotte ;
   - **SVC-03** Logistique automobile ;
   - **SVC-04** Préparation automobile.
4. **Méthode commune** — reprise simplifiée HOME-05 (lien ancre ou bloc unique).
5. **Informations utiles pour une demande** — liste non exhaustive, champs alignés futur TBD-003 `[À CONFIRMER]`.
6. **CTA devis** — bloc final P0.
7. **FAQ** — **section omise par défaut** ; ajout uniquement si paires Q/R validées Jores.

### 15.3 Critères d’acceptation proposition

- [ ] Jores valide titres et périmètre des 4 chapitres ;
- [ ] Kyria valide faisabilité contenu + perf images ;
- [ ] PRD TBD-011 mis à jour **après** validation humaine (hors scope THL-UX-001).

---

## Annexe A — Synthèse passes BMAD (THL-UX-001)

Passes exécutées sur les livrables UX (un flux, pas sept documents séparés).

| Passe | Verdict | Points clés |
|---|---|---|
| **UX strategist** | PASS | Promesse PRÉCISION EN MOUVEMENT ; CTA devis ; pas fausse instantanéité |
| **Information architect** | PASS | Nav alignée PRD ; Réalisations conditionnelle ; hiérarchie CTA |
| **Visual designer** | PASS | Système dans `THL-DESIGN.md` ; pas cartes SaaS génériques |
| **Accessibility reviewer** | PASS | WCAG 2.2 AA cible ; focus ; reduced-motion ; contrastes #DC2626 à tester |
| **Responsive reviewer** | PASS | 320–1920 ; HOME.md par breakpoint |
| **Content reviewer** | PARTIAL | DRAFT_CONTENT partout ; zéro invention chiffrée ; validation Jores requise |
| **Relecture Tech Lead (Kyria)** | EN ATTENTE | Cohérence PRD, perf hero, pas de dépendance GSAP imposée |

## Annexe B — Traçabilité PRD (extrait accueil)

| PRD | Couverture UX |
|---|---|
| FR-001, FR-037, FR-038 | HOME-02 Hero |
| FR-036 | Pas Réalisations nav |
| FR-011, CAP-005 | HOME-07 conditionnel |
| FR-034 | Motion §12 |
| FR-042 | CTA libellés §6 |
| TBD-011 | §15 proposition |

---

## Annexe C — Synthèse THL-UX-001A / 001B / 001C

| Domaine | Verdict |
|---|---|
| Hero full-bleed | Verrouillé (001A) |
| Typographie Hero px | Verrouillé (001B) |
| Header 320–1279 drawer / 1280+ inline | Verrouillé (001B) |
| Un seul P0 rouge dans le Hero | Verrouillé (001B) |
| Focus bouton primaire double anneau | Verrouillé (001B) |
| Chapitre « La méthode Hive » + transition 300 ms | Verrouillé (001B) |
| Matrice HOME-05–06 timeline/principes V/H | Verrouillé (001C) |
| Hero 92svh desktop / 100svh tablette-mobile | Verrouillé (001C) |
| PROD placeholders | Interdits |

Relecture Kyria : **EN ATTENTE**.

---

**VERDICT document** = DRAFT — en attente validation Jores (contenu) et Kyria (technique UX).
