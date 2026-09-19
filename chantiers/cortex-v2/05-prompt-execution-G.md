# Lane G : recette

Tu exécutes la lane G du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--G`, branche `lane/G`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-4-installation/recette/`, `chantiers/cortex-v2/06-verification.md`.

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-4-installation/recette/parcours_blanc.py` : neuf étapes (`04-contrat.md` §5), trois profils sur `fixtures.py` (cadrage, inventaire par `scan.py` quand la lane D est mergée, scaffold, lint, régimes pointeur et copie), fédération sur trois exports fictifs, validité des manifestes plugin, grep white-label et zéro chemin absolu sur `skills/ notice/ outils/ README.md`, tableau C1 à C10. Tant que les lanes ne sont pas mergées, la recette est rouge : c'est attendu, elle est la cible. Chaque contrôle nouveau porte son « défaut plausible » comme en v1.
- `chantiers/cortex-v2/06-verification.md` : le tableau C1 à C10 avec, pour chaque critère, la commande et sa sortie ; les contrôles manuels (installation vivante du plugin, sonde Cowork, maillon 0 sur la machine Windows) avec leur sortie collée.
- `fixtures.py` : n'y touche que si un profil manque un signal dont la recette a besoin, et dis-le.

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/G`, messages commençant par « Lane G : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
