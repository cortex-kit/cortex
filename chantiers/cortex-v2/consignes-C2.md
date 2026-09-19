# Consignes du chef d'orchestre, reprise de la lane C après merge (2026-09-19)

Worktree `~/Dev/cortex--C2`, branche `fix/C`, issue de `main`. Tu possèdes `skills/cortex-1-cadrage/`, `skills/cortex-3-ontologie/`, `skills/cortex-4-installation/scripts/cortex_config.py`, `skills/cortex-4-installation/template/config.example.yaml`, plus, pour cette reprise seulement, le déplacement de `rejeu_profil.py` vers `skills/cortex-4-installation/recette/`. Lis `04-contrat.md` en entier, amendements compris, puis `chantiers/cortex-v2/audit-C.md`.

1. Bloquant 1, option 1 : les trois « Bloc config proposé » de `references/profils/*.md` ne gardent que `profil`, `mode`, `commun`, `donnees.regime`, `collecte` ; les domaines de départ restent en prose pour `00-cadrage.md` ; `config.yaml` garde `domaines: []` et `cycles: []` jusqu'au maillon 3. Critère C2 réécrit : `charger` relit les trois config sans erreur et `valider_installable` ne signale que l'absence de domaines.
2. Défaut 3 : `rejeu_profil.py` estampille `00-cadrage.md` en `statut: brouillon`, contrôles humains à `arbitre` avec le motif « rejeu sans personne » (contrat amendé).
3. Défaut 4 : `git mv skills/cortex-1-cadrage/scripts/rejeu_profil.py skills/cortex-4-installation/recette/rejeu_profil.py`, chemins relatifs adaptés, une ligne dans `cortex-1-cadrage/SKILL.md` qui le nomme comme outil de recette ; supprime le dossier `scripts/` de cortex-1.
4. Mineurs 5 à 9 : messages qui nomment la clé au lieu d'un traceback (`donnees`, `substrats` mal formés), `--help` de `cortex_config.py` à 0, « quatrième des neuf », accents dans les messages, tiret cadratin restant. Retire « Sur accord, lancer `cortex-N` » de `cortex-1` et `cortex-3` (invariant I10, la Notice suffit).
5. Rejoue le critère C2 réécrit, `cortex_config.py --autotest`, `rejeu_profil.py --autotest`, les cinq blocs `[?]` sur la fixture employé ; colle les sorties.

Commits sur `fix/C` préfixés « Lane C : », aucun push, aucun merge. Rapport final : sorties, hash des commits, points en attente.
