# Rapport : lane A (code), Phase H2

Worktree `~/Dev/cortex--h2a`, branche `lane/h2a`, partie de `fix/phase-h` (`158d6c0`). Exécutant Opus 5.5. Rien de poussé, mergé ni rebasé. Recette : 117 contrôles avant la lane, 138 après, sortie 0.

## Commits

| Tâche | Hash | Objet |
|---|---|---|
| A1 | `65a1267` | `poste.py` : dossier des outils de uv, `present: null` et « à vérifier » |
| A2 | `50106cc` | `poste.py` : `--voie`, `voie_proposee` |
| A3 | `6408268` | `poste.py` : `options_proposees` vide sans `--options` |
| A4 | `59c040e` | `lint_sante.empreinte_commun()`, appelée par `federe.py`, comparée par le lint |
| A5 | `5c14e50` | `federe.py --inscrire` |
| A5 bis | `e763585` | consigne du chef d'orchestre : `--attendu` déjà membre ignoré avec un message |
| A6 | `2a11809` | `etat.py` : étape 8 d'un groupe, statut `en_cours` |
| A7 | `72ed49a` | hooks ancrés sur `${CLAUDE_PROJECT_DIR}` |
| A8 | `cc28331` | `scan.py` : dossier de médias seuls hors projets |
| A8 bis | `2e2253b` | retour silent-failure : l'écart du scan se retire au rejeu |
| A9 | aucun | non nécessaire, voir plus bas |
| A10, A11 | ce commit | recette, contre-épreuves, `05-execution.md` coché, ce rapport |

## Fichiers touchés

```
skills/cortex-0-poste/scripts/poste.py
skills/cortex-2-inventaire/scripts/scan.py
skills/cortex-4-installation/recette/parcours_blanc.py
skills/cortex-4-installation/scripts/etat.py
skills/cortex-4-installation/scripts/lint_sante.py
skills/cortex-4-installation/scripts/scaffold.py            (HOOKS seul)
skills/cortex-4-installation/template/vault/.claude/hooks/session_start.py
skills/cortex-4-installation/template/vault/.claude/hooks/stop.py
skills/cortex-8-federation/scripts/federe.py
chantiers/cortex-v2/phase-h2-majeurs/05-execution.md        (cases de la lane A)
chantiers/cortex-v2/phase-h2-majeurs/rapport-A.md
```

Tous dans la liste de la lane A de `03-backlog-technique.md`. `rend_notice.py` non touché.

## Ce qui change, correctif par correctif

**A1, détection.** Un outil se cherche dans le PATH, puis dans le dossier des outils de uv (`uv tool dir --bin`, repli `~/.local/bin`, qui vaut `%USERPROFILE%\.local\bin` sous Windows par `Path.home()`), puis par la sonde `uvx` pour markitdown. Un binaire trouvé vaut présent, sans `uvx`. Une sonde `uvx` qui échoue (code non nul, `OSError`, délai) rend `present: null` et sa `raison` ; seule l'absence d'`uvx` vaut `false`. `gh auth status` : « not logged into any » vaut `connecte: false`, tout autre échec `connecte: null` avec la raison, sans la ligne qui nomme le compte. `--dry-run` imprime `<outil> : à vérifier (<raison>)` pour `null`. Les sondes tournent avec un dossier courant temporaire : `markitdown --version` dépose un fichier `:memory:.ses` dans le dossier courant, et la Phase H en a laissé un dans `~/Cortex/` le 2026-09-27 à 18:19.

**A2, voie.** `--voie {connecteur,softeria,mcp-email,imap,aucune}`. Sans elle, une voie calculée qui installe (`softeria`, `mcp-email`) s'écrit `aucune`, et `mail.voie_proposee` garde la voie calculée.

**A3, options.** `options_proposees` vaut la liste de `--options`, vide sans elle ou sur `aucune`. La constante `OPTIONS` disparaît, plus rien ne la lit. Fixture `poste_json` de la recette alignée (`[]`).

**A4, lint du commun.** `lint_sante.empreinte_commun()` est la seule définition ; `federe.py` n'a plus de `def empreinte`. Même algorithme qu'avant, déplacé : sur un même commun, l'ancien `federe.empreinte` et la nouvelle fonction rendent `fdca3d39…ba3c` tous deux, donc les communs déjà scellés restent valides. `commun_edite_main` garde la marque « généré » et ajoute un constat `{file: <racine>, raison: « le commun ne correspond plus à son empreinte… »}` quand `.cortex-genere` existe et diffère.

**A5, inscription.** `federe.py --inscrire <slug> --redacteur --export --config [--nom] [--attendu …]`, conforme au §4. Refuse aussi un slug hors `[a-z0-9-]` et une valeur portant un guillemet ou un saut de ligne (`cortex_config` ne lit pas les échappements). Consigne du chef d'orchestre intégrée : un `--attendu` qui nomme un rédacteur déjà membre (comparaison sans casse ni espaces multiples) est ignoré, sans erreur, avec la ligne `[i] <nom> est déjà membre du groupe : non ajouté aux attendus`.

**A6, étape 8.** En `mode: federe`, si `07-federation.md` n'est pas `valide`, `etat.py` lit `<commun.racine>/federation.yaml` : absent, « groupe non inscrit » ; `attendus` non vide, « en attente de <noms> » ; un membre sans `remis_le` dans `<vault>/_cortex/06-passation.md` (vault = parent du parent de l'export), « en attente de <slugs> ». Dans ces cas l'étape vaut `arbitre` et la phrase suivante n'est jamais « relie les cerveaux » ; sinon elle vaut l'étape 8 à faire. `remis_le` se lit par le frontmatter : une valeur vide ne compte pas. `statut: en_cours` se lit « En cours ».

**A7, hooks.** `HOOKS` porte `python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/<hook>.py"` ; les deux hooks résolvent le vault par `CLAUDE_PROJECT_DIR`, sinon par `Path(__file__).parents[2]`, plus jamais par le dossier courant.

**A8, médias.** `ecarts()` pose `dossier_sans_domaine` pour un dossier dont toutes les extensions sont des images ou des vidéos, hors de `chemins.dossiers_projets`, quel que soit le nombre de fichiers. Indice : `<chemin> : 3 fichier(s), photos ou vidéos seulement`. Au rejeu, les écarts de médias posés par le scan (reconnus à la fin de leur indice) se reposent en entier : un dossier qui a reçu un `.docx` sort de la liste ; un `dossier_sans_domaine` dérivé par l'agent reste, sauf s'il porte le même `source_id` qu'un écart reposé.

**A9.** Aucun lecteur du `present` des outils dans la notice : le `present` de `rend_notice.py` l. 152 est celui de l'étape, toujours booléen. Rien à faire.

## Commandes d'acceptation (06-verification, lane A), sur `lane/h2a`

Recette complète :

```
$ python3 skills/cortex-4-installation/recette/parcours_blanc.py      # sortie=0
  C1   Neuf étapes, maillon 0, notice          28/28 VERT
  C2   Trois profils, régime, section Notice   12/12 VERT
  C3   Inventaire outillé sur les fixtures     17/17 VERT
  C4   Couche vault                            22/22 VERT
  C5   Régimes pointeur et copie                4/4  VERT
  C6   Fédération sur trois exports fictifs    15/15 VERT
  C7   Manifestes plugin                        4/4  VERT
  C8   White-label                              1/1  VERT
  C9   Zéro chemin absolu                       2/2  VERT
  C10  Paquet, notice hors ligne, README       10/10 VERT
138 contrôle(s) passé(s), 0 en échec.
```

Auto-tests, sortie 0 chacun :

```
poste.py --autotest          : poste.py : auto-test OK
etat.py --autotest           : etat.py : auto-test OK
lint_sante.py --autotest     : OK lint_sante.py : … lettre de lecteur, empreinte du commun
federe.py --autotest         : OK : commun de 14 projets, 11 acteurs (2 fusionnés), 2 domaines, identique sur deux générations, lint v1 vert
scaffold.py --autotest       : OK scaffold.py : forme ~, settings.json, hooks, …
scan.py --autotest           : OK scan.py : … refus de `contenu`, dossier de médias seuls
session_start.py --autotest  : OK session_start.py
stop.py --autotest           : OK stop.py
```

Vingt et un contrôles de recette ajoutés, tous préfixés « H2 » : C1 (11), C3 (1), C4 (4), C6 (5).

**A1 détection**, joué à la main (`HOME` temporaire, `PATH=/usr/bin:/bin`) :

```
--- montage : -rwxr-xr-x graphify ; PATH=/usr/bin:/bin
--- A1 détection, faux graphify posé :
uv : absent → brew install uv
markitdown : absent → uv tool install "markitdown[all]"
gh : absent → brew install gh
github-desktop : absent → brew install --cask github
buzz : absent → brew install --cask buzz
--- témoin, sans le faux binaire (0 fichier) :
…
graphify : absent → uv tool install "graphifyy[pdf,office]"
```

Contre-épreuve, ancien `poste.py`, faux binaire posé : `graphify : absent → uv tool install "graphifyy[pdf,office]"`.

**A1 non mesurable**, vrai `uvx` (`/opt/homebrew/bin/uvx`), `UV_CACHE_DIR` dans un dossier `dr-xr-xr-x`, markitdown hors du PATH :

```
markitdown : à vérifier (sonde uvx en échec : error: Failed to initialize cache at `/tmp/claude-501/a1ro/cache` ; Caused by: failed to create directory `/tmp/claude-501/a1ro/cache`: Permission denied (os error 13))
```

Contre-épreuve, ancien code, même montage : `markitdown : absent → uv tool install "markitdown[all]"`. Dans le bac à sable de cette session, la vraie sonde gh rend `(None, 'gh auth status illisible ici : - The token in keyring is invalid.')` ; l'ancien code lisait `connecte: false`.

**A2 voie**, `poste.py --ecrire --atelier <tmp> --fournisseur m365 --no-open` :

```
mail = {'fournisseur': 'm365', 'boites': 1, 'voie': 'aucune', 'voie_proposee': 'softeria', 'domaine': '', 'mx': ''}
avec --voie softeria :
mail = {'fournisseur': 'm365', 'boites': 1, 'voie': 'softeria', 'voie_proposee': 'softeria', 'domaine': '', 'mx': ''}
```

Contre-épreuve, ancien code : `'voie': 'softeria'` sans `--voie`.

**A3 options**, même commande : `options_proposees = []`. Contre-épreuve : `['wispr-flow', 'superwhisper', 'noota']`.

**A4 lint du commun.** Recette C6 : commun généré par `federe.py` depuis deux exports écrits par le vrai `export.py`, puis une ligne ajoutée à `HELENE - OPE - Belvédère.md` sous son en-tête « généré ». Témoin (commun intact) : `commun_edite_main == []`, vert. Après édition : constat « empreinte », vert. Contre-épreuve (ancien `lint_sante.py` et ancien `federe.py`) : `[XX] … est signalée (empreinte) : []`, le témoin restant vert.

**A4 une seule empreinte.** `grep -n "def empreinte" skills/cortex-8-federation/scripts/federe.py` : aucune ligne (code 1). Témoin : le même grep sur `fix/phase-h` rend `184:def empreinte(commun):`. Deux générations successives : contrôle C6 « deux générations ne diffèrent que sur genere_le » vert, et l'auto-test de `federe.py` compare les deux sceaux.

**A5 inscription.** C6 : deux `--inscrire helene` donnent un seul membre et `attendus == ["Karim B"]` ; `--inscrire karim --attendu "Hélène V"` vide `attendus`, imprime « Hélène V est déjà membre », puis `federe.py --config` génère le commun sur ce fichier. Dossier étranger (`reel-helene`, 6 fichiers) : sortie 1, liste et sha256 des fichiers identiques avant et après. Contre-épreuve sur l'ancien `federe.py` : les trois rouges, par option inconnue (code 2). Comme l'option est nouvelle, ce rouge ne prouve que l'absence de la commande ; deux mutations le complètent : le refus du dossier étranger neutralisé (`and False`) rend `[XX] … sort en 1 et n'y écrit rien : code 0` ; `ignores = []` fait tomber l'auto-test sur `AssertionError: {'membres': ['helene'], 'attendus': ['Karim Benali'], 'ignores': []}`.

**A6 attendus et étape 8.** C1 : un remis plus un attendu, arbitré « en attente de Karim B », phrase ≠ « relie les cerveaux » ; deux membres dont un non remis, arbitré « en attente de karim » ; les deux remis, `a_faire` et « relie les cerveaux » (témoin) ; `07-federation.md` en `en_cours`, « En cours ». Contre-épreuve, ancien `etat.py` :

```
[XX] … un autre attendu … : a_faire / None / relie les cerveaux
[XX] … un seul remis … : a_faire / None / relie les cerveaux
[ok] H2 témoin : les deux membres remis, « relie les cerveaux »
[XX] … statut en_cours … : illisible
```

Lecture des vaults réels de la Phase H, sans écriture : `attente_groupe({'commun': {'racine': '~/Cortex/alcyon-commun'}})` rend `None` (Hélène et Karim remis), et le format réduit `---\nremis_le: 2026-09-27\n---` est bien lu.

**A7 hooks.** `settings.json` d'un vault généré :

```
36:            "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start.py\""
46:            "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/stop.py\""
```

`cd /tmp && CLAUDE_PROJECT_DIR=<vault> python3 <vault>/.claude/hooks/stop.py --autotest` : `OK stop.py`, sortie 0. La commande SessionStart de `settings.json` jouée depuis `/tmp` : `Contrôle de santé : 0 problème(s) bloquant(s), 0 point(s) à surveiller.` Contre-épreuve, commande relative de `fix/phase-h` depuis `/tmp` : `can't open file '/private/tmp/.claude/hooks/stop.py': [Errno 2] No such file or directory`, sortie 2. Recette C4, ancien code : trois rouges (commande non ancrée, hook introuvable depuis un autre dossier, hook sans `CLAUDE_PROJECT_DIR` muet). Le quatrième contrôle C4, `stop.py --autotest` lancé hors du vault, reste vert sur l'ancien code aussi : il ne discrimine rien, c'est un contrôle de fumée, compté comme tel.

**A8 médias.** C3 : trois `.jpg` dans `Divers/Photos`, trois `.docx` dans `Divers/Notes`, six fichiers posés vérifiés ; un seul candidat, celui des photos. Contre-épreuve, ancien `scan.py` : `[XX] … : 6 fichiers posés, code 0, []`. Le témoin `.docx` mord : en mutation (`docx` ajouté aux médias), le contrôle passe rouge avec deux candidats.

**Périmètre.**

```
$ git diff --stat fix/phase-h..lane/h2a -- skills
 skills/cortex-0-poste/scripts/poste.py             | 194 +++++++++++++++----
 skills/cortex-2-inventaire/scripts/scan.py         |  71 ++++++-
 .../recette/parcours_blanc.py                      | 206 ++++++++++++++++++++-
 skills/cortex-4-installation/scripts/etat.py       |  92 ++++++++-
 skills/cortex-4-installation/scripts/lint_sante.py |  61 +++++-
 skills/cortex-4-installation/scripts/scaffold.py   |   5 +-
 .../template/vault/.claude/hooks/session_start.py  |  16 +-
 .../template/vault/.claude/hooks/stop.py           |  10 +-
 skills/cortex-8-federation/scripts/federe.py       | 157 +++++++++++++---
 9 files changed, 724 insertions(+), 88 deletions(-)
```

Un filtre de la liste des fichiers modifiés contre les neuf fichiers de la lane rend vide (code 1) ; témoin : retirer un seul nom du filtre fait apparaître les autres. `git diff fix/phase-h..lane/h2a -- …/cloture/export.py` : 0 ligne ; témoin : le même diff sur `a7b7678`, dernier commit d'`export.py`, en rend 41. Aucune ligne ajoutée ou retirée ne porte `sandbox` ni `poser_identite` ; témoin : le même grep sur `01955f6` en compte 3. Le diff de `scaffold.py` ne porte que sur `HOOKS` et son commentaire.

## Contrôle silent-failure

Agent `silent-failure-hunter` sur les sept fichiers du critère, diff `fix/phase-h..lane/h2a`. Deux constats, un corrigé, un laissé au contrat.

- **Corrigé (`2e2253b`).** `scan.py` : un `dossier_sans_domaine` posé par le scan n'était ni purgé ni remplacé au rejeu quand le dossier cessait d'être un dossier de médias ; il survivait à tous les rejeux. Il se repose désormais en entier. Ajouter le type à `ECARTS_DU_DISQUE`, comme l'agent le proposait, aurait effacé aussi les écarts du même type que l'agent dérive du cadrage ; le tri se fait donc sur la fin de l'indice. Mutation : sans ce tri, l'auto-test tombe sur l'écart périmé encore présent.
- **Laissé, texte du contrat.** `lint_sante.py` : le constat d'empreinte réunit deux causes (« une note a été éditée à la main ou le commun est périmé ») et ne nomme pas de fichier. C'est le message fixé mot pour mot par le §9, et le sceau est un hash unique : il dit que le commun a changé, pas où. Le remède est le même dans les deux cas (relancer la fédération, qui écrase une édition à la main). Le contrôle par note, juste au-dessus, continue de nommer chaque note sans marque.
- **Jugé sain par l'agent.** Les sondes `uvx` et `gh` (null avec raison sur échec, false seulement sur absence prouvée), le repli `uv tool dir --bin` vers `~/.local/bin` (mandaté), les refus d'`--inscrire` tous placés avant toute écriture, le `except ValueError` d'`etat.py`, exactement ce que lève `cortex_config.charger`.

## Points en attente

Aucun point ne bloque la lane. Ceux qui suivent relèvent d'une décision ou d'un fichier hors lane A.

1. **Libellé de l'étape 8 dans la notice (décision).** `rend_notice.py` l. 151 rend toute étape arbitrée par « sans objet : <raison> ». En groupe, la notice affichera donc « Arbitré, sans objet : en attente de karim », là où le produit attend « arbitrée, en attente de Karim ». Le §1 n'ouvre `rend_notice.py` à la lane A que pour `present: null`. Options : autoriser une ligne dans `rend_notice.py` (ne préfixer « sans objet » que pour la raison solo) ; ou laisser ainsi pour le parcours C.
2. **Nom de skill visible dans la notice (constat, hors lane).** Chaque ligne du tableau de bord porte en petit le nom du maillon (`cortex-8-federation`), mot proscrit par le §5. Ni le contrat ni le backlog ne le traitent.
3. **Lane B, `skills/cortex-2-inventaire/SKILL.md`.** Le tableau des écarts dit `dossier_sans_domaine` « plus de 5 fichiers », dérivé par l'agent. Le scan pré-remplit désormais les dossiers de médias seuls hors projets, quel que soit leur nombre ; le SKILL.md peut le dire, comme il le dit pour les deux autres écarts du scan.
4. **Interprétations du §3, à confirmer par l'audit.** Un `07-federation.md` en `brouillon` ou `en_cours` donne l'état « En cours » (la règle générale et la dernière ligne du §3), et non `a_faire` ; la phrase suivante vaut « relie les cerveaux » dans les deux cas. Ajout hors texte : un groupe à un seul membre inscrit, sans attendu, reste arbitré (« en attente d'un second rédacteur »), parce que `federe.py` refuse moins de deux membres et la notice ne doit pas proposer une commande vouée au refus.
5. **`federation.yaml` est dans l'empreinte du commun** (§9 : tous les fichiers hors sceau). Une inscription après la génération rend donc le commun « périmé » au lint jusqu'à la fédération suivante. C'est vrai dans les faits (un membre de plus) ; à savoir pour le parcours C.
6. **Raison d'attente.** Avec des attendus, la raison nomme la personne (« en attente de Karim Benali ») ; sans attendu, le slug (« en attente de karim »), comme le §3 le prévoit. L'annexe écrit « en attente de `karim` » pour Hélène remise avant le cadrage de Karim : dans ce cas précis, Karim figure encore dans `attendus` et la notice dira son nom complet.
7. **Restes de la Phase H.** `~/Cortex/:memory:.ses` (2026-09-27 18:19) vient de la sonde markitdown lancée depuis `~/Cortex` ; corrigé à la source (A1), le fichier reste à supprimer lors de la préparation de la lane C, hors périmètre ici.
8. **`recette/rejeu_profil.py`** (hors lane) lit `present` comme un booléen : un outil `null` y compte comme absent de la liste `outils`. Sans effet sur la chaîne, à savoir.
9. **Windows.** Les contrôles de recette à faux exécutables (C1, A1 à A3) se jouent hors Windows ; sous Windows ils rendent une ligne verte explicite « contrôle joué hors Windows ». Le contrôle manuel M3 reste le seul témoin Windows.
