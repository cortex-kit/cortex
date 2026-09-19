# Consignes du chef d'orchestre, reprise de la lane B après merge (2026-09-19)

Worktree `~/Dev/cortex--B2`, branche `fix/B`, issue de `main` après merge des six lanes. Tu possèdes `skills/cortex-0-poste/`, `skills/stop-slop/`, `outils/`, `notice/`, `skills/cortex-4-installation/scripts/{etat,rend_notice,notice}.py` et `notice.md`, `fabricant/`, `README.md`, `PROVENANCE.md`. Lis `04-contrat.md` en entier, amendements compris, puis `chantiers/cortex-v2/audit-B.md`.

1. Bloquant 1 : `poste.py:210`, aucun antislash dans une expression f-string ; `for f in $(git ls-files '*.py'); do /usr/bin/python3 -c "import ast,sys; ast.parse(open('$f').read())"; done` doit passer sous le Python système (3.9).
2. Défaut 2 : `installe_par_cortex` survit à deux `--ecrire` successifs ; témoin dans l'auto-test.
3. Défauts 5, 6, 7, 13, 14 : « 1 sur 9 » et jamais « 0 sur 8 » ; l'étape 8 n'est arbitrée « vault solo » qu'une fois `profil` connu ; `notice.py` pose `notice_ouverte_le` ; `poste.outils` liste tout le kit avec `present` vrai ou faux ; `organisation.code` (le slug demandé au maillon 0) écrit dans `config.yaml` et `poste.json`.
4. Défauts 8 à 11 : « 1 annexe » au singulier, commentaire de `PAQUET` à jour, tolérance d'un dossier `cortex-<non numérique>`, `recette/` exclu du zip.
5. Rejoue tes critères d'acceptation (poste.py --dry-run, notice hors ligne, `notice_ouverte_le`, zip par glob) et les cinq auto-tests, colle les sorties.

Commits sur `fix/B` préfixés « Lane B : », aucun push, aucun merge. Rapport final : sorties, hash des commits, points en attente.
