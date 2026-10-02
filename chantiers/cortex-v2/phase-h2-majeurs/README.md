# Phase H2 : les majeurs du parcours réel

Le parcours réel de la Phase H (client fictif Alcyon Promotion, 2026-09-27) a laissé 3 bloquants et 10 majeurs. Les bloquants sont corrigés sur `fix/phase-h` et rejoués. Cette phase traite les 10 majeurs et les mineurs peu coûteux, puis rejoue le parcours complet. La Phase H est validée, et le tag v2.0.0 autorisé, quand ce parcours sort sans bloquant et avec au plus 3 majeurs.

## Ordre de lecture

1. `01-cadrage.md` : pourquoi, périmètre, non-objectifs, décisions actées.
2. `02-backlog-produit.md` : ce que la personne doit vivre autrement, défaut par défaut.
3. `03-backlog-technique.md` : fichiers par lane, points d'accroche dans le code.
4. `04-contrat.md` : les interfaces partagées entre les lanes A et B, et les règles de conduite.
5. `05-execution.md` : les tâches, lane par lane, et les points d'arrêt.
6. `06-verification.md` : critères cochables, contre-épreuves, Definition of Done.
7. `07-prompt-execution-A.md`, `07-prompt-execution-B.md`, `07-prompt-execution-C.md` : le seul fichier à coller dans la session d'une lane.
8. `08-prompt-verification.md` : l'audit à froid d'une lane, en session neuve.
9. `annexe-parcours-alcyon.md` : le script du parcours rejoué en Phase C.

Source des défauts : `~/Cortex-test/verdict-phase-h.md`, hors dépôt.

## Lanes

| Lane | Objet | Worktree | Branche | Exécutant | Effort |
|---|---|---|---|---|---|
| A | code : `poste.py`, `etat.py`, `lint_sante.py`, `federe.py`, hooks, `scan.py`, recette | `~/Dev/cortex--h2a` | `lane/h2a` | Opus 5.5 | `high` |
| B | conduite : les neuf `SKILL.md`, `doctrine.md`, `README.md`, `outils/OUTILS.md` | `~/Dev/cortex--h2b` | `lane/h2b` | Opus 5.5 | `high` |
| C | parcours Alcyon complet, pilote au clavier | `~/Cortex` (poste) | aucune | Opus 5.5 | `high` |

A et B partent en parallèle depuis `fix/phase-h`, fichiers disjoints. C part après le merge de A et B dans `fix/phase-h`. Auditeur de chaque lane : Opus 5.5, effort `high`, session neuve.

## Statut

Tenu par le chef d'orchestre, jamais par une lane.

| Étape | État | Date |
|---|---|---|
| Pack écrit | fait | 2026-09-29 |
| Lane A | faite, auditée (mergeable, 1 majeur repris), reprise mergée | 2026-10-02 |
| Lane B | faite, auditée (3 bloquants repris), reprise mergée | 2026-10-02 |
| Audits A et B | faits | 2026-10-02 |
| Merge dans `main` (= `fix/phase-h`) | fait, plugin rc.7 | 2026-10-02 |
| Lane C, parcours | lancée (pilote Opus depuis `~/Cortex-test`, plugin rc.7, fixtures neuves) | 2026-10-02 |

## Version

Pack écrit le 2026-09-29 sur `fix/phase-h` (`01955f6`), plugin 2.0.0-rc.6, recette 117 contrôles verts.
