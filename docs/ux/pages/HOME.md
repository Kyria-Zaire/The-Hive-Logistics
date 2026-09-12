# Page d’accueil `/` — Spécification UX/UI

> **Ticket** = THL-UX-001 / **001A** / **001B** / **THL-UX-001C**
> **Version** = 0.1.3
> **Statut** = DRAFT_FOR_HUMAN_APPROVAL
> **PRD** = v0.1.2 — FR-001, FR-014–015, FR-027, FR-030, FR-034, FR-036–038, FR-042, FR-045
> **Concept** = **PRÉCISION EN MOUVEMENT**

Copy : **DRAFT_CONTENT — À VALIDER PAR JORES** sauf mention contraire.

---

## Carte de composition (normative)

Une seule composition active par section. Détails par section ci-dessous.

| ID | Objectif | Fond | Composition retenue | Média | Rythme vertical | Transition entrante | CTA | Mobile (390 / 320) |
|---|---|---|---|---|---|---|---|---|
| HOME-01 | Naviguer | Transparent → anthracite au scroll | 320–1279 : wordmark + drawer ; 1280+ : nav inline + CTA compact outline | Aucun | 64–72 px | Aucune | P0 rouge Hero ; menu ; CTA compact ≥1280 | Drawer ; P0 Hero |
| HOME-02 | Convertir + ancrer marque | Photo full-bleed + overlay | Texte **bas-gauche** ; véhicule **droite** ; grille fine | Photo hero obligatoire PROD | 92svh desktop ; 100svh tablette/mobile (§) | Révélation initiale unique | P0 rouge devis + P1 `#services` | H1+CTA1 sans scroll 390×844 |
| HOME-03 | Déclaration marque | `color-bg-deep` | Prose une colonne, règle accent gauche | **Aucune** (texte seul) | 64 px padding section | Aucune | Lien « Découvrir notre approche » → `/a-propos` | Prose pleine largeur |
| HOME-04 | Éduquer services | `color-bg-deep` | 4 blocs **alternés** ≥1024 ; **pile** 320–1023 | Cadre photo par bloc | 96 px entre blocs | Aucune | **Voir tous les services** → `/services` | Pile image→texte |
| HOME-05+06 | Méthode + engagements | `color-bg-elevated` (chapitre continu) | **320–1279 px :** timeline verticale puis principes en rail vertical ; **1280 px+ :** timeline horizontale puis principes sur une ligne horizontale | Aucun | Chapitre unique ~120–160 px padding | Entrée chapitre 300 ms (§) | P0 devis fin chapitre | Timeline V + principes V |
| HOME-07 | Preuve | `color-bg-deep` | Grille éditoriale cas | Photos validées | 96 px | Aucune | Devis | Stack |
| HOME-08 | Vision courte | `color-bg-deep` | Prose 680 px max | Aucun | 48 px | Aucune | Aucun | Prose |
| HOME-09 | Conversion + légal | CTA elevated + footer anthracite | CTA centré puis footer 3 col (≥1280) | Aucun | 64 px CTA + footer | Aucune | Devis + contact | Stack footer |

---

## Narration (ordre DOM)

1. HOME-01 — Header
2. HOME-02 — Hero
3. HOME-03 — Déclaration de marque
4. HOME-04 — Services éditoriaux (`id="services"`)
5. HOME-05 + HOME-06 — Chapitre **« La méthode Hive »** (wrapper `<section aria-labelledby="methode-hive">`)
6. HOME-07 — Réalisations (conditionnel)
7. HOME-08 — Vision courte
8. HOME-09 — Conversion et footer

---

## HOME-01 — Header

### Objectif

Orientation et accès menu sans dupliquer le CTA primaire sur mobile.

### Contenu

Wordmark ; liens Accueil, Services, À propos, Contact (drawer &lt;1280, inline ≥1280) ; CTA **compact outline** « Demander un devis » (≥1280 px, **pas** rouge primaire) ; pas de Réalisations si CAP-005 inactive.

### Hiérarchie

Skip link → logo → menu / nav → CTA (desktop).

### Composition (unique)

| Viewport | Composition |
|---|---|
| 320–1279 px | Wordmark gauche ; bouton menu 44×44 droite ; **pas de CTA dans la barre** ; drawer pour nav + lien devis |
| 1280 px et plus | Wordmark ; navigation inline ; **CTA compact outline** : libellé « Demander un devis », icône Lucide `ArrowUpRight` 16 px `aria-hidden="true"`, fond transparent, texte blanc, bordure blanche ; barre 72 px ; max-width 1280 px centré |

### Média

Aucun.

### Interactions

Scroll &gt; 48 px : fond `color-bg-anthracite` ; menu : focus trap, focus visible §7 DESIGN.

### Mouvement

Transition fond 250 ms ; reduced motion : instantané.

### Accessibilité

`nav aria-label="Principale"` ; `aria-expanded` menu ; CTA header ≥1280 px seulement.

### Dépendances

`[À CONFIRMER — Owner: Jores — Gate: PREPROD]` wordmark TBD-027.

### Critères d’acceptation

- [ ] 390 px : wordmark + menu seulement ;
- [ ] CTA devis accessible via Hero + menu mobile ;
- [ ] 1280 px : nav inline + CTA **compact** (pas rouge) ;
- [ ] Un seul bouton **primaire rouge** visible dans le Hero (pas de P0 rouge header).

---

## HOME-02 — Hero

### Objectif

Promesse FR-037/038 ; CTA devis ; ancrage `#services`.

### Contenu (DRAFT_CONTENT — À VALIDER PAR JORES)

- **Eyebrow :** Mobilité automobile premium
- **H1 (une phrase DOM, FR-037) :** Nous déplaçons plus que des véhicules.
  - Visuel : mots **plus que** en **Instrument Serif Italic** dans un `<span>` sans casser la phrase pour l’AT.
- **Paragraphe :** Convoyage, gestion de flotte et logistique automobile, orchestrés avec précision.
- **CTA P0 (primaire rouge) :** Demander un devis → `/demande-de-devis` — fond `#FF5757`, texte `#0A0A0A`
- **CTA P1 (secondaire outline) :** Découvrir nos services → `#services`

### Typographie H1 (verrouillée)

| Viewport | Taille H1 | Line-height | max-width H1 |
|---|---|---|---|
| 320 px | 40 px | 0.92 | 100 % conteneur |
| 390 px | 48 px | 0.92 | 100 % |
| 768 px | 64 px | 0.94 | 100 % |
| 1024 px | 80 px | 0.94 | 100 % |
| 1440 px | 112 px | 0.90 | 760 px |
| 1920 px | 128 px | 0.90 | 760 px |

Interpolation fluide entre ancres ; pas de troncature ; « plus que » en Instrument Serif Italic.

### Composition (unique — full-bleed)

- Photographie **plein écran** (pas de split, pas de carrousel, pas vidéo, pas WebGL, pas faux 3D) ;
- Ambiance **nocturne** ; véhicule **dominant à droite** ; **espace négatif à gauche** pour texte ;
- Overlay sombre contrôlé + **grille éditoriale** fine derrière zone texte (DESIGN §4) ;
- Bloc contenu **aligné bas-gauche** ; safe areas `env(safe-area-inset-*)`.

### Hauteurs (`svh`)

| Viewport | Hauteur Hero |
|---|---|
| 1920 px | **min-height: 92svh** |
| 1440 px | **min-height: 92svh** |
| 1024 px | **min-height: 100svh** |
| 768 px | **min-height: 100svh** ; `object-position` recentré |
| **390 × 844** | **100svh** ; **H1 + paragraphe + CTA primaire visibles sans défilement** |
| **320 × 568** | **100svh** ; **H1 + CTA primaire visibles** ; CTA secondaire **immédiatement sous** le fold autorisé |

Priorité : lisibilité et non-collision &gt; afficher tous les éléments sur 320 px.

### Média

- PROD : photo validée CNT-004 — **pas de placeholder Hero** ;
- RECETTE : asset test ou blocage release ;
- `alt=""` si décoratif ; sinon `[À CONFIRMER — Owner: Jores — Gate: PROD]` alt descriptif.

### Interactions

Hover/focus CTA ; pas de scale photo obligatoire (micro scale desktop ≤1.02 autorisée, désactivée reduced-motion).

### Mouvement

**Seule** animation de page au load : stagger eyebrow → H1 → texte → CTA (400 ms max, translateY 12 px). Pas de fade-in sur les autres sections.

### Accessibilité

Un H1 ; contraste texte/overlay ; boutons 44 px ; focus visible.

### Critères d’acceptation

- [ ] H1 phrase unique accessible ;
- [ ] CTA secondaire → `#services` uniquement ;
- [ ] Full-bleed verrouillé.

### PROD sans photo

**Gate déploiement** — ne pas publier Hero placeholder.

---

## HOME-03 — Déclaration de marque

### Objectif

Manifeste discipline / confiance — composition **texte seul**.

### Contenu (DRAFT_CONTENT — À VALIDER PAR JORES)

**H2 :** Une logistique automobile pensée avec rigueur

Chaque déplacement exige anticipation, clarté et respect du véhicule. Nous structurons la demande, qualifions le besoin avec vous et organisons la prise en charge sans promesse automatisée.

**Lien éditorial obligatoire :** **Découvrir notre approche** → `/a-propos` — style lien texte secondaire avec flèche ; pas de bouton rouge.

### Composition (unique)

| Viewport | Composition |
|---|---|
| 1280 px et plus | Prose max 680 px, colonne gauche dans max-width 1280 ; règle accent 48 px `#FF5757` à gauche du H2 |
| 768–1279 px | Prose max 680 px, marge 24 px |
| 320–767 px | Padding 16–24 px, body-lg |

**Pas de portrait**, pas de vignette personne.

### Mouvement

Aucun.

### Critères d’acceptation

- [ ] Pas de carte « valeurs » icônes ;
- [ ] Texte seul ;
- [ ] Lien « Découvrir notre approche » présent vers `/a-propos`.

---

## HOME-04 — Services éditoriaux

### Objectif

FR-002 aperçu ; ancre **`id="services"`**.

### Contenu (DRAFT_CONTENT — À VALIDER PAR JORES)

**H2 :** Nos expertises

| Service | Besoin | Description |
|---|---|---|
| Convoyage automobile premium | Organiser le déplacement de véhicules | Accompagnement du déplacement de véhicules selon votre contexte. |
| Gestion et coordination de flotte | Coordonner les mouvements | Coordination opérationnelle des mouvements de flotte. |
| Logistique automobile | Structurer les flux | Accompagnement logistique automobile adapté à vos contraintes. |
| Préparation automobile | Préparer la remise | Préparation automobile **selon le périmètre validé** `[À CONFIRMER — Owner: Jores — Gate: PREPROD]`. |

CTA section : **Voir tous les services** → `/services`

### Composition (unique)

| Viewport | Composition |
|---|---|
| 1024 px et plus | Blocs alternés image/texte (grille 12 col) ; image ~45 %, texte ~55 % ; décalage vertical d’une unité gutter entre blocs pairs/impairs |
| 320–1023 px | Une colonne : image ratio 16:9 puis texte ; espacement 48 px entre blocs |

### Média

Cadre photo par service ; PROD : image validée ou fallback graphique **sans texte** ; RECETTE : placeholder interne non publiable.

### Mouvement

Aucune animation scroll obligatoire.

### Critères d’acceptation

- [ ] Pas 4 cartes SaaS identiques ;
- [ ] 768 px = pile unique (normatif).

---

## Chapitre « La méthode Hive » (HOME-05 + HOME-06)

Wrapper visuel continu : fond `color-bg-elevated`, padding vertical 120 px desktop / 80 px mobile.

### HOME-05 — Méthode (processus)

**H2 chapitre (id `methode-hive`) :** La méthode Hive

**Sous-titre H3 :** Comment se déroule une demande

| # | Titre | Texte |
|---|---|---|
| 01 | Demande | Vous formulez votre besoin via le devis ou le contact. |
| 02 | Qualification | Nous examinons les informations et reprenons contact si nécessaire. |
| 03 | Prise en charge | Organisation opérationnelle du service convenu. |
| 04 | Livraison et confirmation | Restitution et confirmation avec vous. |

Note : *Chaque demande est traitée par l’équipe — pas de confirmation automatique en ligne.*

**Composition HOME-05 — timeline (unique) :**

| Viewport | Composition |
|---|---|
| 320–1279 px | **Timeline verticale** : numéros 01–04, ligne fine `color-surface-border`, contenu empilé |
| 1280 px et plus | **Timeline horizontale** : 4 colonnes ; numéros 01–04 typographiques |

**Pas de** variante 2×2. **Pas de** timeline horizontale sous 1280 px.

**Transition chapitre (HOME-05+06, unique) :** à l’entrée du chapitre « La méthode Hive » — durée **300 ms**, opacity 0→1, translateY max **12 px** ; **désactivée** avec `prefers-reduced-motion` ; **contenu présent dans le HTML** sans JavaScript.

### HOME-06 — Engagements (intégrés)

**H3 (même chapitre, pas de H2 séparé) :** Nos principes

**Composition HOME-06 — principes (unique) :**

| Viewport | Composition |
|---|---|
| 320–1279 px | **Principes en rail vertical** numérotés 01–04 |
| 1280 px et plus | **Principes sur une ligne horizontale**, séparés par traits verticaux 1 px (pas de cartes) |

Typographie numérotée 01–04 ; **aucune icône décorative** ; titre fort + une phrase par principe.

1. **Communication claire** — Points de contact et étapes expliqués.
2. **Prise en charge structurée** — Processus défini pour chaque demande.
3. **Respect du véhicule** — Exigence centrale de notre métier.
4. **Suivi humain** — `[À CONFIRMER — Owner: Jores — Gate: PREPROD]` modalités d’interlocuteur.

CTA fin de chapitre : **Demander un devis** → `/demande-de-devis`

### Critères chapitre

- [ ] HOME-05 et HOME-06 même fond sans rupture carte ;
- [ ] Pas 4 cartes flottantes HOME-06 ;
- [ ] 320–1279 : timeline verticale + principes rail vertical ;
- [ ] 1280+ : timeline horizontale + principes ligne horizontale.

---

## HOME-07 — Réalisations (conditionnelles)

**Absent du DOM** par défaut (CAP-005 inactive).

Si actif : H2 Réalisations ; cas validés TBD-016 ; CTA devis ; grille éditoriale ≥1024, stack mobile. Pas de placeholder public.

---

## HOME-08 — Vision courte

### Contenu par défaut (DRAFT_CONTENT — À VALIDER PAR JORES)

**H2 :** Perspectives

THE HIVE LOGISTICS oriente son développement vers des services de **mobilité automobile** premium — coordination, logistique et préparation — avec une ambition d’élargissement progressif **des services proposés**, sous validation métier et juridique.

**Bloc location premium :** **masqué par défaut**. Affiché **uniquement** après validation explicite Jores :

> `[À CONFIRMER — Owner: Jores — Gate: PREPROD]` *Formulation location automobile premium — ne pas publier sans GO.*

**Interdit dans copy publique :** mention marketing immobilier / chauffeur privé (exclusion PRD, non argument commercial).

### Composition

Prose max 680 px ; 320–1920 identique structure ; pas de CTA investissement.

---

## HOME-09 — Conversion et footer

### CTA final (DRAFT_CONTENT — À VALIDER PAR JORES)

**H2 :** Parlons de votre besoin
Texte : Décrivez votre demande de devis ou contactez-nous.
**P0 :** Demander un devis | **P1 :** Nous contacter → `/contact`

### Footer

- Wordmark ; liens Services, À propos, Contact, Devis ; légal FR-013 ;
- **Coordonnées :** rendues **uniquement** si gate PRD TBD-001 satisfait ; sinon **section omise** (pas de texte substitut public) ;
- **Réseaux :** FR-041 — lien absent si non approuvé ;
- **Pas de carte** (TBD-017 défaut V1) ;
- Copyright année dynamique.

### Composition

| Viewport | Composition |
|---|---|
| 1280 px et plus | Bandeau CTA centré max 720 px ; footer 3 colonnes |
| 768–1279 px | Bandeau CTA ; footer 2 colonnes |
| 320–767 px | CTA empilé pleine largeur max 360 px ; footer en pile |

---

## Annexe A — Options écartées (non normatives)

| Sujet | Option rejetée |
|---|---|
| Hero | Split 55/45 ; stack photo au-dessus texte mobile |
| Hero CTA | CTA devis uniquement dans header mobile |
| CTA services | Destination `/services` ou `#services-apercu` |
| HOME-03 | Portrait 3:4 |
| HOME-04 768 | Grille 2 colonnes |
| HOME-05 | Timeline 2×2 ; horizontal &lt;1280 |
| HOME-06 | Grille 4 cartes engagements |
| HOME-08 | Paragraphe exclusion immobilier/chauffeur en copy |
| Bouton primaire | Texte blanc sur `#FF5757` |
| Typo | Inter + Instrument Sans |
| Focus | `:focus { outline: none }` global |
| Chargement | Skeleton global pages marketing |

---

## Annexe B — Matrice viewport (résumé)

| Section | 320 | 390 | 768 | 1024 | 1440 | 1920 |
|---|---|---|---|---|---|---|
| HOME-01 | drawer | drawer | drawer | drawer | nav inline + CTA compact | nav inline + CTA compact |
| HOME-02 | full-bleed | full-bleed | full-bleed | full-bleed | full-bleed | full-bleed |
| HOME-04 | pile | pile | pile | alterné | alterné | alterné |
| HOME-05–06 | timeline V + principes V | timeline V + principes V | timeline V + principes V | timeline V + principes V | timeline H + principes H | timeline H + principes H |

---

**Statut** = DRAFT_FOR_HUMAN_APPROVAL — revue Jores + Kyria post-001C.
