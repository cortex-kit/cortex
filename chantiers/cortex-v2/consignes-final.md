# Consignes du chef d'orchestre, reprise finale après l'audit final (2026-09-19)

Worktree `~/Dev/cortex--final`, branche `fix/final`, issue de `main`. Mandat du chef : tu peux toucher tous les fichiers cités par `chantiers/cortex-v2/audit-final.md`, et eux seuls. Lis `04-contrat.md` en entier (amendements compris, dont le dernier sur I10) puis `audit-final.md`.

1. M-1 : I10 strict. Remplace chaque « On enchaîne ? » (cinq) par « quand vous voulez continuer, dites « <phrase canonique du maillon suivant> » » ; reporte l'arbitrage dans `references/doctrine.md:53` et `cortex-1-cadrage/SKILL.md:28` ; ajoute dans `parcours_blanc.py` un contrôle qui échoue si un SKILL.md maillon contient « On enchaîne » ou « lance `cortex- » hors section Notice.
2. M-2 : les quatre appels de skill en clôture (`cortex-1:178`, `cortex-3:163`, `cortex-4:129`, `cortex-5`) deviennent la phrase canonique de `PHRASES`.
3. Y-1 à Y-4 : `LISEZ-MOI.html` ne renvoie plus à un README absent du zip (donner la ligne d'installation dans la notice, ou renvoyer à `PROVENANCE.md`) ; `Architecture - Vue d'ensemble.md:70` dit six skills et deux sous-agents, sans « hors v1 » (N-8) ; `06-verification.md` mis à jour sur l'état de `main` (113 à 0, C4 16/16, écart `outillage_seul` clos) ; M4 ajouté aux contrôles manuels imprimés par la recette.
4. N-1 à N-7 : neuf maillons partout, ordinaux par position (« maillon N, le maillon 0 compris » ou rien), « étape » à la place de « maillon » dans les messages adressés à la personne, forme `uvx --from "markitdown[all]" markitdown` dans toute prose et dans le libellé M2, garde sur liste vide dans le grep white-label de `cortex-7`, compteur solo « 8 faites et 1 arbitrée » dans `etat.py main()`. N-5 (`stop-slop` en anglais) : ne traduis pas, ajoute une ligne en tête du SKILL.md qui dit que la référence est en anglais et que la skill répond en français.
5. Rejoue la recette (0 attendu, avec ton nouveau contrôle), les auto-tests touchés, `ast.parse` sous `/usr/bin/python3`, les greps white-label et chemins absolus. Colle les sorties.

Commits sur `fix/final` préfixés « Final : », aucun push, aucun merge. Rapport final : sorties, hash des commits, points en attente.
