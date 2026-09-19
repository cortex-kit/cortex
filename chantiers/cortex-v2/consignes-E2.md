# Consignes du chef d'orchestre, reprise de la lane E après merge (2026-09-19)

Tu reprends la lane E sur l'arbre fusionné (worktree `~/Dev/cortex--E2`, branche `fix/E`). Tu possèdes `skills/cortex-4-installation/SKILL.md`, `skills/cortex-4-installation/scripts/{scaffold,lint_sante}.py`, `skills/cortex-4-installation/template/` (sauf `config.example.yaml`), `skills/cortex-5-ingest/`, `skills/cortex-6-agents-metier/`, `skills/cortex-7-passation/`, rien d'autre. Lis `04-contrat.md` en entier, amendements compris, puis `chantiers/cortex-v2/audit-E.md`.

1. B-1 : `copie_structurant.py` appelle `uvx --from "markitdown[all]" markitdown <src>` depuis un dossier temporaire (`cwd`), jamais depuis le vault ; même forme dans `cortex-5-ingest/SKILL.md` et les docstrings.
2. A-1 : dans `lint_sante.py`, la détection d'une lettre de lecteur se fait sur la chaîne `C:\Users` telle qu'écrite (un seul antislash dans le texte lu) ; ajoute un témoin dans l'auto-test.
3. A-2 : `scaffold.py` copie `copie_structurant.py` dans `<vault>/.claude/skills/ingest/` et `ingest/SKILL.md` décrit le rafraîchissement d'un structurant périmé en régime copie.
4. A-3 : `lint/SKILL.md` du vault documente les quatre contrôles ajoutés (régime, `structurant_perime`, `visibilite`, dernière clôture).
5. A-4 : le slug est `organisation.code` partout (contrat amendé) ; vérifie tes usages et dis-le.
6. Mineurs : M-2 (double annonce), M-3 (rendu lisible des constats à valeur dict, une ligne par constat : fichier puis raison), M-4 (`CLAUDE_PROJECT_DIR` puis repli sur le dossier courant, dans `session_start.py` et `stop.py`), M-5 (garde-fou de `export.py` fondé sur la présence du gabarit, pas sur `parents[5]`), M-6 (`argparse` avec `--autotest` dans les deux hooks), M-7 (retire « Sur accord, lancer `cortex-N+1` » de tes trois SKILL.md, la Notice suffit), M-8 (zéro tiret cadratin dans les lignes que tu touches).
7. Rejoue les huit critères d'acceptation de la ligne E et tes six auto-tests, colle les sorties. M-1 (permissions non mesurables hors session interactive) va dans `06-verification.md` par la lane G, pas par toi.

Commits sur `fix/E` préfixés « Lane E : », aucun push, aucun merge. Rapport final : sorties, hash des commits, points en attente.
