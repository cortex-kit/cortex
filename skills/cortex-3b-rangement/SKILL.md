---
name: cortex-3b-rangement
description: Étape 3 bis de la chaîne Cortex, facultative, entre la décision des domaines et la construction. Propose de ranger les dossiers de travail de la personne (noms parlants et datés, procédures de l'entreprise réunies dans un dossier commun, sommaire AGENTS.md lisible par toute IA), fait valider la liste par lots de quatre, l'applique par range.py, la vérifie, et sait la défaire. Jamais de suppression, jamais de copie, accord renforcé pour un dossier partagé avec des collègues ; une base en ligne reçoit une proposition, rien d'autre. Produit 03-rangement.md. Déclencher quand la personne dit « rangeons mes dossiers » (phrase de la notice), « range mes dossiers », « annule le rangement », « défais le rangement », « maillon 3b », ou dispose d'une carte des domaines signée. Ne PAS confondre avec cortex-4-installation, qui construit le second cerveau, ni avec cortex-5-ingest, qui le remplit.
---

# cortex-3b-rangement : ranger l'existant, sur accord

Étape facultative, entre la carte des domaines et la construction. Le second cerveau pointe vers les dossiers de la personne ; si ces dossiers s'appellent « Nouveau document (3) » et « Scan_0042 », le pointeur est juste et personne ne s'y retrouve. Cette étape propose des noms parlants, réunit les procédures de l'entreprise en un seul endroit, et pose un sommaire que toute IA lit. Elle vient après les domaines, pour que les noms reprennent leur vocabulaire, et avant la construction, pour que les liens du second cerveau naissent sur les chemins définitifs.

**Rien ne s'impose.** Un refus entier est une réponse complète : l'étape s'inscrit refusée et la construction reste ouverte.

## Ce que l'étape peut faire, et ce qu'elle ne fait jamais

Le seul code qui écrit hors du second cerveau et de l'atelier est `range.py` (doctrine §12). Il renomme, déplace dans un même espace, crée le dossier commun et son dossier des procédures, écrit le sommaire, publie un assistant. Chaque geste est journalisé et se défait.

Il ne supprime rien, n'écrase rien, ne duplique rien, ne convertit aucune procédure, n'ouvre aucun fichier présent seulement en ligne, et ne déplace jamais d'un espace à un autre (un OneDrive à soi vers une bibliothèque partagée) : ce geste-là, la personne le fait dans son outil, et l'étape vérifie après coup. Les gardes vivent dans le script, pas dans cette page.

## Étape 0 : bloquante

1. `_cortex/02-ontologie.md` en `statut: valide` : les noms suivent le vocabulaire des domaines signés. Le script le vérifie lui-même (code 3 sinon).
2. `_cortex/config.yaml` se charge et porte `collecte.racines`, `collecte.partagees` et le bloc `referentiel` posés au cadrage.
3. Aucune commande n'entre dans un dossier de travail par `cd` : chaque chemin se nomme en entier (doctrine §9).
4. Le second cerveau n'est pas construit. L'installation inscrit `construit_le` dans `03-rangement.md`, et le script refuse ensuite de proposer, d'appliquer ou de défaire (code 3) : ranger après la construction casserait ses liens, et ranger après la remise est hors de cette étape. Le dire ainsi à la personne.

**Si un contrôle échoue, s'arrêter.** Ranger sans domaines signés, c'est nommer avec un vocabulaire qui changera.

**Devant la personne**, ses mots, jamais ceux de l'outil (doctrine §8) : « vos dossiers », « la liste des changements », « le dossier commun », « le sommaire pour les IA », « défaire ». Jamais racine, journal, plan, JSON, geste, référentiel, `AGENTS.md`, régime, pointeur, profil, ni un nom de script. Un nom de fichier ou de dossier affiché dans une ligne de la liste (`…/Référentiel/AGENTS.md`) est une donnée, pas un mot de l'outil : il s'affiche tel quel.

## 1. Proposer

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --proposer
```

Le script parcourt les dossiers déclarés et écrit la liste (`03-rangement.json`) et sa version lisible (`03-rangement.md`). Il propose un nom parlant pour chaque nom illisible, range les procédures d'entreprise dans le dossier commun, signale les doublons probables et les fichiers présents seulement en ligne. Règles de nom : `references/nomenclature.md`. Au-delà de `sante.max_gestes_rangement` changements, la liste s'arrête et le dit.

**Dossier commun absent** (`referentiel.etat` à `aucun` ou `inconnu`) : avec un seul dossier partagé déclaré, la liste propose de le créer dedans. Avec plusieurs, la liste porte `dossier_commun_a_choisir` : demander lequel, puis relancer avec `--referentiel "<dossier partagé>/Référentiel"`. Sans aucun, la liste porte le signalement `dossier_commun_absent` : demander où l'entreprise range ce qu'elle partage ; ce dossier est un nouveau dossier de travail, qui se demande, s'ouvre une fois pour vérifier qu'il répond, s'écrit en forme `~` dans `collecte.racines` et `collecte.partagees`, jamais deviné. Avant tout geste, la config se valide ; une erreur se corrige avant de relancer :

```bash
python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/cortex_config.py" <chemin de _cortex/>/config.yaml
```

Puis relancer la proposition.

Un dossier de travail qui est un dépôt git ou un vault, ou qui s'y trouve, ne reçoit aucune proposition (signalement `racine_dans_un_depot`). Liste vide : le script écrit `statut: rien_a_ranger`. Le dire en une phrase et passer à la fin (§9).

## 2. Le résumé

Une phrase qui compte, avant tout lot :

> J'ai relevé 37 changements possibles dans vos dossiers : 22 noms illisibles à renommer, 9 procédures à regrouper, 6 doublons à vérifier. Rien n'est supprimé, rien n'est copié, tout peut être défait. On les regarde quatre par quatre ?

Un refus ici vaut refus entier :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --clore refuse
```

## 3. Les lots de quatre

Les lignes portent un numéro de lot. Pour chaque lot, dans l'ordre : écrire les quatre lignes **en entier dans le message** (doctrine §10), puis une seule question AskUserQuestion à choix multiple, une option par ligne, « cochez celles que vous gardez ». Une ligne non cochée ne se fait pas.

> 1. `Nouveau document (3).docx` devient `Accueil d'un nouveau client - 2026-03-12.docx` (nom illisible ; titre lu dans le document)
> 2. `Scan_0042.pdf` devient `Clients - 2026-02-01.pdf` (nom illisible ; nom déduit du dossier)

Un fichier présent seulement en ligne n'a pas été ouvert : son nom vient du dossier. Proposer « ce nom », « un autre nom » (réponse libre) ; un autre nom passe par `--nommer r002="Objet en clair"`. Le vocabulaire des domaines signés s'applique de la même façon quand la personne le préfère.

Les lignes cochées s'appliquent aussitôt, lot par lot :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --appliquer --ids r001,r003
```

Code 3 : une garde a levé, rien n'a bougé ; lire la raison et la dire dans les mots de la personne (« ce nom est déjà pris dans ce dossier », « ce fichier a changé depuis tout à l'heure, je repropose »). Une ligne dont le fichier a changé se repropose par `--proposer`. Code 1 : un geste a échoué en route (droits, client de synchronisation) ; ce qui précède est fait, le lot s'arrête, le dire, et proposer de défaire ou de réessayer. Code 1 aussi quand les gestes sont faits et que seul le sommaire n'a pas suivi (le message le dit) : le dire tel quel, la clôture le rafraîchira une fois la cause levée.

## 4. Les procédures au classement douteux

Une ligne `classe: a_demander` ne s'applique pas. Une question par procédure, groupées par quatre :

> Cette procédure vaut-elle pour toute l'entreprise, ou c'est votre façon de faire à vous ?

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --classer r004=entreprise,r005=personnelle
```

Personnelle : elle reste chez la personne, renommée si son nom est illisible ; le second cerveau y pointera. D'entreprise : elle rejoint le dossier commun, et le second cerveau pointera vers le dossier commun, jamais vers une copie.

## 5. Les dossiers partagés : accord renforcé

Les lignes `partage: true` forment des lots à part, après les autres. La confirmation est séparée de la première et dit, mot pour mot :

> D'autres personnes travaillent dans ce dossier : leurs liens et leurs raccourcis vers ces fichiers ne marcheront plus.

Puis la liste des lignes concernées, en entier, et une question oui ou non. Sur oui seulement :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --appliquer --ids r002,r003,r005 --renforce
```

## 6. Le dossier commun et son sommaire

Le sommaire est écrit par le script seul et se régénère après chaque lot qui touche le dossier commun, et à la clôture : il liste tout le dossier, quel que soit l'ordre des lots. Une note ajoutée à la main ne survit qu'à travers la colonne des propriétaires. Défaire le rend mot pour mot tel qu'il était. S'il n'est présent qu'en ligne, rien ne s'y écrit : demander de le rendre disponible sur le poste.

**Existant** : « Votre dossier commun garde son organisation. J'y ajoute un sommaire que toute IA lira avant de répondre sur une procédure, la charte ou les signatures. » Le sommaire s'affiche en entier avant l'accord, tel qu'il s'écrira : le script l'imprime sans rien écrire, pour les lignes du lot qui le portent, et c'est ce texte-là que l'application écrit.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --montrer-index --ids <lignes du lot> [--proprietaire "Procédures/<nom>=<Nom>"]
```

Le recopier en entier dans le message, puis poser la question. Un sommaire déjà présent sans la marque de Cortex (signalement `index_etranger`) se montre tel quel, et la question porte sur le fait de le laisser : il n'est jamais remplacé.

**Absent** : « Votre entreprise n'a pas de dossier commun pour ses procédures. Je peux en créer un dans <dossier partagé> et y ranger les <N> procédures qui valent pour tous. Voyez avec qui de droit avant de dire oui. » Les lignes de création viennent d'abord, celles du rangement ensuite, celle du sommaire en dernier, toutes en lots renforcés ; la création passe avant toute ligne qui en dépend.

**Propriétaires** : pour chaque document du sommaire, demander qui en est responsable (par lots de quatre, réponse libre acceptée). La réponse passe par `--proprietaire "Procédures/<nom>=<Nom>"` sur la commande qui applique la ligne du sommaire ; sans réponse, `Non renseigné`.

## 7. Ce que la personne fait elle-même

Les lignes `manuel` relient deux espaces différents. Une liste « à faire vous-même dans OneDrive / Drive », chemin de départ et chemin d'arrivée en entier. Quand la personne dit l'avoir fait :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --verifier
```

Il constate le déplacement (taille et date, jamais le contenu) et l'inscrit. Un geste qu'elle renonce à faire se retire par `--annuler --ids r004`. Un geste en attente ne bloque pas la construction, mais le remplissage ne crée aucune fiche vers ce fichier tant qu'il n'est pas constaté.

## 8. La base en ligne

Si la liste porte un bloc `base`, l'afficher comme une proposition : « Votre base de projets gagnerait à … ». La personne l'applique elle-même dans son outil. **Rien ne s'écrit dans la base**, même sur accord.

## 9. Finir

1. Vérifier ce qui a été fait :
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --verifier
   ```
   Code 1 : un écart (un fichier rangé a bougé entre-temps). Le dire, ne pas clore.
2. Clore. Le script refuse tant qu'une ligne acceptée n'est pas faite, et inscrit le dossier commun créé dans `config.yaml` :
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --clore applique
   ```
3. Remettre l'inventaire à jour sur les nouveaux noms (amendement A1), sans toucher aux réponses déjà données : le rejeu garde la messagerie, les bases, les résumés et les preuves.
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/../cortex-2-inventaire/scripts/scan.py" --config <chemin de _cortex/>/config.yaml --out <chemin de _cortex/>/01-inventaire.json
   ```
4. En groupe (`mode: federe`), un dossier commun créé ici rejoint le fichier du groupe, pour que le commun le cite ; la commande est celle du cadrage, avec le chemin désormais inscrit dans `config.yaml` :
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/../cortex-8-federation/scripts/federe.py" --inscrire <slug> --redacteur "<Prénom Nom>" \
       --export "~/Cortex/<slug>/vault/_export/<slug>" --config "<commun.racine>/federation.yaml" \
       --nom "<organisation>" --referentiel "<referentiel.chemin>"
   ```
   Si le groupe a déjà un dossier commun, le script garde le sien et le dit : le dire à la personne.
5. Afficher le bilan (message de clôture), puis la notice.

## Défaire

« annule le rangement », à tout moment avant la construction :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/range.py" --atelier <chemin de _cortex/> --annuler
```

Le journal se rejoue à l'envers : chaque fichier reprend son nom et sa place, un dossier créé et resté vide disparaît, un sommaire inchangé depuis son écriture disparaît. Ce que la personne a déplacé elle-même dans son outil, elle le remet elle-même : le dire. Après la construction, le script refuse : défaire casserait les liens du second cerveau. Le dire, sans chercher à contourner. Pour une seule ligne : `--annuler --ids r003`.

## Interdits

- **Ne jamais parler, lire ni faire valider hors de la doctrine** : les mots devant la personne, ce que la chaîne lit, ce qui se valide à l'écran, ce qui demande un accord (`cortex-1-cadrage/references/doctrine.md` §8 à §12).
- **Jamais un geste hors de `range.py`**, ni un `mv`, ni un `rm`, ni une écriture à la main dans un dossier de travail. Jamais `cd` vers un dossier de travail.
- **Jamais une ligne appliquée sans avoir été affichée en entier** et cochée.
- **Jamais un dossier partagé sans l'accord renforcé**, posé à part, avec la phrase sur les liens qui casseront.
- **Jamais ouvrir un fichier présent seulement en ligne** : le lire le téléchargerait.
- **Jamais écrire dans une base en ligne.** Une proposition, rien d'autre.
- **Jamais copier une procédure**, ni la convertir à côté de l'original.
- **Jamais supprimer un doublon** : il se signale, la personne décide.

## Message de clôture

```
Vos dossiers sont rangés.

- <N> changements faits, <M> refusés, rien supprimé, rien copié
- <K> à faire vous-même dans votre outil de partage, <dits ou aucun>
- dossier commun : <créé et doté d'un sommaire | sommaire ajouté | aucun>
- tout se défait tant que le second cerveau n'est pas construit :
  dites « annule le rangement »

La suite construit votre second cerveau sur ces noms-là. Sa
condition d'entrée : la carte des domaines signée, c'est fait.

Quand vous voulez continuer, dites « construis mon second cerveau ».
```

**Sur un refus, ou s'il n'y avait rien à ranger :**

```
Vos dossiers restent tels quels, c'est noté.

Le second cerveau pointera vers eux sous leurs noms actuels. Vous
pourrez revenir sur ce choix avant la construction en disant
« rangeons mes dossiers ».

Quand vous voulez continuer, dites « construis mon second cerveau ».
```

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
