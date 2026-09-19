# Lane B : poste et notice

Tu exécutes la lane B du chantier Cortex v2. Tu travailles dans le worktree `~/Dev/cortex--B`, branche `lane/B`, déjà créés. Tu opères en autonomie : quand tu as assez pour agir, agis ; ne finis jamais sur une promesse, agis par appel d'outil.

→ Fable 5 : effort `high`. Pas de refactor, de nettoyage ni d'abstraction non demandés. Chaque affirmation de progrès s'appuie sur une sortie d'outil réelle.

## Lire d'abord, dans l'ordre

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ta ligne), puis `04-contrat.md` en entier. Le contrat est gelé : tu t'y conformes, tu ne le modifies pas.

## Ce que tu possèdes

`skills/cortex-0-poste/`, `outils/`, `notice/`, `skills/cortex-4-installation/scripts/{etat,rend_notice,notice}.py`, `skills/cortex-4-installation/scripts/notice.md`, `fabricant/`, `README.md`, `PROVENANCE.md`.

Tout autre fichier est interdit. Un changement qui te paraît nécessaire ailleurs s'écrit dans ton rapport (fichier, valeur attendue, pourquoi), il ne s'exécute pas.

## Livrables

- `skills/cortex-0-poste/SKILL.md` : la phrase d'entrée « installe mon second cerveau » dans la `description`, l'ordre des gestes (détecter, proposer, installer sur accord, brancher le mail, écrire `poste.json` et le bloc `poste`, ouvrir la notice), la section « Notice » de `04-contrat.md` §10.
- `skills/cortex-0-poste/scripts/poste.py` : `--dry-run` (une ligne par outil absent avec la commande de l'OS courant), détection OS, détection du fournisseur mail par question et MX (`04-contrat.md` §3), écriture de `_cortex/poste.json` (schéma §3) et du bloc `poste` de `config.yaml`. Ne jamais installer sans accord explicite.
- `outils/OUTILS.md` : un tableau par famille (`02-arbo.md` §Outils) : rôle, install mac et Windows, licence, URL, verdict. Le fork `cortex-kit/mcp-email` est la seule référence mail IMAP.
- `skills/cortex-4-installation/scripts/etat.py` : neuf étapes (`04-contrat.md` §5), `profil`, `regime`, `phrase_suivante`, `notice_ouverte_le` ; `rend_notice.py` : rendu pas à pas (étape courante en tête, phrase suivante en évidence, étapes faites repliées), `--no-open` ; `notice.py` complété ; `notice.md` réécrit pour un novice (les neuf étapes en langage ordinaire, les trois gestes, les promesses négatives).
- `notice/LISEZ-MOI.html` : rendu de l'état vierge par la même chaîne, hors ligne.
- `README.md` : les trois gestes, un lien vers `notice/LISEZ-MOI.html` et `outils/OUTILS.md`, rien d'autre.
- `fabricant/scripts/fabrique.py` : copie `skills/cortex-*` par glob (les maillons présents), les annexes de `kit.txt`, compte le zip en conséquence. `PROVENANCE.md` : pour les quatre annexes internes qui portent des marques, écris le verdict que le chef d'orchestre t'a donné (traiter ou retirer) ; sans consigne, retire-les de `kit.txt` et dis-le.

## Règles

- Zéro chemin absolu : forme `~` dans les données, `${CLAUDE_SKILL_DIR}` dans les skills. Zéro marque tierce (`01-cadrage.md` §Marques interdites) ; une marque héritée de la v1 se remplace par un terme générique.
- Scripts en Python stdlib pure, un auto-test minimal par script (`python3 <script> --autotest` ou bloc `__main__`), moins de 300 lignes par SKILL.md.
- Prose française, directe, sans tiret cadratin, sans ouverture rhétorique.
- Un point qui exige une décision absente du pack : fais tout ce qui n'en dépend pas, arrête-toi sur ce point, signale-le avec les options. Ne tranche pas à la place du chef d'orchestre.

## Acceptation

Chaque critère de ta ligne dans `03-backlog.md`, prouvé dans ton rapport par la commande exacte et sa sortie.

## Clôture

Commits sur `lane/B`, messages commençant par « Lane B : ». Pas de push, pas de merge, pas de rebase. Rapport final : fichiers créés et modifiés, hash des commits, sortie de chaque commande d'acceptation, points en attente de décision.
