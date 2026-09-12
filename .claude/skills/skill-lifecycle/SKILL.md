---
name: skill-lifecycle
description: "Créer, évaluer, améliorer ou benchmarker un skill de développement du projet avec critères observables et sans accumulation de règles génériques."
---

# Skill Lifecycle

Choisir un mode explicite : `CREATE`, `EVAL`, `IMPROVE` ou `BENCHMARK`.

## CREATE

Définir les requêtes déclencheuses, les exclusions, les décisions non évidentes et les preuves attendues. Créer un dossier nommé en minuscules avec `SKILL.md`, frontmatter `name`/`description` et seulement les ressources nécessaires.

## EVAL

Tester le skill sur une requête réaliste isolée. Évaluer déclenchement, respect du périmètre, qualité de l’artefact, sécurité et coût de contexte. Ne pas fournir à l’évaluateur la réponse attendue.

## IMPROVE

Modifier uniquement ce qu’un échec observé justifie. Retirer répétitions, prescriptions génériques et collisions. Rejouer l’évaluation concernée.

## BENCHMARK

Comparer skill activé/désactivé sur les mêmes cas et critères : correction, omissions, sécurité, temps, tokens et retouches humaines. Une différence de style seule n’est pas un gain.

Toujours valider frontmatter, liens et absence de placeholders. Ne jamais donner des permissions larges dans `allowed-tools` sans besoin concret et revue humaine.
