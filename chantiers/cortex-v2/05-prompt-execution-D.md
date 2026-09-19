# Lane D : scan outillé

Tu exécutes la lane D du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--D`, branche `lane/D`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-2-inventaire/`.

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-2-inventaire/scripts/scan.py` : stdlib, `--racine` (répétable) ou `--config`, `--out` ; parcourt le disque dans les bornes de `collecte` et les mesure en entiers (`04-contrat.md` §4, bloc `bornes`) ; relève dossiers, extensions, dates, dépôts git, signaux de base déportée (exports csv d'outils, fichiers `.base`, liens) ; extrait le texte des candidats structurants par `uvx markitdown` si présent, borné en octets, texte réduit à des mots-signaux (jamais stocké) ; refuse d'écrire un champ `contenu`.
- `skills/cortex-2-inventaire/SKILL.md` : appel de `scan.py`, puis remplissage du bloc `mail` par l'agent selon la voie de `poste.json` et le tableau `04-contrat.md` §7 ; `ecarts_candidats` dérivés ; Graphify proposé (jamais installé d'office) quand un dépôt de code ou un dossier de plus de 500 documents est détecté ; la section « Notice » inchangée.
- Auto-test de `scan.py` sur `skills/cortex-4-installation/recette/fixtures/dirigeant/` (générer par `python3 skills/cortex-4-installation/recette/fixtures.py` si absent).

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/D`, messages commençant par « Lane D : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
