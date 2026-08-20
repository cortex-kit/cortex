---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Conventions — ontologie et contrat de données

Référence unique du système. Toute automatisation doit produire des notes conformes à ce contrat. Remonte vers [[Centre]].

Cette note ne porte **aucun enum en dur** : les valeurs qui varient d'une installation à l'autre — domaines, cycles, phases, axes commerciaux, seuils — vivent dans `config.yaml` et sont reflétées en lecture seule dans [[Configuration]]. La doctrine s'applique à elle-même la règle qu'elle impose : pointeur jamais copie.

## 1. L'ontologie

| Métaphore | Objet | Rôle |
|---|---|---|
| Le centre de gravité | [[Centre]] | point d'entrée unique, la note la plus connectée |
| Les centres secondaires | `10 - Domaines/` | les métiers ou process, entre 1 et 6 |
| Les nœuds à cycle de vie | `20 - Projets/` | unités de travail avec une échéance |
| Les petits nœuds nombreux | tâches `- [ ]` inline | hors du graphe, volontairement |
| Les captures non triées | `99 - Inbox/` | à trier ou à jeter |
| Les orbites | liens `[[ ]]` | la gravité, c'est-à-dire la densité de liens |
| Les thèmes transverses | tags `#` | ce qui traverse plusieurs domaines |

**Règle de gravité** : chaque note porte une propriété `domaine` qui la rattache à son centre, et chaque centre remonte à [[Centre]]. Aucune note orpheline — contrôle dur du lint.

Une note orpheline n'est pas seulement inélégante : elle est introuvable autrement qu'en s'en souvenant, ce qui est exactement la fonction que le vault est censé remplacer.

## 2. Le dossier porte le type, la propriété porte la logique, le lien porte la gravité

Principe architectural central :

- le **DOSSIER** détermine le TYPE — physique, stable ;
- la **PROPRIÉTÉ `domaine`** détermine l'appartenance logique — couleur, filtrage ;
- les **LIENS `[[ ]]`** créent les relations visibles dans le graphe.

**Ne jamais coder le domaine dans l'arborescence.** Deux projets de domaines différents vivent tous les deux dans `20 - Projets`. Le domaine est une propriété, pas un dossier.

La raison est pratique : une réorganisation de domaines — et il y en aura une — se fait alors en changeant une propriété, sans déplacer un seul fichier, donc sans casser un seul lien. Un vault dont les domaines sont des dossiers se réorganise à la main, ce qui veut dire qu'il ne se réorganise jamais.

## 3. Le contrat de frontmatter

| Propriété | Type | Valeurs / format | Sur quels types |
|---|---|---|---|
| `type` | texte | hub, meta, domaine, projet, action, acteur, ressource, decision, identite | toutes |
| `domaine` | lien | `"[[Nom du domaine]]"` | toutes sauf hub |
| `statut` | texte | idee, actif, attente, termine, archive | projet, domaine, acteur |
| `cycle` | texte | une clé de `config.cycles`, ou `aucun` | projet |
| `facturable` | booléen | true, false | projet |
| `phase` | texte | **valeur exacte de l'enum de son `cycle`** | projet |
| `progression` | nombre | 0 à 100 | projet |
| `priorite` | texte | P0, P1, P2, P3 | projet, action |
| `debut` / `echeance` | date | AAAA-MM-JJ | projet, action |
| `date` | date | AAAA-MM-JJ | decision |
| `client` / `partenaire` | lien | `"[[Acteur]]"` | projet |
| `responsable` | texte | | projet |
| `budget` | nombre | | projet |
| `payeur` | texte | une valeur de `config.payeurs` | projet |
| `vehicule` | texte | une valeur de `config.vehicules` | projet, acteur |
| `dossier_local` | texte | **chemin RELATIF** à `config.chemins.dossiers_projets` | projet |
| `substrat_canonique` | texte | l'outil qui porte le canon | projet |
| `url_canonique` | texte | l'adresse dans cet outil | projet, acteur |
| `repo` / `claude_md` | texte | | projet de code |
| `dernier_journal` | date | patché par la skill `cloture` | projet |
| `blocages_actifs` | nombre | patché par la skill `cloture` | projet |
| `categorie` | texte | client, prospect, partenaire, fournisseur | acteur |
| `courriel` / `telephone` | texte | | acteur |
| `dernier_contact` | date | AAAA-MM-JJ | acteur |
| `source_url` / `source_type` | texte | | ressource |

**Règle stricte de nommage : noms de propriétés en minuscules, sans accent, sans tiret.** Le tiret est interprété comme une soustraction par les moteurs de requête. Utiliser `_` si besoin.

### Deux propriétés qui méritent une explication

**`cycle` et non `nature`.** Un seul mot ne peut pas porter deux axes indépendants — « quel vocabulaire de phase s'applique » et « est-ce commercial ». Dans le système dont ce produit est extrait, il n'en portait qu'un nom pour les deux, et le résultat a été deux définitions contradictoires de ses valeurs autorisées dans deux notes canoniques différentes, puis sept fiches dont la `phase` était sortie de tout vocabulaire. D'où la séparation : `cycle` pour le vocabulaire, `facturable` pour l'axe commercial.

**`substrat_canonique` + `url_canonique`, et non le nom d'un outil.** Nommer une propriété d'après un fournisseur inscrit ce fournisseur dans l'ontologie. Le jour où l'organisation change d'outil, il faut renommer la propriété partout — ou vivre avec un nom qui ment.

## 4. Les tags

**Tags de domaine** : `#d/<code>`, où `<code>` vient de `config.domaines[].code`. Ils pilotent la couleur du graphe.

La casse et la liste des codes sont **contraintes par le lint**, pas documentées. C'est délibéré : dans le système d'origine, la casse était documentée et a dérivé quand même — deux variantes du même code, l'une en majuscules et l'autre développée, cohabitaient avec la forme canonique. Une convention qui n'est pas vérifiée par une machine n'est pas une convention, c'est un souhait.

**Tags transverses** : libres mais contrôlés. Ils portent des thèmes qui traversent les domaines.

**Anti-pattern, refusé par le lint** : un tag qui encode une logique déjà portée par une propriété — `#domaine-x`, `#vehicule-y`, `#phase-z`. Deux façons de dire la même chose finissent par se contredire.

Double rattachement volontaire : le **lien** `domaine` sert aux requêtes et à la gravité ; le **tag** `#d/<code>` sert à colorer le graphe de façon fiable.

## 5. Les actions : inline par défaut

Seuil de décision :

- **macro-action de pilotage** — un pointeur à vérifier, une décision à ancrer, un trou à qualifier, une dépendance transverse → case `- [ ]` sous `## Actions` de la fiche projet ;
- **micro-tâche** (moins d'une journée, sans sous-étapes) → case dans la fiche, hors du graphe ;
- **jalon avec dépendances et échéance critique** → note `type: action` dédiée.

Justification : trois cents tâches font trois cents fichiers, donc un graphe illisible. Garder les petites tâches hors du graphe préserve sa lisibilité, qui est sa seule utilité.

**Anti-pattern** : recopier ici le backlog du substrat canonique. Le vault marque le pointeur, la décision, la macro-action ou le trou. Le travail détaillé reste où il est suivi.

### Les trous qualifiés

Pas de section dédiée. Un trou est une ligne de `## Actions` :

```
- [ ] Qualifier <sujet> #d/<code> #trou [trou_id:: slug] [trou_statut:: ouvert]
```

`trou_statut` : `ouvert` → `valide` → `clos`. Le tag `#trou` est obligatoire pour qu'un lint puisse agréger.

**La skill `cloture` ne marque que les trous déjà validés.** Elle n'en invente jamais un, et ne fait jamais passer `ouvert` à `valide` sans accord explicite : un trou est un constat, et un constat inventé par un agent est indistinguable d'un constat réel une fois écrit.

Un trou clos reste dans `## Actions`, coché, jusqu'à l'archivage de la fiche. La trace de ce qui a été levé vaut autant que la liste de ce qui reste.

## 6. Le graphe

Les groupes de couleur sont **générés** dans `.obsidian/graph.json` depuis `config.domaines[].couleur`. Aucune configuration manuelle, aucun plugin.

Le graphe n'est pas décoratif : c'est la structure de pilotage. Chaque objet a une masse — son nombre de liens — et une position — son domaine. Une note très liée est une note qui compte, et c'est un indicateur plus honnête que sa longueur.

Réglages utiles : masquer les pièces jointes, désactiver l'affichage des tags (sinon bruit), resserrer la force des liens.

## 7. Les sections des fiches projet

Ordre canonique, et il est réservé :

`## Actions` → `## Décisions` → `## Journal` → `## Pointeurs`

Toute autre section doit être justifiée par le type de projet.

**Partage strict des zones d'écriture entre skills** : chaque skill n'écrit que dans les sections qui lui sont attribuées, et `## Pointeurs` n'est jamais réécrit automatiquement. Sans ce partage, deux skills se marchent dessus et la dernière lancée écrase le travail de l'autre.

`## Pointeurs` contient les adresses des sources canoniques. **Aucun contenu canonique n'y est recopié.**

## 8. Le carnet de décisions

Le vault garde la mémoire du **pourquoi**, jamais du **quoi** technique, déjà présent dans l'historique du dépôt ou du substrat.

**Seuil** : on ne journalise que les décisions **structurantes** — choix d'architecture, bascules de stratégie, arbitrages, abandons motivés. Pas le quotidien opérationnel.

- Décision structurante ou transverse → note `type: decision` dans `60 - Journal/`, depuis [[_Template Décision]]. Nœud lié, visible dans le graphe, requêtable.
- Décision mineure locale → puce datée sous `## Décisions` de la fiche projet.

Contrat de la note `decision` : `type`, `date` (celle où la décision est actée), `domaine` (optionnel si transverse), `projet` (liste de liens), `statut` (`actee`, `revisee`, `annulee` — pour tracer un revirement).

Corps : la décision, le pourquoi, **l'arbitrage écarté**, le pointeur vers l'artefact. Nom de fichier : `AAAA-MM-JJ - Titre court.md`, pour un tri chronologique par nom.

L'arbitrage écarté est la partie la plus utile et la plus souvent omise. Dans six mois, la question ne sera pas « qu'a-t-on décidé » — c'est visible dans le résultat — mais « avait-on envisagé l'autre voie, et pourquoi l'a-t-on écartée ». Sans cette section, on refait le débat.

## 9. Les fiches identité

Type `identite`, dossier `80 - Identité`. Données d'immatriculation **semi-publiques**, pour remplir un formulaire administratif en lisant le frontmatter plutôt qu'en ressaisissant.

**Ligne rouge de sécurité, cardinale : aucune donnée sensible en clair.**

Interdits, sans exception : coordonnées bancaires, mots de passe, identifiants fiscaux ou sociaux, numéros de sécurité sociale, scans de pièces d'identité.

Ces éléments vivent hors du vault — gestionnaire de mots de passe ou dossier chiffré — et la fiche n'en porte qu'un pointeur textuel. La raison est mécanique : un vault est synchronisé, sauvegardé, indexé et parfois lu par un agent. Chacune de ces propriétés est utile, et chacune est une voie de fuite pour un secret. Le vault est conçu pour être **facilement lisible** ; c'est incompatible avec le stockage d'un secret.

Le champ des données à ne jamais écrire est plus large que la liste : en cas de doute sur un élément, il ne va pas dans le vault.
