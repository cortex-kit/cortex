# Outils du poste

Ce que le maillon 0 installe, branche, propose ou écarte, avec la commande de chaque OS, la licence et l'adresse. Aucun de ces outils n'est redistribué dans le paquet : chacun s'installe depuis son éditeur, sur accord de la personne, outil par outil. Le paquet lui-même ne contient que ses maillons et l'annexe `stop-slop` (voir `PROVENANCE.md`).

Sous Windows, `py` vaut `python3` et `winget` est fourni avec le système. Sous Linux, les commandes visent la famille Debian ; une autre distribution adapte le gestionnaire de paquets.

Où travailler : Claude Code en terminal ou en application de bureau. La version dans le navigateur ne convient pas, elle tourne dans un conteneur distant sans accès au disque alors que le vault vit sur le poste ; l'application de bureau reste à recetter sur ce parcours.

## Installés par le maillon 0

| Outil | Rôle | Install mac | Install Windows | Install Linux | Licence | URL | Verdict |
|---|---|---|---|---|---|---|---|
| Claude Code | l'application dans laquelle tout se passe | prérequis, installé par la personne | prérequis | prérequis | propriétaire, conditions Anthropic | claude.com/code | prérequis, jamais installé par le script |
| Homebrew | gestionnaire de paquets, mac seulement | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` | sans objet | sans objet | BSD 2 clauses | brew.sh | prérequis mac, signalé par `--dry-run` |
| Obsidian | lecteur et éditeur du vault, core plugins Bases, Daily notes, Templates, Graph, Properties | `brew install --cask obsidian` | `winget install --id Obsidian.Obsidian -e` | `flatpak install -y flathub md.obsidian.Obsidian` | propriétaire, gratuit en usage personnel, licence commerciale pour une société | obsidian.md | installé |
| uv et Python 3.12 | exécute les scripts du parcours, installe Python si besoin | `brew install uv` | `winget install --id astral-sh.uv -e` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | MIT ou Apache 2.0 | astral.sh/uv | installé |
| markitdown | convertit Word, PDF, tableurs, présentations en texte pour l'inventaire | `uv tool install markitdown` | idem | idem | MIT | github.com/microsoft/markitdown | installé |
| git | historique du vault | `brew install git` | `winget install --id Git.Git -e` | `sudo apt-get install -y git` | GPL 2 | git-scm.com | installé |
| gh | dépôt privé en ligne, `gh auth login` par la personne | `brew install gh` | `winget install --id GitHub.cli -e` | `sudo apt-get install -y gh` | MIT | cli.github.com | installé |
| GitHub Desktop | voir l'historique sans terminal | `brew install --cask github` | `winget install --id GitHub.GitHubDesktop -e` | pas de version officielle, `gh` suffit | MIT | desktop.github.com | installé sur mac et Windows |
| Buzz | transcription audio locale (Whisper) | `brew install --cask buzz` | `winget install --id ChidiWilliams.Buzz -e` | `uv tool install buzz-captions` | MIT | github.com/chidiwilliams/buzz | installé |
| Node LTS | requis seulement par Softeria ou `mcp-email` | `brew install node` | `winget install --id OpenJS.NodeJS.LTS -e` | `sudo apt-get install -y nodejs` | MIT | nodejs.org | installé si la voie mail l'exige |

## Branchés selon profil

| Outil | Rôle | Install mac | Install Windows | Licence | URL | Verdict |
|---|---|---|---|---|---|---|
| Connecteur Gmail (claude.ai) | en-têtes de la boîte de travail, une boîte Google | activé dans claude.ai, réglages connecteurs | idem | conditions Anthropic et Google | claude.ai | voie `connecteur`, une boîte Google |
| Connecteur Google Calendar, Google Drive | agenda et documents partagés | idem | idem | idem | claude.ai | selon profil |
| Connecteur Microsoft 365 (claude.ai) | en-têtes Outlook, agenda, SharePoint, avec droits d'administration | activé dans claude.ai, consentement admin | idem | conditions Anthropic et Microsoft | claude.ai | voie `connecteur`, M365 avec admin |
| Connecteur Slack, Noota | messages d'équipe, notes de réunion | idem | idem | idem | claude.ai | selon profil |
| Softeria `ms-365-mcp-server` | Outlook personnel ou M365 sans admin, preset `outlook` | `npx -y @softeria/ms-365-mcp-server` (Node requis) | idem | MIT | github.com/softeria/ms-365-mcp-server | voie `softeria` |
| `cortex-kit/mcp-email` | plusieurs boîtes IMAP, dont deux boîtes Google ou plus ; la seule référence mail IMAP du parcours | `npx -y` depuis le fork, Node requis | idem | MIT (fork) | github.com/cortex-kit/mcp-email | voie `mcp-email` |

## Proposés en option

| Outil | Rôle | Install mac | Install Windows | Licence | URL | Verdict |
|---|---|---|---|---|---|---|
| Wispr Flow | dictée vocale dans toute application | depuis l'éditeur | depuis l'éditeur | propriétaire, abonnement | wisprflow.ai | option, installée par la personne |
| Superwhisper | dictée vocale locale, mac | depuis l'éditeur | sans objet | propriétaire | superwhisper.com | option mac |
| Graphify | carte d'un dépôt de code ou d'un gros dossier de documents | proposé au maillon 2 sur détection | idem | voir l'éditeur | à confirmer par le maillon 2 | option, jamais sur le vault |
| Obsidian Web Clipper | capture de pages web dans le vault | extension du navigateur | idem | MIT | obsidian.md/clipper | option |
| pandoc | conversion de documents de repli | `brew install pandoc` | `winget install --id JohnMacFarlane.Pandoc -e` | GPL 2 | pandoc.org | option, si markitdown ne suffit pas |
| docling | extraction de PDF complexes | `uv tool install docling` | idem | MIT | github.com/docling-project/docling | option, gros PDF |
| `whisper-ctranslate2` | transcription en ligne de commande | `uv tool install whisper-ctranslate2` | idem | MIT | github.com/Softcatala/whisper-ctranslate2 | option, si Buzz ne convient pas |

## Écartés

| Outil | Motif |
|---|---|
| Obsidian Local REST API et `mcp-obsidian` | un plugin communautaire requis et un serveur local en plus, pour ce que la lecture directe des fichiers markdown fait déjà |
| Obsidian Git | plugin communautaire ; `git` et `gh` couvrent le besoin, la clôture fait le commit |
| `gws` et `workspace-mcp` | exigent un projet Google Cloud et des identifiants OAuth : hors de portée d'un novice |
| GongRzhe Gmail MCP | dépôt archivé, plus maintenu |
| WhatsApp MCP | session non officielle, risque de blocage du compte |
| unstructured | dépendances lourdes pour un gain nul face à markitdown |
| Installeur python.org | `uv` installe Python et le tient à jour, sans case « Add to PATH » à cocher |
