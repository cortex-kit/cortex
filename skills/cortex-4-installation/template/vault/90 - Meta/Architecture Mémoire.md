---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Architecture Mémoire — document de cadrage

Remonte vers [[Centre]]. Contrat de données : [[Conventions]].

Ce document cadre tout le vault. **Aucune note ne doit contredire ce qui suit.** Toute évolution du modèle se décide ici d'abord, sinon la doctrine se fragmente en versions locales qui divergent sans que personne ne s'en aperçoive.

## 0. Raison d'être : 4 fonctions, 4 couches

Ce vault n'est pas un classeur. Il remplit quatre fonctions, qui se traduisent en quatre couches empilées sur un socle d'état.

| Fonction | Couche | Rôle |
|---|---|---|
| Garder la mémoire des travaux et des décisions | JOURNAL | le pourquoi de ce qui a été fait |
| Mettre les process à plat, puis automatiser | PLAYBOOK | procédures répétables + carte des outils |
| Voir où en sont les projets | VUE | tableau de bord, dans un second temps |
| Se transmettre à un tiers | contrainte transverse | critère de qualité, pas une couche (§5) |

La couche ÉTAT — domaines, projets, acteurs — est le socle sur lequel les quatre reposent.

## 1. Règle cardinale

**Une seule source de vérité par type de fait.** Ce vault ne recopie rien : il indexe, relie, et pointe vers la source canonique.

C'est le prolongement de la thèse : le DOSSIER porte le type, la PROPRIÉTÉ porte la logique, le LIEN porte la gravité, la NOTE porte un pointeur — jamais une copie.

La raison n'est pas l'élégance. Un fait présent en deux endroits finit par différer, et à ce moment-là on ne sait plus lequel croire — donc on ne croit plus ni l'un ni l'autre, et la mémoire ne sert plus à rien. Un doublon n'est pas une redondance de sécurité, c'est une divergence différée.

**Métrique d'audit : 0 note recopiant plus de {{SEUIL_JOURNAL}} lignes d'une source canonique.** Contrôle dur du lint.

## 2. Les substrats et leur ownership

La mémoire de l'organisation vit sur plusieurs substrats. Ce vault ne les remplace pas : il les indexe.

Cette matrice est le premier livrable de l'installation. Elle se remplit **une fois**, à partir de l'inventaire réel, et elle est ce qui rend toutes les autres règles applicables : sans elle, « une source de vérité par fait » est un slogan.

| Type de fait | Source de vérité | Rôle du vault |
|---|---|---|
| Documents, livrables, fichiers bruts | _à renseigner_ | note projet : `dossier_local` |
| État détaillé des projets ou dossiers | _à renseigner_ | note projet : `substrat_canonique` + `url_canonique`, miroir léger |
| Code et décisions techniques | _à renseigner_ | note projet : `repo`, `claude_md` |
| Coordonnées des personnes | _à renseigner_ | pointer, jamais recopier |
| Procédures exécutables | `.claude/skills/` | pointer |
| **Relations, état transverse, priorités, DÉCISIONS, macro-actions, trous qualifiés** | **ce vault** | **source de vérité ici** |

La dernière ligne est le territoire propre du vault. Tout le reste, il le pointe.

**Un lien manquant dans cette table est un piège.** Si un type de fait n'a pas de source déclarée, il finira écrit deux fois. Mieux vaut une ligne `_à renseigner_` visible qu'une case remplie au hasard.

### Le lien interdit

Il en existe au moins un dans toute installation : le sens d'écriture qui créerait une double écriture sur un champ déjà miroir. Il se déclare explicitement, avec la mention **INTERDIT**, dans [[Architecture - Vue d'ensemble]] (c). Un sens interdit non écrit est un sens qui sera pris.

## 3. Les 4 couches en détail

### 3.1 ÉTAT (le socle)

Où en sont les choses maintenant. Une note par projet, domaine, acteur. Frontmatter conforme à [[Conventions]].

**Chaque projet actif porte au moins un pointeur canonique** — `url_canonique`, `repo` ou `dossier_local`. Contrôle dur du lint : un projet sans pointeur est un projet dont on ne peut pas retrouver le travail réel, donc une fiche qui ne sert à rien.

### 3.2 JOURNAL (le carnet de décisions)

Ce que le vault garde en mémoire, c'est le **POURQUOI**, pas le QUOI.

Le code est déjà historisé dans son dépôt ; l'état des dossiers dans son substrat. Le vault ne consigne donc ni les modifications, ni les changements de statut. Il consigne uniquement **ce qui n'existe nulle part ailleurs** : les décisions et les arbitrages.

- Un commit dit **quoi** a changé. Le journal dit **pourquoi** on l'a décidé.
- On y note : choix d'architecture, bascules de stratégie, arbitrages commerciaux, raisons d'un abandon.
- Format : date, décision, pourquoi, pointeur vers l'artefact.

Deux seuils, deux formats : décision structurante ou transverse → note `type: decision` dans `60 - Journal/`, requêtable et visible dans le graphe. Décision mineure locale → puce datée sous `## Décisions` de la fiche projet. Contrat détaillé : [[Conventions]].

**Une entrée de journal fait {{SEUIL_JOURNAL}} lignes au maximum.** Contrôle dur. Au-delà, ce n'est plus une décision, c'est un compte rendu — et un compte rendu appartient au substrat canonique. Ce plafond est ce qui garde le journal lisible à trois semaines, qui est le seul moment où on le relit.

### 3.3 PLAYBOOK (process et outillage)

Deux livrables :

1. **La carte des outils** : quel projet tourne sur quoi, et où sont rangées les clés — un pointeur, jamais le secret.
2. **Le runbook de démarrage** : la checklist répétable, qui pointe vers les skills quand elles couvrent une étape. Voir [[Runbook - Nouveau Projet]].

**L'automatisation vient APRÈS la mise à plat, jamais avant.** On ne standardise un process qu'une fois cartographié, et on n'automatise qu'une étape stable. Automatiser un process instable ne fait que le rendre plus difficile à corriger.

### 3.4 VUE (tableau de bord)

Explicitement dans un second temps. Une vue **lit** les sources de vérité selon leur ownership ; elle ne stocke rien.

À construire en dernier, sur données propres : **un tableau de bord sur un modèle d'état sale ne vaut rien**, il donne seulement l'impression rassurante de piloter.

### 3.5 Les 4 opérations canoniques

Elles cadrent toutes les sessions. Détail dans le `CLAUDE.md` racine.

- **Ingest** — créer des pointeurs synthétiques vers des sources externes, jamais une copie longue. Note `type: ressource`, résumé ≤ {{SEUIL_JOURNAL}} lignes, cross-références obligatoires. Voir [[Ingest - Sources externes]].
- **Query** — lire dans l'ordre : [[Centre]] → note de domaine → note(s) de projet → contenu lié par `[[ ]]`. Cet ordre n'est pas une préférence : lire une fiche projet sans son domaine fait manquer le contexte qui la rend interprétable.
- **Lint** — vérifier la santé contre les métriques du §7. `python3 .claude/skills/lint/lint_sante.py --vault .`
- **Cloture** — vérifier la cohérence entre les substrats, rapporter les trous, puis marquer **seulement** les pointeurs, décisions, macro-actions et trous validés manquants. Aucune écriture si tout est déjà marqué : dans ce cas, rapport de conformité uniquement.

La clôture est une opération, pas une couche : elle n'ajoute aucune source de vérité, elle audite l'existant.

## 4. Les axes de classement

`domaine` porte la gravité et la couleur : c'est le process ou le métier qui s'applique.

Deux axes commerciaux **optionnels** sont disponibles, activés par la configuration : `vehicule` (la marque qui vend) et `payeur` (qui verse l'argent). Liste vide = axe non utilisé, et c'est le cas par défaut.

Ne jamais les confondre, et ne jamais leur faire partager une valeur : une marque n'est pas un payeur. Le lint le vérifie. Ces deux axes ne servent qu'aux organisations qui vendent sous plusieurs marques ou encaissent via plusieurs entités ; ailleurs, les laisser vides est le bon choix.

## 5. Transmission : traitée

Un vault n'est transmissible que si aucune de ses notes ne dépend de la machine qui l'a créé.

**Aucun chemin absolu dans le vault.** Tout chemin passe par `chemins.dossiers_projets` de la configuration, et `dossier_local` est **relatif** à cette racine. Contrôle dur du lint.

C'est la seule contrainte qui rende la transmission réelle, et c'est aussi celle qu'on enfreint le plus facilement, parce qu'un chemin absolu fonctionne parfaitement — sur une machine. Dans l'installation qui a servi de modèle à ce produit, 96 fichiers portaient 193 chemins absolus, et la transmission était restée déclarée « reportée » pour cette seule raison.

Corollaires : un pointeur vers un substrat externe est une **URL**, jamais un chemin monté localement. Et la configuration est un fichier du vault, pas un réglage de l'éditeur.

## 6. Fraîcheur : sens unique

Tout flux automatique va dans **un seul sens**, du substrat canonique vers le vault. Aucune écriture inverse.

**Interdiction : le vault n'écrit jamais vers un substrat sur un champ miroir.** Une synchronisation bidirectionnelle sur le même champ produit un conflit dont on ne peut pas décider automatiquement, et le résultat est que la valeur alterne silencieusement entre deux états.

Un miroir se reconnaît à ceci : la valeur est saisie ailleurs et copiée ici pour la commodité. Elle n'est pas à nous. On la lit.

## 7. Santé mesurable

Les cibles ci-dessous sont **exécutables**, pas déclaratives. Chacune est un contrôle du lint, et les quatre premières sont bloquantes.

- 0 note recopiant plus de {{SEUIL_JOURNAL}} lignes d'une source canonique.
- 100 % des projets actifs avec un pointeur canonique vivant.
- 0 tag encodant une logique déjà portée par une propriété.
- 0 `phase` hors de l'enum de son `cycle`.
- 0 note orpheline : sans `domaine` ni lien sortant.
- 0 chemin absolu.
- Couverture : tout engagement actif a un nœud dans le vault.

Une métrique qui n'est pas mesurée par un script n'est pas une métrique, c'est une intention. C'est la leçon la plus coûteuse du système dont ce produit est extrait : ses deux dérives les plus graves — les journaux devenus des comptes rendus, et `phase` sorti de son vocabulaire sur sept fiches — étaient **détectées et affichées en avertissement pendant des mois**, sans rien empêcher.

## 8. Ordre de construction

1. **ÉTAT assaini** — domaines déclarés, contrat de frontmatter respecté, lint vert.
2. **JOURNAL** — le format est posé, le réflexe de clôture tourne.
3. **PLAYBOOK** — les procédures répétables, une fois qu'on a vu ce qui se répète.
4. **Automatisation** — seulement sur les étapes devenues stables.
5. **VUE** — en dernier, sur données propres.

Prendre cet ordre à l'envers est l'erreur classique : on construit le tableau de bord d'abord, parce que c'est ce qui se voit, et il affiche fidèlement un état qui n'est pas fiable.
