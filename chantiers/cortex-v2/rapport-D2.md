# Rapport de la reprise de la lane D (2026-09-19)

Worktree `~/Dev/cortex--D2`, branche `fix/D`, issue de `main` après le merge des six lanes.
Périmètre touché : `skills/cortex-2-inventaire/` seulement (`SKILL.md`, `scripts/scan.py`).
Aucun push, aucun merge.

## Commits

| Hash | Sujet |
|---|---|
| `3b8b628` | Lane D : rejeu non destructif du scan, source_id unique entre racines, budget d'extraction et de temps |

## Les treize défauts, un par un

| Défaut | Traitement | Où |
|---|---|---|
| D-1 rejeu destructif | `ecrire()` relit le JSON présent et appelle `fusionner()`. Remplacés : `format`, `version`, `genere_le`, `racines`, `bornes`, `extraction`, `disque`, `depots`. Conservés : `mail`, `bases`, `agenda`, `profil`, `regime`, les `resume` et `preuve_de` par `source_id`, les écarts dérivés par l'agent | `scan.py` `CLES_REJEU`, `fusionner()`, `ecrire()` |
| D-2 `source_id` en collision | `prefixes()` désambiguïse par le dernier segment du parent quand deux racines portent le même nom de base | `scan.py` `prefixes()` |
| D-3 `sante.max_structurants` détourné | `collecte.max_extractions` (défaut 40). `sante.max_structurants` n'est plus lu par `scan.py` | `scan.py` `inventaire()` |
| D-4 pas de budget de temps | `collecte.budget_secondes` (défaut 120), mesuré en `time.monotonic()`, contrôlé à chaque racine, à chaque dossier dépilé et avant chaque extraction. Arrêt propre, `bornes.depassement` à `true`, racines et dossiers non ouverts comptés dans `dossiers_au_dela` | `scan.py` `scanner()` |
| D-5 import invisible | `import cortex_config` en tête sous `try`, message explicite si le maillon 4 manque, code de retour 1 | `scan.py` ligne 37, `main()` |
| D-6 assertion aveugle au booléen | Les compteurs se testent avec `not isinstance(v, bool)`, le drapeau à part | `scan.py` `_autotest()` |
| D-7 `tilde()` rend un absolu | Docstring qui pose la règle (absolu toléré hors du dossier personnel, contrat amendé §4), `os.path.abspath` au lieu de `.resolve()` : une racine liée symboliquement ne sort plus du dossier personnel | `scan.py` `tilde()` |
| D-8 `graphify_propose` sur tout `.git` | Posé à `bool(d["langages"])` après le calcul des langages | `scan.py` `scanner()` |
| D-9 proposition répétée par niveau | Une seule proposition par sous-arbre : une entrée dont un ancêtre a déjà proposé est passée | `scan.py` `scanner()` |
| D-10 `.lnk` signal de base déportée | Retiré de `EXT_LIEN` | `scan.py` ligne 49 |
| D-11 identifiant de skill au novice | « Dis "décidons mes domaines". » | `SKILL.md:165` |
| D-12 boucle des langages imbriquée | Sortie de la boucle des racines | `scan.py` `scanner()` |
| D-13 `e.stat()` hors du `try` | `is_dir`, `is_file` et `stat` sous un `try` unique par entrée : une permission retirée ou un volume démonté en cours de parcours fait sauter l'entrée, pas le scan | `scan.py` `scanner()` |

## Sorties

### Auto-test

```
$ python3 skills/cortex-2-inventaire/scripts/scan.py --autotest
OK scan.py : bornes en entiers, `depassement` booléen, base déportée, dépôt, profondeur, rejeu non destructif, `source_id` unique entre racines, refus de `contenu`
rc=0
```

Deux témoins ajoutés à l'auto-test.

Rejeu : un `mail` rempli (`voie: connecteur`, `en_tetes_lus: 1840`, un agrégat), un `bases` d'une entrée, un `agenda` d'une entrée, un écart `correspondant_non_declare` et un `resume` plus un `preuve_de` sur chaque entrée `disque` sont posés à la main dans le fichier ; un fichier est ajouté sur le disque ; le scan est rejoué sur le même `--out`. Contrôlé après rejeu : les cinq blocs sont intacts, l'écart de l'agent apparaît une fois et une seule, l'écart `depot_non_declare` a été recalculé sans doublon, et `bornes.fichiers_vus` est passé de 4 à 5, donc le disque a bien été relu.

Unicité : deux racines `A/Travail` et `B/Travail` rendent `['a-travail', 'a-travail-projets', 'b-travail', 'b-travail-projets']`.

### Les trois fixtures, avec `time`

Cache `uv` chaud, hors bac à sable (`uvx` a besoin du cache `uv`, hors de la liste blanche du bac à sable ; dedans, `extraction.echecs` monte et le script dégrade proprement, comme l'audit l'avait relevé).

```
=== employe ===
/tmp/claude/f-employe.json : 15 dossiers, 148 fichiers, 0 dépôt(s), 7 extraction(s), 1 écart(s), dépassement=false
python3 … --racine … --config … --out …   2,77s user 0,64s system 98% cpu 3,461 total

=== dirigeant ===
/tmp/claude/f-dirigeant.json : 42 dossiers, 374 fichiers, 0 dépôt(s), 20 extraction(s), 0 écart(s), dépassement=false
python3 … --racine … --config … --out …   10,76s user 2,28s system 108% cpu 12,003 total

=== societe ===
/tmp/claude/f-societe.json : 27 dossiers, 104 fichiers, 0 dépôt(s), 0 extraction(s), 0 écart(s), dépassement=false
python3 … --racine … --config … --out …   0,03s user 0,01s system 89% cpu 0,049 total
```

Dirigeant : 12,0 s pour un plafond d'acceptation à 60 s, `extraction.echecs` à 0, 20 extractions. Les chiffres de dossiers et de fichiers sont ceux de l'audit.

### Rejeu en conditions réelles sur la fixture dirigeant

```
posé à la main : en_tetes_lus 1840 | bases 1 | agenda 1 | écarts 1
/tmp/claude/inv2-dirigeant.json : 42 dossiers, 374 fichiers, 0 dépôt(s), 20 extraction(s), 1 écart(s), dépassement=false
après rejeu    : en_tetes_lus 1840 | bases 1 | agenda 1 | écarts 1
resume conservés : 42 / 42
écart agent conservé : True
```

### Budget de temps

```
budget_secondes = 0, deux racines : 0 dossiers vus, 2 au-delà, depassement = True
```

### Contrôles d'acceptation

| Contrôle | Commande | Sortie | Verdict |
|---|---|---|---|
| Aucun champ `contenu` | `grep -c '"contenu"' <inventaire>` | `0` | passe |
| Schéma §4 | vérification des clés en Python | manquantes `[]` ; supplément racine `extraction`, `bornes` `dossiers_au_dela` et `extractions`, `disque` `fichiers_arbre` et `signaux_base_deportee`, tous prévus par l'amendement §4 | passe |
| Types de `bornes` | idem | huit `int`, `depassement` en `bool` | passe |
| `source_id` uniques | idem | `True` | passe |
| Chemins en forme `~` | idem | `True` sur toutes les entrées, `.resolve()` retiré compris | passe |
| Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\" skills/cortex-2-inventaire/` | rc=1, zéro ligne | passe |
| Marques interdites | `grep -rwiE "evrard\|marcon\|kockpit\|misteria\|devprom\|cosmos\|claudia" skills/cortex-2-inventaire/` | rc=1, zéro ligne | passe |
| Stdlib seule | `grep -nE "^import\|^from" scan.py` | 13 lignes stdlib plus `cortex_config`, import interne au dépôt admis par le contrat §6 | passe |
| `ast.parse` | `python3 -c "import ast; ast.parse(...)"` | `ast.parse ok` | passe |
| `--help` | `scan.py --help` | rc=0 | passe |
| Moins de 300 lignes | `wc -l SKILL.md` | `200` | passe |
| Périmètre | `git diff --name-only` | `SKILL.md`, `scripts/scan.py` | passe |

### Recette

```
$ python3 skills/cortex-4-installation/recette/parcours_blanc.py
101 contrôle(s) passé(s), 4 en échec.
EN ÉCHEC : C1 le compteur annonce 9/9 quand les neuf lignes sont faites, C1 le tableau de bord
vierge affiche neuf lignes à faire, C4 SessionStart lance le lint bref, Stop rappelle la clôture,
C10 LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante
```

Les quatre échecs portent sur le compteur de `etat.py`, les hooks et le zip, aucun sur `cortex-2-inventaire`. Ils sont antérieurs à cette reprise et relèvent des lanes B, E et G.

## Décisions prises en séance

Deux écarts ont été soumis au chef d'orchestre et tranchés.

1. **Rejeu, clés remplacées.** `format` et `version` sont écrasés en plus des six clés nommées au contrat §4 : ce sont des constantes de schéma écrites par le scripteur, et un fichier v1 rejoué ressortirait sinon en `version: 1` avec un contenu v2. Le chef d'orchestre amende le contrat en conséquence.
2. **Rejeu, écarts candidats.** Tri par type : `base_deportee_non_declaree` et `depot_non_declare`, les deux seuls que `scan.py` sait produire, sont recalculés ; les quatre autres types du contrat §4 sont réputés venir de l'agent et survivent. Retenu contre un champ `pose_par` qui aurait demandé un amendement du schéma.

## Points en attente

Deux valeurs à porter dans des fichiers qui n'appartiennent pas à la lane D (contrat §1).

**Lane C, `skills/cortex-4-installation/template/config.example.yaml`.** Le bloc `collecte` doit gagner les deux clés de l'amendement §2, que `scan.py` lit désormais. Sans elles le script tourne sur ses défauts, mais l'exemple commenté ne documente pas les bornes du maillon 2 :

```yaml
collecte:
  max_extractions: 40            # conversions markitdown au maillon 2 (≠ sante.max_structurants, copie du maillon 5)
  budget_secondes: 120           # durée totale du scan ; au-delà, arrêt propre et bornes.depassement
```

**Lane E, `skills/cortex-6-agents-metier/SKILL.md:120`.** Même défaut que D-11, jumeau relevé par l'audit et toujours présent après les merges. Valeur attendue :

```
2. Dis « prépare la remise ».
```

Rien d'autre n'est en attente : les treize défauts sont traités, les deux témoins demandés par les consignes sont dans l'auto-test, et les sorties des trois fixtures sont collées ci-dessus.
