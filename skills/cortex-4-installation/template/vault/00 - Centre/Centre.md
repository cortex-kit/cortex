---
type: hub
tags:
  - hub
---
# Centre — {{ORGANISATION}}

> [!info] Le point d'entrée. Toute note remonte ici, directement ou par son domaine.

Ce vault est la mémoire longue et le pilotage léger de {{ORGANISATION}}. Il pointe vers les substrats qui portent le travail réel ; il n'en garde aucune copie.

## Par où je commence

| Je veux… | Je lis |
|---|---|
| comprendre le système en 30 secondes | [[Architecture - Vue d'ensemble]] |
| démarrer ou finir une session | [[Runbook - Sessions de travail]] |
| créer un projet | [[Runbook - Nouveau Projet]] |
| savoir où vit une information | [[Architecture Mémoire]] §2 |
| connaître le contrat de données | [[Conventions]] |
| voir les valeurs de cette installation | [[Configuration]] |
| mener un chantier interne | [[Runbook - Chantiers (phase packs)]] |
| intégrer une source externe | [[Ingest - Sources externes]] |
| poser une question sur mon travail | dire « parle », puis la question : la réponse cite les notes |
| savoir ce qui a bougé | dire « bilan » |
| reprendre à froid après une absence | [[Amorçage]] |

## Les domaines

{{DOMAINES_LISTE}}

## Quoi regarder, et dans quel ordre

Il n'y a pas de tableau de bord ici, et c'est volontaire : une vue construite sur un état qui n'est pas encore propre donne l'impression rassurante de piloter. Elle viendra quand les données la mériteront.

En attendant, quatre gestes couvrent tout, sans aucun plugin à installer :

1. **Ce qui est actif** — ouvrir `20 - Projets`, trier sur `statut` puis `priorite` dans le panneau Propriétés.
2. **Ce qui arrive** — trier sur `echeance` dans le même panneau.
3. **Ce qui a bougé récemment** — trier sur `dernier_journal`. Un projet actif sans entrée depuis deux semaines est un projet dont on ne sait plus rien : le lint le signale.
4. **Ce qui est en souffrance** — `python3 .claude/skills/lint/lint_sante.py --vault .` Les contrôles durs sont les vrais problèmes ; les avertissements sont de la dette à surveiller.

Le **graphe** montre la structure : ce qui est très lié est ce qui compte. Le panneau **Liens entrants** d'une note répond déjà à « qu'est-ce qui dépend de ça ».

Si Dataview est installé un jour, [[Vue Obsidian (Dataview, optionnel)]] contient les requêtes équivalentes. Aucune autre note n'en dépend : le vault fonctionne entièrement sans.

## Le journal des décisions

`60 - Journal/` — une note par décision structurante, nommée `AAAA-MM-JJ - Titre`, donc triée chronologiquement par son nom.

C'est la partie du vault qui prend de la valeur avec le temps. L'état se périme, les décisions et leurs raisons ne se périment pas — et la question qui revient à six mois n'est jamais « qu'a-t-on fait » mais « pourquoi a-t-on écarté l'autre voie ».

## L'inbox

`99 - Inbox/` — les captures non triées. Elle doit se vider, pas grossir. Une inbox qui accumule est le symptôme d'un vault dans lequel on ne sait plus où ranger, donc d'une ontologie à revoir plutôt que d'une discipline à durcir.
