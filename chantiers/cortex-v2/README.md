# Chantier Cortex v2 : Phase Pack

Cortex v2 fait d'un second cerveau v1 (sept maillons, vault pointeur, zip) un produit installable par un novice, en français, par plugin Claude Code, adapté à trois profils, avec un maillon d'équipement du poste, un scan outillé, un agent de dialogue, un suivi après remise et une fédération de plusieurs vaults.

## Ordre de lecture

1. `01-cadrage.md` : pourquoi, périmètre, non-objectifs, les 19 décisions, les invariants.
2. `02-arbo.md` : arborescence cible du dépôt et du vault, la chaîne v2 en face des cinq étapes.
3. `03-backlog.md` : phases et lanes, fichiers possédés, acceptation mesurable.
4. `04-contrat.md` : le contrat gelé. Toute lane le lit en entier avant d'écrire.
5. `05-prompt-execution-<lane>.md` : le seul fichier à coller dans la session d'une lane.
6. `06-prompt-review.md` : l'audit à froid d'une lane, dans une session neuve.

## Statut

| Phase | État | Date |
|---|---|---|
| A1 Repo | faite | 2026-09-19 |
| A2 Contrat | faite | 2026-09-19 |
| B, C, D, E, F | lancées en onglets cmux (`surface:148` à `152`), bypass total, worktrees `~/Dev/cortex--<lane>` | 2026-09-19 |
| G Recette | lancée en préparatoire (`surface:153`) | 2026-09-19 |
| H Parcours réel | après G | |
| I Remise | après H | |

## Conduite

- Chaque lane vit dans un worktree : `git -C ~/Dev/cortex worktree add ~/Dev/cortex--<lane> -b lane/<lane>`, créé par le chef d'orchestre avant d'ouvrir la session.
- Une lane ne touche que les fichiers qu'elle possède (`04-contrat.md` §1). Un besoin ailleurs se signale, il ne s'exécute pas.
- Ordre de merge : B, C, D, E, F, puis G. Chaque merge est précédé d'un audit à froid (`06-prompt-review.md`) en session neuve.
- Modèle exécutant des lanes B à G : Fable 5.1, effort `high` (lancées le 2026-09-19). Décision du 2026-09-19 : les sessions suivantes (audits à froid, relances de G, phases H et I) tournent en Opus 5, effort `high` ; les lanes Fable sont fermées dès leur rapport final.
- Le chef d'orchestre relaie, ne recopie pas, et ne franchit aucun point d'arrêt à la place de la personne.

## Version

Pack écrit le 2026-09-19 sur le commit de Phase A1 (`d386243`).
