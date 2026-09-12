---
name: thl-code-review
description: "Revoir un diff ou ticket THE HIVE LOGISTICS pour détecter bugs, régressions, failles et tests manquants sans modifier le code par défaut."
---

# Code Review THE HIVE

Par défaut, rester en lecture seule.

Vérifier le diff et ses appelants pour : correction fonctionnelle, conformité au ticket, sécurité, données, concurrence, erreurs, accessibilité, responsive, performance, compatibilité de migration et couverture de tests.

Classer chaque finding :

- `P0` exploitation/perte de données/incident immédiat ;
- `P1` bug ou faille bloquant la livraison ;
- `P2` défaut significatif à corriger ;
- `P3` amélioration non bloquante.

Chaque finding contient fichier, emplacement, scénario reproductible, impact et correction minimale. Ne pas lister de préférence personnelle sans conséquence observable.

Terminer par `APPROVE`, `REQUEST_CHANGES` ou `BLOCKED`, puis les tests manquants et risques résiduels.
