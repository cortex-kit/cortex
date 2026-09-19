# 06 : Vérification (lane G)

Recette v2, rejouée le 2026-09-19 sur `fix/final` (branche issue de `main` après merge des six lanes et de la reprise finale).

**114 contrôles passés, 0 en échec, sortie 0.** L'écart `outillage_seul` de la lane E, ouvert au moment de la ligne G, est clos : `fix/E` a porté le correctif et les deux contrôles C4 passent. Le compte est monté de 113 à 114 avec le contrôle I10 posé par la reprise finale (aucun maillon ne porte « On enchaîne » ni « lance `cortex- »). Tout est vert, les dix critères compris.

Aucun contrôle n'est marqué `[--]` : tout ce qui est écrit ici est mesuré. Les trois contrôles qui ne peuvent pas l'être par un script, plus le quatrième ajouté le 2026-09-19, sont les contrôles manuels M1 à M4, en fin de fichier.

À rejouer après chaque modification du dépôt, puis en Phase I sur le tag.

## Commande unique

```
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?
```

Sortie du 2026-09-19 (`fix/final`) : sections v1 23 ok / 0 en échec ; tableau :

```
Tableau C1 à C10 (contrôles passés / total)
  C1   Neuf étapes, maillon 0, notice                     §3 §5 §10    lane B       17/17 VERT
  C2   Trois profils, régime, section Notice              §2 §10       lane C       12/12 VERT
  C3   Inventaire outillé sur les fixtures                §4           lane D       16/16 VERT
  C4   Couche vault : permissions, hooks, skills, agents  §9           lane E       16/16 VERT
  C5   Régimes pointeur et copie, structurant périmé      §2           lane E        4/4  VERT
  C6   Fédération sur trois exports fictifs               §6           lane F        9/9  VERT
  C7   Manifestes plugin                                  §11          lane chef     4/4  VERT
  C8   White-label                                        01-cadrage   lane toutes   1/1  VERT
  C9   Zéro chemin absolu                                 I2, §11      lane toutes   2/2  VERT
  C10  Paquet, notice hors ligne, README                  §11          lane B       10/10 VERT
  M1   Installation vivante du plugin (marketplace add, install, details) manuel, sortie collée dans 06-verification.md
  M2   Sonde Cowork bureau : uvx --from "markitdown[all]" markitdown --version dans le bac à sable manuel, sortie collée dans 06-verification.md
  M3   Maillon 0 et installation du plugin sur la machine Windows manuel, sortie collée dans 06-verification.md
  M4   Permissions du vault en session interactive (allow, additionalDirectories, deny) manuel, sortie collée dans 06-verification.md

114 contrôle(s) passé(s), 0 en échec.
Recette verte.
```

Sortie de `echo $?` : `0`.

## Tableau C1 à C10

| Critère | Contrat | Lane | Ce qui est vérifié | 2026-09-19 |
|---|---|---|---|---|
| C1 Neuf étapes, maillon 0, notice | §3 §5 §10 | B | `etat.py` à neuf étapes 0 à 8 avec les artefacts du contrat ; maillon 0 lu depuis `poste.json` (fait si `notice_ouverte_le`) ; étape 8 `arbitre` « vault solo » en mode solo ; pivot avec `profil`, `regime`, `phrase_suivante`, `notice_ouverte_le` ; **atelier solo complet : 8 faites et 1 arbitrée, jamais 9/9 (§5 amendé)** ; **atelier `mode: federe` complet : 9 sur 9** ; page vierge à **8 pastilles « À faire »**, la neuvième étant l'étape courante rendue en tête hors tableau ; zéro URL ; `notice.py --no-open` ; `poste.py --dry-run` une ligne par outil absent | 17/17 vert |
| C2 Trois profils, régime, section Notice | §2 §10 | C | `fixtures.py` en moins de 10 s ; `references/profils/{employe,dirigeant,societe}.md` ; trois configs de profil installables ; `profil: autre` et `regime: mixte` refusés avec la clé nommée ; neuf SKILL.md maillons avec la section Notice ; moins de 300 lignes ; **aucun maillon ne porte « On enchaîne » ni « lance `cortex- » : la section Notice seule propose la suite (I10, arbitrage 2026-09-19)** | 12/12 vert |
| C3 Inventaire outillé sur les fixtures | §4 | D | `scan.py` sur employé, dirigeant, société (camille) : sortie 0 en moins de 60 s ; format `cortex/inventaire` v2 ; `bornes` en entiers ; aucun champ `contenu` ; **forme `~` exigée seulement si les fixtures vivent sous le dossier personnel, sinon l'absolu est accepté et la sortie le dit (§4 amendé)** ; `export-notion-*.csv` signalé comme base déportée sur employé | 16/16 vert |
| C4 Couche vault : permissions, hooks, skills, agents | §9 | E | `settings.json` : `additionalDirectories` = `collecte.racines`, `deny` Write et Edit par racine, aucun allow ouvert ; **hooks vérifiés comme scripts : `settings.json` appelle `.claude/hooks/session_start.py` et `stop.py`, les deux fichiers sont livrés, `session_start.py` contient `lint_sante.py` et `--bref`, `stop.py` contient « clôture », chacun sort en 0 sur `--autotest` (§9 amendé)** ; skills `parle` et `bilan` ; sous-agents `tools: Read, Grep, Glob` ; `{{DOSSIERS_PROJETS}}` en forme `~` ; **un fichier binaire déposé sous `template/vault/.claude/` ne casse pas `--outillage-seul`, et le lint embarqué est quand même réactualisé** | 16/16 vert |
| C5 Régimes pointeur et copie, structurant périmé | §2 | E | lint 0 en pointeur ; en copie, note `50 - Ressources/Structurants/<type>/` avec `source_path`, `hash`, `copie_le` : contrôle « 10 lignes » suspendu, lint 0 ; source modifiée, `structurant_perime` levé | 4/4 vert |
| C6 Fédération sur trois exports fictifs | §6 | F | trois `_export/<slug>/` construits selon §6 depuis les noms de `fixtures.societe` ; `federation.yaml` lisible ; `federe.py` sort 0 ; deux générations identiques hors `genere_le` ; Centre, README « ne pas éditer », `.cortex-genere` ; projets préfixés du slug ; acteur commun fusionné `source_vault` multiple ; domaine fusionné ; `visibilite: prive` refusée et absente | 9/9 vert |
| C7 Manifestes plugin | §11 | chef | `plugin.json` (name cortex, version, description) ; `marketplace.json` (name cortex-kit, un plugin, `source: ./`) ; un SKILL.md par dossier de `skills/` (10) avec `name` = dossier et `description` ; `fabricant` hors plugin | 4/4 vert |
| C8 White-label | 01-cadrage | toutes | aucune marque interdite dans `skills/` (annexes comprises), `notice/`, `outils/`, `README.md` ; liste portée en douze empreintes sha256 (le dépôt est public) ; détection par mot, bigramme et trigramme normalisés | 1/1 vert |
| C9 Zéro chemin absolu | I2, §11 | toutes | aucun `/Users/<nom>/`, `/home/<nom>/`, `X:\` dans le même périmètre ; **les lignes qui définissent le motif de détection (`re.compile`, chaîne brute `r"…"`, commande `grep`) et les fragments cités entre backticks sont exclus : un motif montré n'est pas un chemin de machine, et la sortie l'annonce** ; les maillons se référencent par `${CLAUDE_SKILL_DIR}` | 2/2 vert |
| C10 Paquet, notice hors ligne, README | §11 | B | `fabrique.py` sort 0 ; le zip compte les maillons présents par glob (9) plus le kit (1) et deux fichiers à la racine ; `recette/` hors zip ; un SKILL.md par dossier à la bonne profondeur ; PROVENANCE couvre le kit ; **`LISEZ-MOI.html` du zip à 8 pastilles « À faire »**, zéro URL ; `notice/LISEZ-MOI.html` et `outils/OUTILS.md` présents ; README avec les trois gestes | 10/10 vert |

## Sortie par critère (2026-09-19, `fix/final`)

### C1 Neuf étapes, maillon 0, notice

```
C1. Neuf étapes, maillon 0, notice (§3 §5 §10 ; lane B) : défaut plausible : un tableau de bord qui compte sept quand la chaîne en a neuf
  [ok] etat.py porte neuf étapes numérotées 0 à 8
  [ok] les artefacts des neuf étapes sont ceux du contrat §5
  [ok] le pivot porte les neuf étapes
  [ok] le pivot se régénère à l'identique hors horodatage
  [ok] le maillon 0 est lu depuis poste.json : fait quand notice_ouverte_le est renseigné
  [ok] un poste.json sans notice_ouverte_le ne compte pas comme fait
  [ok] l'étape 8 vaut arbitre avec la raison « vault solo » en mode solo
  [ok] le pivot porte profil, regime, phrase_suivante et notice_ouverte_le
  [ok] la phrase suivante est en langage ordinaire, jamais un nom de maillon
  [ok] le trou en 03 est porté avec sa raison en clair
  [ok] l'étape 4 se déduit d'un artefact aval, jamais devinée
  [ok] atelier solo complet : 8 faites et 1 arbitrée (§5 amendé), jamais 9/9
  [ok] atelier fédéré complet : le compteur annonce 9 sur 9
  [ok] le tableau de bord vierge affiche 8 pastilles « À faire », la 9e étant la courante en tête
  [ok] aucune URL distante dans la notice
  [ok] notice.py --no-open régénère etat.json et notice.html et sort en 0
  [ok] poste.py --dry-run sort en 0 et n'imprime qu'une ligne par outil absent, avec sa commande
```

### C2 Trois profils, régime, section Notice

```
C2. Trois profils, régime, section Notice (§2 §10 ; lane C) : défaut plausible : un profil inconnu accepté, un régime hybride inventé
  [ok] fixtures.py génère trois arbres en moins de 10 s
  [ok] cortex-1-cadrage/references/profils/employe.md existe
  [ok] cortex-1-cadrage/references/profils/dirigeant.md existe
  [ok] cortex-1-cadrage/references/profils/societe.md existe
  [ok] la config employe (régime copie) est installable
  [ok] la config dirigeant (régime pointeur) est installable
  [ok] la config societe (régime pointeur) est installable
  [ok] profil: autre est refusé et le message nomme la clé
  [ok] regime: mixte est refusé et le message nomme la clé
  [ok] neuf SKILL.md maillons, chacun avec la section Notice et l'appel de notice.py (I10)
  [ok] chaque SKILL.md maillon fait moins de 300 lignes
  [ok] aucun maillon n'enchaîne, la section Notice seule propose la suite (I10, arbitrage 2026-09-19)
```

### C3 Inventaire outillé sur les fixtures

```
C3. Inventaire outillé sur les fixtures (§4 ; lane D) : défaut plausible : un inventaire qui copie du contenu ou ment sur ses bornes
  [ok] scan employe : sort en 0 en moins de 60 s
  [ok] scan employe : format cortex/inventaire v2, profil et régime portés
  [ok] scan employe : bornes en entiers, depassement booléen, max_dossiers respecté
  [ok] scan employe : aucun champ contenu, nulle part
  [ok] scan employe : disque non vide, chemins en forme ~, source_id et substrat portés
  [ok] employé : export-notion-*.csv apparaît comme signal de base déportée
  [ok] scan dirigeant : sort en 0 en moins de 60 s
  [ok] scan dirigeant : format cortex/inventaire v2, profil et régime portés
  [ok] scan dirigeant : bornes en entiers, depassement booléen, max_dossiers respecté
  [ok] scan dirigeant : aucun champ contenu, nulle part
  [ok] scan dirigeant : disque non vide, chemins en forme ~, source_id et substrat portés
  [ok] scan societe : sort en 0 en moins de 60 s
  [ok] scan societe : format cortex/inventaire v2, profil et régime portés
  [ok] scan societe : bornes en entiers, depassement booléen, max_dossiers respecté
  [ok] scan societe : aucun champ contenu, nulle part
  [ok] scan societe : disque non vide, chemins en forme ~, source_id et substrat portés
```

### C4 Couche vault : permissions, hooks, skills, agents

```
C4. Couche vault (§9 ; lane E) : défaut plausible : un agent qui peut écrire dans les dossiers de travail
  [ok] scaffold accepte une config v2 complète
  [ok] additionalDirectories reprend collecte.racines
  [ok] une règle deny Write et Edit par racine
  [ok] aucune règle allow n'ouvre Write, Edit ni un Bash libre
  [ok] hooks SessionStart et Stop présents dans settings.json
  [ok] settings.json appelle .claude/hooks/session_start.py et stop.py
  [ok] les deux scripts de hook sont livrés dans .claude/hooks/
  [ok] session_start.py lance lint_sante.py --bref
  [ok] stop.py rappelle la clôture
  [ok] session_start.py --autotest sort en 0
  [ok] stop.py --autotest sort en 0
  [ok] les skills de agents.skills sont livrées, parle et bilan comprises
  [ok] les sous-agents sont en lecture seule (tools : Read, Grep, Glob)
  [ok] {{DOSSIERS_PROJETS}} est substitué en forme ~ (défaut n°7 v1)
  [ok] un fichier binaire sous le gabarit .claude/ ne casse pas --outillage-seul
  [ok] le lint embarqué est réactualisé malgré le fichier binaire
```

### C5 Régimes pointeur et copie, structurant périmé

```
C5. Régimes pointeur et copie (§2 ; lane E) : défaut plausible : une copie qui dérive de sa source sans que personne le voie
  [ok] lint 0 en régime pointeur
  [ok] scaffold en régime copie
  [ok] lint 0 en régime copie : le contrôle « 10 lignes » est suspendu sur Structurants/
  [ok] un structurant modifié à la source lève structurant_perime
```

### C6 Fédération sur trois exports fictifs

```
C6. Fédération sur trois exports fictifs (§6 ; lane F) : défaut plausible : un commun qui change à chaque génération ou qui publie une note privée
  [ok] federation.yaml est lisible par cortex_config.charger
  [ok] federe.py génère le commun et sort en 0
  [ok] deux générations ne diffèrent que sur genere_le
  [ok] Centre, README « généré, ne pas éditer » et empreinte .cortex-genere présents
  [ok] les projets portent le slug du rédacteur en préfixe
  [ok] un acteur présent chez trois rédacteurs donne une note unique avec source_vault multiple
  [ok] un domaine porté par trois rédacteurs est fusionné en une note
  [ok] chaque note du commun porte source_vault
  [ok] une note visibilite: prive dans un export est refusée et absente du commun
```

### C7 Manifestes plugin

```
C7. Manifestes plugin (§11) : défaut plausible : un plugin qui s'installe et n'expose aucune skill
  [ok] plugin.json : name cortex, version, description
  [ok] marketplace.json : le dépôt est sa propre marketplace (source ./, plugin cortex)
  [ok] un SKILL.md par dossier de skills/ (10), name = dossier, description présente
  [ok] la skill fabricant reste hors plugin (lien .claude/skills/fabricant, absente de skills/)
```

### C8 White-label

```
C8. White-label (01-cadrage §Marques interdites) : défaut plausible : une marque du fabricant héritée de la v1 livrée à un tiers
  [ok] aucune marque interdite dans skills/ notice/ outils/ README.md
```

### C9 Zéro chemin absolu

```
C9. Zéro chemin absolu (I2, §11) : défaut plausible : un chemin de la machine du fabricant qui rend le kit inopérant ailleurs
  — exclus : les lignes qui définissent le motif de détection (re.compile, chaîne brute r"…", commande grep) et les fragments cités entre backticks ; un motif montré n'est pas un chemin de machine.
  [ok] aucun chemin absolu (/Users/, /home/, lettre de lecteur) dans skills/ notice/ outils/ README.md
  [ok] les maillons se référencent par ${CLAUDE_SKILL_DIR}, jamais par ~/.claude/skills
```

### C10 Paquet, notice hors ligne, README

```
C10. Paquet, notice hors ligne, README (§11 ; lane B) : défaut plausible : un kit muet, une fuite de licence, une notice qui renvoie en ligne
OK — /tmp/claude-501/cortex-recette-brgkw_i3/cortex-temoin.zip : 10 dossiers (9 maillons + 1 annexes), LISEZ-MOI.html, PROVENANCE.md, version recette
  [ok] la fabrication sort en 0
  [ok] le zip compte les maillons présents par glob (9) plus le kit (1) et deux fichiers à la racine
  [ok] un SKILL.md à la bonne profondeur par dossier
  [ok] zéro SKILL.md en profondeur 2 dans le zip, le critère qui décide si le kit est vu ou muet
  [ok] chaque entrée du manifeste est dans le zip avec un frontmatter valide
  [ok] chaque emprunt du zip est couvert par PROVENANCE.md
  [ok] LISEZ-MOI.html du zip : 8 pastilles « À faire » (la 9e en tête), zéro URL distante
  [ok] notice/LISEZ-MOI.html présente, hors ligne (zéro URL)
  [ok] outils/OUTILS.md présent avec une ligne par outil du maillon 0
  [ok] README.md porte les trois gestes : install du plugin, la phrase d'entrée, la clôture
```

## Commandes d'acceptation de la ligne G

### Recette à 0

```
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?
```

Sortie du 2026-09-19 (`fix/final`) : `114 contrôle(s) passé(s), 0 en échec.` / `Recette verte.` ; `echo $?` → `0`. L'écart `outillage_seul` de la lane E est clos depuis le merge de `fix/E` ; aucun écart n'est ouvert.

### Fixtures déterministes

```
python3 skills/cortex-4-installation/recette/fixtures.py
```

```
employe     149 fichiers
dirigeant   374 fichiers
societe     104 fichiers
déterminisme vérifié
```

### Compilation de tous les scripts du dépôt

```
PYTHONPYCACHEPREFIX="$TMPDIR/pyc" python3 -m py_compile $(find . -name '*.py' -not -path './.git/*')
```

Sortie du 2026-09-19 : aucune, code 0, sur les 17 fichiers `.py` du dépôt (`fabricant/scripts/fabrique.py`, les scripts des neuf maillons, les deux hooks du gabarit, `export.py` du gabarit, `fixtures.py` et `parcours_blanc.py`).

`PYTHONPYCACHEPREFIX` n'est pas un ornement : sans lui, `py_compile` dépose un `__pycache__` dans `template/vault/.claude/hooks/` et `scaffold.py --outillage-seul` s'y cassait avant le correctif de `fix/E`. Détourner le bytecode hors du dépôt garde aussi l'arbre de travail propre.

### Grep white-label

La liste en clair vit chez le chef d'orchestre, hors dépôt ; la recette porte ses douze empreintes sha256 et cherche mot, bigramme et trigramme normalisés (minuscules, sans accent).

```
python3 -c "import sys; sys.path.insert(0,'skills/cortex-4-installation/recette'); import parcours_blanc as pb; pb.c8_white_label()"
```

```
[ok] aucune marque interdite dans skills/ notice/ outils/ README.md
```

Zéro ligne.

### Grep chemins absolus

```
grep -rnE '/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|\b[A-Z]:\\[A-Za-z]' skills/ notice/ outils/ README.md
```

Sortie du 2026-09-19 : zéro ligne, sans aucune exclusion. La recette applique en plus une exclusion de sûreté (lignes qui définissent le motif de détection, fragments entre backticks) pour que le contrôle ne se morde pas la queue sur `parcours_blanc.py`, `lint_sante.py` et `cortex-7-passation/SKILL.md` si l'un d'eux reformule son motif ; aujourd'hui elle n'écarte rien.

Audit à froid signé : (ligne à remplir par le chef d'orchestre, date et verdict)

## Contrôles manuels

Chaque contrôle porte sa commande, ce qui est attendu, et une ligne « Sortie » vide que le chef d'orchestre remplit avec la sortie collée. Tant qu'une ligne « Sortie » est vide, le contrôle n'est pas fait : il n'est ni vert ni rouge, il est en attente.

### M1 Installation vivante du plugin

Sur le poste du fabricant, depuis la marketplace locale puis, après la Phase I, depuis GitHub :

```
claude plugin marketplace add ~/Dev/cortex
claude plugin install cortex@cortex-kit
claude plugin details cortex@cortex-kit
```

Attendu : installation sans erreur ; `details` liste autant de skills que de dossiers dans `skills/` (9 maillons + 1 annexe = 10, compte par glob, jamais 13) ; dans une session neuve, la phrase « installe mon second cerveau » déclenche `cortex-0-poste`.

Sortie : 2026-09-19, ce Mac (macOS, Claude Code 2.1.263). `claude plugin marketplace add ~/Dev/cortex` → « Successfully added marketplace: cortex-kit » ; `claude plugin install cortex@cortex-kit` → « Successfully installed plugin: cortex@cortex-kit (scope: user) » ; après bump de version, `claude plugin marketplace update cortex-kit && claude plugin update cortex@cortex-kit` → « Plugin "cortex" updated from 2.0.0-dev to 2.0.0-rc.1 » ; `claude plugin details cortex@cortex-kit` → Skills (10) : cortex-0-poste … cortex-8-federation, stop-slop ; Agents 0, Hooks 0, MCP 0. Le cache `~/.claude/plugins/cache/cortex-kit/cortex/2.0.0-rc.1/skills/cortex-0-poste/scripts/poste.py` existe et la description porte « installe mon second cerveau ». Leçon : sans changement de `version` dans `plugin.json`, `plugin update` répond « already at the latest version » et ne rafraîchit pas le cache.


### M2 Sonde Cowork bureau

Sonde web du 2026-09-19 (chef d'orchestre) : Cowork sur claude.ai tourne dans un conteneur distant sans accès au disque ; le vault vit sur le poste, seule l'application Cowork bureau peut le servir. À rejouer dans l'application bureau :

```
uvx --from "markitdown[all]" markitdown --version
python3 --version
ls ~/Cortex
```

Attendu : les trois commandes répondent depuis le poste (version de markitdown, Python 3.12, le dossier des vaults visible). Si `uvx` manque, noter la commande d'installation proposée par le maillon 0.

Sortie :


### M3 Maillon 0 et installation du plugin sur la machine Windows

Sur la machine Windows du fabricant (nom à fixer par le chef d'orchestre), dans un terminal :

```
claude plugin marketplace add cortex-kit/cortex
claude plugin install cortex@cortex-kit
py skills\cortex-0-poste\scripts\poste.py --dry-run
```

puis, dans Claude Code : « installe mon second cerveau », jusqu'à l'ouverture de la notice.

Attendu : `--dry-run` imprime une ligne par outil absent avec la commande Windows (winget) ; après le maillon 0, `_cortex/poste.json` porte `os: windows` et `notice_ouverte_le` ; `notice.html` s'ouvre dans le navigateur ; aucun chemin `C:\Users\<nom>` dans `config.yaml` (forme `~`).

Sortie :


### M4 Permissions du vault, en session interactive

Les règles `allow` et `additionalDirectories` d'un `settings.json` de vault sont **ignorées par `claude -p`** tant que le dossier n'a pas été ouvert une fois en interactif : la session non interactive répond « workspace has not been trusted » et n'applique que les règles `deny`. Un contrôle scripté ne peut donc pas prouver que les permissions du vault fonctionnent : il prouverait seulement que `deny` tient, ce que la recette vérifie déjà sur le fichier (C4).

La preuve vivante se fait en session interactive, une fois le vault ouvert et la confiance accordée. Dans le vault livré :

```
cd <vault>
claude
```

puis, dans la session :

1. `git status`, attendu : passe sans demande de permission (`allow` porte `Bash(git status:*)`).
2. Lire une note de `~/Documents`, attendu : passe (`additionalDirectories`).
3. Écrire dans `~/Documents/<un fichier>`, attendu : refusé par la règle `deny Write(~/Documents/**)`, sans possibilité d'accorder.
4. `python3 .claude/skills/lint/lint_sante.py --vault .`, attendu : passe sans demande.

Attendu : les quatre gestes se comportent comme ci-dessus, et la session n'affiche pas « workspace has not been trusted ».

Sortie : 2026-09-19, deux sessions interactives (Sonnet, mode normal, dossier approuvé) dans un vault scaffoldé `~/Cortex-test-m4`. Run 1, racine `$TMPDIR/m4-racine` (sous `/var/folders`, lien symbolique vers `/private/var`) : `ls` sans prompt, **Write accepté** (« File created successfully »), la règle `deny` écrite sous la forme donnée ne matche pas le chemin réel. Run 2, racine `~/Cortex-test-m4-racine` : `ls` sans prompt (« 1 fichier »), **Write refusé** : « File is in a directory that is denied by your permission settings », aucun fichier créé. Le hook Stop a rendu « 1 fichier(s) modifié(s) sans clôture » dans les deux runs : c'était `.claude/skills/lint/__pycache__/` laissé par le hook SessionStart. Correctifs du chef d'orchestre : `scaffold.py` écrit aussi la forme réelle d'une racine symbolique dans `deny` et `additionalDirectories` ; le gabarit livre un `.gitignore` (`__pycache__/`, `*.pyc`, `.DS_Store`, `:memory:.ses`).
