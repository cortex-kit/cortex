# Lane C : profils et doctrine

Tu exécutes la lane C du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--C`, branche `lane/C`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-1-cadrage/`, `skills/cortex-3-ontologie/`, `skills/cortex-4-installation/scripts/cortex_config.py`, `skills/cortex-4-installation/template/config.example.yaml` (commentaires et valeurs d'exemple seulement).

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-1-cadrage/SKILL.md` : la question de profil en langage ordinaire, posée une fois, écrite dans `config.yaml` ; le régime de donnée fixé par la présence d'une base déportée (`04-contrat.md` §2) ; le bloc `collecte.racines` proposé depuis `references/profils/<profil>.md` et confirmé ; la lecture de `_cortex/poste.json` pour pré-remplir substrats et voie mail.
- `skills/cortex-1-cadrage/references/profils/{employe,dirigeant,societe}.md` : pour chaque profil, les questions (métier, N+1, collègues, parties prenantes, projets portés et subis, outils, rituels), les substrats attendus, les racines proposées, les plafonds, les domaines de départ, les pièges. `societe` décrit le passage en `mode: federe` et le rôle de `cortex-8-federation`.
- `skills/cortex-3-ontologie/SKILL.md` : l'entretien de compréhension (`04-contrat.md` §8) avant la décision des domaines, la section « Ce que l'inventaire a révélé » de `02-ontologie.md`.
- `skills/cortex-1-cadrage/references/secteurs.md` : le dénominateur des seuils devient les notes, pas les projets.
- `skills/cortex-4-installation/scripts/cortex_config.py` : `valider_installable` refuse `profil` et `donnees.regime` hors enum avec un message qui nomme la clé ; auto-test étendu.

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/C`, messages commençant par « Lane C : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
