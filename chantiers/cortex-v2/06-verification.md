# 06 : Vérification (lane G)

Recette v2 écrite le 2026-09-19, préparatoire : rouge jusqu'au merge des lanes B à F, c'est la cible. Chaque critère ci-dessous est un groupe de contrôles de `parcours_blanc.py` ; la commande est la même pour tous, la sortie collée est celle du jour, sur `lane/G` avant tout merge. À rejouer après chaque merge, puis en Phase I sur le tag.

## Commande unique

```
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?
```

Sortie du 2026-09-19 (lane/G, avant merge) : sections v1 23 ok / 0 en échec ; tableau :

```
Tableau C1 à C10 (contrôles passés / total)
  C1   Neuf étapes, maillon 0, notice                     §3 §5 §10    lane B        6/16 ROUGE
  C2   Trois profils, régime, section Notice              §2 §10       lane C        5/11 ROUGE
  C3   Inventaire outillé sur les fixtures                §4           lane D        0/1  ROUGE
  C4   Couche vault : permissions, hooks, skills, agents  §9           lane E        3/9  ROUGE
  C5   Régimes pointeur et copie, structurant périmé      §2           lane E        2/4  ROUGE
  C6   Fédération sur trois exports fictifs               §6           lane F        0/1  ROUGE
  C7   Manifestes plugin                                  §11          lane chef     4/4  VERT
  C8   White-label                                        01-cadrage   lane toutes   0/1  ROUGE
  C9   Zéro chemin absolu                                 I2, §11      lane toutes   1/2  ROUGE
  C10  Paquet, notice hors ligne, README                  §11          lane B        7/10 ROUGE
  M1   Installation vivante du plugin (marketplace add, install, details) manuel, sortie collée dans 06-verification.md
  M2   Sonde Cowork bureau : uvx markitdown --version dans le bac à sable manuel, sortie collée dans 06-verification.md
  M3   Maillon 0 et installation du plugin sur la machine Windows manuel, sortie collée dans 06-verification.md

51 contrôle(s) passé(s), 31 en échec.
EN ÉCHEC : C1 etat.py porte neuf étapes numérotées 0 à 8, C1 les artefacts des neuf étapes sont ceux du contrat §5, C1 le pivot porte les neuf étapes, C1 le maillon 0 est lu depuis poste.json : fait quand notice_ouverte_le est renseigné, C1 l'étape 8 vaut arbitre avec la raison « vault solo » en mode solo, C1 le pivot porte profil, regime, phrase_suivante et notice_ouverte_le, C1 la phrase suivante est en langage ordinaire, jamais un nom de maillon, C1 le compteur annonce 9/9 quand les neuf lignes sont faites, C1 le tableau de bord vierge affiche neuf lignes à faire, C1 poste.py présent, C2 cortex-1-cadrage/references/profils/employe.md existe, C2 cortex-1-cadrage/references/profils/dirigeant.md existe, C2 cortex-1-cadrage/references/profils/societe.md existe, C2 profil: autre est refusé et le message nomme la clé, C2 regime: mixte est refusé et le message nomme la clé, C2 neuf SKILL.md maillons, chacun avec la section Notice et l'appel de notice.py (I10), C3 scan.py présent, C4 additionalDirectories reprend collecte.racines, C4 une règle deny Write et Edit par racine, C4 hooks SessionStart et Stop présents dans settings.json, C4 SessionStart lance le lint bref, Stop rappelle la clôture, C4 les skills de agents.skills sont livrées, parle et bilan comprises, C4 les sous-agents sont en lecture seule (tools : Read, Grep, Glob), C5 lint 0 en régime copie : le contrôle « 10 lignes » est suspendu sur Structurants/, C5 un structurant modifié à la source lève structurant_perime, C6 federe.py présent, C8 aucune marque interdite dans skills/ notice/ outils/ README.md, C9 aucun chemin absolu (/Users/, /home/, lettre de lecteur) dans skills/ notice/ outils/ README.md, C10 LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante, C10 notice/LISEZ-MOI.html présente, hors ligne (zéro URL), C10 outils/OUTILS.md présent avec une ligne par outil du maillon 0
```

## Tableau C1 à C10

| Critère | Contrat | Lane | Ce qui est vérifié | 2026-09-19 |
|---|---|---|---|---|
| C1 Neuf étapes, maillon 0, notice | §3 §5 §10 | B | `etat.py` à neuf étapes 0 à 8 avec les artefacts du contrat ; maillon 0 lu depuis `poste.json` (fait si `notice_ouverte_le`) ; étape 8 `arbitre` « vault solo » ; pivot avec `profil`, `regime`, `phrase_suivante`, `notice_ouverte_le` ; 9/9 ; notice vierge à neuf lignes, zéro URL ; `notice.py --no-open` ; `poste.py --dry-run` une ligne par outil absent | 6/16 rouge |
| C2 Trois profils, régime, section Notice | §2 §10 | C | `fixtures.py` en moins de 10 s ; `references/profils/{employe,dirigeant,societe}.md` ; trois configs de profil installables ; `profil: autre` et `regime: mixte` refusés avec la clé nommée ; neuf SKILL.md maillons avec la section Notice ; moins de 300 lignes | 5/11 rouge |
| C3 Inventaire outillé sur les fixtures | §4 | D | `scan.py` sur employé, dirigeant, société (camille) : sortie 0 en moins de 60 s ; format `cortex/inventaire` v2 ; `bornes` en entiers ; aucun champ `contenu` ; chemins en forme `~` ; `export-notion-*.csv` signalé comme base déportée sur employé | 0/1 rouge |
| C4 Couche vault : permissions, hooks, skills, agents | §9 | E | `settings.json` : `additionalDirectories` = `collecte.racines`, `deny` Write et Edit par racine, aucun allow ouvert ; hooks SessionStart (lint `--bref`) et Stop (clôture) ; skills `parle` et `bilan` ; sous-agents `tools: Read, Grep, Glob` ; `{{DOSSIERS_PROJETS}}` en forme `~` | 3/9 rouge |
| C5 Régimes pointeur et copie, structurant périmé | §2 | E | lint 0 en pointeur ; en copie, note `50 - Ressources/Structurants/<type>/` avec `source_path`, `hash`, `copie_le` : contrôle « 10 lignes » suspendu, lint 0 ; source modifiée, `structurant_perime` levé | 2/4 rouge |
| C6 Fédération sur trois exports fictifs | §6 | F | trois `_export/<slug>/` construits selon §6 depuis les noms de `fixtures.societe` ; `federation.yaml` lisible ; `federe.py` sort 0 ; deux générations identiques hors `genere_le` ; Centre, README « ne pas éditer », `.cortex-genere` ; projets préfixés du slug ; acteur commun fusionné `source_vault` multiple ; domaine fusionné ; `visibilite: prive` refusée et absente | 0/1 rouge |
| C7 Manifestes plugin | §11 | chef | `plugin.json` (name cortex, version, description) ; `marketplace.json` (name cortex-kit, un plugin, `source: ./`) ; un SKILL.md par dossier de `skills/` avec `name` = dossier et `description` ; `fabricant` hors plugin | 4/4 vert |
| C8 White-label | 01-cadrage | toutes | aucune marque interdite dans `skills/` (annexes comprises), `notice/`, `outils/`, `README.md` ; liste portée en empreintes sha256 (le dépôt est public) ; détection par mot, bigramme et trigramme normalisés | 0/1 rouge |
| C9 Zéro chemin absolu | I2, §11 | toutes | aucun `/Users/<nom>/`, `/home/<nom>/`, `X:\` dans le même périmètre ; les maillons se référencent par `${CLAUDE_SKILL_DIR}` | 1/2 rouge |
| C10 Paquet, notice hors ligne, README | §11 | B | `fabrique.py` sort 0 ; le zip compte les maillons présents par glob plus le kit, deux fichiers à la racine ; un SKILL.md par dossier à la bonne profondeur ; PROVENANCE couvre le kit ; `LISEZ-MOI.html` du zip à neuf étapes, zéro URL ; `notice/LISEZ-MOI.html` et `outils/OUTILS.md` présents ; README avec les trois gestes | 7/10 rouge |

## Sortie par critère (2026-09-19)

### C1 Neuf étapes, maillon 0, notice

```
Neuf étapes, maillon 0, notice (§3 §5 §10 ; lane B) : défaut plausible : un tableau de bord qui compte sept quand la chaîne en a neuf
  [XX] etat.py porte neuf étapes numérotées 0 à 8 : [1, 2, 3, 4, 5, 6, 7]
  [XX] les artefacts des neuf étapes sont ceux du contrat §5
  [XX] le pivot porte les neuf étapes : 7
  [ok] le pivot se régénère à l'identique hors horodatage
  [XX] le maillon 0 est lu depuis poste.json : fait quand notice_ouverte_le est renseigné : {}
  [ok] un poste.json sans notice_ouverte_le ne compte pas comme fait
  [XX] l'étape 8 vaut arbitre avec la raison « vault solo » en mode solo : {}
  [XX] le pivot porte profil, regime, phrase_suivante et notice_ouverte_le : {'profil': None, 'regime': None, 'phrase_suivante': None, 'notice_ouverte_le': None}
  [XX] la phrase suivante est en langage ordinaire, jamais un nom de maillon
  [ok] le trou en 03 est porté avec sa raison en clair
  [ok] l'étape 4 se déduit d'un artefact aval, jamais devinée
  [XX] le compteur annonce 9/9 quand les neuf lignes sont faites : ['faite', 'faite', 'faite', 'faite_deduite', 'faite', 'faite', 'faite']
  [XX] le tableau de bord vierge affiche neuf lignes à faire : 7
  [ok] aucune URL distante dans la notice
  [ok] notice.py --no-open régénère etat.json et notice.html et sort en 0
  [XX] poste.py présent : attendu au merge de la lane B
```

### C2 Trois profils, régime, section Notice

```
Trois profils, régime, section Notice (§2 §10 ; lane C) : défaut plausible : un profil inconnu accepté, un régime hybride inventé
  [ok] fixtures.py génère trois arbres en moins de 10 s
  [XX] cortex-1-cadrage/references/profils/employe.md existe
  [XX] cortex-1-cadrage/references/profils/dirigeant.md existe
  [XX] cortex-1-cadrage/references/profils/societe.md existe
  [ok] la config employe (régime copie) est installable
  [ok] la config dirigeant (régime pointeur) est installable
  [ok] la config societe (régime pointeur) est installable
  [XX] profil: autre est refusé et le message nomme la clé : []
  [XX] regime: mixte est refusé et le message nomme la clé : []
  [XX] neuf SKILL.md maillons, chacun avec la section Notice et l'appel de notice.py (I10) : 7 maillons, sans notice : []
  [ok] chaque SKILL.md maillon fait moins de 300 lignes
```

### C3 Inventaire outillé sur les fixtures

```
Inventaire outillé sur les fixtures (§4 ; lane D) : défaut plausible : un inventaire qui copie du contenu ou ment sur ses bornes
  [XX] scan.py présent : attendu au merge de la lane D
```

### C4 Couche vault : permissions, hooks, skills, agents

```
Couche vault (§9 ; lane E) : défaut plausible : un agent qui peut écrire dans les dossiers de travail
  [ok] scaffold accepte une config v2 complète
  [XX] additionalDirectories reprend collecte.racines : None
  [XX] une règle deny Write et Edit par racine : []
  [ok] aucune règle allow n'ouvre Write, Edit ni un Bash libre
  [XX] hooks SessionStart et Stop présents dans settings.json : []
  [XX] SessionStart lance le lint bref, Stop rappelle la clôture
  [XX] les skills de agents.skills sont livrées, parle et bilan comprises : ['cloture', 'ingest', 'lint', 'nouveau-projet']
  [XX] les sous-agents sont en lecture seule (tools : Read, Grep, Glob) : {'auditeur-ontologie.md': 'Read, Grep, Glob, Bash', 'chercheur-vault.md': 'Read, Grep, Glob'}
  [ok] {{DOSSIERS_PROJETS}} est substitué en forme ~ (défaut n°7 v1)
```

### C5 Régimes pointeur et copie, structurant périmé

```
Régimes pointeur et copie (§2 ; lane E) : défaut plausible : une copie qui dérive de sa source sans que personne le voie
  [ok] lint 0 en régime pointeur
  [ok] scaffold en régime copie
  [XX] lint 0 en régime copie : le contrôle « 10 lignes » est suspendu sur Structurants/ : 
== Lint Ateliers Roumier == (16/42 notes auditees, 26 ignorees)

[!] 1 fiche(s) avec une entree de journal trop longue :
    - {"file": "50 - Ressources/Structurants/organigramme/Organigramme.md", "entree_max": 16, "seuil": 10}

[X] Au moins un controle DUR en echec. Code retour 1.

  [XX] un structurant modifié à la source lève structurant_perime : ['orphelins', 'pointeur_canonique_absent', 'tags_anti_pattern', 'tags_hors_domaines', 'phase_hors_enum', 'progression_absente', 'journal_entree_obese', 'moustaches_residuelles', 'chemins_absolus', 'commun_edite_main', 'journal_total_long', 'dernier_journal_perime', 'agents_perimes', 'notes_sans_frontmatter', 'contrat_config_invalide', 'liens_casses', 'stats']
```

### C6 Fédération sur trois exports fictifs

```
Fédération sur trois exports fictifs (§6 ; lane F) : défaut plausible : un commun qui change à chaque génération ou qui publie une note privée
  [XX] federe.py présent : attendu au merge de la lane F
```

### C7 Manifestes plugin

```
Manifestes plugin (§11) : défaut plausible : un plugin qui s'installe et n'expose aucune skill
  [ok] plugin.json : name cortex, version, description
  [ok] marketplace.json : le dépôt est sa propre marketplace (source ./, plugin cortex)
  [ok] un SKILL.md par dossier de skills/ (8), name = dossier, description présente
  [ok] la skill fabricant reste hors plugin (lien .claude/skills/fabricant, absente de skills/)
```

### C8 White-label

```
White-label (01-cadrage §Marques interdites) : défaut plausible : une marque du fabricant héritée de la v1 livrée à un tiers
  [XX] aucune marque interdite dans skills/ notice/ outils/ README.md : 1 ligne(s) : ['skills/stop-slop/SKILL.md:8']
```

### C9 Zéro chemin absolu

```
Zéro chemin absolu (I2, §11) : défaut plausible : un chemin de la machine du fabricant qui rend le kit inopérant ailleurs
  [XX] aucun chemin absolu (/Users/, /home/, lettre de lecteur) dans skills/ notice/ outils/ README.md : 2 ligne(s) : ['skills/cortex-4-installation/scripts/notice.md:51', 'skills/cortex-4-installation/scripts/notice.md:53']
  [ok] les maillons se référencent par ${CLAUDE_SKILL_DIR}, jamais par ~/.claude/skills
```

### C10 Paquet, notice hors ligne, README

```
Paquet, notice hors ligne, README (§11 ; lane B) : défaut plausible : un kit muet, une fuite de licence, une notice qui renvoie en ligne
OK — /tmp/claude-501/cortex-recette-obm57ntv/cortex-temoin.zip : 8 dossiers (7 maillons + 1 annexes), LISEZ-MOI.html, PROVENANCE.md, version recette
  [ok] la fabrication sort en 0
  [ok] le zip compte les maillons présents par glob (7) plus le kit (1) et deux fichiers à la racine
  [ok] un SKILL.md à la bonne profondeur par dossier
  [ok] zéro SKILL.md en profondeur 2 dans le zip, le critère qui décide si le kit est vu ou muet
  [ok] chaque entrée du manifeste est dans le zip avec un frontmatter valide
  [ok] chaque emprunt du zip est couvert par PROVENANCE.md
  [XX] LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante : 7
  [XX] notice/LISEZ-MOI.html présente, hors ligne (zéro URL)
  [XX] outils/OUTILS.md présent avec une ligne par outil du maillon 0
  [ok] README.md porte les trois gestes : install du plugin, la phrase d'entrée, la clôture
```

## Commandes d'acceptation de la ligne G

Recette à 0 après merge :

```
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?
```

Sortie du 2026-09-19 : `1` (attendu avant merge, voir le tableau).

Grep white-label (la liste en clair vit chez le chef d'orchestre, hors dépôt ; la recette porte ses empreintes) :

```
grep -rwiE "<liste 01-cadrage>" skills/ notice/ outils/ README.md
```

Sortie du 2026-09-19, réduite à fichier:ligne : `skills/stop-slop/SKILL.md:8` (prénom du fabricant dans une phrase de déclenchement, hérité de la v1 ; `notice/` et `outils/` n'existent pas encore).

Grep chemins absolus :

```
grep -rnE '/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|\b[A-Z]:\\[A-Za-z]' skills notice outils README.md | grep -v recette/fixtures/
```

Sortie du 2026-09-19 :

```
skills/cortex-4-installation/scripts/notice.md:51:   `C:\Users\VOTRE_NOM\.claude\skills\`
skills/cortex-4-installation/scripts/notice.md:53:   `C:\Users\VOTRE_NOM\.claude\` et créez-y un dossier nommé `skills`.
```

Audit à froid signé : (ligne à remplir par le chef d'orchestre, date et verdict)

## Contrôles manuels

Chaque contrôle porte sa commande, ce qui est attendu, et une ligne « Sortie » vide que le chef d'orchestre remplit avec la sortie collée.

### M1 Installation vivante du plugin

Sur le poste du fabricant, depuis la marketplace locale puis, après la Phase I, depuis GitHub :

```
claude plugin marketplace add ~/Dev/cortex
claude plugin install cortex@cortex-kit
claude plugin details cortex@cortex-kit
```

Attendu : installation sans erreur ; `details` liste autant de skills que de dossiers dans `skills/` (9 maillons + 1 annexe après merge, compte par glob, jamais 13) ; dans une session neuve, la phrase « installe mon second cerveau » déclenche `cortex-0-poste`.

Sortie :


### M2 Sonde Cowork bureau

Sonde web du 2026-09-19 (chef d'orchestre) : Cowork sur claude.ai tourne dans un conteneur distant sans accès au disque ; le vault vit sur le poste, seule l'application Cowork bureau peut le servir. À rejouer dans l'application bureau :

```
uvx markitdown --version
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


## Écarts constatés hors lane G (à porter par la lane propriétaire ou le chef d'orchestre)

| Fichier | Lane | Constat | Valeur attendue |
|---|---|---|---|
| `fabricant/scripts/rend_deck.py`, `fabricant/modeles/bento-runtime.html` | B | Le deck dépend de la skill `presentation`, retirée du kit le 2026-09-19 ; `import rend_deck` faisait sortir la recette v1 en 1 avant tout contrôle | Décision 2026-09-19 : retiré par la lane B ; le contrôle deck est retiré de la recette |
| `skills/stop-slop/SKILL.md:8` | chef (annexe) | Prénom du fabricant dans la phrase de déclenchement | Terme générique (« l'utilisateur ») |
| `skills/cortex-4-installation/scripts/notice.md:51,53` | B | `C:\Users\VOTRE_NOM\...` : lettre de lecteur, C9 rouge | `%USERPROFILE%\.claude\skills\`, ou décision d'exempter les segments en majuscules |
| `skills/cortex-4-installation/template/vault/.claude/agents/auditeur-ontologie.md` | E | `tools: Read, Grep, Glob, Bash` | `tools: Read, Grep, Glob` (§9) |
| `skills/cortex-4-installation/scripts/etat.py:163` | B | `main()` imprime `/7` en dur | `/{len(pivot['etapes'])}` |
| `fabricant/SKILL.md:72-77`, `PROVENANCE.md` | B | Marques du fabricant en clair (hors périmètre du grep, mais dépôt public) | Termes génériques dans `fabricant/SKILL.md` ; `PROVENANCE.md` garde les attributions exigées par les licences |
