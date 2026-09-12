---
name: createur-workflow
description: "Concevoir ou modifier un workflow CI/CD reproductible, à moindre privilège et séparé entre recette, préproduction et production."
---

# Créateur workflow

Avant l’écriture, cartographier déclencheur, permissions, secrets, artefacts, environnements et rollback.

Exigences :

- checks rapides avant jobs coûteux ;
- versions et lockfiles reproductibles ;
- actions tierces pinnées par SHA complet ;
- permissions GitHub minimales et explicites ;
- aucun secret exposé aux PR non fiables ;
- artefact construit une fois puis promu ;
- RECETTE automatique possible après checks ; PREPROD contrôlée ; PROD avec approbation humaine ;
- migrations séparées, observables et non destructives ;
- concurrence empêchant deux déploiements incompatibles ;
- logs sans secrets et conservation adaptée ;
- rollback documenté et testable.

Ne jamais exécuter le workflow ou déployer depuis ce skill sans autorisation explicite.
