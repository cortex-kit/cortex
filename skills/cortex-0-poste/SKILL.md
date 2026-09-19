---
name: cortex-0-poste
description: Maillon 0 de la chaîne Cortex, le point d'entrée du parcours. Équipe l'ordinateur de la personne pour un second cerveau (lecteur de notes, uv, markitdown, git, gh, GitHub Desktop, transcripteur audio), reconnaît sa messagerie par question et MX, écrit _cortex/poste.json et le bloc poste de config.yaml, puis ouvre la notice pas à pas. N'installe jamais rien sans accord explicite, outil par outil. Déclencher quand la personne écrit « installe mon second cerveau », « équipe mon poste », « prépare mon ordinateur pour le second cerveau », « maillon 0 », « qu'est-ce qui manque sur mon poste ». Ne PAS confondre avec cortex-1-cadrage, qui pose les questions de départ une fois le poste équipé.
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

C'est le point d'entrée. Si `_cortex/poste.json` existe déjà avec `notice_ouverte_le` renseigné, le maillon est fait : le dire, proposer de rouvrir la notice, et s'arrêter.

Le dossier d'atelier n'existe pas encore. Poser une seule question, en langage ordinaire :

> « Quel nom court voulez-vous donner à votre second cerveau ? Un mot, sans espace : votre prénom, votre société, ce que vous voulez. »

La réponse, en minuscules, devient `<slug>`. L'atelier vit dans `~/Cortex/<slug>/_cortex/`, hors de tout dossier synchronisé. Le maillon 1 y trouvera `config.yaml` avec le bloc `poste` déjà écrit.

## 1. Détecter

Toujours en premier, jamais rien d'autre avant :

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --dry-run

Une ligne par outil du kit absent, avec la commande de l'OS courant : `<outil> : absent → <commande>`. Aucune ligne : le poste est équipé, passer au mail. Sur Mac sans Homebrew, une ligne de prérequis sort sur la sortie d'erreur : il passe en premier.

Le kit, dans cet ordre : lecteur de notes (`obsidian`), `uv` et Python, `markitdown`, `git`, `gh`, `github-desktop`, transcripteur audio (`buzz`). `node` n'en fait pas partie : il ne se propose que si la voie mail l'exige (voir §3).

## 2. Proposer, puis installer sur accord

Traduire chaque ligne en une phrase que la personne comprend, puis demander son accord par une question fermée, un outil par option (AskUserQuestion, choix multiples). Dire à quoi sert chaque outil en six mots :

| Outil | À quoi il sert |
|---|---|
| obsidian | lire et parcourir vos notes |
| uv | faire tourner les petits programmes du parcours |
| markitdown | lire vos documents Word, PDF, tableurs (toujours avec l'extra `[all]`, le paquet nu ne les lit pas) |
| git | garder l'historique de vos notes |
| gh | sauvegarder vos notes en privé en ligne |
| github-desktop | voir cet historique sans terminal |
| buzz | transcrire vos enregistrements audio |

Sur accord, et seulement pour les outils cochés :

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --installer obsidian,markitdown --atelier ~/Cortex/<slug>/_cortex

Le script exécute la commande de chaque outil nommé, rien d'autre, et mémorise ce qu'il a installé. Un refus est une réponse : l'outil reste absent, `poste.json` le dira, le maillon continue. Une commande qui échoue se signale et se reprend à la main, le maillon ne s'arrête pas pour ça.

Ensuite, deux gestes qui demandent la personne :

- **Les core plugins du lecteur de notes.** Bases, Daily notes, Templates, Graph, Properties. Ils s'activent dans les réglages du lecteur, une fois le vault ouvert au maillon 4 : le dire ici, ne rien faire maintenant.
- **`gh auth login`.** Si `gh` est présent et non connecté, proposer de lancer la connexion dans le terminal. C'est la personne qui se connecte dans son navigateur, jamais le script. Sans compte, la sauvegarde en ligne attendra le maillon 4 : le noter, continuer.

Proposer enfin, sans insister, les options : dictée vocale (`wispr-flow`, `superwhisper`), prise de notes de réunion (`noota`), carte de code (`graphify`, seulement si un dépôt de code existe). Chaque option acceptée s'installe par la personne elle-même, depuis le site de l'éditeur : le script ne les installe pas. Leur liste va dans `options_proposees`.

## 3. Brancher le mail

Une question, en langage ordinaire :

> « Quelle adresse utilisez-vous pour le travail ? »

Puis :

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --mail <adresse> [--boites N]

Le script lit le MX du domaine (`nslookup`, sur les trois OS) et rend le fournisseur : `gmail`, `m365`, `outlook_perso`, ou vide. Vide : poser la question à trois options (« votre messagerie est-elle Google, Microsoft, ou autre ? »), relancer avec `--fournisseur gmail|m365|autre`, et `--imap` si un accès IMAP est possible.

Deux compléments à demander quand ils changent la voie :

- `gmail` : combien de boîtes brancher ? Une seule → connecteur claude.ai ; deux ou plus → `mcp-email` (`--boites 2`).
- `m365` : la personne administre-t-elle son compte Microsoft 365 ? Oui → connecteur (`--admin`) ; non → `softeria`.

La voie retenue va dans `poste.json` et dans le bloc `poste`. Si la voie est `softeria` ou `mcp-email`, le script signale `node` absent avec sa commande : le proposer comme un outil de plus, sur accord. Le branchement lui-même (connecteur, serveur MCP) se fait au maillon 2, avec `collecte.mail_optin` tracé au cadrage : ici on décide de la voie, on ne lit rien.

Une personne sans adresse de travail répond « aucune » : `--fournisseur autre` sans `--imap` donne la voie `aucune`.

## 4. Écrire l'atelier et ouvrir la notice

    python3 "${CLAUDE_SKILL_DIR}/scripts/poste.py" --ecrire --atelier ~/Cortex/<slug>/_cortex --mail <adresse> [--fournisseur X] [--boites N] [--admin] [--imap] [--options wispr-flow,noota]

Le script mesure une dernière fois les outils, écrit `_cortex/poste.json` (schéma du contrat : `os`, `outils` avec `present`, `version`, `installe_par_cortex`, `connecte` pour `gh`, `options_proposees`, `mail`, `notice_ouverte_le`), écrit ou remplace le bloc `poste` de `_cortex/config.yaml` (créé s'il manque), puis régénère et ouvre la notice. `notice_ouverte_le` est posé à ce moment : c'est lui qui marque l'étape 0 faite.

Dire à la personne, en une phrase, ce qui est en place, ce qui a été refusé, et la phrase suivante que la notice affiche : « faisons le cadrage ».

## Sortie : `_cortex/poste.json` et le bloc `poste`

Forme `~` pour tout chemin, jamais un chemin absolu. Le bloc `poste` est le miroir de `poste.json` :

    poste:
      os: macos
      outils: [obsidian, uv, markitdown, git, gh]
      mail_fournisseur: gmail
      mail_boites: 1
      mail_voie: connecteur

`outils` liste les outils présents à la fin du maillon, installés par Cortex ou déjà là.

## Interdits

- **Ne jamais installer sans accord explicite**, outil par outil. `--installer` ne reçoit que des noms cochés par la personne. Jamais de `--installer` déduit d'un `--dry-run`.
- **Ne jamais lancer une installation en dehors du script**, ni `brew`, ni `winget`, ni `curl | sh` à la main : la commande vient de `poste.py`, pour qu'elle soit la même partout et tracée.
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
