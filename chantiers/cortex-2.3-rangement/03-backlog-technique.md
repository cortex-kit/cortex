# 03 : Backlog technique

Tout se fait dans le worktree `~/Dev/cortex--rangement`, branche `lane/rangement`. Stdlib Python 3.9 minimum, comme le reste du dépôt.

## Fichiers à créer

| Fichier | Rôle |
|---|---|
| `skills/cortex-3b-rangement/SKILL.md` | L'étape 3 bis : déclencheurs (« rangeons mes dossiers », « range mes dossiers », « annule le rangement »), conduite par lots, accord renforcé, gestes manuels, base en ligne, interdits, section « Notice » identique aux neuf maillons. |
| `skills/cortex-3b-rangement/scripts/range.py` | Proposer, appliquer, vérifier, annuler, écrire l'index, publier un assistant. Auto-test `--autotest`. Contrat : `04-contrat.md` §3 à §6. |
| `skills/cortex-3b-rangement/references/nomenclature.md` | Ce qui rend un nom illisible, la forme d'un nom parlant et daté, les caractères interdits, ce qui ne se renomme jamais, le gabarit d'`AGENTS.md`. |
| `chantiers/cortex-2.3-rangement/rapport.md` | Rapport de la lane : fait, écarts au contrat, valeurs attendues hors possession, suivis. |

## Fichiers à modifier

| Fichier | Changement |
|---|---|
| `skills/cortex-1-cadrage/SKILL.md` | Les deux questions (dossier partagé, dossier commun de l'entreprise), écriture de `collecte.partagees` et du bloc `referentiel`. |
| `skills/cortex-1-cadrage/references/doctrine.md` | §12 « Ce que la chaîne écrit hors du vault » ; amendement daté au §5 ; §9 cite le référentiel comme racine déclarée. |
| `skills/cortex-1-cadrage/references/profils/{employe,dirigeant,societe}.md` | La question du dossier commun dans l'ordre du fichier. |
| `skills/cortex-3-ontologie/SKILL.md` | Le message de fin propose « rangeons mes dossiers » puis « construis mon second cerveau ». |
| `skills/cortex-4-installation/scripts/cortex_config.py` | Valide `collecte.partagees` (sous-ensemble de `racines`), `referentiel.chemin` (sous une racine déclarée, forme `~`), `referentiel.etat`, `sante.max_gestes_rangement` ; refuse `process` dans `donnees.structurants`. |
| `skills/cortex-4-installation/template/config.example.yaml` | Les clés nouvelles, commentées ; `process` retiré de `structurants`. |
| `skills/cortex-4-installation/scripts/etat.py` | Entrée « 3b » entre 3 et 4, phrase, états `arbitre` et `en_cours` (journal partiel), auto-test étendu. |
| `skills/cortex-4-installation/scripts/notice.py`, `rend_notice.py` | Seulement si l'entrée « 3b » l'exige pour s'afficher. |
| `skills/cortex-4-installation/SKILL.md` | Garde : refus de construire si l'étape 3b est `en_cours`. |
| `skills/cortex-4-installation/scripts/scaffold.py` | Substitution de `{{REFERENTIEL}}` (forme `~`, ou phrase d'absence) ; le référentiel suit déjà les règles des racines. |
| `skills/cortex-4-installation/template/vault/CLAUDE.md` | Règle : pour une procédure, la charte, une signature, un modèle ou un assistant d'entreprise, lire d'abord l'`AGENTS.md` du dossier commun. |
| `skills/cortex-4-installation/template/vault/.claude/skills/parle/SKILL.md` | Même règle à la lecture. |
| `skills/cortex-4-installation/template/vault/.claude/skills/ingest/SKILL.md` | Procédure personnelle : note-pointeur ; procédure d'entreprise : jamais de note par document. |
| `skills/cortex-4-installation/template/vault/.claude/skills/lint/SKILL.md` | Une phrase : `process` toléré avec avertissement (A6). Ajout du 2026-10-04, après l'audit. |
| `skills/cortex-5-ingest/SKILL.md` | §2 bis : la procédure sort des types copiables ; note `Référentiel commun` ; notes-pointeurs des procédures personnelles. |
| `skills/cortex-5-ingest/scripts/copie_structurant.py` | Refus du type `process`, message qui nomme la règle. |
| `skills/cortex-6-agents-metier/SKILL.md` | Question « pour vous seul ou pour toute l'entreprise ? » ; publication d'un assistant d'entreprise par `range.py --publier`. |
| `skills/cortex-8-federation/SKILL.md`, `scripts/federe.py` | Clé `referentiel` de `federation.yaml` ; note `50 - Ressources/Référentiel commun.md` et ligne dans `Centre.md` du commun. |
| `skills/cortex-7-passation/SKILL.md` | Le guide d'usage cite le dossier commun et son sommaire, si `referentiel.etat` n'est pas `aucun`. |
| `skills/cortex-4-installation/recette/fixtures.py` | Un arbre en désordre et un dossier commun partagé dans la fixture dirigeant ; un fichier « en ligne seulement » simulé. |
| `skills/cortex-4-installation/recette/parcours_blanc.py` | Les contrôles de `06-verification.md`. |
| `notice/LISEZ-MOI.html`, `README.md` | Régénéré ou complété pour la phrase « rangeons mes dossiers », si leur source l'exige. |

## Ne pas toucher

`.claude-plugin/`, `chantiers/cortex-v2/`, `skills/cortex-0-poste/`, `skills/cortex-2-inventaire/`, `skills/cortex-4-installation/scripts/lint_sante.py`, `template/vault/.claude/skills/{miroir,agenda}/`, `fabricant/`, `outils/`.

## Architecture

- `range.py` est le seul code qui écrit hors du vault et de l'atelier. Il ne lit que les racines déclarées dans `config.yaml`, nomme toujours un chemin en entier, ne change jamais de dossier courant.
- La skill porte la conduite (lots, questions, mots) ; le script porte les gardes. Une garde ne vit jamais seulement dans la prose de la skill.
- L'atelier reçoit `03-rangement.md` (lisible, frontmatter `statut`), `03-rangement.json` (la liste), `03-rangement-journal.jsonl` (ce qui a été fait).
- Le maillon 6 réutilise `range.py --publier` ; aucun second code d'écriture hors du vault.

## Dépendances

Aucune nouvelle. `uvx --from "markitdown[all]" markitdown` (déjà présent) sert seulement à lire le titre d'un document local pour proposer son nom, dans les bornes d'extraction existantes, depuis un dossier temporaire.

## Commandes de référence

```bash
cd ~/Dev/cortex--rangement
python3 skills/cortex-3b-rangement/scripts/range.py --autotest
python3 skills/cortex-4-installation/scripts/etat.py --autotest
python3 skills/cortex-4-installation/scripts/cortex_config.py --autotest
python3 skills/cortex-4-installation/scripts/scaffold.py --autotest
python3 skills/cortex-8-federation/scripts/federe.py --autotest
python3 skills/cortex-5-ingest/scripts/copie_structurant.py --autotest
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo "exit=$?"
```
