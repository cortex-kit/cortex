# Lane F : fédération

Tu exécutes la lane F du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--F`, branche `lane/F`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-8-federation/`.

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-8-federation/SKILL.md` : quand la fédération commence (au moins deux vaults membres remplis), comment `federation.yaml` se crée dans le commun (`04-contrat.md` §6), comment relancer `federe.py`, ce que le commun ne fait jamais (être édité, porter une note `prive`), l'artefact `_cortex/07-federation.md` avec ses contrôles, la section « Notice » de §10.
- `skills/cortex-8-federation/scripts/federe.py` : stdlib, lit `federation.yaml` par `cortex_config.charger`, lit chaque `_export/<slug>/index.json`, vide et régénère le commun (Centre, Domaines fusionnés, Projets et Acteurs avec `source_vault`, acteur commun à deux rédacteurs fusionné en `source_vault: [a, b]`), `README.md` généré, `.cortex-genere` ; idempotent hors `genere_le` ; refuse une note `visibilite: prive` trouvée dans un export.
- Auto-test : trois exports construits à la main dans un dossier temporaire selon §6 (les fixtures `societe/` fournissent les noms), deux générations, `diff -r` vide hors `genere_le`.

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/F`, messages commençant par « Lane F : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
