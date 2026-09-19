# 04 : Contrat gelé

Ce fichier fixe ce que les lanes se passent entre elles. Une lane qui a besoin d'autre chose s'arrête et le signale ; elle ne modifie pas ce contrat. Toute clé, tout schéma, tout chemin ci-dessous sont définitifs pour la v2.

## 1. Possession des fichiers

| Lane | Possède, et rien d'autre |
|---|---|
| B | `skills/cortex-0-poste/`, `outils/`, `notice/`, `skills/cortex-4-installation/scripts/{etat,rend_notice,notice}.py`, `skills/cortex-4-installation/scripts/notice.md`, `fabricant/`, `README.md`, `PROVENANCE.md` |
| C | `skills/cortex-1-cadrage/`, `skills/cortex-3-ontologie/`, `skills/cortex-4-installation/scripts/cortex_config.py`, `skills/cortex-4-installation/template/config.example.yaml` |
| D | `skills/cortex-2-inventaire/` |
| E | `skills/cortex-4-installation/SKILL.md`, `skills/cortex-4-installation/scripts/{scaffold,lint_sante}.py`, `skills/cortex-4-installation/template/` (sauf `config.example.yaml`), `skills/cortex-5-ingest/`, `skills/cortex-6-agents-metier/`, `skills/cortex-7-passation/` |
| F | `skills/cortex-8-federation/` |
| G | `skills/cortex-4-installation/recette/`, `chantiers/cortex-v2/06-verification.md` |
| chef d'orchestre | `.claude-plugin/`, `LICENSE`, `.gitignore`, `chantiers/cortex-v2/` hors 06-verification |

Règles :
- Une lane qui doit changer une valeur dans un fichier d'une autre lane écrit la valeur attendue dans son rapport ; le chef d'orchestre la porte ou l'arbitre.
- `config.example.yaml` est complet depuis A2. B, E et F n'y ajoutent rien ; C peut y corriger un commentaire ou une valeur d'exemple.
- La section « Notice » des SKILL.md (A2) est identique dans les neuf maillons ; les lanes B et F la reprennent telle quelle dans `cortex-0-poste` et `cortex-8-federation`.

## 2. `config.yaml` v2

Parseur : sous-ensemble YAML de `cortex_config.py`, mappings à un niveau, listes inline, listes de dicts inline. Pas de commentaire en fin d'une ligne qui porte une liste inline. L'exemple complet et commenté vit dans `skills/cortex-4-installation/template/config.example.yaml`. Les clés nouvelles ou modifiées :

```yaml
conduite: solo                      # solo | consultant ; absente = consultant
profil: employe                     # employe | dirigeant | societe
mode: solo                          # solo | federe (clé v1, conservée)
commun:
  racine: "~/Cortex/commun"         # "" si mode solo ; forme ~
  export: "_export"                 # dossier d'export dans CE vault
  visibilite_defaut: prive          # prive | commun
donnees:
  regime: pointeur                  # pointeur | copie
  structurants: [organigramme, process, fiche_de_poste, contrat, projet, acteur, tenants_aboutissants, fil_structurant]
collecte:
  racines: ["~/Documents", "~/Desktop/Travail"]
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  plafond_projets: 60
  plafond_acteurs: 80
  plafond_domaines: 6
sante:
  max_lignes_entree_journal: 10
  max_lignes_journal: 60
  journal_perime_jours: 14
  pointeur_canonique_obligatoire: true
  interdire_orphelins: true
  agent_metier_revue_mois: 6
  max_notes_parle: 12
  max_structurants: 40
  jours_sans_cloture_alerte: 7
poste:
  os: macos                         # macos | windows | linux
  outils: [obsidian, uv, markitdown, git, gh, github-desktop, buzz]
  mail_fournisseur: gmail           # gmail | m365 | outlook_perso | autre | ""
  mail_boites: 1
  mail_voie: connecteur             # connecteur | mcp-email | softeria | aucune
agents:
  skills: [cloture, nouveau-projet, ingest, lint, parle, bilan]
  sousagents: [chercheur-vault, auditeur-ontologie]
  metier: []
  hooks: [session-start, stop]
```

Sémantique :
- `profil` est posé au maillon 1 par une question en langage ordinaire, une seule fois. Il choisit `references/profils/<profil>.md` (lane C), qui liste les questions, les substrats attendus, les racines proposées, les plafonds et les domaines de départ. `societe` implique `mode: federe` pour chaque rédacteur.
- `donnees.regime` est fixé au maillon 1 : `pointeur` dès que `substrats.base_projets` est non vide ou qu'une base déportée est choisie ; `copie` sinon. Le maillon 5 ne copie que les types listés dans `structurants`, par lots de quatre, jusqu'à `sante.max_structurants`. Les copies vont dans `50 - Ressources/Structurants/<type>/<nom>.md` avec le frontmatter `type: structurant`, `structurant: <type>`, `source_path` (forme `~`), `hash` (sha256 de la source), `copie_le`. Le lint suspend le contrôle « 10 lignes » sur ce dossier et lève `structurant_perime` quand le hash de la source diffère.
- `collecte.racines` est la liste des dossiers parcourus par `scan.py`. Forme `~` obligatoire. `scaffold.py` en dérive `additionalDirectories` et les règles `deny`.
- `poste` est écrit par le maillon 0, miroir de `_cortex/poste.json`.
- `commun.export` est relatif au vault. `commun.racine` et `collecte.racines` sont les seuls chemins hors vault de tout le produit.

## 3. `_cortex/poste.json`

```json
{
  "format": "cortex/poste",
  "version": 1,
  "genere_le": "2026-09-19T10:12:00",
  "os": "macos",
  "outils": {
    "obsidian": {"present": true, "version": "1.14.2", "installe_par_cortex": false},
    "uv": {"present": true, "version": "0.9.1", "installe_par_cortex": true},
    "markitdown": {"present": true, "version": "0.1.7", "installe_par_cortex": true},
    "git": {"present": true, "version": "2.50", "installe_par_cortex": false},
    "gh": {"present": true, "version": "2.96", "installe_par_cortex": true, "connecte": true},
    "github-desktop": {"present": false, "version": "", "installe_par_cortex": false},
    "buzz": {"present": false, "version": "", "installe_par_cortex": false},
    "node": {"present": false, "version": "", "installe_par_cortex": false}
  },
  "options_proposees": ["wispr-flow", "superwhisper", "noota", "graphify"],
  "mail": {"fournisseur": "gmail", "boites": 1, "voie": "connecteur", "domaine": "exemple.test", "mx": "aspmx.l.google.com"},
  "notice_ouverte_le": "2026-09-19T10:12:03"
}
```

`poste.py --dry-run` imprime, sans rien installer, une ligne par outil absent : `<outil> : absent → <commande de l'OS>`. Sans `--dry-run`, il propose chaque installation et n'exécute que sur accord. La détection du fournisseur : une question (« quelle adresse utilisez-vous pour le travail ? »), puis le MX du domaine (`nslookup -type=MX <domaine>` sur les trois OS, stdlib `subprocess`), lu ainsi : `google.com` ou `googlemail.com` → `gmail` ; `outlook.com` ou `protection.outlook.com` avec un domaine `outlook.com`, `hotmail.*`, `live.*` → `outlook_perso`, sinon → `m365` ; autre → question à trois options. Voie retenue : `gmail` et une boîte → `connecteur` ; `gmail` et deux boîtes ou plus → `mcp-email` ; `m365` avec admin → `connecteur` ; `m365` sans admin ou `outlook_perso` → `softeria` ; `autre` → `mcp-email` si IMAP, sinon `aucune`.

## 4. `_cortex/01-inventaire.json` v2

Superset du schéma v1. Aucune source ne porte de champ `contenu` ; `scan.py` refuse de l'écrire. `scan.py` remplit `disque` et `bornes` ; l'agent remplit `mail` (§7) et `bases` ; `agenda` reste optionnel.

```json
{
  "format": "cortex/inventaire",
  "version": 2,
  "genere_le": "2026-09-19T11:00:00",
  "profil": "employe",
  "regime": "copie",
  "racines": ["~/Documents"],
  "bornes": {"profondeur_max_vue": 3, "dossiers_vus": 41, "fichiers_vus": 148, "octets_extraits": 183204,
             "profondeur_arbre": 3, "max_dossiers": 200, "depassement": false},
  "disque": [
    {"source_id": "documents-projets-refonte-intranet", "substrat": "espace_documentaire", "type": "dossier",
     "chemin": "~/Documents/Projets/Refonte intranet", "profondeur": 2, "fichiers": 12, "sous_dossiers": 0,
     "extensions": {"md": 7, "xlsx": 2, "docx": 1, "pdf": 2}, "derniere_maj": "2026-08-30", "premiere_maj": "2025-11-02",
     "depot_git": false, "signal_ontologique": {"mots": ["projet", "refonte", "intranet"], "structurant_candidat": ["cahier-des-charges.docx"]},
     "resume": "≤ 10 lignes", "preuve_de": []}
  ],
  "bases": [
    {"source_id": "base-projets", "substrat": "base_projets", "type": "base", "titre": "Projets", "url": "…",
     "signal_ontologique": {"proprietes": ["Statut", "Client"], "enums": {"Statut": ["Idée", "En cours", "Clos"]}},
     "volume": 47, "derniere_maj": "2026-08-11", "resume": "≤ 10 lignes", "preuve_de": []}
  ],
  "depots": [
    {"source_id": "depot-outil-interne", "type": "depot", "chemin": "~/Dev/outil", "langages": ["python"], "dernier_commit": "2026-07-04", "readme_20_lignes": "…", "graphify_propose": true}
  ],
  "mail": {
    "voie": "connecteur", "periode_mois": 12, "en_tetes_lus": 1840, "plafond": 2000,
    "agregats": [{"domaine": "nordaline.test", "volume": 612}, {"domaine": "fournitech.test", "volume": 121}],
    "acteurs": [{"adresse_domaine": "fournitech.test", "nom_affiche": "R. Lemaitre", "volume": 121, "declare": false}],
    "sujets_recurrents": [{"objet_normalise": "revue fournisseurs", "occurrences": 38, "premier": "2025-10-03", "dernier": "2026-09-12"}],
    "fils_structurants": []
  },
  "agenda": [{"titre": "Comité projet hebdo", "recurrence": "hebdomadaire", "occurrences": 40}],
  "ecarts_candidats": [
    {"type": "correspondant_non_declare", "indice": "fournitech.test, 121 messages", "source_id": "mail"}
  ]
}
```

`fils_structurants` n'existe qu'en régime `copie` : une entrée `{fil_id, objet, participants_anonymises, periode, messages, resume ≤ 10 lignes}` par fil validé au maillon 5, jamais un corps de mail. `ecarts_candidats` est ce que le maillon 3 transforme en questions (§8). Les types d'écart : `correspondant_non_declare`, `dossier_sans_domaine`, `reunion_recurrente_sans_projet`, `projet_non_declare`, `base_deportee_non_declaree`, `depot_non_declare`.

## 5. `_cortex/etat.json` à neuf étapes

`ETAPES` dans `etat.py` (lane B) devient :

```
(0, "cortex-0-poste",         "Poste",          "poste.json"),
(1, "cortex-1-cadrage",       "Cadrage",        "00-cadrage.md"),
(2, "cortex-2-inventaire",    "Inventaire",     "01-inventaire.md"),
(3, "cortex-3-ontologie",     "Ontologie",      "02-ontologie.md"),
(4, "cortex-4-installation",  "Installation",   None),            # trou en 03, raison conservée
(5, "cortex-5-ingest",        "Remplissage",    "04-ingest.md"),
(6, "cortex-6-agents-metier", "Agents métier",  "05-agents-metier.md"),
(7, "cortex-7-passation",     "Passation",      "06-passation.md"),
(8, "cortex-8-federation",    "Fédération",     "07-federation.md"),
```

`poste.json` est lu comme un artefact JSON (présent = étape faite si `notice_ouverte_le` est renseigné) ; les autres restent des markdown à frontmatter `statut`. L'étape 8 vaut `arbitre` avec la raison « vault solo » quand `mode: solo`. Le pivot gagne `profil`, `regime`, `phrase_suivante` (la phrase à prononcer pour l'étape suivante, en langage ordinaire, tirée d'une table de `etat.py`) et `notice_ouverte_le`. Conséquence assumée : les quatre assertions à sept de `parcours_blanc.py` passent au rouge dès le merge de B et jusqu'au merge de G, qui les porte à neuf. Aucune lane autre que G ne touche `parcours_blanc.py`.

## 6. Export et fédération

`cloture` (lane E) écrit, à chaque clôture, `<vault>/<commun.export>/<slug>/` :

```
_export/<slug>/
├── index.json          {"format": "cortex/export", "version": 1, "slug": "…", "exporte_le": "…", "notes": [{"chemin": "20 - Projets/X.md", "hash": "sha256"}]}
├── 10 - Domaines/…     copie des notes dont visibilite vaut commun, frontmatter enrichi de source_vault et exporte_le
├── 20 - Projets/…
├── 40 - Acteurs/…
└── 60 - Journal/…
```

Une note sans clé `visibilite` prend `commun.visibilite_defaut`. Une note `visibilite: prive` n'est jamais exportée. L'export est regénéré en entier à chaque clôture (dossier vidé puis réécrit), donc idempotent.

`<commun>/federation.yaml`, lisible par `cortex_config.charger` :

```yaml
version: 1
nom: "Ateliers Roumier"
membres:
  - { slug: camille, export: "~/Cortex/camille/_export/camille" }
  - { slug: yasmine, export: "~/Cortex/yasmine/_export/yasmine" }
  - { slug: marc,    export: "~/Cortex/marc/_export/marc" }
```

`federe.py --config <commun>/federation.yaml` (lane F) vide puis régénère `<commun>/` : `00 - Centre/Centre.md` (index par rédacteur et par domaine), `10 - Domaines/` fusionnés par nom, `20 - Projets/<SLUG> - <titre>.md` et `40 - Acteurs/` avec `source_vault`, `README.md` « généré par federe.py le <date>, ne pas éditer », `.cortex-genere` (sha256 de l'ensemble hors `genere_le`). Deux générations sur les mêmes exports ne diffèrent que sur `genere_le`. Un acteur présent chez deux rédacteurs donne une note unique avec `source_vault: [a, b]`.

## 7. Agrégat mail par connecteur

Le bloc `mail` est rempli par l'agent (skill `cortex-2`), jamais par `scan.py`. Lecture d'en-têtes seulement, sur `collecte.mail_mois`, plafonnée ; le plafond atteint se déclare dans `bornes.depassement`.

| Voie | Outil | Requête | Plafond |
|---|---|---|---|
| `connecteur` Gmail | `search_threads` du connecteur claude.ai | `newer_than:<mail_mois>m`, paginé, champs expéditeur, destinataires, objet, date | 2 000 en-têtes |
| `connecteur` Microsoft 365 | `outlook_email_search` du connecteur | période de `mail_mois` mois, champs `from`, `subject`, `receivedDateTime` | 2 000 en-têtes |
| `softeria` | `ms-365-mcp-server`, preset `outlook` | `messages?$select=from,subject,receivedDateTime&$top=100`, paginé | 2 000 en-têtes |
| `mcp-email` | `list_emails` par dossier (`INBOX`, `Sent`) et par compte | période de `mail_mois` mois, en-têtes seuls | 2 000 en-têtes par boîte |

Règle de bascule : `gmail` et une boîte → connecteur ; deux boîtes ou plus → `mcp-email` ; `m365` avec admin → connecteur ; `outlook_perso` ou `m365` sans admin → `softeria`. Sans `collecte.mail_optin: true` tracé au cadrage, aucune requête.

Ce que l'agent dérive : `agregats` (domaine expéditeur → volume), `acteurs` (domaine ou expéditeur avec 10 messages ou plus, `declare` confronté aux parties prenantes du cadrage), `sujets_recurrents` (objet normalisé : minuscules, sans `re:`/`tr:`/`fwd:`, sans numéro, 5 occurrences ou plus). Jamais un corps, jamais une adresse individuelle en clair hors `acteurs`.

## 8. Entretien de compréhension (maillon 3, lane C)

Entrée : `ecarts_candidats` de l'inventaire et le cadrage. Pour chaque écart, une question en langage ordinaire, par lots de quatre (AskUserQuestion), options fermées plus « autre ». La réponse écrit une ligne `[?] → réponse` dans `02-ontologie.md`, section « Ce que l'inventaire a révélé ». Un écart sans réponse reste `[?]`. L'entretien s'arrête quand la liste est vide ou que la personne le demande. Il précède la décision des domaines.

## 9. Couche agent du vault

Skills livrées par `scaffold.py` dans `<vault>/.claude/skills/` : `cloture`, `nouveau-projet`, `ingest`, `lint` (v1), `parle`, `bilan` (lane E). Sous-agents dans `<vault>/.claude/agents/` : `chercheur-vault`, `auditeur-ontologie`, `tools: Read, Grep, Glob`, jamais d'écriture.

`parle` : charge `00 - Centre`, puis la ou les notes domaine désignées par la question, puis les notes liées à ces domaines dont le frontmatter correspond, jusqu'à `sante.max_notes_parle` ; au-delà, délègue la recherche à `chercheur-vault` avec la question. Répond en citant `[[ ]]`. N'écrit jamais. Termine en proposant une clôture si l'échange a produit une décision.

`bilan` : lit `60 - Journal`, `git log` et `_cortex/etat.json` ; rend notes touchées, clôtures faites, orphelins, structurants périmés, prochaine étape. Déclenché à la demande, et proposé par le hook SessionStart à J+7 et J+30 de la remise.

Hooks, dans `<vault>/.claude/settings.json` seulement (jamais dans le plugin) :
- `SessionStart` : `python3 .claude/skills/lint/lint_sante.py --vault . --bref` puis rappel si la dernière clôture date de plus de `sante.jours_sans_cloture_alerte` jours (lu dans `git log -1 --format=%ci`).
- `Stop` : rappel « clôture » si `git status --porcelain` n'est pas vide.

`settings.json` généré :

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Bash(python3 .claude/skills/lint/lint_sante.py:*)", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(find:*)", "Bash(wc:*)", "Bash(ls:*)", "Bash(head:*)", "Bash(file:*)", "Bash(du:*)"],
    "deny": ["Write(~/Documents/**)", "Edit(~/Documents/**)", "Write(~/Desktop/Travail/**)", "Edit(~/Desktop/Travail/**)"],
    "additionalDirectories": ["~/Documents", "~/Desktop/Travail"]
  },
  "hooks": { "SessionStart": [...], "Stop": [...] }
}
```

Une règle `deny` par racine de `collecte.racines`, pour `Write` et `Edit`.

## 10. Ligne « Notice » des maillons (invariant I10)

Chaque SKILL.md maillon se termine par la section posée en A2 :

```
## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
```

`notice.py` régénère `etat.json` et `notice.html`, ouvre le HTML (`open`, `start`, `xdg-open`), sort toujours en 0. `--no-open` en recette.

## 11. Recette (lane G)

`parcours_blanc.py` couvre : neuf étapes, trois profils sur `fixtures.py`, régimes pointeur et copie, fédération sur les trois exports fictifs, validité des manifestes plugin (`plugin.json` et `marketplace.json` parsés, `source` vaut `./`, un `SKILL.md` par dossier de `skills/`), grep white-label, zéro chemin absolu (`/Users/`, `/home/`, lettre de lecteur) dans `skills/`, `notice/`, `outils/`, `README.md`. L'installation vivante du plugin (`claude plugin marketplace add`, `claude plugin install`) reste un contrôle manuel consigné dans `06-verification.md` avec sa sortie.

## Lectures prises en A2

- La fédération garde les clés v1 `mode` et `commun` (déjà testées par la recette, invariant I5) ; `commun` gagne `export` et `visibilite_defaut`. Aucun bloc `federation:` séparé : deux clés pour une même chose auraient divergé.
- `federation.yaml` vit dans le vault commun, pas dans un vault membre : c'est l'objet qui n'appartient à aucun rédacteur.
- La sonde Cowork et la création de l'org GitHub sont des gestes du chef d'orchestre, hors lane.
- `fixtures.py` produit les arbres sur disque (ignorés par git) ; la Roumier « en mémoire » de la recette v1 est un vault de trois notes, pas un arbre de fichiers : les deux coexistent.
- Le stub `notice.py` d'A2 fait déjà le travail complet (régénère, ouvre) ; la lane B y ajoute la phrase suivante et les neuf étapes.
