# Consignes du chef d'orchestre, reprise de la lane D après merge (2026-09-19)

Worktree `~/Dev/cortex--D2`, branche `fix/D`, issue de `main`. Tu possèdes `skills/cortex-2-inventaire/`. Lis `04-contrat.md` en entier, amendements compris, puis `chantiers/cortex-v2/audit-D.md`.

1. D-1 : fusion si `--out` existe, selon le contrat amendé (§4, rejeu du scan) ; témoin dans l'auto-test : un bloc `mail` et un bloc `bases` posés à la main survivent au rejeu.
2. D-2 : `source_id` unique entre racines ; témoin avec deux racines `A/Travail` et `B/Travail`.
3. D-3 et D-4 : `collecte.max_extractions` (défaut 40) et `collecte.budget_secondes` (défaut 120), `sante.max_structurants` n'est plus lu par `scan.py` ; dépassement déclaré dans `bornes.depassement`.
4. Mineurs D-5 à D-13 : `import cortex_config` en tête avec un message clair en cas d'absence ; assertion sur `depassement` booléen ; `tilde()` documentée (absolu toléré hors du dossier personnel, contrat amendé) sans `.resolve()` qui sortirait du dossier personnel ; `graphify_propose` seulement si `langages` non vide et une fois par sous-arbre ; `.lnk` retiré des signaux ; « décidons mes domaines » à la place de l'identifiant de skill ; boucle des langages sortie de la boucle des racines ; `e.stat()` dans le `try`.
5. Rejoue `scan.py --autotest`, le scan des trois fixtures avec `time` (moins de 60 s sur dirigeant, cache `uv` chaud), colle les sorties.

Commits sur `fix/D` préfixés « Lane D : », aucun push, aucun merge. Rapport final : sorties, hash des commits, points en attente.
