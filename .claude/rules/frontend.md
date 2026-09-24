---
paths:
  - "apps/web/**/*.{ts,tsx,css,scss}"
  - "packages/ui/**/*.{ts,tsx,css,scss}"
---

# Frontend Next.js

- TypeScript strict, types explicites aux frontières et aucune utilisation non justifiée de `any`.
- Server Components par défaut ; ajouter `use client` uniquement pour une interaction qui l’exige.
- Séparer contenu, composants de présentation et logique d’intégration.
- Utiliser les primitives accessibles existants avant de créer un composant fondamental.
- Les composants shadcn sont une base à adapter, pas une identité visuelle prête à livrer.
- Définir couleurs, espacements, typographies, rayons, ombres et mouvement via des tokens.
- Préserver la direction THE HIVE : noir/blanc/anthracite, `#DC2626`, photographie premium nocturne, espaces généreux.
- Interdire les faux chiffres, faux témoignages, faux partenaires et textes métier inventés.
- `next/image` pour les images locales adaptées ; dimensions, `sizes`, priorité du LCP et alt pertinents.
- Animation limitée à `transform` et `opacity` quand possible ; honorer `prefers-reduced-motion`.
- Aucun effet ne doit bloquer navigation, lecture, Core Web Vitals ou appareils modestes.
- Valider 1440 px, 1024 px, 768 px et 390 px, clavier et zoom 200 %.

[MAJ 20/09/2026] Accent rouge changé sur décision client (Jores) : #FF5757 → #DC2626.
