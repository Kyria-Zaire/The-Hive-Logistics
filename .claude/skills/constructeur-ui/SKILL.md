---
name: constructeur-ui
description: "Construire une page ou section Next.js responsive de THE HIVE LOGISTICS à partir d'une maquette ou d'un ticket validé."
---

# Constructeur UI

Lire `AGENTS.md` et `.claude/rules/frontend.md`.

1. Identifier contenu, composants, états, interactions et breakpoints attendus.
2. Vérifier les assets disponibles ; ne jamais inventer logo, métrique, témoignage ou partenaire.
3. Définir la structure sémantique et les tokens nécessaires avant le JSX.
4. Construire mobile, medium et desktop comme compositions intentionnelles.
5. Réutiliser les primitives accessibles et adapter visuellement shadcn si pertinent.
6. Garder les animations rares, fonctionnelles et compatibles `prefers-reduced-motion`.
7. Tester clavier, focus, zoom 200 %, débordement horizontal et images lentes/manquantes.
8. Effectuer une recette visuelle réelle aux largeurs prévues et joindre les écarts au rapport.

Refuser les recettes UI génériques : grille uniforme de cartes, gradients arbitraires, glassmorphism automatique, icônes décoratives incohérentes ou contenu de remplissage.
