---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Runbook - Sessions de travail

Remonte vers [[Architecture Mémoire]] (couche PLAYBOOK). Comment démarrer et finir n'importe quelle session de travail, par type.

## Boussole : je veux… → je fais

| Je veux… | Je fais |
|---|---|
| travailler sur un dossier client ou un projet | `cd "{{DOSSIERS_PROJETS}}/<CODE>/<Nom>" && claude` — le CLAUDE.md du projet fait le reste |
| piloter, ranger, décider, lancer un chantier | session vault : `cd "<racine du vault>" && claude`, puis [[Amorçage]] |
| coder | `cd <dépôt> && claude`, `git pull` d'abord, commit et push à la fin |
| voir où j'en suis | [[Centre]], section « quoi regarder », puis la skill `lint` |
| reprendre un chantier interne | son pack `90 - Meta/passation/<chantier>/` + [[Runbook - Chantiers (phase packs)]] |
| intégrer une source externe | [[Ingest - Sources externes]] |
| comprendre une incohérence | la skill `lint`, puis la matrice d'ownership d'[[Architecture Mémoire]] §2 |

## Où vit quoi — une source de vérité par fait

C'est la table la plus utile du vault. La colonne « jamais dans » compte autant que la première : c'est elle qui évite les doublons, et un doublon est une divergence différée.

À compléter à l'installation avec les substrats réels.

| Donnée | Vit dans | Jamais dans |
|---|---|---|
| état détaillé et travaux d'un dossier | _le substrat déclaré_ | le vault |
| fichiers, livrables, sources brutes | _l'espace documentaire déclaré_ | un dépôt de code |
| code et décisions techniques | le dépôt, son CLAUDE.md | le vault |
| **mémoire longue, décisions, pointeurs, pilotage macro** | **le vault** | le substrat métier |
| secrets, clés, identifiants | gestionnaire de secrets | le vault, un dépôt, un substrat partagé |
| conversations d'agent | local, par machine | le vault |

**Une conversation n'est pas un lieu de mémoire.** Ce qui doit lui survivre atterrit dans le substrat métier (les travaux), l'espace documentaire (les fichiers) ou le vault (les décisions et les pointeurs). Tout le reste disparaît, et c'est normal — c'est même la raison d'avoir un vault.

## 1. Session vault — pilotage, ontologie, chantiers

- **Démarrer** : `cd "<racine du vault>" && claude`. Amorçage : [[Amorçage]], puis [[Architecture - Vue d'ensemble]] si le contexte est ambigu.
- **Pendant** : écritures dans le vault seulement. Les décisions structurantes sont filées dans `60 - Journal/`. Aucune écriture directe vers un substrat externe hors skill dédiée.
- **Finir** : skill `cloture`. Vérifier le récap.

## 2. Session projet — un dossier client, une mission, un chantier métier

- **Démarrer** : `cd "<dossier du projet>" && claude`. Le CLAUDE.md du projet pointe vers son substrat canonique et vers sa fiche de vault.
- **Pendant** : les travaux détaillés dans le substrat, les fichiers dans l'espace documentaire, la fiche de vault en pilotage léger seulement.
- **Finir** : skill `cloture`.

## 3. Session code — un dépôt

- **Démarrer** : `cd <dépôt> && claude`, puis `git pull`. Les dépôts vivent hors de tout dossier synchronisé par un service de fichiers : un `.git` dans un dossier de synchronisation se corrompt tôt ou tard, parce que deux machines réécrivent l'index en même temps.
- **Pendant** : commits mono-sujet au fil de l'eau. **Un correctif repéré sur un autre dépôt se note dans le vault, il ne s'exécute pas** — c'est ce qui garde un commit lisible et évite de mélanger deux intentions.
- **Finir** : `git add` ciblés, commit, `git pull --rebase`, push. Arbre propre avant de fermer.

## 4. Session distante — sans accès à la machine

- **Démarrer** : la session part d'un clone frais. Elle n'a ni les dossiers locaux, ni les tâches planifiées, ni les skills de la machine. Sonder l'état par le dépôt distant : `git fetch`, `git log`, comptages, `git branch -r` pour voir si une autre session est en vol.
- **Pendant** : écritures sur **sa** branche uniquement, jamais la principale. Un périmètre par session. Ce qui exige la machine se traduit en **geste exact à coller**, jamais en contournement improvisé.
- **Finir** : pousser la branche, mettre les statuts de pack à jour. Le merge est un mandat explicite, pas une initiative.

## Transverse, toutes sessions

- **Un seul rédacteur par vault.** Deux sessions qui écrivent en même temps dans le même vault produisent des conflits sur `## Journal` et `## Actions` qu'il faut résoudre à la main.
- **Un seul exécutant par périmètre.** Concurrence détectée = arrêt et arbitrage.
- **Les secrets ne touchent jamais le vault.** Voir la ligne rouge de [[Conventions]] §9.
- **Tout artefact réutilisable produit en conversation doit atterrir dans le vault.** Une décision structurante → `60 - Journal/`. Une analyse transverse → `90 - Meta/`. Une simple cross-référence → deux liens `[[ ]]` et rien de plus. Pointeur jamais copie.

Le dernier point est celui qu'on oublie le plus, et c'est le seul qui fasse la différence entre un vault vivant et un dossier de notes mortes. Une analyse qui reste dans une conversation est perdue à la fin de la conversation : le travail a été fait, il ne sera pas retrouvé.
