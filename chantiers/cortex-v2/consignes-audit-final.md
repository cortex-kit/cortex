# Audit à froid final du chantier Cortex v2 (2026-09-19)

Tu audites `main` de `~/Dev/cortex` après fusion des six lanes et des six reprises. Tu ne modifies rien d'autre que ton rapport. Modèle Opus 5, effort high.

## Lire
`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `04-contrat.md` en entier (amendements compris), `03-backlog.md`, `06-verification.md`.

## Rejouer, sorties collées
1. `python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?` (attendu 0, 113 contrôles).
2. Grep white-label (liste de `01-cadrage.md` plus `kockpit`, `evrardmarcon`) sur `skills/ notice/ outils/ README.md fabricant/` : zéro ligne.
3. Grep chemins absolus (`/Users/`, `/home/`, lettre de lecteur) sur les mêmes dossiers, hors motifs de détection et témoins d'auto-test.
4. `ast.parse` de chaque `.py` du dépôt sous `/usr/bin/python3` (3.9).
5. Chaque script avec `--autotest` : sortie 0.
6. Un scaffold en régime `pointeur` et un en régime `copie` depuis `config.example.yaml` modifié, lint à 0 sur chacun ; `--outillage-seul` sur un vault dont `.claude/hooks/` porte un `__pycache__`.
7. Une fédération de trois exports fictifs par `federe.py`, deux générations identiques hors `genere_le`, lint du commun à 0.
8. `python3 fabricant/scripts/fabrique.py --sortie <tmp>/cortex.zip` : 10 dossiers, `recette/` absent du zip.
9. `claude plugin details cortex@cortex-kit` : 10 skills.

## Lire comme un novice
Chaque `SKILL.md` des neuf maillons et de `stop-slop`, `notice/LISEZ-MOI.html`, `outils/OUTILS.md`, `README.md` : la phrase canonique de chaque maillon est dans sa description, la section Notice est identique et conforme au §10, aucun maillon ne lance le suivant, aucune marque, aucun chemin absolu, aucun vocabulaire d'atelier non défini, et surtout : à chaque étape, la personne sait quoi dire ensuite. Signale tout ce qui l'empêcherait d'avancer seule.

## Rendre
`chantiers/cortex-v2/audit-final.md`, non commité : tableau de replay (critère, commande, sortie, verdict, confiance), défauts par sévérité avec fichier et ligne, puis une phrase : prêt pour la Phase H (parcours réel) ou non, et ce qui manque.
