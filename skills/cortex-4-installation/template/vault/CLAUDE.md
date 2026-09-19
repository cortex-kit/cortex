# CLAUDE.md — second cerveau de {{ORGANISATION}}

Chargé automatiquement pour toute session d'agent lancée depuis ce dossier. C'est le contrat d'entrée : ce qui suit prime sur toute habitude.

## Ce qu'est ce vault, et ce qu'il n'est pas

Ce vault est la **mémoire longue et le pilotage léger** de {{ORGANISATION}}. Il indexe, relie et pointe. Il ne stocke pas.

| Il est | Il n'est pas |
|---|---|
| la mémoire du **pourquoi** des décisions | un journal de ce qui a changé (l'historique le fait) |
| l'état transverse et les priorités | le canon détaillé d'un dossier |
| l'annuaire des relations entre les choses | un espace de stockage de documents |
| le playbook des process répétables | un gestionnaire de tâches |
| le vault d'**un seul rédacteur**, {{REDACTEUR}} | un wiki d'équipe |

La confusion à éviter est toujours la même, et elle est confortable : tout mettre au même endroit. Un vault qui devient un double du substrat métier a doublé le travail de saisie et divisé par deux la confiance dans les deux copies.

## Règle d'entrée en session

1. Lire [[Architecture - Vue d'ensemble]] si le contexte est ambigu. C'est la carte.
2. Pour une question sur un projet : lire la fiche **complète** — frontmatter, `## Actions`, dernière entrée de `## Journal` — avant de répondre.
3. Restituer l'état et la prochaine action **avant** d'agir.

## Les 4 opérations canoniques

Toute session tombe dans l'une de ces quatre. Détail dans [[Architecture Mémoire]] §3.5.

**Ingest** — une source externe devient une note-pointeur dans `50 - Ressources/Sources externes/`. Résumé de {{SEUIL_JOURNAL}} lignes maximum, cross-références obligatoires. Procédure : [[Ingest - Sources externes]].

**Query** — lire dans cet ordre : [[Centre]] → note de domaine → note(s) de projet → contenu lié par `[[ ]]`. L'ordre n'est pas une préférence : une fiche projet lue sans son domaine perd le contexte qui la rend interprétable.

**Lint** — vérifier la santé contre les métriques d'[[Architecture Mémoire]] §7 :
`python3 .claude/skills/lint/lint_sante.py --vault .`

**Cloture** — vérifier la cohérence entre substrats, rapporter les trous, puis marquer **seulement** ce qui manque et a été validé. Si tout est déjà marqué : rapport de conformité, aucune écriture.

## Écritures permises

- Le vault : pointeurs, décisions, macro-actions, trous qualifiés, fiches projet.
- `.claude/` : les skills et sous-agents de ce vault.

## Écritures interdites

- **Tout substrat externe sur un champ miroir.** Sens unique, toujours : le substrat est canonique, le vault est miroir en lecture. Une écriture inverse crée un conflit qu'aucune règle ne peut trancher automatiquement.
- **Tout dépôt ou dossier non rattaché au projet courant.** Un correctif repéré au passage sur un autre périmètre se **note**, il ne s'exécute pas.
- **Aucun chemin absolu**, nulle part. Tout chemin passe par `chemins.dossiers_projets` de la configuration, et `dossier_local` est relatif. C'est ce qui rend ce vault utilisable sur une autre machine que celle qui l'a créé.
- **Aucune donnée sensible en clair** : coordonnées bancaires, mots de passe, identifiants fiscaux ou sociaux, scans d'identité. Voir [[Conventions]] §9. Ce vault est synchronisé, sauvegardé et lisible par un agent — trois qualités utiles, trois voies de fuite.

## Le contrat de données en trois lignes

- Les propriétés sont en minuscules, sans accent, sans tiret.
- `phase` appartient à l'enum de son `cycle`. `tags` utilise les codes de domaine déclarés. Les deux sont des **contrôles durs** du lint.
- Une entrée de `## Journal` fait {{SEUIL_JOURNAL}} lignes au maximum. Contrôle dur.

Ces trois contraintes sont vérifiées par une machine, et c'est délibéré : le système dont ce vault est issu documentait les mêmes règles sans les contrôler, et les trois ont dérivé.

Contrat complet : [[Conventions]]. Valeurs de cette installation : [[Configuration]] (généré, lecture seule).

## Détection de projet

Dès qu'un nom de projet est cité, avant toute action :

1. Chercher la fiche dans `20 - Projets/` (approximatif, insensible à la casse et aux accents — les noms propres sont saisis de plusieurs façons).
2. Lire la fiche complète.
3. Afficher un encart de 5 à 8 lignes : état et phase, dernier delta, macro-actions, blocage ou trou.
4. Proposer à copier-coller : `cd "<dossier_local résolu>" && claude`. **Proposé, jamais exécuté.**
5. Si la fiche ou le `dossier_local` est absent : **le signaler comme un trou**, proposer la skill `nouveau-projet`. Ne jamais deviner.

Le point 5 compte plus qu'il n'y paraît : une valeur devinée par un agent est indistinguable d'une valeur réelle une fois écrite, et c'est ainsi qu'un vault perd sa fiabilité — non par une grosse erreur, mais par une série de comblements plausibles.

## Les skills de ce vault

| Skill | Quand |
|---|---|
| `cloture` | à la fin de toute tâche, mission ou chantier. 3 à 10 fois par jour, moins de 30 secondes |
| `nouveau-projet` | création d'un projet : fiche, dossier, CLAUDE.md |
| `ingest` | une source externe à intégrer |
| `lint` | audit de santé, avant toute reprise à froid |

## Les sous-agents

`chercheur-vault` pour « qu'est-ce qu'on sait sur X » — il lit beaucoup, rend court. `auditeur-ontologie` pour les constats de conformité.

**Aucun sous-agent n'écrit.** Toute écriture reste dans le fil principal, là où {{REDACTEUR}} valide.

## Statut

Vault instancié le {{DATE}}. Mode `{{MODE}}`.
