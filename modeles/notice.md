# Votre second cerveau

Ce paquet installe un second cerveau : un dossier de notes structurées que
Claude Code lit, remplit et entretient pour vous. Chaque projet, chaque
personne, chaque décision y trouve une place. Vous posez des questions en
langage ordinaire, l'outil retrouve et relie.

Tout reste sur votre machine. Rien n'est envoyé nulle part : pas de compte,
pas de télémétrie, pas de connexion requise une fois Claude Code installé.

## Avant d'installer : la seule condition

L'installation demande Python, un langage déjà présent sur Mac et Linux.

**Sur Windows, Python doit être installé d'abord.** Rendez-vous sur le site
python.org, téléchargez Python, et pendant l'installation **cochez la case
« Add Python to PATH »**. Sans cette case, rien ne fonctionnera. C'est la
seule installation supplémentaire du parcours, et elle prend cinq minutes.

Il vous faut aussi Claude Code, l'application dans laquelle tout se passe.
Si vous lisez cette notice, elle est probablement déjà sur votre machine.

## Installer, selon votre machine

Le geste est le même partout : déplacer les dossiers de ce paquet dans le
dossier des skills de Claude Code. Un skill est un savoir-faire que Claude
Code charge tout seul quand il en a besoin.

**Si un dossier du même nom existe déjà chez vous, ne remplacez rien.**
Gardez votre version, notez le nom du dossier de ce paquet que vous avez
laissé de côté, et signalez-le dans Claude Code à la première session.

### Sur Mac

1. Double-cliquez sur le fichier zip : les dossiers apparaissent à côté.
2. Dans le Finder, menu « Aller » puis « Aller au dossier », collez :
   `~/.claude/skills/`
3. Glissez tous les dossiers du paquet dans ce dossier. C'est fini.

### Sur Windows

1. Vérifiez la condition Python ci-dessus. C'est le préalable, pas une note.
2. Clic droit sur le fichier zip, « Extraire tout ».
3. Dans l'Explorateur, collez ce chemin dans la barre d'adresse :
   `C:\Users\VOTRE_NOM\.claude\skills\`
4. Déplacez tous les dossiers extraits dans ce dossier. C'est fini.

Dans Claude Code sous Windows, la commande `py` remplace `python3`. Vous
n'aurez pas à la taper : Claude Code s'en charge, mais si un message parle
de `python3`, lisez `py`.

### Sur Linux

1. Décompressez le zip.
2. Déplacez tous les dossiers dans `~/.claude/skills/` (créez le dossier
   s'il n'existe pas).
3. C'est fini.

## Démarrer

Ouvrez Claude Code et écrivez exactement ceci :

**« installe mon second cerveau »**

La première étape démarre et pose ses questions : qui vous êtes, où sont vos
dossiers de travail, ce que l'outil peut regarder et ce qu'il n'ouvrira pas.
Comptez une dizaine de questions, puis un récapitulatif à confirmer. Ensuite
la chaîne se déroule et vous demande votre accord avant chaque étape.

Comptez une douzaine de minutes, hors temps de réflexion sur vos réponses.

## Suivre l'avancée

Le tableau de bord en haut de cette page montre les sept étapes de
l'installation. Avant de commencer, les sept sont à faire : c'est normal,
c'est votre point de départ.

Pendant et après l'installation, demandez à Claude Code :
**« où en est mon installation ? »**. Il régénère le tableau de bord dans le
dossier de travail `_cortex/`, fichier `notice.html`, et vous dit ce qui est
fait, ce qui reste, et ce qui bloque.

L'étape 4 ne produit pas de fichier de suivi : son résultat est votre second
cerveau lui-même, et sa preuve est un contrôle de santé qui sort à zéro
erreur. Le tableau de bord le dit à sa ligne, pour que personne ne croie à
une étape oubliée.

## Ce que contient le paquet

Sept étapes d'installation, qui se suivent dans l'ordre :

- **cortex-1-cadrage** : les questions de départ. Qui écrit, où sont les
  dossiers, quelles limites.
- **cortex-2-inventaire** : la mesure de l'existant. L'outil compte vos
  dossiers et vos outils, sans rien lire en profondeur.
- **cortex-3-ontologie** : la carte. Vos grandes familles d'activité,
  décidées sur preuve et confirmées par vous.
- **cortex-4-installation** : la construction. Le dossier de notes est créé,
  vide et sain.
- **cortex-5-ingest** : le remplissage. Vos projets réels entrent dans
  l'outil, sous forme de fiches qui pointent vers vos vrais fichiers.
- **cortex-6-agents-metier** : les assistants sur mesure. Souvent la réponse
  honnête est « pas encore » : ils se méritent par l'usage.
- **cortex-7-passation** : la remise. Une fiche de reprise à froid, pour
  vous dans six mois.

Six compagnons de travail, disponibles dès l'installation :

- **stop-slop** : retire les tics d'écriture machine de vos textes.
- **humanizer** : même combat, sur la base du guide Wikipedia des signes
  d'écriture artificielle.
- **prompt-architect** : transforme une idée floue en demande précise pour
  l'outil.
- **presentation** : produit des supports de présentation, en page web et en
  PowerPoint.
- **compte-rendu** : transforme des notes de réunion, une photo ou un audio
  en compte rendu propre.
- **email-auditor** : relit un mail et en propose trois versions selon le
  destinataire.

## Quatre compléments, à obtenir auprès d'Anthropic

Les skills de fichiers Word, PDF, PowerPoint et Excel (docx, pdf, pptx,
xlsx) sont l'œuvre d'Anthropic et leur licence interdit de les redistribuer
dans un paquet. Elles ne sont donc pas dans ce zip.

Bonne nouvelle : elles accompagnent déjà Claude dans la plupart des offres,
sans rien installer. Sinon, leur source publique est le dépôt
github.com/anthropics/skills, consultable sous les conditions d'Anthropic.

## Le geste qui décide de tout

Quand vous finissez une séance de travail, dites à Claude Code :
**« j'ai fini »**. L'outil range ce que la séance a produit : le journal du
projet, les décisions, ce qui bloque. C'est ce geste, répété, qui fait d'un
dossier de notes une mémoire. Sans lui, l'outil reste propre et vide.

## Ce que l'outil ne fait jamais

- Il n'envoie rien hors de votre machine.
- Il ne lit pas votre messagerie sans votre accord explicite, tracé.
- Il ne copie pas vos documents : il pointe vers eux.
- Il ne se met pas à jour tout seul. Une nouvelle version arrivera comme
  celle-ci : un zip et une notice.
