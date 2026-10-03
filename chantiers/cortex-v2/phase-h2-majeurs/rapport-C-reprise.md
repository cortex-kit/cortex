# Rapport : reprise finale après la lane C

- Date : 2026-10-03
- Worktree `~/Dev/cortex--h2c`, branche `fix/h2c`, issue de `360d143`. Aucun push, aucun merge, aucun tag.
- Consignes : `consignes-C-reprise.md`, points 1 à 7. Lus avant : `verdict-phase-h2.md`, `04-contrat.md` (H2) et le dernier amendement de `chantiers/cortex-v2/04-contrat.md` (2026-10-03).

## Ce qui a changé, point par point

### 1. P-ecrit, la parade

- `cortex-4-installation/SKILL.md` : la seule commande en `cd` des SKILL.md (`cd "<vault>" && gh repo create … --source .`) devient `gh repo create cortex-<slug> --private --source "<vault>" --push`. Le contrôle vivant qui a produit la trace chez Karim demande désormais `find "<racine>" -type f, sans cd`, et la raison est écrite à côté.
- `scaffold.py` : la commande de dépôt privé affichée et exécutée passe `--source "<vault>"`, sans `cd`.
- Doctrine §9 : une commande nomme la racine en entier, jamais `cd` vers une racine ni hors du vault, avec la raison (le harnais laisse `.claude/` dans tout dossier où une commande entre par `cd`).
- Gabarit `CLAUDE.md` du vault, section « Écritures interdites », et `Guide d'usage.md` (maillon 7, §1, question « Qu'est-ce que je ne dois jamais faire ? ») : la phrase « ne jamais se déplacer dans un dossier de travail avec `cd`, le harnais y laisse une trace ; nommer le dossier en entier ».
- Recette, C9 : contrôle « aucun SKILL.md ne prescrit un cd vers un chemin », sur les 16 SKILL.md (neuf maillons, six skills du vault, stop-slop).

### 2. Q-vocab

- Maillon 4, récapitulatif : « Dis « clôture » à la fin de trois vraies séances de travail » au lieu de « Fais tourner `cloture` ». Règle ajoutée sous les messages : « l'installation », jamais « le scaffold » ; aucun nom de skill ou de script ; une limite du kit ne devient pas une question à la personne (le cas `etat.py` de Karim).
- Maillon 6 : même règle, et un assistant non testé se dit en clair, jamais « le contrôle est marqué arbitré ».
- Maillon 7, guide d'usage : « dire « clôture » » au lieu de « lancer `cloture` ».
- Recette, C2 : contrôle de vocabulaire étendu aux récapitulatifs, soit les blocs de code des sections « Message de clôture » et « Récap » des neuf maillons et des six skills du vault (17 blocs). Motifs refusés : tout identifiant entre accents graves, `.py`, `cortex-N`, maillon, scaffold, skill, « contrôle arbitré », consultant, solo, fédéré, régime, pointeur, écart, profil.

### 3. Q-repose

Doctrine §11, « Réponse acquise » : une réponse libre qui dit l'usage tranche le traitement, aucune question « comment le traiter ? » ne la suit. Maillon 1 (questions du profil) et maillon 2 (étape 0 et bases) : l'outil noté « par ses exports, sans adresse » se relève par ses exports, ne bloque pas l'étape 0, et son traitement ne se redemande pas.

Écart à la consigne : elle cite « doctrine §10 ». Le §10 de `doctrine.md` est « Ce qui se valide se voit » ; la règle des réponses acquises vit au §11 (§8 du contrat H2). La phrase est au §11.

### 4. m-trace

- Nouveau `template/vault/.claude/skills/cloture/cloture.py` (stdlib, auto-test) : ajoute les chemins nommés et l'export du commun, commite par `subprocess` sous l'identité locale du vault (à défaut le rédacteur de `config.yaml`, jamais celle du poste), retire toute ligne `Co-Authored-By`, `Claude-Session`, `claude.ai/code` ou « Generated with Claude » du message, pousse si un distant existe.
- `scaffold.py` : `allow` perd `git add`, `git commit`, `git push` et gagne `cloture.py` ; `deny` gagne `Bash(git commit:*)`. Auto-test mis à jour.
- Skill `cloture` §8 : le commit passe par le script. Maillons 5, 6 et 7 : leurs écritures dans le vault s'enregistrent par le même script. Maillon 7, contrôle 1 de la recette d'acceptation : `git log --all --format=%B | grep -iE "co-authored-by|claude-session|claude\.ai/code"`, attendu vide.
- Recette, C4 : commit de clôture par `cloture.py` sur le vault scaffoldé, et règle `deny`.

Vérification sur un vault scaffoldé (`config_v2` de la recette, rédacteur Hélène Vasseur), témoin compris :

```
$ scaffold.py --config config.yaml --out vault   # sortie 0
$ python3 .claude/skills/cloture/cloture.py --vault . --message '<message avec Co-Authored-By et Claude-Session>' '60 - Journal/2026-10-03 - Essai.md'
✓ Enregistré : Clôture : essai
↻ Sauvegarde en ligne absente.
# sortie 0
$ git log --format='%h %an <%ae>%n%B---'
444ab5a Hélène Vasseur <roumier@exemple.test>
Clôture : essai
---
c7980f6 Hélène Vasseur <roumier@exemple.test>
Vault initial (scaffold Cortex)
---
$ git log --all --format=%B | grep -ciE 'co-authored-by|claude-session'
0 # sortie 1
# témoin : même message par `git commit -m` tapé, puis le même grep
2 # sortie 0
$ settings.json deny : ['Edit(/tmp/claude-501/verif-mtrace-b9miksgx/travail/**)', 'Edit(/private/tmp/claude-501/verif-mtrace-b9miksgx/travail/**)', 'Bash(git commit:*)']
```

### 5. Mineurs

- m-nom : maillon 0, le nom court et l'adresse se demandent par question ouverte ; rien ne se propose depuis le compte Claude du poste, son adresse, l'utilisateur de l'ordinateur ou le dossier personnel. Ligne ajoutée aux interdits.
- m-matrice : maillon 5, nouveau §4 bis : la table « qui fait foi » signée au maillon 3 se reporte dans `90 - Meta/Architecture Mémoire.md` §2, le lien interdit dans la table des flux d'`Architecture - Vue d'ensemble`. Contrôle de sortie `grep -c "| _à renseigner_ |" … # attendu : 0`, contrôle d'état `matrice_reportee`. Choix du maillon 5 plutôt que du scaffold : la matrice vit dans `02-ontologie.md`, pas dans `config.yaml`, et le scaffold ne lit que la config.
- m-PLU : la cause n'était pas le nom de fichier, déjà lu par `scan.py`, mais la règle des quatre lettres : « PLU » en a trois. `mots()` garde désormais, pour les noms de fichiers et de dossiers seulement, les sigles de deux ou trois capitales. Auto-test ajouté. Contre-épreuve sur un dossier `Foncier/PLU Lyon 2026 synthese.pdf` :

```
HEAD (avant) : ['lyon', 'synthese', 'foncier']
fix/h2c : ['lyon', 'synthese', 'plu', 'foncier']
```

- m-outils : maillon 0, libellés d'option en langage ordinaire (« Lecteur de notes (Obsidian) »), option « Aucun » à la question des outils et « Aucune » à celle des options.

### 6. Version

`plugin.json` passe à `2.0.0`. `README.md` ne portait plus « version 2 en chantier » depuis `cdd0201` ; il dit « Version 2.0.0 » et « une suite d'étapes guidées » au lieu de « une chaîne de maillons guidés » (mot interdit devant la personne, doctrine §8). `notice/LISEZ-MOI.html` régénéré par `rend_notice.rendre(etat.generer(atelier vierge, paquet="2.0.0"))`, après correction de sa source `scripts/notice.md` : « pose une question par écart » devient « pose une question sur chaque point à éclaircir ». Diff de la notice : cette ligne et la ligne de génération (`paquet 2.0.0`). `notice.md` sort de la liste des fichiers cités par la consigne ; sans lui, la notice régénérée par le fabricant reprendrait « écart ».

## 7. Recette, auto-tests, greps

Recette complète, `/usr/bin/python3 skills/cortex-4-installation/recette/parcours_blanc.py`, sous sandbox :

```
Tableau C1 à C10 (contrôles passés / total)
  C1   Neuf étapes, maillon 0, notice                     §3 §5 §10    lane B       29/29 VERT
  C2   Trois profils, régime, section Notice              §2 §10       lane C       13/13 VERT
  C3   Inventaire outillé sur les fixtures                §4           lane D       17/17 VERT
  C4   Couche vault : permissions, hooks, skills, agents  §9           lane E       24/24 VERT
  C5   Régimes pointeur et copie, structurant périmé      §2           lane E        4/4  VERT
  C6   Fédération sur trois exports fictifs               §6           lane F       16/16 VERT
  C7   Manifestes plugin                                  §11          lane chef     4/4  VERT
  C8   White-label                                        01-cadrage   lane toutes   1/1  VERT
  C9   Zéro chemin absolu                                 I2, §11      lane toutes   3/3  VERT
  C10  Paquet, notice hors ligne, README                  §11          lane B       10/10 VERT

144 contrôle(s) passé(s), 0 en échec.
Recette verte.
```

144 contrôles, 140 au verdict de la lane C : les quatre nouveaux sont ceux des points 1, 2 et 4.

```
  [ok] H2 : les récapitulatifs de fin (17 blocs, 15 SKILL.md) ne nomment ni skill, ni script, ni mot de la chaîne (doctrine §8)
  [ok] H2 : un commit de clôture (cloture.py du vault) signe sous l'identité du vault, sans Co-Authored-By ni Claude-Session
  [ok] H2 : git commit tapé refusé (deny), la clôture passe par cloture.py (allow)
  [ok] H2 : aucun SKILL.md (16, skills du vault comprises) ne prescrit un cd vers un chemin
```

Contre-épreuve : la nouvelle recette jouée sur une copie de `HEAD` (`git archive 360d143`, seul `parcours_blanc.py` remplacé) sort en 1, les quatre nouveaux contrôles rouges, les 140 anciens verts :

```
  [XX] H2 : les récapitulatifs de fin (17 blocs, 15 SKILL.md) ne nomment ni skill, ni script, ni mot de la chaîne (doctrine §8) : {'cortex-4-installation': ['`cloture`']}
  [XX] H2 : un commit de clôture (cloture.py du vault) signe sous l'identité du vault, sans Co-Authored-By ni Claude-Session : code 2, 'Camille Roumier\nVault initial (scaffold Cortex)\n\n', … can't open file '…/vault-pointeur/.claude/skills/cloture/cloture.py': [Errno 2] No such file or directory
  [XX] H2 : git commit tapé refusé (deny), la clôture passe par cloture.py (allow) : ['Edit(…/fixtures/dirigeant/**)', 'Edit(~/Desktop/Travail/**)']
  [XX] H2 : aucun SKILL.md (16, skills du vault comprises) ne prescrit un cd vers un chemin : 1 ligne(s) : ['skills/cortex-4-installation/SKILL.md:68']
140 contrôle(s) passé(s), 4 en échec.
```

Auto-tests, `/usr/bin/python3 <script> --autotest` :

```
fabricant/scripts/fabrique.py : sortie 0
skills/cortex-0-poste/scripts/poste.py : sortie 0
skills/cortex-2-inventaire/scripts/scan.py : sortie 0
skills/cortex-4-installation/recette/rejeu_profil.py : sortie 0
skills/cortex-4-installation/scripts/cortex_config.py : sortie 0
skills/cortex-4-installation/scripts/etat.py : sortie 0
skills/cortex-4-installation/scripts/lint_sante.py : sortie 0
skills/cortex-4-installation/scripts/notice.py : sortie 0
skills/cortex-4-installation/scripts/rend_notice.py : sortie 0
skills/cortex-4-installation/scripts/scaffold.py : sortie 0
skills/cortex-4-installation/template/vault/.claude/hooks/session_start.py : sortie 0
skills/cortex-4-installation/template/vault/.claude/hooks/stop.py : sortie 0
skills/cortex-4-installation/template/vault/.claude/skills/cloture/cloture.py : sortie 0
skills/cortex-4-installation/template/vault/.claude/skills/cloture/export.py : sortie 0
skills/cortex-5-ingest/scripts/copie_structurant.py : sortie 0
skills/cortex-8-federation/scripts/federe.py : sortie 0
```

`scaffold.py --autotest` est sorti une fois en 1 pendant la reprise (son assertion figeait la liste `deny` sans `git commit`) ; assertion mise à jour, sortie 0 ensuite.

`ast.parse` et greps :

```
$ /usr/bin/python3 --version
Python 3.9.6
$ find skills fabricant -name "*.py" | xargs /usr/bin/python3 -c "import ast,sys; …"
18 fichiers, ast.parse OK
(sortie 0)

$ grep -rnE '(^|[[:space:];&|(`])cd +["'']?(~|\$|<|/|\.\.)' --include=SKILL.md skills | wc -l
       0
# témoin, HEAD :
HEAD:skills/cortex-4-installation/SKILL.md:68:cd "<vault>" && gh repo create cortex-<slug> --private --source . --push

$ grep -rnE "/Users/|/home/" skills notice outils README.md --include="*.md" --include="*.html" --include="*.json" --include="*.yaml" | grep -v "grep -rE" | wc -l
       0
```

White-label : contrôle C8 de la recette, 1/1 vert (empreintes des marques interdites sur `skills/`, `notice/`, `outils/`, `README.md`). Chemins absolus : C9, 3/3 vert.

## Ce qui reste hors de cette reprise

- Le parcours n'a pas été rejoué : les corrections de prose (Q-vocab, Q-repose, m-nom, m-outils, m-matrice) sont vérifiées par lecture et par les contrôles de recette, pas par une session vivante.
- `marketplace.json` garde « une chaîne de maillons guidés » dans sa description : fichier hors du mandat.
- Le gabarit du vault propose encore à la personne de lancer une session dans le dossier d'un projet (`CLAUDE.md`, détection de projet, point 4, et le runbook des sessions). C'est un geste humain, pas une commande d'assistant, et le `CLAUDE.md` du projet vit dans ce dossier par conception ; à trancher si la trace `.claude/` d'une session lancée là pose le même problème sur un dossier synchronisé.
