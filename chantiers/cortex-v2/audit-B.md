# Audit à froid de la lane B (session neuve, 2026-09-19)

Worktree `~/Dev/cortex--B`, branche `lane/B`. Aucun fichier modifié par l'audit, sauf ce rapport, non commité.

Base de comparaison : `git merge-base main HEAD` = `2e0ee29`. `main` a avancé de trois commits depuis (`6fe114a`, `98463af`, `0c09255`), dont l'amendement du contrat que la lane a reçu par `consignes-B.md`. Les écarts `chantiers/` visibles dans `git diff main --stat` viennent de cette avance de `main`, pas de la lane. Le périmètre réel de B tient en 16 fichiers.

## Tableau de replay

| Critère | Commande | Sortie (extrait) | Verdict | Confiance |
|---|---|---|---|---|
| Périmètre §1 | `git diff 2e0ee29 --stat` | 16 fichiers ; 14 dans la colonne « Possède », plus `skills/stop-slop/SKILL.md` et `chantiers/cortex-v2/consignes-B.md` | échoue (hors contrat, autorisés par consigne) | haute |
| Acceptation 1, dry-run | `python3 skills/cortex-0-poste/scripts/poste.py --dry-run` | `markitdown : absent → uv tool install "markitdown[all]"` / `github-desktop : absent → brew install --cask github` / `buzz : absent → brew install --cask buzz` ; `exit=0` | passe | haute |
| Témoin de l'acceptation 1 | recensement indépendant des 7 outils du kit (`command -v`, `/Applications`) | 3 absents : markitdown, github-desktop, buzz | passe, 3 lignes = 3 absents | haute |
| Acceptation 2, hors ligne | `grep -cE "https?://" notice/LISEZ-MOI.html` | `0` | passe | haute |
| Acceptation 3, `notice_ouverte_le` | `poste.py --ecrire --atelier <vide> --mail jane@exemple.test --fournisseur gmail --no-open` | `notice_ouverte_le = '2026-09-19T12:34:54'`, `etapes = 9`, `phrase_suivante = 'faisons le cadrage'`, `version = 2 cortex/etat` | passe | haute |
| Acceptation 4, zip | `python3 fabricant/scripts/fabrique.py --sortie $TMPDIR/z.zip` | `exit=0` ; « 9 dossiers (8 maillons + 1 annexes), LISEZ-MOI.html, PROVENANCE.md » | passe, critère amendé (6 annexes → stop-slop seule, `consignes-B.md`) | haute |
| Marques interdites | `grep -rniE "evrard\|marcon\|evrardmarcon\|mister ?ia\|misteria\|devprom\|voies ?d.?egypte\|vde\|cosmos\|claudia\|kockpit" skills/ chantiers/ notice/ outils/ README.md PROVENANCE.md fabricant/` | `(vide)` ; témoin sur un mot réellement présent : 36 lignes, le grep est vivant | passe | haute |
| Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\" skills/ notice/ outils/ README.md` | 3 lignes, toutes des motifs de détection préexistants sur `main` (`parcours_blanc.py:230`, `lint_sante.py:284`, `cortex-7-passation/SKILL.md:66`) | passe pour la lane B, échoue pour la ligne G telle qu'écrite | haute |
| `--help` sort 0 | 5 scripts de la lane | tous `exit=0` | passe | haute |
| Auto-tests | `--autotest` sur poste, etat, rend_notice, notice, fabrique | 5 × « auto-test OK », `exit=0` | passe | haute |
| Stdlib pure | `grep -nE "^import\|^from"` sur les 5 scripts | stdlib seule, plus les imports frères `cortex_config`, `etat`, `rend_notice` | passe | haute |
| Portabilité Python | `ast.parse` sous `/usr/bin/python3` (3.9.6) sur les 15 `.py` du dépôt | `KO 3.9 : skills/cortex-0-poste/scripts/poste.py`, seul fichier du dépôt dans ce cas | échoue | haute |
| SKILL.md, frontmatter et taille | `cortex-0-poste` 136 lignes, `fabricant` 98 lignes | `name` et `description` présents ; phrase d'entrée « installe mon second cerveau » dans la `description` | passe | haute |
| Section « Notice » §10 | `diff` avec `skills/cortex-1-cadrage/SKILL.md` | identique au mot près | passe | haute |
| Contrat §5, `ETAPES` et `PHRASES` | lecture de `etat.py:48-74` | les neuf tuples de §5 et les dix phrases de l'amendement §5, à l'identique | passe | haute |
| Contrat §3, schéma `poste.json` | `cat _cortex/poste.json` après l'acceptation 3 | `format`, `version`, `genere_le`, `os`, `outils` (`connecte` sur gh, `node` mesuré), `options_proposees`, `mail`, `notice_ouverte_le` | passe | haute |
| Contrat §3, lecture MX | auto-test de `poste.py` | sorties `nslookup` mac et Windows figées, 5 cas de fournisseur, 6 cas de voie | passe sur figé, non mesurable en réel (nslookup bloqué par le bac à sable) | moyenne |
| Amendement, slug au maillon 0 | `skills/cortex-0-poste/SKILL.md:31-35` | question posée en langage ordinaire, atelier `~/Cortex/<slug>/_cortex/` | passe | haute |
| Amendement, `markitdown[all]` par uvx | `poste.py:45`, `outils/OUTILS.md:18` | `uvx --from "markitdown[all]" markitdown` des deux côtés | passe | haute |
| Amendement, deck retiré | `grep -rn "rend_deck\|bento\|deck"` | `fabricant/` propre ; restes dans `parcours_blanc.py` (lane G) et `02-arbo.md:25` (chef d'orchestre) | passe dans le périmètre | haute |
| Amendement §11, `%USERPROFILE%` | `grep -rn USERPROFILE` | `notice.md:82`, `LISEZ-MOI.html:76`, jamais de lettre de lecteur | passe | haute |
| I10, aucun maillon n'invoque le suivant | `notice.py:4-7`, `cortex-0-poste/SKILL.md` §Interdits | « La notice propose, elle ne lance rien » ; `notice.py` sort toujours 0 | passe | haute |
| I2, I3, I6, I7 | greps ci-dessus et revue des diffs | aucun chemin absolu, aucune marque, aucun sous-agent ajouté, plugins core d'Obsidian seuls, Obsidian Git et Local REST API écartés dans OUTILS.md | passe | haute |
| `LISEZ-MOI.html` reproductible | régénération témoin par `etat.py` puis `rend_notice.py`, `diff` hors horodatage | `IDENTIQUE hors horodatage` | passe | haute |
| Notice vierge | lecture du rendu | 8 pastilles « À faire », l'étape 0 en tête hors tableau, phrase « installe mon second cerveau » en évidence | passe | haute |
| Zip hors ligne | `zipfile` sur `LISEZ-MOI.html` du zip | 0 occurrence de `https?://`, `paquet 2026-09-19` | passe | haute |
| Recette v1 | `python3 skills/cortex-4-installation/recette/parcours_blanc.py` | `ModuleNotFoundError: No module named 'rend_deck'` à la ligne 36, zéro contrôle exécuté | échoue, plus largement que ce que §5 annonçait | haute |

## Défauts par sévérité

### Bloquant

1. **`skills/cortex-0-poste/scripts/poste.py:210`** — `SyntaxError: f-string expression part cannot include a backslash` sous tout Python antérieur à 3.12. Le backslash dans une expression f-string n'est légal que depuis PEP 701. C'est le seul fichier du dépôt dans ce cas : les quatorze autres `.py`, v1 comprise, parsent sous 3.9. Le maillon 0 est le premier geste du produit et s'exécute avant que `uv` n'ait installé Python 3.12 ; sur un Mac de série, `/usr/bin/python3` vaut 3.9.6 et la toute première commande de la notice meurt avant d'afficher une ligne.

### À corriger avant merge

2. **`skills/cortex-0-poste/scripts/poste.py:243-247`** — `installe_par_cortex` est relu dans une clé racine que `ecrire()` n'écrit jamais. Deux `--ecrire` successifs perdent la trace du premier lot. Mesuré : après le lot 1, `{'git': True}` ; après le lot 2, `{'gh': True}`, `git` retombé à `false`.
3. **Périmètre, `04-contrat.md` §1** — `skills/stop-slop/SKILL.md` et `chantiers/cortex-v2/consignes-B.md` sortent de la colonne « Possède » de la lane B. Les deux sont autorisés par `consignes-B.md`, aucun n'a été porté au contrat. Un audit qui applique §1 à la lettre les compte bloquants.
4. **`skills/cortex-4-installation/recette/parcours_blanc.py:36`** — après merge de B, la recette ne démarre plus du tout. `04-contrat.md` §5 annonçait quatre assertions rouges, pas l'arrêt du harnais entier. Conséquence directe de la suppression de `rend_deck.py`, ordonnée par l'amendement §5. La lane B a signalé le correctif exact pour G dans son rapport (ligne 36 et bloc deck autour de la ligne 326).

### Mineur

5. **`skills/cortex-4-installation/scripts/rend_notice.py:187`** — la notice affiche « Prochaine étape · 0 sur 8 » pour neuf étapes. Un novice lit « étape zéro ».
6. **`skills/cortex-4-installation/scripts/etat.py:139`** — l'étape 8 passe « Arbitré, vault solo » dès le maillon 0, parce que `conf.get("mode", "solo")` s'applique à une config qui ne porte pas encore de profil. Un futur utilisateur `societe` voit « sans objet », puis le voit repasser « À faire » au maillon 1.
7. **`skills/cortex-4-installation/scripts/notice.py`** — ne pose jamais `notice_ouverte_le` ; seul `poste.py --ecrire` le fait. L'amendement §5 écrit « posé dès que la notice est régénérée, même avec `--no-open` ». Le chemin `--installer` sans `--ecrire` laisse un `poste.json` qui bloque l'étape 0 en « En cours » jusqu'au prochain `--ecrire`.
8. **`fabricant/scripts/fabrique.py:169`** — « 1 annexes » dans la sortie.
9. **`fabricant/scripts/fabrique.py:41`** — commentaire périmé : `PAQUET = _ICI.parent  # ~/.claude/skills/cortex-paquet`, alors que le dossier est `fabricant/` à la racine du dépôt.
10. **`fabricant/scripts/fabrique.py:47`** — `int(n.split("-")[1])` lève `ValueError` sur tout dossier `skills/cortex-<non numérique>`.
11. **`fabricant/scripts/fabrique.py:137`** — le zip embarque `cortex-4-installation/recette/` (`parcours_blanc.py`, `fixtures.py`) chez le novice. Hérité de la v1, pas une régression de B.
12. **`chantiers/cortex-v2/02-arbo.md:25`** — cite encore `rend_deck.py` dans `fabricant/`. Fichier du chef d'orchestre.
13. **`skills/cortex-0-poste/scripts/poste.py:205-212`** — `bloc_poste_yaml` ne liste que les outils présents ; l'exemple de `04-contrat.md` §2 montre le kit entier. Divergence documentée dans le SKILL.md, à trancher pour que C et E lisent la même chose.
14. **`skills/cortex-0-poste/`** — le slug n'entre ni dans `config.yaml` ni dans `poste.json`. Les lanes C et E devront le rétro-déduire du chemin pour `commun.racine` et le dépôt `cortex-<slug>`.
15. **Ligne G de `03-backlog.md`** — le grep « zéro chemin absolu » rend trois lignes qui sont des motifs de détection, pas des chemins (`parcours_blanc.py:230`, `lint_sante.py:284`, `cortex-7-passation/SKILL.md:66`). Préexistant à B, mais le critère G échouera tel qu'écrit.

## Verdict

**Non mergeable en l'état.** Le défaut 1 rend le premier geste du produit inexécutable sur le poste type qu'il est censé équiper. Les défauts 2 à 4 touchent la traçabilité contractuelle et le harnais de recette. Les vingt-deux autres critères passent, chacun sur une sortie de commande.

## Suites actées par le chef d'orchestre (2026-09-19)

1. **Défaut bloquant 1 et défauts 2 à 4** : corrigés par une session de reprise `fix/B` sur l'arbre fusionné, les lanes Fable étant fermées. Chaque correctif est re-mesuré avec la commande qui l'a mis au jour :
   - défaut 1 : `ast.parse` de `poste.py` sous `/usr/bin/python3` (3.9.6) doit passer, et les quinze `.py` du dépôt avec lui ;
   - défaut 2 : deux `--ecrire` successifs doivent conserver `installe_par_cortex` du premier lot ;
   - défaut 3 : `04-contrat.md` §1 amendé, puis `git diff <merge-base> --stat` relu contre la colonne « Possède » ;
   - défaut 4 : `python3 skills/cortex-4-installation/recette/parcours_blanc.py` doit démarrer et rendre son tableau, les assertions à sept restant rouges jusqu'au merge de G.
2. **Contrat §1** (option retenue, recommandation de l'audit) : amender §1 avant les audits suivants. Ajouter `skills/stop-slop/` à la colonne B, et acter que `chantiers/cortex-v2/consignes-<lane>.md` reste au chef d'orchestre même quand le commit part de la branche de lane. Sans cet amendement, chaque audit de C à F remontera le même écart comme bloquant.
3. **Ordre de merge** (option retenue, recommandation de l'audit) : garder B, C, D, E, F, puis G. La reprise `fix/B` répare la recette sur l'arbre fusionné juste après le merge de B, donc les audits de C à F disposent d'un harnais qui démarre, sans avoir à avancer G.

## Défauts laissés à la charge des lanes aval

- Défauts 5 à 7 et 13 à 14 : périmètre `cortex-0-poste` et `cortex-4-installation/scripts/`, à reprendre par `fix/B` si le chef d'orchestre élargit son mandat, sinon à porter en Phase H.
- Défauts 8 à 11 : `fabricant/`, cosmétique et robustesse, sans effet sur le produit livré.
- Défaut 12 : `chantiers/cortex-v2/02-arbo.md:25`, fichier du chef d'orchestre.
- Défaut 15 : ligne G de `03-backlog.md`, le critère « zéro chemin absolu » à reformuler pour ne pas compter les motifs de détection.
