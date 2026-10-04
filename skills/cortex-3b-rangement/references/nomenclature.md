# Nomenclature du rangement

Ce que `range.py` tient pour illisible, la forme d'un nom parlant, et ce qui ne se touche jamais. Contrat : `chantiers/cortex-2.3-rangement/04-contrat.md` §6 et §7. Le script porte ces règles ; ce fichier les explique à qui conduit l'étape.

## Un nom illisible

Un nom est illisible quand ni la personne ni une IA ne devinent ce que le fichier contient sans l'ouvrir. Quatre familles :

| Famille | Exemples |
|---|---|
| Nom par défaut d'un logiciel | `Nouveau document`, `Sans titre`, `Untitled`, `Document1`, `Classeur1` |
| Sortie d'un appareil | `Scan_0001`, `IMG_1234`, `DSC01234`, `Capture d'écran …` |
| Marque de copie ou de version | `(1)`, `Copie de …`, `… - copie`, `final`, `def`, `v2` sans objet |
| Chiffres seuls | `20240312`, `001` |

Un nom qui porte une marque de copie ou de version garde ce qui reste s'il est parlant : `Budget (1).xlsx` devient `Budget - <date>.xlsx`. Un nom sans rien de parlant prend le titre du document, ou à défaut le nom de son dossier.

Ne sont pas illisibles : un nom court mais clair (`Devis Malbrun`, `PV-reception`), un numéro dans un nom qui dit l'objet (`CR-2026-05`, `plan-001`).

## Un nom parlant et daté

    <Objet en clair> - AAAA-MM-JJ.<ext>

- **Objet** : le titre lu dans le document (première ligne d'un texte, premier paragraphe d'un `.docx`, objet d'un `.eml`) ; sinon le nom débarrassé de ses marques ; sinon le nom du dossier. Un document présent seulement en ligne ne s'ouvre jamais : son objet vient du dossier, et la ligne le signale pour que la personne confirme ou donne le nom (`--nommer`).
- **Date** : celle de la version. Celle du nom d'origine s'il en porte une, sinon la date de modification du fichier.
- **Extension** : jamais changée.
- **Caractères refusés**, pour que le nom tienne aussi sous Windows : `/ \ : * ? " < > |`, une espace ou un point en fin de nom. 120 caractères au plus.
- **Deux fichiers qui prendraient le même nom** dans un dossier : le second reçoit un numéro après l'objet (`Clients 2 - 2026-02-01.pdf`). Une destination déjà occupée n'est jamais écrasée (G1).
- **Le vocabulaire des domaines** décidés à l'étape des domaines sert au nom quand il s'applique : la personne le donne par `--nommer`, le script ne le devine pas. Aucun préfixe de code n'est imposé à un dossier existant.

## Une procédure

Un fichier dont le nom dit `process`, `processus`, `procédure`, `mode opératoire` ou `protocole`. Son classement :

| Où elle est | Classe | Ce qui se propose |
|---|---|---|
| dans le dossier commun | entreprise | rien : le dossier commun garde son organisation |
| dans un dossier partagé avec des collègues | entreprise | la ranger dans `<dossier commun>/Procédures/`, nom parlant et daté |
| dans un dossier à soi, nom qui dit « mon », « perso » | personnelle | un nom parlant si le sien est illisible ; elle reste chez la personne |
| dans un dossier à soi, sans indice | à demander | la question « pour vous seul ou pour toute l'entreprise ? », puis `--classer` |

Une procédure d'entreprise qui doit changer d'espace (d'un dossier à soi vers un dossier partagé d'un autre outil) devient un geste `manuel`. Sans dossier commun où la ranger, la liste le signale (`dossier_commun_absent`) et l'étape propose d'en créer un.

## Ce qui ne se renomme ni ne se déplace jamais

- un fichier ou un dossier caché (nom commençant par un point), un fichier système (`.DS_Store`, `Thumbs.db`, `desktop.ini`), un fichier de verrou bureautique (`~$…`) ;
- un dossier qui est un dépôt git, et tout ce qu'il contient ;
- un paquet d'application (`.app`, `.bundle`, `.photoslibrary`, `.pages`, `.numbers`, `.key`) ;
- un vault Obsidian (dossier qui porte `.obsidian/`) ;
- l'atelier `_cortex/` et le dossier du second cerveau ;
- un lien symbolique, qui n'est pas suivi ;
- les dossiers eux-mêmes : seuls les fichiers se renomment. Un dossier ne se crée que pour le dossier commun et ses procédures.

## Le sommaire du dossier commun

`AGENTS.md`, à la racine du dossier commun, écrit et réécrit par `range.py` seulement. Il porte la marque `<!-- cortex-3b-rangement: index AAAA-MM-JJ -->` ; un `AGENTS.md` sans cette marque n'est pas à Cortex et ne se réécrit jamais (G7).

```markdown
# Dossier commun de <Organisation>

Ce dossier porte les documents de référence de l'organisation : procédures, charte graphique, signatures, modèles, assistants. Toute IA qui travaille pour l'organisation lit ce sommaire avant de répondre sur l'un de ces sujets, puis le document lui-même.

<!-- cortex-3b-rangement: index 2026-10-04 -->

## Documents

| Document | Objet | Propriétaire | Date |
|---|---|---|---|
| [Facturation d'une affaire - 2025-11-04.docx](Procédures/Facturation%20d'une%20affaire%20-%202025-11-04.docx) | Facturation d'une affaire | Non renseigné | 2025-11-04 |

## Assistants

| Assistant | Ce qu'il fait | Fichier |
|---|---|---|
| lecteur-de-baux | Relève échéances, loyers et clauses d'un bail | [SKILL.md](assistants/lecteur-de-baux/SKILL.md) |

## Règles
- Une procédure par fichier ; le nom dit l'objet et la date de version.
- Une version nouvelle remplace l'ancienne au même endroit ; l'ancienne va dans `Archives/`.
```

- **Documents** : tout fichier du dossier commun, hors `Archives/`, `assistants/`, fichiers cachés et le sommaire lui-même ; 200 lignes au plus, le reste se compte sur une dernière ligne.
- **Propriétaire** : il se demande. La réponse passe par `--proprietaire "<chemin relatif>=<nom>"` ; sans réponse, `Non renseigné`. Une réécriture garde les propriétaires déjà inscrits.
- **Assistants** : un dossier `assistants/<nom>/SKILL.md` par assistant publié pour toute l'entreprise ; la colonne « Ce qu'il fait » reprend la première phrase de sa description.
