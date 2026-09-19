# Rapport de la reprise E (session Opus, worktree `~/Dev/cortex--E2`, branche `fix/E`, 2026-09-19)

Base de fusion `087cd92`. Trois commits, aucun push, aucun merge. Les onze fichiers touchés sont tous dans la colonne « Possède » de la lane E.

## Commits

| Hash | Objet |
|---|---|
| `40f4344` | B-1, A-1 à A-4, M-2 à M-8 |
| `b890a0e` | Le commentaire du lint portait une lettre de lecteur littérale et déclenchait C9 |
| `4a8c66a` | 18e entrée `allow` (décision du chef d'orchestre) et `--outillage-seul` face à un `.pyc` |

## Empreinte

```
$ git diff 087cd92 HEAD --stat
 skills/cortex-4-installation/SKILL.md                            |  6 +-
 skills/cortex-4-installation/scripts/lint_sante.py               | 51 +++++--
 skills/cortex-4-installation/scripts/scaffold.py                 | 76 ++++++++--
 .../template/vault/.claude/hooks/session_start.py                | 27 ++-
 .../template/vault/.claude/hooks/stop.py                         | 24 ++-
 .../template/vault/.claude/skills/cloture/export.py              | 14 +-
 .../template/vault/.claude/skills/ingest/SKILL.md                | 27 +++
 .../template/vault/.claude/skills/lint/SKILL.md                  | 19 +-
 skills/cortex-5-ingest/SKILL.md                                  |  6 +-
 skills/cortex-5-ingest/scripts/copie_structurant.py              | 53 ++++--
 skills/cortex-6-agents-metier/SKILL.md                           |  2 +-
 11 files changed, 266 insertions(+), 39 deletions(-)
```

## Ce qui a été corrigé

### B-1, forme de l'appel à markitdown

`copie_structurant.py` appelle désormais `uvx --from "markitdown[all]" markitdown <src>`, depuis un dossier temporaire créé pour l'occasion, jamais depuis le vault. La commande vit dans la constante `CMD_MARKITDOWN`, dont l'auto-test porte le témoin, et la source est résolue en absolu avant le changement de répertoire. Même forme dans `cortex-5-ingest/SKILL.md:73` et dans les deux docstrings du script.

### A-1, la lettre de lecteur

`lint_sante.py:340` :

```python
for m in re.finditer(r"(/Users/[\w.-]+|/home/[\w.-]+|[A-Za-z]:\\)", text):
```

Un seul antislash dans la chaîne brute, donc un seul dans le texte lu. Témoin dans l'auto-test : une note portant un chemin Windows écrit comme il s'écrit, et l'assertion que `chemins_absolus` la voit. Vérification vivante sur un vault scaffoldé :

```
[!] 1 fichier(s) avec un chemin absolu :
    - 10 - Domaines/Windows.md : C:\
```

Le commentaire qui accompagnait la correction portait lui-même la forme littérale et faisait passer C9 de la recette au rouge sur le fichier même qui fait le contrôle. Réécrit en `b890a0e`, C9 est revenu au vert.

### A-2, le rafraîchissement d'un structurant

`scaffold.py` dépose `copie_structurant.py` dans `<vault>/.claude/skills/ingest/` (fonction `copier_ingest`, appelée à l'installation et par `--outillage-seul`). Le script y trouve `cortex_config.py` chez son voisin `lint/` et se passe de `scaffold.forme_tilde`, qui n'est pas livré au client, par un repli local documenté comme tel. Preuve sur un vault scaffoldé, plugin hors du chemin :

```
$ cd <vault> && python3 .claude/skills/ingest/copie_structurant.py --vault . \
      --source <src>/PROCESS-affaire.md --type process --domaine "Actifs"
✓ ecrite : 50 - Ressources/Structurants/process/PROCESS-affaire.md (37 octets, sha256 9d7ac93dbe53...)
```

La skill `ingest` du vault gagne deux sections : « Régime copie : les structurants » et « Rafraîchir un structurant périmé », qui donne la commande et les quatre cas (source changée, source déplacée, source supprimée, frontmatter incomplet).

### A-3, les quatre contrôles documentés

`lint/SKILL.md` du vault décrit le régime, `structurant_perime`, la suspension du plafond de lignes sur `50 - Ressources/Structurants/`, `visibilite`, la lecture de la dernière clôture et l'option `--bref`. `visibilite_hors_enum` rejoint le tableau des contrôles durs ; `structurant_perime` et `cloture_ancienne` rejoignent la ligne de dette.

### A-4, le slug

Le slug est `organisation.code`, et il l'est déjà partout dans le code de la lane : `export.py:43` et `scaffold.py` pour `cortex-<slug>`. Ce qui manquait était la phrase. Elle est dans `cortex-4-installation/SKILL.md`, sous la commande `gh repo create`, et en tête d'`export.py` : `~/Cortex/<slug>/`, `_export/<slug>/`, `cortex-<slug>` et l'entrée du membre dans `federation.yaml` dérivent tous de cette clé.

### Les mineurs

| Défaut | Correction |
|---|---|
| M-2 | `bref()` ne compte plus `structurant_perime` deux fois. Sortie : `Contrôle de santé : 0 problème(s) bloquant(s), 1 point(s) à surveiller.` |
| M-3 | `ligne_constat()` rend un constat en une ligne, fichier puis raison. Sortie : `- 50 - Ressources/Structurants/process/PROCESS-affaire.md : source modifiee depuis la copie` |
| M-4 | `racine_vault()` dans les deux hooks : `CLAUDE_PROJECT_DIR`, repli sur le dossier courant. `stop.py` lance son `git status` dans ce dossier. |
| M-5 | Le second chemin de `sys.path` d'`export.py` n'est ajouté que si `cortex_config.py` s'y trouve vraiment, au lieu de compter les parents. |
| M-6 | `argparse` avec `--autotest` dans `session_start.py` et `stop.py` ; `--help` sort 0 par contrat. |
| M-7 | « Sur accord, lancer `cortex-N+1` » retiré des trois SKILL.md possédés. La substance qui n'était pas un lancement a été conservée. |
| M-8 | Zéro tiret cadratin dans les lignes ajoutées : `git diff -U0 \| grep "^+" \| grep -c "—"` rend `0`. |

### Les deux points venus du chef d'orchestre en cours de reprise

**18e entrée `allow`.** `Bash(python3 .claude/skills/ingest/copie_structurant.py:*)` rejoint la liste. Le rafraîchissement d'un structurant est du même registre que les quatre gestes de la clôture : une routine que le lint, `cloture`, `parle` et `bilan` proposent. Le contrat §9 est amendé en conséquence, et la recette de la lane G doit compter 18 entrées.

**`--outillage-seul` face à un `.pyc`** (défaut trouvé par la reprise G dans un fichier de la lane E). `outillage_seul` lisait en UTF-8 tout fichier de `template/vault/.claude/` et sortait en 1 dès qu'un `__pycache__` traînait dans le gabarit. Le filtre de l'installation est maintenant partagé : `ignorable()` écarte `__pycache__` et les `.pyc`, `SUFFIXES_TEXTE` décide de la substitution, le reste est copié tel quel. L'installation avait le même trou dans l'autre sens, elle copiait le `.pyc` chez le client ; elle est corrigée au même endroit. Témoin dans l'auto-test : un `.pyc` planté dans le gabarit, sortie 0 exigée et absence de `__pycache__` dans le vault. Contre-épreuve, correctif retiré :

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 0: invalid continuation byte
```

## Les six auto-tests

```
$ python3 skills/cortex-4-installation/scripts/scaffold.py --autotest
OK scaffold.py : forme ~, settings.json, hooks, skills parle, bilan et ingest, .pyc ignore, depot prive propose   rc=0
$ python3 skills/cortex-4-installation/scripts/lint_sante.py --autotest
OK lint_sante.py : structurant_perime, plafond suspendu, visibilite, cloture_ancienne, --bref, lettre de lecteur   rc=0
$ python3 skills/cortex-5-ingest/scripts/copie_structurant.py --autotest
OK copie_structurant.py   rc=0
$ python3 .../template/vault/.claude/skills/cloture/export.py --autotest
OK export.py   rc=0
$ python3 .../template/vault/.claude/hooks/session_start.py --autotest
OK session_start.py   rc=0
$ python3 .../template/vault/.claude/hooks/stop.py --autotest
OK stop.py   rc=0
```

`--help` sort 0 sur les six, par `argparse` cette fois et non par accident.

## Les huit critères d'acceptation

| # | Critère | Sortie | Verdict |
|---|---|---|---|
| 1 | Lecture permise dans un vault scaffoldé | `claude -p "compte les fichiers de <racine>" --output-format json` : `permission_denials: []`, `is_error: false`, « 3 fichiers, tous dans `sous/` » | passe, réserve M-1 |
| 2 | Écriture refusée hors vault | `claude -p "écris un fichier x dans <racine>/y"` : « `<racine>` est un dossier de travail déclaré en **lecture seule** … Je n'écris pas, et je ne contourne pas le deny par Bash. » ; `find <racine> -type f` rend les 3 fichiers d'origine | passe, réserve M-1 |
| 3 | `parle` cite des liens que le lint résout | 6 liens cités : `Actifs`, `Architecture - Vue d'ensemble`, `Architecture Mémoire`, `Centre`, `Conventions`, `Développement`, tous résolus vers un `.md` du vault | passe |
| 4 | Un structurant modifié à la source lève `structurant_perime` | `[i] 1 structurant(s) dont la source a change depuis la copie : - 50 - Ressources/Structurants/process/PROCESS-affaire.md : source modifiee depuis la copie` | passe |
| 5 | `structurant_perime` est une dette, le lint reste à 0 | `[OK] Vault sain.` avec le constat affiché, `rc=0` | passe |
| 6 | `lint_sante.py --vault <vault>` = 0 en pointeur et en copie | pointeur : `[OK] Vault sain.` `rc=0` (15/44 notes) ; copie : `[OK] Vault sain.` `rc=0` (16/45 notes) | passe |
| 7 | `settings.json` conforme §9 et amendements | 18 entrées `allow`, `deny` = `Write(<racine>/**)` et `Edit(<racine>/**)`, `additionalDirectories` = les racines, hooks SessionStart et Stop | passe |
| 8 | Forme des hooks (amendement §9) | `.claude/hooks/{session_start,stop}.py`, appelés par `python3 .claude/hooks/<nom>.py`. Depuis un sous-dossier avec `CLAUDE_PROJECT_DIR` : `Contrôle de santé : 0 problème(s) bloquant(s), 0 point(s) à surveiller.` ; `stop.py` : `{"systemMessage": "3 fichier(s) modifié(s) sans clôture. …"}` | passe |

Export §6, vérifié au passage : mode solo, « mode solo : aucun export, rien à faire. » ; mode fédéré, « ✓ Export : 1 note(s) dans `_export/acme/` » avec `index.json` au format `cortex/export` v1 et le frontmatter enrichi de `source_vault: acme` et `exporte_le`.

Réserve M-1, inchangée et déjà connue : `claude -p` répond « Ignoring 18 permissions.allow entries … this workspace has not been trusted » et « Ignoring 1 permissions.additionalDirectories entry ». Les règles `deny`, elles, sont bien lues, et c'est sur elles que le refus du critère 2 s'appuie. Les critères 1 et 2 passent mais ne prouvent ce qu'ils prétendent prouver qu'une fois le vault ouvert en interactif. Contrôle manuel pour `06-verification.md`, lane G.

## Recette

```
$ python3 skills/cortex-4-installation/recette/parcours_blanc.py
101 contrôle(s) passé(s), 4 en échec.
EN ÉCHEC : C1 le compteur annonce 9/9 quand les neuf lignes sont faites,
           C1 le tableau de bord vierge affiche neuf lignes à faire,
           C4 SessionStart lance le lint bref, Stop rappelle la clôture,
           C10 LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante
```

C5 (régimes pointeur et copie, structurant périmé) est à 4/4 vert, C9 à 2/2 vert.

## Valeurs attendues hors périmètre

**Lane G, `parcours_blanc.py`, contrôle C4.** Le contrôle lit `settings.json` et exige `lint_sante.py` et `--bref` dans la commande du hook SessionStart, plus le mot « clôture » dans celle du hook Stop. L'amendement §9 du 2026-09-19 a changé la forme : `scaffold.py` livre `.claude/hooks/session_start.py` et `stop.py`, et `settings.json` les appelle par `python3 .claude/hooks/<nom>.py`. Le contrôle mesure donc une forme que le contrat a retirée, et c'est lui qui est en retard, pas la lane. Valeur attendue : vérifier que les deux scripts existent, que `settings.json` les appelle, et lancer `session_start.py --autotest` et `stop.py --autotest` plutôt que d'inspecter une commande inline. Échec antérieur à cette reprise.

**Lane G, `parcours_blanc.py`, nombre d'entrées `allow`.** 18 depuis `4a8c66a`, contre 17 auparavant.

**Lane C, M-7.** « Sur accord, lancer `cortex-N+1` » subsiste dans `skills/cortex-1-cadrage/SKILL.md:202` et `skills/cortex-3-ontologie/SKILL.md:191`, à contre-courant de l'amendement I10. Fichiers de la lane C.

**Lane G, M-1.** Le contrôle vivant des permissions n'est reproductible qu'en session interactive, le vault devant avoir été ouvert une fois et approuvé. À consigner dans `06-verification.md` comme contrôle manuel, à l'image de l'installation du plugin.

## Points en attente de décision

Aucun. Les deux points ouverts en cours de reprise ont été tranchés par le chef d'orchestre et appliqués : la 18e entrée `allow` et le filtre par suffixe de `--outillage-seul`.
