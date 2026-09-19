# Rapport final de la reprise B2 (worktree `~/Dev/cortex--B2`, branche `fix/B`, 2026-09-19)

Commit unique : **`6d85db5`** — « Lane B : poste.py parse sous Python 3.9, installe_par_cortex survit, slug en organisation.code ». Aucun push, aucun merge.

Périmètre : 7 fichiers, tous dans la colonne « Possède » de la lane B (`04-contrat.md` §1).

```
fabricant/scripts/fabrique.py                      |  32 +++++--
notice/LISEZ-MOI.html                              |   4 +-
skills/cortex-0-poste/SKILL.md                     |  15 ++-
skills/cortex-0-poste/scripts/poste.py             | 103 ++++++++++++++-----
skills/cortex-4-installation/scripts/etat.py       |   8 +-
skills/cortex-4-installation/scripts/notice.py     |  40 +++++++-
skills/cortex-4-installation/scripts/rend_notice.py|   5 +-
```

## Bloquant 1 — `poste.py` sous Python 3.9

`bloc_poste_yaml` portait un antislash dans une expression f-string, illégal avant PEP 701. `fusionner_bloc` construit les paires en Python nu ; `ecrire_bloc_poste` disparaît, absorbé par la même fonction, qui sert aussi au bloc `organisation`.

```
$ /usr/bin/python3 -V
Python 3.9.6
$ for f in $(git ls-files '*.py'); do /usr/bin/python3 -c "import ast; ast.parse(open('$f').read())"; done
fichiers: 17 ; ko=0
```

## Défaut 2 — `installe_par_cortex` survit à deux `--ecrire`

`ecrire()` relisait la trace dans une clé racine qu'il n'écrivait jamais. Elle se relit maintenant des deux côtés : clé racine laissée par `--installer` seul, et drapeau par outil de l'écriture précédente (`deja_par_cortex`).

```
$ echo '{"installe_par_cortex": ["git"]}' > $AT/poste.json      # ce que laisse --installer git
$ poste.py --ecrire --atelier $AT --slug acme --mail jane@exemple.test --fournisseur gmail --no-open
après --ecrire 1 : ['git']
après --ecrire 2 : ['git']
```

Avant correctif, l'audit mesurait `['git']` puis `[]`. Témoin dans l'auto-test de `poste.py` : deux `ecrire()` d'affilée sur un état d'outils figé, hors réseau.

## Défauts 5, 6, 7, 13, 14

```
$ notice.py --atelier <atelier vierge> --no-open ; grep -o "Prochaine étape · . sur ." notice.html
Prochaine étape · 1 sur 9                       # défaut 5, plus jamais « 0 sur 8 »
pastilles « À faire » : 8                       # amendement §5, l'étape courante en tête hors tableau

$ etat.generer(<config mode: solo, sans profil>)["etapes"][8]["etat"]
sans profil : a_faire                           # défaut 6
avec profil : arbitre

$ echo '{"format":"cortex/poste","installe_par_cortex":["git"]}' > $AT/poste.json
$ notice.py --atelier $AT --no-open
OK — $AT/notice.html : 1/9 étape(s) faite(s)
notice_ouverte_le = 2026-09-19T12:53:27         # défaut 7, posé même avec --no-open

$ cat $AT/config.yaml                           # défauts 13 et 14
organisation:
  code: acme
poste:
  os: macos
  outils: [obsidian, uv, markitdown, git, gh, github-desktop, buzz]
  mail_fournisseur: gmail
  mail_boites: 1
  mail_voie: connecteur
$ poste.json → organisation: {'code': 'acme'} ; outils : les 8 mesurés avec present vrai ou faux
```

`--slug` est optionnel : sans lui, le slug se déduit du chemin de l'atelier (`~/Cortex/<slug>/_cortex`).

## Défauts 8 à 11 — `fabricant/`

```
$ python3 fabricant/scripts/fabrique.py --sortie $TMPDIR/z.zip
OK — /tmp/.../z.zip : 10 dossiers (9 maillons + 1 annexe), LISEZ-MOI.html, PROVENANCE.md, version 2026-09-19
exit=0
recette embarquée : aucune
URL distantes dans LISEZ-MOI.html : 0
racine : ['LISEZ-MOI.html', 'PROVENANCE.md']
```

`PAQUET` commente désormais `<dépôt>/fabricant`. `_rang` range un dossier `cortex-<non numérique>` en fin de liste au lieu de faire lever `int()`.

## Rejeu des critères d'acceptation et des auto-tests

```
$ poste.py --dry-run
markitdown : absent → uv tool install "markitdown[all]"
github-desktop : absent → brew install --cask github
buzz : absent → brew install --cask buzz
exit=0

$ grep -cE "https?://" notice/LISEZ-MOI.html
0

auto-tests : poste, etat, rend_notice, notice, fabrique → 5 × « auto-test OK », exit=0
--help     : les 5 scripts → exit=0
marques interdites sur skills/ notice/ outils/ README.md PROVENANCE.md fabricant/ → vide (témoin : le grep rend « Cortex » sur README.md)
chemins absolus dans les 7 fichiers modifiés → aucun
imports → stdlib seule, plus les imports frères cortex_config, etat, rend_notice
```

`notice/LISEZ-MOI.html` régénéré par la même chaîne (`etat.generer` puis `rend_notice.rendre`), il portait encore « 0 sur 8 ».

## Recette : état avant et après

Le défaut 4 de l'audit (la recette ne démarrait plus) était déjà réparé sur `main` au moment de la reprise. La recette tourne.

| | Contrôles passés | En échec |
|---|---|---|
| `HEAD` avant reprise | 100 | 4 |
| après `6d85db5` | 101 | 4 |

Aucune régression : même jeu d'échecs, un contrôle de plus au vert. Les deux mesures sont prises depuis un dossier sous `~` (hors de `~`, trois contrôles C3 échouent en plus, ce que l'amendement §4 prévoit).

## Hors de mon périmètre, valeurs attendues (`04-contrat.md` §1)

- **Lane G, `skills/cortex-4-installation/recette/parcours_blanc.py`** — trois assertions contredisent l'amendement §5 (« le compteur d'un atelier solo complet dit 8 faites et 1 arbitrée, jamais 9/9 ; la page vierge et `LISEZ-MOI.html` comptent 8 pastilles À faire »). La fixture `complet` porte `profil: dirigeant` et `mode: solo`, donc l'étape 8 vaut `arbitre` :
  - ligne 548 : `m_etat.faites(pivot_complet) == 8`, et `pivot_complet["etapes"][8]["etat"] == "arbitre"` ;
  - ligne 554 : `html_vierge.count("À faire") == 8` ;
  - ligne 911 : `lisezmoi.count("À faire") == 8`.
  Les libellés des trois contrôles suivent (« huit lignes faites et une arbitrée », « huit lignes à faire »).
- **Lane C, `skills/cortex-1-cadrage/scripts/rejeu_profil.py:100`** — le bloc `poste` reconstruit depuis `poste.json` liste les seuls outils présents, alors que `poste.outils` porte désormais le kit entier (défaut 13). Valeur attendue : la liste du kit dans l'ordre du contrat, donc `[o for o in poste.get("outils", {}) if o != "node"]`, `node` n'appartenant pas au kit.
- Le quatrième échec de la recette (`C4 SessionStart lance le lint bref, Stop rappelle la clôture`) est du ressort de la lane E, inchangé par cette reprise.

## Points en attente

Aucun. Les dix défauts listés par `consignes-B2.md` sont corrigés et re-mesurés par la commande qui les avait mis au jour.
