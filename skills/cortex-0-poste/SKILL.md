---
name: cortex-0-poste
description: Maillon 0 de la chaîne Cortex, le point d'entrée du parcours. Équipe l'ordinateur de la personne pour un second cerveau (lecteur de notes, uv, markitdown, git, gh, GitHub Desktop, transcripteur audio, carte de dossiers graphify), reconnaît sa messagerie par question et MX, écrit _cortex/poste.json et le bloc poste de config.yaml, puis ouvre la notice pas à pas. Présente chaque outil avant de demander, et le choix de la personne vaut accord : ce qui est coché s'installe aussitôt, rien d'autre. Déclencher quand la personne écrit « installe mon second cerveau », « équipe mon poste », « prépare mon ordinateur pour le second cerveau », « maillon 0 », « qu'est-ce qui manque sur mon poste ». Ne PAS confondre avec cortex-1-cadrage, qui pose les questions de départ une fois le poste équipé.
---

# cortex-0-poste : le poste avant tout

Premier des neuf maillons, et le seul qui touche à l'ordinateur lui-même. La personne qui arrive ici a écrit « installe mon second cerveau » et n'a, le plus souvent, aucune compétence technique. Tout se dit en langage ordinaire, tout se fait sur accord, et rien ne se lance à sa place.

Le script du maillon : `${CLAUDE_SKILL_DIR}/scripts/poste.py`, stdlib pure, `py` vaut `python3` sous Windows. Il ne fait que ce qu'on lui demande par option : lister, installer une liste explicite, reconnaître la messagerie, écrire l'atelier.

## La chaîne complète

| Maillon | Rôle |
|---|---|
| **`cortex-0-poste`** | **ce maillon : outils, messagerie, notice** |
| `cortex-1-cadrage` | qui, quel profil, quels dossiers, quelles bornes |
| `cortex-2-inventaire` | mesure du disque et de la messagerie, sans lire en profondeur |
| `cortex-3-ontologie` | les domaines, sur preuve, après entretien |
| `cortex-4-installation` | le vault et sa couche d'agents |
| `cortex-5-ingest` | l'inventaire devient des notes |
| `cortex-6-agents-metier` | les agents sur mesure |
| `cortex-7-passation` | la remise et le suivi |
| `cortex-8-federation` | plusieurs vaults reliés à un commun |

**Aucun maillon n'invoque le suivant.** La notice propose la phrase à prononcer, la personne décide.

## Étape 0 : rien n'est requis

C'est le point d'entrée. Lister les noms des dossiers de `~/Cortex/`, leurs noms seuls, sans rien ouvrir dedans. Puis poser une seule question, en langage ordinaire, toujours la première :

> « Quel nom court voulez-vous donner à votre second cerveau ? Un mot, sans espace : votre prénom, votre société, ce que vous voulez. »

Si un atelier existe déjà sur le poste, la même question porte les ateliers existants comme options, à côté de « un nouveau nom ». Un atelier trouvé n'est jamais présumé celui de la personne qui parle, et ne se décrit pas d'après son contenu (`cortex-1-cadrage/references/doctrine.md` §11).

La réponse, en minuscules, devient `<slug>`. Si `~/Cortex/<slug>/_cortex/poste.json` existe déjà avec `notice_ouverte_le` renseigné, le maillon est fait pour cet atelier : le dire, proposer de rouvrir la notice, et s'arrêter. L'atelier vit dans `~/Cortex/<slug>/_cortex/`, hors de tout dossier synchronisé. Le slug est `organisation.code` : `poste.py` l'écrit dans `config.yaml` et dans `poste.json`, et c'est lui que reprendront `_export/<slug>/`, le dépôt `cortex-<slug>` et `federation.yaml`. Le maillon 1 y trouvera `config.yaml` avec le bloc `poste` déjà écrit.

## 1. Détecter

Toujours en premier, jamais rien d'autre avant :

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --dry-run

Une ligne par outil du kit absent, avec la commande de l'OS courant : `<outil> : absent → <commande>`. Une ligne `<outil> : à vérifier (<raison>)` dit que la sonde n'a pas pu mesurer, sans prouver l'absence : l'outil se dit « à vérifier » à la personne, jamais « absent », ne se propose pas à l'installation et ne déclenche aucune question technique. On ne propose jamais de corriger un script, le `PATH` ou la configuration du shell : c'est une affaire de fabricant, pas de la personne. Aucune ligne : le poste est équipé, passer au mail. Sur Mac sans Homebrew, une ligne de prérequis sort sur la sortie d'erreur : il passe en premier.

Le kit, dans cet ordre : lecteur de notes (`obsidian`), `uv` et Python, `markitdown`, `git`, `gh`, `github-desktop`, transcripteur audio (`buzz`). `node` n'en fait pas partie : il ne se propose que si la voie mail l'exige (voir §3).

## 2. Présenter, puis installer sur le choix

Avant toute question, présenter chaque outil manquant en deux ou trois phrases de langage ordinaire : ce qu'il fait, ce qui se passe sans lui dans le parcours, qu'il est gratuit et qu'il tourne sur l'ordinateur. La personne ne doit pas avoir à demander « c'est quoi ? ». Le tableau sert de pense-bête, pas de réponse :

| Outil | À quoi il sert |
|---|---|
| obsidian | lire et parcourir vos notes |
| uv | faire tourner les petits programmes du parcours |
| markitdown | lire vos documents Word, PDF, tableurs (toujours avec l'extra `[all]`, le paquet nu ne les lit pas) |
| git | garder l'historique de vos notes |
| gh | sauvegarder vos notes en privé en ligne |
| github-desktop | voir cet historique sans terminal |
| buzz | transcrire vos enregistrements audio |
| graphify | dessiner la carte d'un gros dossier de documents ou d'un dépôt de code, jamais du second cerveau lui-même |

Puis une seule question fermée (AskUserQuestion, choix multiples, un outil par option, les indispensables pré-cochés : `markitdown`, `obsidian`, `uv`, `git`, `gh` ; `buzz`, `github-desktop` et `graphify` selon ce que la personne a dit d'elle). **Le choix vaut accord** : dès la réponse, lancer l'installation des outils cochés, sans seconde confirmation.

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --installer obsidian,markitdown,graphify --atelier ~/Cortex/<slug>/_cortex

Le script exécute la commande de chaque outil nommé, rien d'autre, et mémorise ce qu'il a installé. Un outil non coché est une réponse : il reste absent, `poste.json` le dira, le maillon continue. Une commande qui échoue se signale et se reprend à la main, le maillon ne s'arrête pas pour ça.

Ensuite, deux gestes qui demandent la personne :

- **Les core plugins du lecteur de notes.** Bases, Daily notes, Templates, Graph, Properties. Ils s'activent dans les réglages du lecteur, une fois le second cerveau installé : le dire ici en ces mots, ne rien faire maintenant.
- **`gh auth login`.** Si `gh` est présent et non connecté, proposer de lancer la connexion dans le terminal. C'est la personne qui se connecte dans son navigateur, jamais le script. Sans compte, la sauvegarde en ligne attendra l'installation du second cerveau : le noter, continuer. Une connexion illisible d'ici (`connecte: null`) n'est pas une connexion expirée : la dire « à vérifier », et ne proposer la connexion que si la personne dit ne pas l'avoir faite.

Proposer enfin, sans insister, les options que le script n'installe pas : dictée vocale (`wispr-flow`, `superwhisper`) et prise de notes de réunion (`noota`), chacune depuis le site de l'éditeur. Ce que la personne retient part dans `--options` au §4, et `options_proposees` vaut exactement cette liste. Une réponse « aucune » ou un silence : pas de `--options`, la liste reste vide.

## 3. Brancher le mail

Une question, en langage ordinaire :

> « Quelle adresse utilisez-vous pour le travail ? »

Puis :

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --mail <adresse> [--boites N]

Le script lit le MX du domaine (`nslookup`, sur les trois OS) et rend le fournisseur : `gmail`, `m365`, `outlook_perso`, ou vide. Vide : poser la question à trois options (« votre messagerie est-elle Google, Microsoft, ou autre ? »), relancer avec `--fournisseur gmail|m365|autre`, et `--imap` si un accès IMAP est possible.

Deux compléments à demander quand ils changent la voie :

- `gmail` : combien de boîtes brancher ? Une seule → connecteur claude.ai ; deux ou plus → `mcp-email` (`--boites 2`).
- `m365` : la personne administre-t-elle son compte Microsoft 365 ? Oui → connecteur (`--admin`) ; non → `softeria`.

`softeria` et `mcp-email` installent quelque chose : elles ne s'écrivent que sur accord (`cortex-1-cadrage/references/doctrine.md` §11). Les proposer par une question qui dit ce qu'elles posent sur le poste. Pour `softeria` : un petit serveur local et l'outil node, qui donnent accès à la boîte sans passer par l'administrateur du compte. Pour `mcp-email` : le même petit serveur et node, avec un accès IMAP par boîte. Oui → `--voie softeria` ou `--voie mcp-email` au §4 ; non → `--voie aucune`, et la messagerie restera hors de l'inventaire. Sans `--voie`, `poste.py` n'écrit jamais une voie qui installe : il écrit `aucune` et garde la voie calculée dans `mail.voie_proposee`.

La voie retenue va dans `poste.json` et dans le bloc `poste`. Si la personne a accepté `softeria` ou `mcp-email`, le script signale `node` absent avec sa commande : le proposer comme un outil de plus, sur accord. Le branchement lui-même (connecteur, serveur MCP) se fait au maillon 2, avec `collecte.mail_optin` tracé au cadrage : ici on décide de la voie, on ne lit rien.

Une personne sans adresse de travail répond « aucune » : `--fournisseur autre` sans `--imap` donne la voie `aucune`.

## 4. Écrire l'atelier et ouvrir la notice

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --ecrire --atelier ~/Cortex/<slug>/_cortex --slug <slug> --mail <adresse> [--fournisseur X] [--boites N] [--admin] [--imap] [--voie connecteur|softeria|mcp-email|imap|aucune] [--options wispr-flow,noota]

Le script mesure une dernière fois les outils, écrit `_cortex/poste.json` (schéma du contrat : `os`, `organisation.code`, `outils` avec `present`, `version`, `installe_par_cortex`, `connecte` pour `gh`, `options_proposees`, `mail`, `notice_ouverte_le`), fusionne les blocs `organisation` et `poste` dans `_cortex/config.yaml` (créé s'il manque, les clés filles déjà posées sont conservées), puis régénère et ouvre la notice. `notice_ouverte_le` est posé à ce moment : c'est lui qui marque l'étape 0 faite. `--slug` omis, le script le déduit du chemin de l'atelier.

Ce que le script a installé lui-même reste tracé d'une écriture à l'autre : relancer `--ecrire` après un second lot ne perd pas le premier.

Dire à la personne, en une phrase, ce qui est en place, ce qui a été refusé, et la phrase suivante que la notice affiche : « faisons le cadrage ». Jamais le numéro de l'étape ni le nom d'un skill : « passe au maillon 1 (cortex-1-cadrage) » est exactement ce qui ne se dit pas.

## Sortie : `_cortex/poste.json` et le bloc `poste`

Forme `~` pour tout chemin, jamais un chemin absolu. Le bloc `poste` est le miroir de `poste.json` :

    organisation:
      code: acme

    poste:
      os: macos
      outils: [obsidian, uv, markitdown, git, gh, github-desktop, buzz]
      mail_fournisseur: gmail
      mail_boites: 1
      mail_voie: connecteur

`outils` liste le kit entier, dans l'ordre du contrat. Qui est présent, dans quelle version, et installé par Cortex ou déjà là : `poste.json` le dit outil par outil, c'est la seule source.

## Interdits

- **Ne jamais parler, lire ni faire valider hors de la doctrine** : les mots devant la personne, ce que la chaîne lit, ce qui se valide à l'écran, ce qui demande un accord (`cortex-1-cadrage/references/doctrine.md` §8 à §11).
- **Ne jamais installer ce qui n'a pas été coché.** Le choix dans la question vaut accord, il n'y a pas de seconde confirmation ; `--installer` ne reçoit que des noms cochés par la personne. Jamais de `--installer` déduit d'un `--dry-run`.
- **Ne jamais lancer une installation en dehors du script**, ni `brew`, ni `winget`, ni `curl | sh` à la main : la commande vient de `poste.py`, pour qu'elle soit la même partout et tracée.
- **Ne jamais écrire une voie mail qui installe sans accord.** `--voie softeria` ou `--voie mcp-email` ne part qu'après un oui à la question qui dit ce qu'elles posent ; un refus écrit `--voie aucune`.
- **Ne jamais dire « absent » d'un outil « à vérifier »**, ni proposer de modifier un script, le `PATH` ou la configuration du shell.
- **Ne jamais présumer qu'un atelier existant est celui de la personne.** Le nom court se demande, toujours.
- **Ne jamais lire la messagerie ici.** Le MX est une requête DNS sur le domaine, pas une lecture de courrier.
- **Ne jamais se connecter à un compte à la place de la personne** (`gh auth login`, connecteurs, éditeurs d'options).
- **Ne jamais écrire hors de `~/Cortex/<slug>/_cortex/`.** Le poste se mesure, il ne se range pas.
- **Ne jamais enchaîner sur le maillon 1.** La notice propose « faisons le cadrage », la personne le dit ou non.

## Où travailler

La version de Claude Code dans le navigateur ne convient pas : elle tourne sur un ordinateur distant qui ne voit pas les dossiers de la personne. Terminal ou application de bureau, cette dernière restant à recetter. Le dire si la personne demande.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
