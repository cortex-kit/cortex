---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Amorçage — comment une session charge ce vault

Remonte vers [[Centre]]. **Obsidian n'est pas requis** : ce vault est un dossier de fichiers `.md` et `.yaml` qu'un agent lit directement, et qu'un `grep` parcourt.

## Le problème

Ce vault est **passif** : il ne s'injecte nulle part. Une nouvelle session ne sait pas qu'il existe tant qu'on ne l'y renvoie pas.

Le lien vault → projet existe déjà, porté par `dossier_local`, `repo` et `url_canonique`. Ce qui manque est le lien **retour**, projet → vault. C'est ce que pose cette note, et c'est ce qui fait la différence entre une mémoire consultée et une mémoire oubliée.

## Surface 1 — une session lancée dans le vault

Le `CLAUDE.md` racine est lu automatiquement. Rien à faire : il porte le contrat d'entrée, les quatre opérations canoniques et l'ordre de lecture.

## Surface 2 — une session lancée dans un dossier de projet

Le `CLAUDE.md` du projet est lu automatiquement. Il doit porter ce bloc en tête, posé à la création du projet par la skill `nouveau-projet` :

```markdown
## Mémoire transverse

L'état, les décisions et les pointeurs de ce projet vivent dans le vault, pas ici.

- Vault : <chemin relatif ou absolu selon la machine>
- Fiche de ce projet : `20 - Projets/<CODE> - <Nom>.md`
- Contrat de données : `90 - Meta/Conventions.md`

Lire la fiche de ce projet, et ses liens, avant toute action de fond.
Ce CLAUDE.md reste canonique pour la TECHNIQUE ; le vault porte l'état et le pourquoi.
```

## Surface 3 — une session sans fichier lu automatiquement

Aucun amorçage n'a lieu. Il faut le donner en première instruction :

> Avant de travailler, lis le vault de {{ORGANISATION}} à `<chemin>`. Commence par `00 - Centre/Centre.md`, puis la fiche du projet concerné, puis `90 - Meta/Conventions.md`.

## Reprise à froid

Après une absence longue, dans cet ordre — il est conçu pour aller du général au particulier sans jamais lire plus que nécessaire :

1. [[Architecture - Vue d'ensemble]] — la carte, si le système n'est plus familier.
2. La skill `lint` — ce qui a dérivé pendant l'absence. C'est le geste le plus rentable : il donne en une commande la liste des projets dont personne ne sait plus rien.
3. `60 - Journal/`, les dernières notes par ordre de nom — les décisions prises depuis.
4. [[Centre]], section « quoi regarder » — l'état courant.

Ne pas commencer par la liste des projets. Un état lu sans les décisions qui l'ont produit se comprend de travers, et on refait des arbitrages déjà tranchés.

## Règle de cohérence

**Le back-pointer ne recopie rien : il pointe.** Le `CLAUDE.md` d'un projet reste canonique pour la technique, le vault pour l'état et les décisions.

Poser le back-pointer fait partie de la création de tout projet : voir [[Runbook - Nouveau Projet]]. Un projet sans back-pointer est un projet dont les sessions ignoreront le vault, donc dont les décisions ne seront jamais consignées.
