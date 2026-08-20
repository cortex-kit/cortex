---
name: cortex-4-installation
description: Installe un vault Cortex — un second cerveau structuré — chez une organisation, à partir d'un fichier de configuration. Crée l'arborescence, la doctrine paramétrée, les templates, et la couche d'agents (4 skills de maintenance, 2 sous-agents). Déterministe et rejouable : détruire et relancer est un geste normal. Déclencher quand l'utilisateur dit "installe le vault", "instancie Cortex", "crée le second cerveau de X", "maillon 4", ou dispose d'un config.yaml prêt. Ne PAS utiliser pour cadrer (cortex-1), inventorier (cortex-2), décider de l'ontologie (cortex-3) ni pour peupler le vault (cortex-5).
---

# cortex-4-installation — matérialiser le vault

Quatrième maillon de la chaîne Cortex. **Zéro jugement, cent pour cent déterministe.**

C'est le point de reprise à coût nul de toute la chaîne : `rm -rf` puis relance est ici un geste normal, pas un incident. C'est précisément pourquoi ce maillon est isolé des maillons de jugement — le cadrage et l'ontologie coûtent le temps du client, la matérialisation coûte une seconde.

## La chaîne complète

| Maillon | Rôle |
|---|---|
| `cortex-1-cadrage` | qui est le client, quelle marque, quels substrats |
| `cortex-2-inventaire` | catalogue de pointeurs vers l'existant, jamais de contenu |
| `cortex-3-ontologie` | les domaines, chacun avec sa preuve chiffrée. Le seul maillon de jugement |
| **`cortex-4-installation`** | **ce maillon — le vault et sa couche d'agents** |
| `cortex-5-ingest` | l'existant retenu devient des notes-pointeurs |
| `cortex-6-agents-metier` | les agents sur mesure, une fois le vault peuplé |
| `cortex-7-passation` | pack de remise et recette d'acceptation |

**Aucun maillon n'invoque le suivant.** Le consultant lance.

## Positionnement

Ce maillon **n'invente rien**. Si une valeur manque dans `config.yaml`, il s'arrête et le dit — il ne comble pas. Une valeur inventée à l'installation se retrouve dans la doctrine du client, où elle sera crue.

Ce qui relève d'un autre maillon : le choix des domaines (`cortex-3`), la collecte des accès (`cortex-1`), le remplissage du vault (`cortex-5`).

## Étape 0 — bloquante

1. `config.yaml` existe et se charge :
   ```bash
   python3 scripts/cortex_config.py <chemin config.yaml>
   ```
2. Le fichier `_cortex/02-ontologie.md` porte `statut: valide` — les domaines ont été arbitrés et signés.

**Si un contrôle échoue, s'arrêter. Pas de repli.** Installer sur une ontologie non validée produit un vault qu'il faudra refaire, et refaire un vault déjà rempli coûte cent fois l'installation.

## Le geste

```bash
python3 scripts/scaffold.py --config <config.yaml> --out "<racine du vault client>"
```

Il crée l'arborescence, substitue les moustaches, **instancie une note par domaine dans `10 - Domaines/`**, génère `graph.json` depuis les domaines, écrit le miroir `90 - Meta/Configuration.md`, copie les scripts de maintenance dans `.claude/skills/lint/`, initialise git, et **échoue si une moustache subsiste** ou si la config est incomplète.

Deux choses qu'il ne fait pas, et c'est délibéré : il ne comble aucune valeur manquante, et il **ne copie pas `marque.mentions_interdites` dans le vault du client**. Cette liste porte les autres clients du consultant ; la copier ferait du fichier censé les interdire celui qui les transporte. Elle reste dans l'atelier, où la recette du maillon 7 la lit.

`--force` écrase une destination existante. **Sans hésiter tant que le vault n'est pas peuplé** — c'est le mode normal de ce maillon, et détruire un vault qui ne contient que le gabarit ne coûte rien.

Dès le maillon 5, ce n'est plus vrai : `--force` fait un `rm -rf` et le vault porte alors le travail du client. Le script refuse désormais de lui-même s'il trouve des notes qui ne viennent pas du gabarit, et demande `--ecraser-vault-peuple` — un second geste, explicite, qu'on n'ajoute pas par réflexe.

Pour rafraîchir la couche d'agents d'un vault déjà livré — c'est le seul cas courant de relance après l'ingest — utiliser `--outillage-seul` :

```bash
python3 scripts/scaffold.py --config <config.yaml> --out "<vault>" --outillage-seul
```

Il réécrit `.claude/` (skills, sous-agents, scripts de lint) et ne touche à rien d'autre. Sans lui, une correction du lint n'atteignait aucun vault installé : les scripts de maintenance sont copiés à l'installation, et le seul geste qui les remplaçait était destructeur.

## Ce qui est livré

- **La doctrine** — `Conventions`, `Architecture Mémoire`, `Architecture - Vue d'ensemble`, les runbooks, l'ingest, l'amorçage. Paramétrée depuis la config, sans aucun enum en dur.
- **Sept templates** de notes et de CLAUDE.md.
- **Le kit d'agents** : les skills `cloture`, `nouveau-projet`, `ingest`, `lint` ; les sous-agents `chercheur-vault` et `auditeur-ontologie`.
- **Dix contrats de dossier**, un `_README` par dossier numéroté.
- **Zéro plugin requis.** Les requêtes Dataview existent, regroupées dans une note optionnelle qu'aucune autre ne référence : si le client l'installe elles marchent, sinon rien ne casse.

## Validation

**Une seule fois, globale.** Montrer l'arborescence produite et le résultat du lint, puis passer.

Ce maillon ne mérite pas de validation fine : régénérer coûte une seconde. Les validations par bloc appartiennent aux maillons dont la sortie est chère à reproduire — le cadrage et l'ontologie.

## Contrôles de sortie

```bash
grep -r "{{" "<vault>" --include='*.md' | grep -v 'Templates/'      # attendu : vide
python3 "<vault>/.claude/skills/lint/lint_sante.py" --vault "<vault>"  # attendu : exit 0
```

Le second contrôle doit être lancé **depuis le vault du client**, pas depuis ce skill : c'est ce qui prouve qu'il est autonome et ne dépend de rien sur la machine du consultant.

## Message de clôture

```
Le vault de <organisation> est installé.

- <N> notes, <M> domaines, mode <solo|federe>
- lint : vert
- couche d'agents : 4 skills, 2 sous-agents, 0 hook

Pour toi :
1. Ouvre le vault et parcours [[Centre]].
2. Fais tourner `cloture` sur une vraie session, trois fois.
3. Quand c'est fluide, lance `cortex-5-ingest` pour y verser l'inventaire.

Ne peuple pas le vault à la main avant l'étape 3 : cortex-5 est idempotent,
il détecterait une note écrite à la main comme un conflit à arbitrer.
```

## Interdits

- **Ne jamais modifier le gabarit pour un client.** Ce qui varie va dans `config.yaml`. Un gabarit forké par client cesse d'être un produit au deuxième client.
- **Ne jamais installer sur une ontologie non validée.**
- **Ne jamais laisser une moustache** non substituée : le client lirait `{{ORGANISATION}}` dans sa propre doctrine.
- **Ne jamais copier `scaffold.py` chez le client.** C'est un outil d'installation ; le client n'a aucune raison de réinstancier son vault, et lui en donner le moyen l'expose à l'écraser.
