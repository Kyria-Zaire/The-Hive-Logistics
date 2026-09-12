# THL-DESIGN — Système visuel THE HIVE LOGISTICS

> **Ticket** = THL-UX-001 / **001A** / **001B** / **THL-UX-001C**
> **Version** = 0.1.3
> **Statut** = DRAFT_FOR_HUMAN_APPROVAL
> **Concept** = **PRÉCISION EN MOUVEMENT**

Tokens pour implémentation Next.js. Aucune fonte payante sans validation Jores + Kyria.

---

## 1. Couleurs sémantiques

### 1.1 Palette de base

| Token | Hex | Usage |
|---|---|---|
| `color-bg-deep` | `#0A0A0A` | Fond principal, overlay hero |
| `color-bg-elevated` | `#141414` | Chapitres alternés (ex. La méthode Hive) |
| `color-bg-anthracite` | `#1C1C1E` | Header solide, footer |
| `color-surface-border` | `#2A2A2E` | Séparateurs, grille éditoriale |
| `color-text-primary` | `#FFFFFF` | Titres, texte principal sur fond sombre |
| `color-text-secondary` | `#B8B8BC` | Corps, légendes |
| `color-text-muted` | `#8A8A8F` | Eyebrows |
| `color-accent` | `#FF5757` | Accent marque — usage restreint |
| `color-accent-hover` | `#E64D4D` | Hover bouton primaire (voir §1.3) |
| `color-focus-ring` | `#FFFFFF` | Anneau focus par défaut sur fond sombre |
| `color-error` | `#FF6B6B` | Erreurs formulaire |
| `color-success` | `#5CB88A` | Succès discret |

### 1.2 Usages autorisés de `#FF5757`

| Autorisé | Interdit |
|---|---|
| Fond bouton primaire (texte `#0A0A0A` uniquement) | Texte blanc `#FFFFFF` sur fond `#FF5757` |
| Règle éditoriale 1–2 px | Grands aplats, glow néon |
| Soulignement lien nav actif (avec texte blanc adjacent) | Paragraphes ou boutons secondaires en rouge plein |

### 1.3 Contrastes mesurés (verrouillés)

| Combinaison | Ratio | Verdict |
|---|---|---|
| `#0A0A0A` sur `#FF5757` | ~6,37:1 | **CTA primaire — conforme** texte normal |
| `#FFFFFF` sur `#FF5757` | ~3,11:1 | **Interdit** pour texte normal |
| `#FF5757` sur `#0A0A0A` (lien, règle) | ~6,37:1 | Conforme pour petits éléments UI |
| `#FFFFFF` sur `#0A0A0A` | >15:1 | Texte hero / corps |

**Bouton primaire (obligatoire) :** fond `#FF5757`, texte `#0A0A0A`, icône `#0A0A0A`.

**Hover primaire :** fond `#E64D4D`, texte `#0A0A0A` — re-vérifier ratio (~6:1, rester ≥ 4,5:1).

---

## 2. Typographie (direction verrouillée)

### 2.1 Familles

| Rôle | Famille | Périmètre |
|---|---|---|
| **UI + titres + corps** | **Instrument Sans Variable** | Navigation, H1–H3, boutons, paragraphes, labels |
| **Accent éditorial** | **Instrument Serif Italic** | Uniquement « plus que » dans le Hero ; au plus **une** courte expression éditoriale par page interne |

Interdit : second sans-serif proche (ex. Inter + DM Sans). Interdit : serif pour paragraphes, boutons, formulaires, navigation.

### 2.2 Licence et hébergement (avant PROD)

- Vérifier licence officielle Instrument Sans / Instrument Serif sur [Google Fonts](https://fonts.google.com/) ou source retenue ;
- Auto-héberger les fichiers `.woff2` (pas de dépendance runtime tierce en PROD si évitable) ;
- Subsets : **`latin`** + **`latin-ext`** ; pas de subset complet ;
- Graisses Instrument Sans Variable : axe `wght` 400–600 (400 corps, 500 UI, 600 titres) ;
- Instrument Serif Italic : **`ital` 1**, `wght` 400–500 pour « plus que » ;
- Fallback stack UI : `"Instrument Sans Variable", system-ui, "Segoe UI", sans-serif` ;
- Fallback accent : `"Instrument Serif", ui-serif, Georgia, serif` (italique).

`[À CONFIRMER — Owner: Jores — Gate: PREPROD]` validation budget/licence si hors OFL.

### 2.3 Échelle typographique (valeurs fixes)

| Token | 320 px | 390 px | 768 px | 1024 px | 1440 px | 1920 px |
|---|---|---|---|---|---|
| `text-hero-h1` (taille) | **40 px** | **48 px** | **64 px** | **80 px** | **112 px** | **128 px** |
| `text-hero-h1` (line-height) | **0.92** | **0.92** | **0.94** | **0.94** | **0.90** | **0.90** |

| Token | 320 px | 390 px | 768 px | 1024 px | 1440 px | 1920 px | Line-height |
|---|---|---|---|---|---|---|---|
| `text-h2` | 1.5rem | 1.625rem | 1.75rem | 2rem | 2.25rem | 2.25rem | 1.15 |
| `text-h3` | 1.125rem | 1.125rem | 1.25rem | 1.375rem | 1.5rem | 1.5rem | 1.25 |
| `text-body-lg` | 1rem | 1.0625rem | 1.0625rem | 1.125rem | 1.125rem | 1.125rem | 1.6 |
| `text-body` | 0.9375rem | 1rem | 1rem | 1rem | 1rem | 1rem | 1.65 |
| `text-eyebrow` | 0.6875rem | 0.75rem | 0.75rem | 0.8125rem | 0.8125rem | 0.8125rem | 1.4, ls 0.08em |
| `text-editorial-accent` | inherit hero | inherit hero | 1.05em italic serif | idem | idem | idem | inherit |

**Hero H1 (implémentation) :** interpolation fluide entre les ancres ci-dessus (pas de troncature, pas de débordement horizontal) ; `max-width` bloc H1 **760 px** à partir de **1280 px** ; « plus que » en Instrument Serif Italic ; phrase unique dans le DOM.

---

## 3. Grille et layout

| Intervalle (px) | Colonnes | Gutter | Marge |
|---|---|---|---|
| 320–767 | 4 | 16 | 16 |
| 768–1023 | 8 | 24 | 24 |
| 1024–1279 | 12 | 24 | 32 |
| 1280–1919 | 12 | 32 | auto, max 1280 |
| 1920+ | 12 | 32 | auto, max 1280 |

**Navigation desktop complète :** à partir de **1280 px** uniquement (pas à 1024 px par défaut).

---

## 4. Hero photographique (spec visuelle)

- **Full-bleed** : image `100%` largeur, `object-fit: cover` ;
- **Véhicule** : `object-position: 75% 50%` (desktop) ; recentrage `60% 50%` à 768 px ; `50% 55%` à 390 px ;
- **Overlay** : dégradé `linear-gradient(105deg, rgba(10,10,10,0.88) 0%, rgba(10,10,10,0.45) 45%, rgba(10,10,10,0.25) 100%)` ;
- **Grille éditoriale** : lignes `1px` `rgba(42,42,46,0.35)` en arrière-plan du bloc texte (CSS background, pas image) ;
- **Bloc texte** : ancré **bas-gauche**, padding `max(24px, env(safe-area-inset-*))` ; H1 `max-width: 760px` ≥1280 px ; paragraphe sous H1 max-width 520 px ;
- **Hauteurs** : 1440/1920 → `min-height: 92svh` ; 768/1024/mobile → `min-height: 100svh` (`pages/HOME.md` HOME-02).

---

## 5. Photographie et médias

- Traitement nocturne premium ; pas de logo constructeur ;
- **Trois** recadrages sources documentés : `hero-desktop.webp` (21:9), `hero-tablet.webp` (4:3), `hero-mobile.webp` (4:5) ;
- **DEV / RECETTE :** placeholder interne autorisé avec bordure « RECETTE ONLY » **hors capture PROD** ;
- **PROD Hero :** image validée obligatoire — **aucun placeholder texte** ; gate déploiement si CNT-004 absent ;
- **PROD autres sections :** fallback graphique premium (texture anthracite + cadre vide **sans copy**) ou omission du bloc image ;
- Lazy-load : hors LCP hero ; dimensions `width`/`height` explicites.

---

## 6. Composants interactifs

### 6.1 Bouton primaire

| État | Fond | Texte | Bordure |
|---|---|---|---|
| Default | `#FF5757` | `#0A0A0A` | none |
| Hover | `#E64D4D` | `#0A0A0A` | none |
| Active | `#D94444` | `#0A0A0A` | none |
| Disabled | `#2A2A2E` | `#8A8A8F` | none |
| Focus-visible | Double anneau §7 (noir interne + blanc externe) | | |

Min-height **44 px** ; padding horizontal 24 px. **Usage :** Hero P0, blocs conversion — **pas** le header ≥1280 px.

### 6.2 CTA header compact (≥1280 px)

| État | Fond | Texte | Bordure |
|---|---|---|---|
| Default | transparent | `#FFFFFF` | `1px #FFFFFF` |
| Hover | transparent | `#FFFFFF` | `1px #FF5757` |
| Focus-visible | Double anneau §7 (adapté fond sombre header) | | |

Libellé : **Demander un devis** ; icône Lucide **`ArrowUpRight`** 16 px, `aria-hidden="true"` ; pas de flèche Unicode textuelle si Lucide est utilisé ; fond transparent ; texte `#FFFFFF` ; bordure `1px #FFFFFF` ; **ne pas** utiliser `#FF5757` en fond.

### 6.3 Bouton secondaire (Hero / sections)

Fond transparent ; texte `#FFFFFF` ; bordure `1px #FFFFFF` ; hover bordure `#FF5757`.

### 6.4 Liens, nav, champs, menu mobile

Chaque contrôle définit **focus-visible** explicite (§7). Champs : bordure focus `#FFFFFF` 2 px + `outline-offset` 2 px.

---

## 7. Politique focus (sans perte clavier)

**Interdit :** règle globale `:focus { outline: none; }` sans remplacement garanti.

**Pattern obligatoire :**

1. Tous les interactifs ont **`:focus-visible`** avec contraste UI ≥ **3:1** sur la surface environnante.
2. Sur fond sombre (liens, nav, secondaire) : `outline: 2px solid #FFFFFF` ; `outline-offset: 3px`.
3. **Bouton primaire rouge** — pattern normatif (équivalent accessible autorisé, **anneau blanc externe obligatoire**) :

```css
.btn-primary:focus-visible {
  box-shadow:
    0 0 0 2px #0A0A0A,
    0 0 0 4px #FFFFFF;
}
```

4. Ne pas utiliser un **seul** anneau noir sur fond sombre sans anneau blanc externe.
5. Ne pas supprimer l’indicateur focus sans remplacement garanti sur le même élément.
6. Menu mobile ouvert : focus trap ; Échap ferme.

Ordre tab accueil : skip link → logo → menu (si visible) → liens nav → CTA header (≥1280 px) → contenu main.

---

## 8. Iconographie

Lucide (ISC) ; fonctionnel uniquement (menu, fermer, externe). Pas d’icônes décoratives dans La méthode Hive.

---

## 9. Tokens de mouvement

| Token | Valeur | Usage |
|---|---|---|
| `duration-fast` | 150 ms | Hover, focus |
| `duration-normal` | 250 ms | Header background |
| `duration-hero-reveal` | 400 ms | Entrée initiale Hero uniquement |
| `duration-chapter` | 300 ms | **Entrée unique** du chapitre « La méthode Hive » : opacity 0→1, translateY max 12 px ; contenu visible sans JS ; off si `prefers-reduced-motion` |
| `ease-out` | cubic-bezier(0.22, 1, 0.36, 1) | |
| `distance-reveal` | 12 px | Hero uniquement |

`prefers-reduced-motion: reduce` : durées 0 ms ; contenu visible sans translate/scale ; pas d’effets **non désactivables**.

Pas de GSAP requis V1.

---

## 10. Checklist design (001A)

- [x] Bouton primaire `#0A0A0A` sur `#FF5757`
- [x] Pas texte blanc sur accent pour CTA
- [x] Instrument Sans + Serif Italic scope
- [x] Focus policy §7
- [ ] Kyria : validation auto-hébergement fonts PREPROD

**Statut** = DRAFT_FOR_HUMAN_APPROVAL
