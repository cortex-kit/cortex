# 02 : Arborescence cible

## Le dépôt `cortex-kit/cortex`

Disposition v1 conservée : chaque skill est autoportée (scripts et gabarit dans son dossier), référencée par `${CLAUDE_SKILL_DIR}`, valable dans le plugin comme dans le zip.

```
cortex/
├── .claude-plugin/plugin.json          name cortex, version, description
├── .claude-plugin/marketplace.json     le dépôt est sa propre marketplace, source "./"
├── .claude/skills/fabricant -> ../../fabricant   skill projet, hors plugin
├── skills/
│   ├── cortex-0-poste/                 B  SKILL.md, scripts/poste.py
│   ├── cortex-1-cadrage/               C  SKILL.md, references/{doctrine,secteurs}.md, references/profils/{employe,dirigeant,societe}.md
│   ├── cortex-2-inventaire/            D  SKILL.md, scripts/scan.py
│   ├── cortex-3-ontologie/             C  SKILL.md (entretien de compréhension)
│   ├── cortex-4-installation/          E  SKILL.md, scripts/{scaffold,cortex_config,lint_sante}.py, template/
│   │                                   B  scripts/{etat,rend_notice,notice}.py, scripts/notice.md
│   │                                   G  recette/{parcours_blanc,fixtures}.py
│   ├── cortex-5-ingest/                E
│   ├── cortex-6-agents-metier/         E  (inchangé)
│   ├── cortex-7-passation/             E
│   ├── cortex-8-federation/            F  SKILL.md, scripts/federe.py
│   └── stop-slop, humanizer, prompt-architect, presentation, compte-rendu, email-auditor   (kit.txt)
├── fabricant/                          B  fabrique.py (zip de repli), rend_deck.py, kit.txt, modeles/
├── outils/OUTILS.md                    B  chaque outil : rôle, install mac et Windows, licence, URL, verdict
├── notice/LISEZ-MOI.html               B  guide hors ligne, régénéré depuis etat.json
├── chantiers/cortex-v2/                chef d'orchestre
├── README.md                           B  trois gestes
├── LICENSE (MIT), PROVENANCE.md        B  verdicts des emprunts qui partent dans le zip
└── .gitignore
```

## Le vault installé (gabarit `cortex-4-installation/template/vault/`)

```
<vault>/
├── config.yaml                         la seule chose qui varie
├── CLAUDE.md                           contrat d'entrée, quatre opérations
├── .claude/settings.json               allow lecture, additionalDirectories = racines, deny Write/Edit sur ces racines
├── .claude/hooks/                      SessionStart : lint léger, rappel si aucune clôture depuis N jours ; Stop : rappel clôture
├── .claude/skills/                     cloture, nouveau-projet, ingest, lint, parle, bilan
├── .claude/agents/                     chercheur-vault, auditeur-ontologie (lecture seule)
├── 00 - Centre/ 10 - Domaines/ 20 - Projets/ 40 - Acteurs/ 50 - Ressources/ 60 - Journal/ 80 - Identité/ 99 - Inbox/
├── 50 - Ressources/Structurants/       régime copie seulement : source_path, hash, copie_le
├── 90 - Meta/                          doctrine paramétrée, runbooks, Guide d'usage, Reprise, Templates/
├── _export/<slug>/                     ce qui part au commun (visibilite: commun), écrit par cloture
└── _cortex/                            atelier : config.yaml, poste.json, 00-cadrage.md … 07-federation.md, etat.json, notice.html
```

Le vault commun (`commun.racine`) est généré par `federe.py`, porte un `README.md` « généré, ne pas éditer », et se régénère à l'identique.

## La chaîne v2 en face des cinq étapes

| Étape | Maillon | Ce qui change par rapport à la v1 |
|---|---|---|
| 1 Installer | `cortex-0-poste` | `poste.py --dry-run` liste ce qui manque avec la commande de l'OS ; installe Obsidian et ses core plugins (Bases, Daily notes, Templates, Graph, Properties), `uv` et Python 3.12, `markitdown`, git, `gh`, GitHub Desktop, Buzz ; propose Wispr Flow, Superwhisper, Noota ; `gh auth login` ; fournisseur mail par question et MX ; écrit `_cortex/poste.json` et le bloc `poste` de `config.yaml` ; ouvre la notice |
| 2 Scanner | `cortex-1`, `cortex-2` | `profil` pilote racines, substrats, plafonds, domaines de départ ; `scan.py` mesure le disque (bornes en entiers) ; `uvx markitdown` extrait le texte des candidats structurants, borné ; le bloc `mail` est rempli par l'agent selon le connecteur (`04-contrat.md` §7) |
| 3 Questionner | `cortex-3` | Entretien de compréhension : chaque écart observé/déclaré devient une question, par lots de quatre ; domaines décidés sur preuve, signés |
| 4 Construire, dialoguer | `cortex-4`, `-5`, `-6`, skill `parle` | settings avec deny, hooks, `gh repo create --private` ; `parle` charge Centre, puis les domaines visés, puis les notes liées jusqu'à `sante.max_notes_parle`, délègue au-delà, cite, n'écrit jamais |
| 5 Alimenter | `cloture`, `cortex-7`, `bilan` | clôture v1 et export fédération ; `bilan` à J+7 et J+30 |
| Plusieurs cerveaux | `cortex-8-federation` | `federation.yaml`, `federe.py`, commun lecture seule, idempotent |

## Outils (veille du 2026-09-19)

| Verdict | Outils |
|---|---|
| Installés par le maillon 0 | Claude Code natif (prérequis), Homebrew (mac), Obsidian, `uv` et Python 3.12, `markitdown` via `uvx`, git, `gh`, GitHub Desktop, Buzz. Node LTS seulement si Softeria ou `mcp-email` |
| Branchés selon profil | Connecteurs claude.ai : Gmail, Google Calendar, Google Drive, Microsoft 365, Slack, Noota. Softeria `ms-365-mcp-server`. `cortex-kit/mcp-email` |
| Proposés en option | Wispr Flow, Superwhisper, Graphify, Obsidian Web Clipper, pandoc, docling, `whisper-ctranslate2` |
| Écartés, motivés dans OUTILS.md | Obsidian Local REST API et `mcp-obsidian`, Obsidian Git, `gws` et `workspace-mcp` (projet Google Cloud), GongRzhe Gmail (archivé), WhatsApp MCP, unstructured, installeur python.org |
