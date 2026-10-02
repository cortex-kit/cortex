# Rapport de la lane B : Phase H2, conduite

Branche `lane/h2b`, partie de `fix/phase-h` (`158d6c0`). Dix commits « Lane H2B », aucun push, aucun merge, aucun rebase. Aucun `.py` touché.

## Tâches et commits

| Tâche | Objet | Commit |
|---|---|---|
| B1 | doctrine §8 mots, §9 lecture, §10 validation visible, §11 accord, réponse acquise, marque, atelier existant | `69b87fe` |
| B2 | une ligne de renvoi à la doctrine §8 à §11, en tête des Interdits des neuf maillons | `0b9562d` |
| B3 | maillon 0 : nom court toujours demandé, question softeria et mcp-email, `--voie`, `--options`, « à vérifier » | `96bbf21`, `bc51816` |
| B4 | maillon 1 et profils : mots, racines demandées, marque sans client, groupe repris, bloc affiché, `--inscrire` | `b4b331e` |
| B5 | maillons 2 à 7 : phrases fautives, messages de clôture, validations affichées | `4c9d8fd`, `bc51816` |
| B6 | maillon 7 : limite Windows natif dans le guide de remise | `2885e04` |
| B7 | maillon 8 : lancement depuis l'atelier, groupe entier remis, contrôle 3 | `836ad9b` |
| B8 | `README.md`, `outils/OUTILS.md` : limite Windows, WSL2 | `b515da2` |
| B8bis | six skills du vault : ligne des mots et de la validation visible ; `cloture` sans « accepter » | `fd5d932` |
| B9 | recette et greps de `06-verification.md`, lane B | ce rapport |
| B10 | ce rapport | voir `05-execution.md` |

## Fichiers touchés

```
 README.md                                          |  2 +
 outils/OUTILS.md                                   |  2 +-
 skills/cortex-0-poste/SKILL.md                     | 28 ++++++-----
 skills/cortex-1-cadrage/SKILL.md                   | 54 ++++++++++++++--------
 skills/cortex-1-cadrage/references/doctrine.md     | 42 +++++++++++++++++
 .../references/profils/dirigeant.md                | 11 ++---
 .../cortex-1-cadrage/references/profils/employe.md | 13 +++---
 .../cortex-1-cadrage/references/profils/societe.md | 13 +++---
 skills/cortex-2-inventaire/SKILL.md                |  9 ++--
 skills/cortex-3-ontologie/SKILL.md                 | 14 +++---
 skills/cortex-4-installation/SKILL.md              | 13 ++++--
 .../template/vault/.claude/skills/bilan/SKILL.md   |  2 +
 .../template/vault/.claude/skills/cloture/SKILL.md |  4 +-
 .../template/vault/.claude/skills/ingest/SKILL.md  |  2 +
 .../template/vault/.claude/skills/lint/SKILL.md    |  4 +-
 .../vault/.claude/skills/nouveau-projet/SKILL.md   |  2 +
 .../template/vault/.claude/skills/parle/SKILL.md   |  2 +
 skills/cortex-5-ingest/SKILL.md                    | 14 +++---
 skills/cortex-6-agents-metier/SKILL.md             |  5 +-
 skills/cortex-7-passation/SKILL.md                 |  5 +-
 skills/cortex-8-federation/SKILL.md                | 33 ++++++++-----
 21 files changed, 187 insertions(+), 87 deletions(-)
```

## Recette complète

`python3 skills/cortex-4-installation/recette/parcours_blanc.py` sur `bc51816` : sortie 0, 117 contrôles passés, 0 en échec, C1 à C10 verts (C2 tient les tailles sous 300 lignes, la section Notice et I10 ; C8 zéro marque ; C9 zéro chemin absolu ; C10 README et `OUTILS.md`). Même chiffre que sur `fix/phase-h` avant la lane : la lane B n'ajoute aucun contrôle de recette, ses preuves sont les greps ci-dessous.

```
  C2   Trois profils, régime, section Notice              §2 §10       lane C       12/12 VERT
  C3   Inventaire outillé sur les fixtures                §4           lane D       16/16 VERT
  C4   Couche vault : permissions, hooks, skills, agents  §9           lane E       18/18 VERT
  C5   Régimes pointeur et copie, structurant périmé      §2           lane E        4/4  VERT
  C6   Fédération sur trois exports fictifs               §6           lane F       10/10 VERT
  C7   Manifestes plugin                                  §11          lane chef     4/4  VERT
  C8   White-label                                        01-cadrage   lane toutes   1/1  VERT
  C9   Zéro chemin absolu                                 I2, §11      lane toutes   2/2  VERT
  C10  Paquet, notice hors ligne, README                  §11          lane B       10/10 VERT
  M1   Installation vivante du plugin (marketplace add, install, details) manuel, sortie collée dans 06-verification.md
  M2   Sonde Cowork bureau : uvx --from "markitdown[all]" markitdown --version dans le bac à sable manuel, sortie collée dans 06-verification.md
  M3   Maillon 0 et installation du plugin sur la machine Windows manuel, sortie collée dans 06-verification.md
  M4   Permissions du vault en session interactive (allow, additionalDirectories, deny) manuel, sortie collée dans 06-verification.md

117 contrôle(s) passé(s), 0 en échec.
Recette verte.
```

`rejeu_profil.py --autotest` sort en 0 avec les blocs de profil passés à `racines: []` : « OK : rejeu des trois profils, cadrage en brouillon, domaines hors config.yaml, écarts en [?], régime pointeur sur base déportée ».

## Commandes de `06-verification.md`, lane B, avec témoins

Chaque critère qui attend zéro porte sa sonde rejouée sur `fix/phase-h`, qui rend non-zéro.

```
### 1. Doctrine
$ grep -n "^## " skills/cortex-1-cadrage/references/doctrine.md
7:## 1. Ce qu'on installe
15:## 2. Le vocabulaire
31:## 3. La chaîne, et pourquoi elle est coupée là
57:## 4. La garde formelle
75:## 5. Les cinq invariants
91:## 6. Ce qui ne se négocie pas avec le client
105:## 7. Le geste qui décide de tout
113:## 8. Les mots qui ne se disent pas
129:## 9. Ce que la chaîne lit
139:## 10. Ce qui se valide se voit
145:## 11. Accord, réponse acquise, marque, atelier existant
(sortie 0)
# témoin, fix/phase-h :
$ git show fix/phase-h:skills/cortex-1-cadrage/references/doctrine.md | grep -n "^## "
7:## 1. Ce qu'on installe
15:## 2. Le vocabulaire
31:## 3. La chaîne, et pourquoi elle est coupée là
57:## 4. La garde formelle
75:## 5. Les cinq invariants
91:## 6. Ce qui ne se négocie pas avec le client
105:## 7. Le geste qui décide de tout
(sortie 0)

### 2. Renvois des neuf maillons
$ grep -L "doctrine.md\` §8 à §11" skills/cortex-[0-8]-*/SKILL.md
(sortie 0)
# témoin, fix/phase-h :
$ git grep -L "doctrine.md\` §8 à §11" fix/phase-h -- ":(glob)skills/cortex-[0-8]-*/SKILL.md"
fix/phase-h:skills/cortex-0-poste/SKILL.md
fix/phase-h:skills/cortex-1-cadrage/SKILL.md
fix/phase-h:skills/cortex-2-inventaire/SKILL.md
fix/phase-h:skills/cortex-3-ontologie/SKILL.md
fix/phase-h:skills/cortex-4-installation/SKILL.md
fix/phase-h:skills/cortex-5-ingest/SKILL.md
fix/phase-h:skills/cortex-6-agents-metier/SKILL.md
fix/phase-h:skills/cortex-7-passation/SKILL.md
fix/phase-h:skills/cortex-8-federation/SKILL.md
(sortie 0)

### 3. Skills du vault
$ grep -L "Devant la personne" skills/cortex-4-installation/template/vault/.claude/skills/*/SKILL.md
(sortie 0)
# témoin, fix/phase-h :
$ git grep -L "Devant la personne" fix/phase-h -- ":(glob)skills/cortex-4-installation/template/vault/.claude/skills/*/SKILL.md"
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/bilan/SKILL.md
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/cloture/SKILL.md
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/ingest/SKILL.md
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/lint/SKILL.md
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/nouveau-projet/SKILL.md
fix/phase-h:skills/cortex-4-installation/template/vault/.claude/skills/parle/SKILL.md
(sortie 0)

### 4. Maillon 0
$ grep -n -o "les ateliers existants comme options[^.]*\|--voie softeria\|--voie aucune\|un petit serveur local[^.]*\|exactement cette liste\|à vérifier (<raison>)" skills/cortex-0-poste/SKILL.md
34:les ateliers existants comme options, à côté de « un nouveau nom »
44:à vérifier (<raison>)
74:exactement cette liste
93:un petit serveur local et l'outil node, qui donnent accès à la boîte sans passer par l'administrateur du compte
93:--voie softeria
93:--voie aucune
130:--voie softeria
130:--voie aucune
(sortie 0)
$ grep -n -i "zshrc\|PATH\|modifier un script\|corriger un script" skills/cortex-0-poste/SKILL.md | cut -c1-200
44:Une ligne par outil du kit absent, avec la commande de l'OS courant : `<outil> : absent → <commande>`. Une ligne `<outil> : à vérifier (<raison>)` dit que la sonde n'a pas pu mesurer, sans prouver 
131:- **Ne jamais dire « absent » d'un outil « à vérifier »**, ni proposer de modifier un script, le `PATH` ou la configuration du shell.
(sortie 0)

### 5. Maillon 1 et profils : racines, marque, inscription
$ grep -n "~/Documents\|~/Desktop" skills/cortex-1-cadrage/SKILL.md skills/cortex-1-cadrage/references/profils/*.md | cut -c1-200
skills/cortex-1-cadrage/SKILL.md:87:**Les racines se demandent, elles ne se proposent pas depuis le disque** (`references/doctrine.md` §9). La question : « où sont vos dossiers de travail sur cet ordi
skills/cortex-1-cadrage/SKILL.md:229:- **Ne jamais proposer une racine trouvée sur le disque**, ni `~/Documents` ou `~/Desktop` par défaut. Les racines se demandent.
skills/cortex-1-cadrage/references/profils/dirigeant.md:34:À demander, jamais à proposer depuis un parcours du disque (`../doctrine.md` §9). La question : « où sont vos dossiers de travail sur cet ord
skills/cortex-1-cadrage/references/profils/employe.md:33:À demander, jamais à proposer depuis un parcours du disque (`../doctrine.md` §9). La question : « où sont vos dossiers de travail sur cet ordin
skills/cortex-1-cadrage/references/profils/societe.md:43:À demander, jamais à proposer depuis un parcours du disque (`../doctrine.md` §9). La question : « où sont vos dossiers de travail sur cet ordin
(sortie 0)
# témoin, fix/phase-h :
$ git grep -n "~/Documents\|~/Desktop" fix/phase-h -- skills/cortex-1-cadrage/SKILL.md "skills/cortex-1-cadrage/references/profils/*.md" | cut -c1-160
fix/phase-h:skills/cortex-1-cadrage/references/profils/dirigeant.md:36:- `~/Documents`
fix/phase-h:skills/cortex-1-cadrage/references/profils/dirigeant.md:93:  racines: ["~/Documents"]
fix/phase-h:skills/cortex-1-cadrage/references/profils/employe.md:26:- Un espace de fichiers personnel ou d'équipe : `~/Documents`, un lecteur réseau, un dossie
fix/phase-h:skills/cortex-1-cadrage/references/profils/employe.md:35:- `~/Documents`
fix/phase-h:skills/cortex-1-cadrage/references/profils/employe.md:36:- `~/Desktop`
fix/phase-h:skills/cortex-1-cadrage/references/profils/employe.md:91:  racines: ["~/Documents", "~/Desktop"]
fix/phase-h:skills/cortex-1-cadrage/references/profils/societe.md:43:- `~/Documents`
fix/phase-h:skills/cortex-1-cadrage/references/profils/societe.md:87:  racines: ["~/Documents"]
(sortie 0)
$ grep -n "racines:" skills/cortex-1-cadrage/references/profils/*.md
skills/cortex-1-cadrage/references/profils/dirigeant.md:92:  racines: []
skills/cortex-1-cadrage/references/profils/employe.md:90:  racines: []
skills/cortex-1-cadrage/references/profils/societe.md:88:  racines: []
(sortie 0)
$ grep -n "clients que tu as déjà servis" skills/cortex-1-cadrage/SKILL.md
(sortie 1)
# témoin, fix/phase-h :
$ git grep -n "clients que tu as déjà servis" fix/phase-h -- skills/cortex-1-cadrage/SKILL.md | cut -c1-160
fix/phase-h:skills/cortex-1-cadrage/SKILL.md:102:`marque.mentions_interdites` reçoit : ta marque, tes outils internes, tes noms propres, et **les clients que tu
(sortie 0)
$ grep -n -- "--inscrire\|vault/_export\|--attendu\|--redacteur" skills/cortex-1-cadrage/SKILL.md | cut -c1-200
165:    python3 "${CLAUDE_SKILL_DIR}/../cortex-8-federation/scripts/federe.py" --inscrire <slug> --redacteur "<Prénom Nom>" \
166:        --export "~/Cortex/<slug>/vault/_export/<slug>" \
168:        [--attendu "<Prénom Nom>" ...]
170:`--redacteur` est la personne qui porte ce vault. `--export` est le chemin que son vault aura, en forme `~`. Un `--attendu` par autre rédacteur nommé dans la liste du groupe et pas encore membre d
(sortie 0)

### 6. Phrases fautives du parcours
$ grep -rn -i "Mode consultant" skills --include=SKILL.md | cut -c1-220
(sortie 0)
$ grep -rn -i "conduite consultant" skills --include=SKILL.md | cut -c1-220
(sortie 0)
$ grep -rn -i "parcours dirigeant" skills --include=SKILL.md | cut -c1-220
skills/cortex-1-cadrage/SKILL.md:53:1 ⇒ `profil: employe`, 2 ⇒ `profil: dirigeant`, 3 ⇒ `profil: societe`. Le profil choisit `references/profils/<profil>.md`, qui donne les questions, les substrats attendus, les racines,
(sortie 0)
$ grep -rn -i "trancher quatre écarts" skills --include=SKILL.md | cut -c1-220
skills/cortex-3-ontologie/SKILL.md:43:**Forme.** Par AskUserQuestion, quatre écarts par appel, chacun en langage ordinaire avec l'indice chiffré et des options fermées plus « autre ». Jamais le nom du type d'écart devant
(sortie 0)
$ grep -rn -i "Accepter l.écart" skills --include=SKILL.md | cut -c1-220
(sortie 0)
$ grep -rn -i "maillon 1 (cortex-1-cadrage)" skills --include=SKILL.md | cut -c1-220
skills/cortex-0-poste/SKILL.md:107:Dire à la personne, en une phrase, ce qui est en place, ce qui a été refusé, et la phrase suivante que la notice affiche : « faisons le cadrage ». Jamais le numéro de l'étape ni le nom 
(sortie 0)
$ grep -rn -i "ci-dessus est-il juste" skills --include=SKILL.md | cut -c1-220
skills/cortex-1-cadrage/SKILL.md:174:Identité, puis white-label, puis substrats, puis bornes. Attendre à chaque bloc. Chaque bloc s'affiche en entier dans le message, ou dans l'aperçu de l'option qui le valide, avant la 
(sortie 0)

### 7. Maillon 8
$ grep -n "Où se lance ce maillon\|notice.py\" --atelier ~/Cortex\|Généré par" skills/cortex-8-federation/SKILL.md | cut -c1-200
27:**Où se lance ce maillon.** Depuis la session de l'atelier, dans `~/Cortex/<slug>/` de la personne qui tient le commun : c'est là que vivent `_cortex/07-federation.md` et la notice. Une session ouv
29:    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier ~/Cortex/<slug>/_cortex
72:| `README.md` | « Généré par `federe.py` le <date>, ne pas éditer », et `genere_le` dans l'en-tête |
96:diff -r "$C-temoin" "$C" | grep "^[<>]" | grep -v genere_le | grep -vc "Généré par"          # attendu : 0
103:Le contrôle 3 ignore les deux lignes datées, `genere_le` et « Généré par … le <date> » du `README.md` : elles changent à chaque passage par construction.
116:`_cortex/07-federation.md`, dans l'atelier de la personne qui tient le commun, depuis la session de cet atelier (Étape 0, « Où se lance ce maillon ») :
(sortie 0)

### 8. Windows
$ grep -n -i "windows" README.md outils/OUTILS.md skills/cortex-7-passation/SKILL.md | grep -i "wsl" | cut -c1-200
README.md:12:Sous Windows natif, les commandes que lance l'assistant ne sont pas confinées à votre second cerveau : seules les règles de lecture et d'édition protègent vos dossiers de travail. Rien ne
outils/OUTILS.md:5:Sous Windows, `py` vaut `python3` et `winget` est fourni avec le système. Limite connue de Windows natif : le confinement qui retient les commandes de l'assistant dans le vault n'y 
skills/cortex-7-passation/SKILL.md:38:**Sous Windows natif, une limite de plus, écrite dans le guide.** `os: windows` dans `_cortex/poste.json` : le guide le dit en clair. Sous Windows sans WSL2, les 
(sortie 0)
# témoin, fix/phase-h :
$ git grep -n -i "wsl" fix/phase-h -- README.md outils/OUTILS.md skills/cortex-7-passation/SKILL.md
(sortie 1)

### 9. Périmètre
$ git diff --stat fix/phase-h..lane/h2b
 README.md                                          |  2 +
 outils/OUTILS.md                                   |  2 +-
 skills/cortex-0-poste/SKILL.md                     | 28 ++++++-----
 skills/cortex-1-cadrage/SKILL.md                   | 54 ++++++++++++++--------
 skills/cortex-1-cadrage/references/doctrine.md     | 42 +++++++++++++++++
 .../references/profils/dirigeant.md                | 11 ++---
 .../cortex-1-cadrage/references/profils/employe.md | 13 +++---
 .../cortex-1-cadrage/references/profils/societe.md | 13 +++---
 skills/cortex-2-inventaire/SKILL.md                |  9 ++--
 skills/cortex-3-ontologie/SKILL.md                 | 14 +++---
 skills/cortex-4-installation/SKILL.md              | 13 ++++--
 .../template/vault/.claude/skills/bilan/SKILL.md   |  2 +
 .../template/vault/.claude/skills/cloture/SKILL.md |  4 +-
 .../template/vault/.claude/skills/ingest/SKILL.md  |  2 +
 .../template/vault/.claude/skills/lint/SKILL.md    |  4 +-
 .../vault/.claude/skills/nouveau-projet/SKILL.md   |  2 +
 .../template/vault/.claude/skills/parle/SKILL.md   |  2 +
 skills/cortex-5-ingest/SKILL.md                    | 14 +++---
 skills/cortex-6-agents-metier/SKILL.md             |  5 +-
 skills/cortex-7-passation/SKILL.md                 |  5 +-
 skills/cortex-8-federation/SKILL.md                | 33 ++++++++-----
 21 files changed, 187 insertions(+), 87 deletions(-)
(sortie 0)
$ git diff --name-only fix/phase-h..lane/h2b | grep -v "\.md$"
(sortie 1)

### 10. Prose
(le tiret cadratin s'écrit ici `$'\xe2\x80\x94'`, pour que ce rapport ne compte pas lui-même dans la sonde ; même octets, même résultat)
$ git diff fix/phase-h..lane/h2b | grep "^+" | grep -c $'\xe2\x80\x94'
0
(sortie 1)
# témoin, la même sonde sur les lignes retirées du même diff :
$ git diff fix/phase-h..lane/h2b | grep "^-" | grep -c $'\xe2\x80\x94'
5
(sortie 0)

### 11. Tailles
$ wc -l skills/cortex-[0-8]-*/SKILL.md
     148 skills/cortex-0-poste/SKILL.md
     239 skills/cortex-1-cadrage/SKILL.md
     201 skills/cortex-2-inventaire/SKILL.md
     211 skills/cortex-3-ontologie/SKILL.md
     172 skills/cortex-4-installation/SKILL.md
     191 skills/cortex-5-ingest/SKILL.md
     159 skills/cortex-6-agents-metier/SKILL.md
     197 skills/cortex-7-passation/SKILL.md
     168 skills/cortex-8-federation/SKILL.md
    1686 total
(sortie 0)
```

Les sorties `(sortie 0)` des `grep -L` vides tiennent au code de retour de `grep -L` sous macOS ; c'est la liste vide qui compte, et le témoin rend les neuf maillons puis les six skills du vault.

### Maillon 8, contrôle 3 sur un commun généré deux fois

Montage : deux exports fictifs de la recette (`export_fictif`, camille et yasmine), `federation.yaml` à deux membres, `federe.py --config` joué, copie témoin, second passage quatre secondes plus tard.

```
$ diff -r "$C-temoin" "$C" | grep "^[<>]"
< genere_le: 2026-10-02T21:45:21
> genere_le: 2026-10-02T21:45:25
< Généré par `federe.py` le 2026-10-02T21:45:21, ne pas éditer.
> Généré par `federe.py` le 2026-10-02T21:45:25, ne pas éditer.
$ diff -r "$C-temoin" "$C" | grep "^[<>]" | grep -vc genere_le                              # ancien contrôle 3, témoin
2
$ diff -r "$C-temoin" "$C" | grep "^[<>]" | grep -v genere_le | grep -vc "Généré par"       # nouveau contrôle 3
0
# témoin positif : une ligne ajoutée à la main dans une note de 20 - Projets
$ diff -r "$C-temoin" "$C" | grep "^[<>]" | grep -v genere_le | grep -vc "Généré par"
1
```

## Phrases fautives du parcours et passage qui les encadre

| Phrase dite au parcours | Skill qui l'a produite | Passage qui l'encadre désormais |
|---|---|---|
| « Mode consultant », « conduite consultant » | maillon 1 (H1, K1) | `cortex-1-cadrage/SKILL.md` Étape 0 : « Ni la question ni la suite ne disent « mode », « conduite », « consultant » ou « solo » : on dit « vous installez pour quelqu'un d'autre » ou « pour vous seul » » ; Interdits : « Ne jamais demander « quel mode » ni prononcer « solo », « consultant » ou « conduite » devant la personne, quelle que soit sa réponse » ; doctrine §8, première ligne du tableau |
| « parcours dirigeant », « profil societe, parcours employé » | maillon 1 (H1, K1) | `cortex-1-cadrage/SKILL.md` Étape 0 : « La suite ne dit jamais « profil », « parcours dirigeant » ni « parcours employé » : elle reprend la réponse de la personne » ; Interdits : « profil », « parcours », … ; doctrine §8 |
| « je dois trancher quatre écarts » | maillon 3 (H3) | `cortex-3-ontologie/SKILL.md` §1 bis, Forme : « L'entretien s'annonce dans ses mots : « j'ai quelques points à éclaircir avec vous sur ce que j'ai trouvé », jamais « je dois trancher quatre écarts » » ; message de clôture : « points à éclaircir : <N> relevés » |
| « Accepter l'écart » | clôture du vault (maillon 8 du parcours) | `template/vault/.claude/skills/cloture/SKILL.md` §5 : « L'avertissement se dit au récap, en phrase ordinaire, et ne devient jamais une question à valider : il n'y a rien à « accepter », c'est un constat » ; ligne « Devant la personne » en tête du skill |
| « Passe au maillon 1 (cortex-1-cadrage) » | maillon 0 (H0) | `cortex-0-poste/SKILL.md` §4 : « Jamais le numéro de l'étape ni le nom d'un skill : « passe au maillon 1 (cortex-1-cadrage) » est exactement ce qui ne se dit pas » ; §2 sans « maillon 4 » (`bc51816`) |
| « Le bloc identité ci-dessus est-il juste ? » sans bloc | maillon 1 (K1) | `cortex-1-cadrage/SKILL.md` §6 : « Chaque bloc s'affiche en entier dans le message, ou dans l'aperçu de l'option qui le valide, avant la question : « le bloc identité ci-dessus est-il juste ? » sans le bloc à l'écran est une validation à l'aveugle » ; doctrine §10 |
| « Le cahier des charges est-il juste ? » sans cahier | maillon 6 (H6) | `cortex-6-agents-metier/SKILL.md` §1 : « elle se valide vue : affichée en entier, telle qu'elle s'écrira […] « Le cahier des charges est-il juste ? » sans le cahier à l'écran est une signature à l'aveugle » |

Autres défauts majeurs de conduite, et où ils sont tenus :

- Lecture hors périmètre (majeur 3) : doctrine §9 ; `cortex-1-cadrage` §1 « Aucun `ls` ni aucune recherche dans le dossier personnel pour deviner la réponse » ; profils, sections « Les racines à demander » et `racines: []`.
- Confidentialité (majeur 4) et question reposée (majeur 2) : doctrine §11 « Marque » et « Réponse acquise » ; `cortex-1-cadrage` §2 réécrit (décision 6), « En groupe, la liste est une décision de groupe », Étape 0 « En groupe, les décisions de groupe se reprennent » ; `cortex-4-installation` : la liste « porte les marques du consultant ».
- Voie softeria sans accord (majeur 6) : `cortex-0-poste` §3 et Interdits ; doctrine §11 « Accord ».
- Détection (majeur 7, versant conduite) : `cortex-0-poste` §1 « à vérifier », §2 `connecte: null`, Interdits.
- Étape 8 et atelier existant (majeur 9) : `cortex-0-poste` Étape 0 ; `cortex-1-cadrage` §5 `--inscrire` ; `cortex-8-federation` Étape 0, condition 4 ; `profils/societe.md`.
- Windows (majeur 8) : `README.md`, `outils/OUTILS.md`, `cortex-7-passation` §1.

## Points en attente

1. **`--attendu` et membres déjà inscrits.** `04-contrat.md` §4 dit « un `--attendu` par autre rédacteur nommé dans la liste du groupe », et « chaque `--attendu` ajoute un nom à la liste `attendus` s'il n'y est pas ». Chez le deuxième rédacteur, passer le nom du premier, déjà membre, le remettrait dans `attendus` et laisserait l'étape 8 arbitrée pour toujours. Le skill du cadrage restreint donc à « pas encore membre de `federation.yaml` ». À trancher par le chef d'orchestre : garder cette lecture, ou demander à la lane A que `--inscrire` ignore un `--attendu` égal au `redacteur` d'un membre.
2. **Décision 6 et contrôle 1 du maillon 7.** La liste ne porte plus les autres clients du consultant. Le contrôle bloquant de white-label n'attrape donc plus, à la remise, le nom d'un autre client : la protection repose sur la lecture bornée (doctrine §9) et sur le gabarit vérifié par C8. Écart assumé, conforme à la décision ; à garder en tête pour le parcours C.
3. **Phrase contradictoire hors périmètre.** `cortex-4-installation/SKILL.md` l. 26 dit qu'en solo « chaque maillon propose le suivant et l'enchaîne après un accord explicite », contraire à l'amendement 2026-09-19 de la doctrine. Ce défaut n'est pas au verdict de la Phase H ; non corrigé, signalé.
4. **Maillon 8, condition 4.** Le skill refuse désormais de relier les cerveaux tant qu'un membre n'est pas remis ou qu'un attendu reste, pour s'aligner sur la règle d'`etat.py` (§3 du contrat). C'est une condition d'étape 0, pas une étape nouvelle ; l'audit dira si elle reste dans le périmètre.
5. **Dépendance à la lane A.** Le texte cite `--voie`, `voie_proposee`, `--options` vide, `present: null` et « à vérifier », `--inscrire`, l'empreinte du lint (`skills/lint/SKILL.md` du vault) tels que le contrat les fige. Ils ne valent qu'une fois `lane/h2a` mergée.
6. **Mineurs non traités, hors périmètre** (`01-cadrage.md`, Exclus) : tutoiement « Pour toi » des messages du consultant, question Sitadel au maillon 2, emplacement du vault absent du skill 4, notice à 4/9 après installation, conflit de porteur.
