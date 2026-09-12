---
name: simplify
description: "Simplifier du code existant complexe ou répétitif sans modifier son comportement public ni élargir le périmètre."
---

# Simplify

1. Établir le comportement actuel avec tests et appelants.
2. Identifier complexité accidentelle, duplication réelle, niveaux d’indirection et branches mortes.
3. Préserver API publique, erreurs, données, accessibilité et performances sauf décision contraire explicite.
4. Simplifier par petites étapes vérifiables.
5. Éviter l’abstraction prématurée : trois lignes similaires ne justifient pas toujours une nouvelle couche.
6. Comparer avant/après : lisibilité, nombre de concepts, couverture et comportement.

Limiter le travail au code touché par le ticket. Ne pas transformer une simplification en refonte générale.
