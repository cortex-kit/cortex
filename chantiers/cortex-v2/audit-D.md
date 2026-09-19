# Audit à froid de la lane D (session neuve, 2026-09-19)

Worktree `~/Dev/cortex--D`, branche `lane/D`, HEAD `cad4f6d`, merge-base avec `main` `2e0ee29`, `main` à `0c09255`.
Auditeur : Opus 5, effort high. Aucune modification du code de la lane ; ce fichier est le seul écrit, non commité.

## Rejeu, critère par critère

| Critère | Commande | Sortie (extrait) | Verdict | Confiance |
|---|---|---|---|---|
| 1. Périmètre fichiers | `git diff --name-only $(git merge-base main HEAD) HEAD` | `chantiers/cortex-v2/consignes-D.md`, `skills/cortex-2-inventaire/SKILL.md`, `skills/cortex-2-inventaire/scripts/scan.py` | passe | haute |
| 1bis. Merge | `git merge-tree --write-tree main HEAD` | merge propre, aucun conflit | passe | haute |
| 2a. Acceptation dirigeant | `python3 skills/cortex-2-inventaire/scripts/scan.py --racine skills/cortex-4-installation/recette/fixtures/dirigeant --config skills/cortex-4-installation/template/config.example.yaml --out $TMPDIR/inv.json` | `42 dossiers, 374 fichiers, 0 dépôt(s), 20 extraction(s), 0 écart(s), dépassement=false` ; rc=0 | passe | haute |
| 2b. Conformité schéma §4 | vérification des clés en Python sur `inv.json` | clés §4 manquantes : `[]` ; supplément : `extraction` (prévu par l'amendement §4) ; `bornes` = `{profondeur_max_vue, dossiers_vus, fichiers_vus, octets_extraits, profondeur_arbre, max_dossiers, dossiers_au_dela, extractions}` en `int`, `depassement` en `bool` conforme à l'exemple du contrat | passe | haute |
| 2c. Aucun champ `contenu` | `grep -c '"contenu"' $TMPDIR/inv.json` | `0` | passe | haute |
| 2d. `time` inférieur à 60 s | `time python3 … --racine …/dirigeant …` | **43,4 s** avec cache `uv` froid ; **0,26 s** avec cache chaud. La lane annonçait 11,1 s | passe, marge faible | haute |
| 2e. Fixture employé | `python3 … --racine skills/cortex-4-installation/recette/fixtures/employe …` | `signaux_base_deportee: ['export-notion-2026-01.csv', …, '…-05.csv']` ; écart `base_deportee_non_declaree` produit | passe | haute |
| 2f. Fixtures régénérées | `rm -rf recette/fixtures && python3 recette/fixtures.py` | `employe 148 / dirigeant 374 / societe 104 fichiers`, `déterminisme vérifié`, 0,35 s, rc=0 | passe | haute |
| 3. Marques interdites | `grep -rwiE "evrard\|marcon\|kockpit\|misteria\|mister ia\|devprom\|voies d.egypte\|vde\|cosmos\|claudia" skills/ chantiers/ notice/ outils/ README.md` (hors `recette/fixtures/`) | 1 ligne : `skills/stop-slop/SKILL.md` (annexe interne connue, lane B). Zéro dans `skills/cortex-2-inventaire/` | passe | haute |
| 4. Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\" skills/cortex-2-inventaire/` | rc=1, zéro ligne. Les 5 occurrences du dépôt sont dans `parcours_blanc.py`, `lint_sante.py`, `notice.md`, `cortex-7` (lanes B, E, G) | passe | haute |
| 5a. `--help` | `python3 skills/cortex-2-inventaire/scripts/scan.py --help` | usage complet des 4 options ; rc=0 | passe | haute |
| 5b. Auto-test | `python3 skills/cortex-2-inventaire/scripts/scan.py --autotest` | `OK scan.py : bornes en entiers, base déportée, dépôt, profondeur, refus de contenu` ; rc=0 | passe | haute |
| 5c. Stdlib seule | `grep -nE "^import\|^from" skills/cortex-2-inventaire/scripts/scan.py` | 12 lignes, toutes stdlib (`argparse, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, collections, datetime, pathlib`). **Mais** `import cortex_config` en ligne 373, hors portée du grep | passe formellement, réserve | haute |
| 6a. Frontmatter | lecture de `skills/cortex-2-inventaire/SKILL.md` | `name: cortex-2-inventaire`, `description:` présente (696 caractères) | passe | haute |
| 6b. Moins de 300 lignes | `wc -l skills/cortex-2-inventaire/SKILL.md` | `200` | passe | haute |
| 6c. Section Notice §10 | md5 des sections `## Notice` des 7 SKILL.md | `9baaa1738e2e663c15276fa0ba210163` pour les sept, identiques | passe | haute |
| 7. Contrat | lecture croisée §2, §4, §7, §10 et amendements du `0c09255` | clés, enums, forme `~`, superset §4, tableau mail par voie : conformes. `uvx --from markitdown[all] markitdown` présent en `scan.py:118` conformément à l'amendement §3 | passe | haute |
| 8. Invariants `01-cadrage` | lecture, grep, inspection | I2 ✓ ; I3 ✓ ; I6 : aucun sous-agent livré par la lane ✓ ; I7 : aucun plugin Obsidian ✓ ; I10 renforcé : la lane a supprimé « Sur accord, lancer `cortex-3-ontologie` » et « On enchaîne ? » au profit de « Puis la section Notice ci-dessous » | passe | moyenne |
| Recette v1 | `python3 skills/cortex-4-installation/recette/parcours_blanc.py` | rc=1, `[erreur] skill presentation introuvable dans skills/` — cause préexistante (`2e0ee29`, décision du chef d'orchestre), sans lien avec la lane D | non mesurable pour D | haute |

## Défauts par sévérité

### Bloquant

Aucun.

### À corriger avant merge

**D-1. `skills/cortex-2-inventaire/scripts/scan.py:313-317` — le rejeu du scan détruit le travail de l'agent.**
`ecrire()` réécrit le fichier entier, sans fusion, sans garde, sans avertissement. Or `SKILL.md:130` prescrit exactement ce geste : « Rejouer le disque seul : `scan.py` avec le même `--out`, puis reporter le bloc `mail` et les blocs de l'agent. »
Preuve : un inventaire dont l'agent avait rempli `mail.en_tetes_lus: 1840`, `mail.agregats: [{domaine: client.test, volume: 612}]` et `bases: [{source_id: base-projets}]` revient après rejeu à `en_tetes_lus 0`, `agregats []`, `bases []`. Perte silencieuse, sur le chemin que la skill recommande elle-même. Les blocs perdus (`mail`, `bases`, `agenda`, `resume`, écarts dérivés) coûtent une campagne de lecture d'en-têtes à refaire.

**D-2. `skills/cortex-2-inventaire/scripts/scan.py:233` — `source_id` non unique entre racines.**
Le préfixe vient de `plat(racine.name)`. Deux racines de même nom de base produisent des identifiants en collision.
Preuve : `inventaire({}, [".../A/Travail", ".../B/Travail"], …)` rend `['travail', 'travail-x', 'travail', 'travail-x']`, uniques = `False`. `ecarts_candidats[].source_id` et `preuve_de` (contrat §4) pointent alors sur deux dossiers différents ; le maillon 3 ne peut plus lever l'ambiguïté. Cas réel plausible : `~/Documents/Travail` et `~/OneDrive/Travail`, ou deux dossiers clients homonymes.

**D-3. `skills/cortex-2-inventaire/scripts/scan.py:297` — `sante.max_structurants` détourné de son sens.**
Le contrat §2 définit cette clé comme le plafond de **copie** au maillon 5 (« Le maillon 5 ne copie que les types listés dans `structurants`, par lots de quatre, jusqu'à `sante.max_structurants` »). `scan.py` s'en sert comme plafond d'**extraction** de mots-signaux au maillon 2. Deux budgets sans rapport partagent une clé : abaisser le quota de copie ampute l'extraction. Le contrat n'ayant pas de clé pour ce second plafond, la valeur attendue est à porter au contrat par le chef d'orchestre.

**D-4. `skills/cortex-2-inventaire/scripts/scan.py:119` — pas de budget de temps global.**
`timeout=60` par fichier, aucun plafond sur la durée totale. Avec `max_extractions` à 40, une série de conversions bloquées coûte jusqu'à 40 minutes, contre une acceptation fixée à 60 s. Le cache `uv` froid consomme déjà 43,4 s des 60 sur la fixture dirigeant. Les budgets existants sont en octets (`OCTETS_PAR_FICHIER`, `OCTETS_TOTAL`), pas en secondes.

### Mineurs

**D-5. `scan.py:35` et `scan.py:373` — dépendance hors stdlib invisible au contrôle.**
`sys.path.insert` vers `cortex-4-installation/scripts`, puis `import cortex_config` à l'intérieur de `main()`. Le grep d'acceptation `^import|^from` ne le voit pas. Aucune capture d'`ImportError` : si le maillon 4 manque (zip partiel, dépôt de lane isolé), l'utilisateur reçoit une trace Python au lieu d'un message.

**D-6. `scan.py:337` — l'assertion « bornes en entiers » ne teste pas `depassement`.**
`assert all(isinstance(v, int) for v in b.values())` : en Python `isinstance(False, int)` vaut `True`. L'assertion passe quel que soit le type booléen. La ligne « bornes tous entiers : True » du rapport de lane repose sur ce contrôle.

**D-7. `scan.py:62-66` — `tilde()` peut rendre un chemin absolu.**
Hors `$HOME`, le chemin sort tel quel : `tilde("/tmp")` rend `/private/tmp`. Le `.resolve()` en ligne 64 peut en outre faire sortir de `$HOME` une racine symlinkée vers un volume externe. Un chemin absolu entre alors dans `01-inventaire.json`, contre l'invariant I2, sans être attrapé par le grep de recette (qui porte sur `skills/`, `notice/`, `outils/`, `README.md`) ni par `lint_sante.py` (qui cherche `/Users/` et `/home/`).

**D-8. `scan.py:252` — `graphify_propose: true` inconditionnel sur tout dossier `.git`.**
La décision 15 et le backlog parlent d'un « dépôt de code ». Un dépôt sans code (vault versionné, dossier de notes sous git) est proposé au même titre. `langages` est calculé quelques lignes plus bas et resterait un filtre naturel.

**D-9. `scan.py:264-266` — `graphify_propose` posé sur chaque ancêtre.**
Le seuil porte sur `fichiers_arbre`, cumulé chez tous les parents. Preuve : un dossier `Gros` à 0 fichier direct et 600 dans son sous-arbre, et son enfant `Gros/sous` qui les porte, ressortent tous deux à `graphify True`. La proposition se répète autant de fois qu'il y a de niveaux.

**D-10. `scan.py:147` — `.lnk` compté comme signal de base déportée.**
`EXT_LIEN = {".url", ".webloc", ".lnk"}`. Sur la machine Windows de la Phase G (décision 19), chaque raccourci de bureau devient un `base_deportee_non_declaree`, donc une question posée à la personne au maillon 3.

**D-11. `SKILL.md:165` — l'identifiant technique au lieu de la phrase canonique.**
« 2. Lance `cortex-3-ontologie`. » L'amendement §5 fixe la phrase canonique du maillon 3 : « décidons mes domaines ». La ligne nomme un identifiant de skill à un novice et double le rôle de la Notice, que la lane a par ailleurs correctement rétablie. Reliquat v1, même forme dans `skills/cortex-6-agents-metier/SKILL.md:120` (lane E).

**D-12. `scan.py:254-263` — boucle des langages imbriquée dans la boucle des racines.**
Le bloc de calcul des `langages` est indenté dans `for racine in racines`, donc recalculé intégralement à chaque racine sur un `disque` qui grandit. Résultat identique, travail en O(racines × disque × depots).

**D-13. `scan.py:220` — `e.stat()` hors du `try`.**
Un `OSError` sur une entrée (permission retirée en cours de parcours, volume démonté) remonte et avorte le scan entier, alors que le reste du code capture soigneusement `OSError` (lignes 126, 158, 168, 193).

### Pour information

- `chantiers/cortex-v2/consignes-D.md` (commit `dcd2852`, auteur : le chef d'orchestre, antérieur aux commits de la lane) arrivera sur `main` au merge. Le motif est déjà accepté : `consignes-G2.md` y est.
- Le contrat §5 annonce que la recette v1 rougit à cause d'`etat.py` à neuf étapes. Elle rougit en réalité sur le retrait de la skill `presentation` (`2e0ee29`). Un amendement du §5 éviterait qu'un auditeur de lane prenne ce rouge pour une régression.
- L'écart entre les 20 extractions de la lane et la 1 extraction d'un rejeu de l'audit vient du bac à sable : sans `UV_CACHE_DIR` accessible, `uvx` échoue et `extraction.echecs` passe à 19. Le script dégrade proprement et déclare l'échec. Ce n'est pas un défaut.

## Verdict

**Mergeable.**

Le périmètre est tenu : la lane n'a touché que `skills/cortex-2-inventaire/`. Le schéma produit est conforme au contrat §4 et à ses amendements, superset compris. Les deux critères d'acceptation du backlog passent sur les deux fixtures, avec les sorties ci-dessus. Le merge vers `main` est propre. Aucun invariant de `01-cadrage.md` n'est cassé, et I10 est mieux tenu qu'avant la lane.

Les quatre défauts « à corriger » touchent la robustesse du script, pas le contrat : ils se traitent en correctifs ciblés après le merge de B et C, avant la Phase G. D-1 est le plus coûteux s'il n'est pas traité : il détruit du travail sur un geste que la skill recommande.

## Décisions actées (chef d'orchestre, 2026-09-19)

- **Suite lane D** : merger, patcher après. `lane/D` entre dans `main` à son rang (B, C, D). Les quatre défauts D-1 à D-4 partent dans une session de reprise `fix/D` sur l'arbre fusionné, avant la Phase G.
- **Parade au défaut D-1** : fusion si `--out` existe. `scan.py` relit le JSON présent et ne remplace que `disque`, `depots`, `bornes`, `racines`, `extraction`, `genere_le` ; `mail`, `bases`, `agenda`, les `resume`, `preuve_de` et les écarts dérivés par l'agent survivent au rejeu. Retenu contre le refus sans `--force` parce que `SKILL.md:130` fait du rejeu du disque seul un geste normal de validation par substrat : le rendre coûteux découragerait la seule parade au scan partiel. Retenu contre le statu quo documentaire parce qu'une perte silencieuse ne se rattrape pas à la relecture.
- **Contrat §5** : amendé par le chef d'orchestre sur la cause réelle du rouge de la recette v1 (retrait de la skill `presentation`, `2e0ee29`), en plus de la cause annoncée (`etat.py` à neuf étapes). Sans quoi chaque audit de lane rouvre le même faux positif.
