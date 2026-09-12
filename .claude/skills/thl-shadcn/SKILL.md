---
name: thl-shadcn
description: "Sélectionner, intégrer et adapter des primitives shadcn pour THE HIVE LOGISTICS avec accessibilité et identité premium."
---

# shadcn pour THE HIVE

- Vérifier qu’un primitive est réellement utile avant de l’ajouter.
- Utiliser la CLI officielle et une version décidée par le projet ; ne pas copier un snippet inconnu.
- Lire le code généré : shadcn devient du code du dépôt et doit respecter nos tests et règles.
- Conserver comportements ARIA, clavier, focus, portal et gestion d’état du primitive.
- Remplacer le style par les tokens THE HIVE plutôt que multiplier les overrides locaux.
- Ne pas ajouter une bibliothèque concurrente pour un composant déjà couvert.
- Tester dark theme, mobile, zoom, reduced motion, erreur et contenu long.
- Documenter toute divergence volontaire avec le primitive upstream.
