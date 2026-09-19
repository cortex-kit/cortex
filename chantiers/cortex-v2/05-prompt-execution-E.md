# Lane E : couche vault

Tu exécutes la lane E du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--E`, branche `lane/E`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-4-installation/SKILL.md`, `skills/cortex-4-installation/scripts/{scaffold,lint_sante}.py`, `skills/cortex-4-installation/template/` sauf `config.example.yaml`, `skills/cortex-5-ingest/`, `skills/cortex-6-agents-metier/`, `skills/cortex-7-passation/`.

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-4-installation/scripts/scaffold.py` : `settings.json` généré selon `04-contrat.md` §9 (allow, `additionalDirectories`, une règle `deny` Write et Edit par racine), hooks SessionStart et Stop, `{{DOSSIERS_PROJETS}}` et toute racine substitués en forme `~`, proposition de `gh repo create <slug> --private --source . --push` sur accord.
- `template/vault/.claude/skills/parle/SKILL.md` et `bilan/SKILL.md` (`04-contrat.md` §9), `cloture/SKILL.md` étendue : export `_export/<slug>/` selon §6, régime copie.
- `skills/cortex-5-ingest/SKILL.md` : en régime copie, structurants proposés par lots de quatre jusqu'à `sante.max_structurants`, copiés dans `50 - Ressources/Structurants/` avec le frontmatter §2 ; fils de mail structurants en résumé anonymisé ; en régime pointeur, comportement v1.
- `skills/cortex-4-installation/scripts/lint_sante.py` : contrôle « 10 lignes » suspendu sur `50 - Ressources/Structurants/`, contrôle `structurant_perime`, contrôle `visibilite` dans l'enum, lecture de `sante.jours_sans_cloture_alerte` ; auto-test.
- `skills/cortex-7-passation/SKILL.md` : suivi J+7 et J+30 par `bilan`, remise qui ouvre la notice.
- `skills/cortex-4-installation/SKILL.md` : les gestes nouveaux du maillon 4 (settings, hooks, dépôt privé).
- Lis avant d'écrire le dépôt public `AgriciDaniel/claude-obsidian` (ledger de provenance par hash) pour le frontmatter des structurants.

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/E`, messages commençant par « Lane E : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
