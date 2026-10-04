# 04 : Contrat

Étend `chantiers/cortex-v2/04-contrat.md`. Toute clé ou forme ci-dessous est définitive pour la 2.3.0 ; une lacune s'écrit dans `rapport.md`, elle ne se comble pas en silence.

## 1. `config.yaml` : clés nouvelles

```yaml
collecte:
  racines: ["~/Documents/Travail", "~/Library/CloudStorage/OneDrive-Exemple/Commun"]
  partagees: ["~/Library/CloudStorage/OneDrive-Exemple/Commun"]
donnees:
  regime: copie
  structurants: [organigramme, fiche_de_poste, contrat, projet, acteur, tenants_aboutissants, fil_structurant]
referentiel:
  etat: existant
  chemin: "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel"
sante:
  max_gestes_rangement: 120
```

- `collecte.partagees` : sous-ensemble de `collecte.racines`, forme `~`. Absente = `[]`. Posée au maillon 1 par la question « d'autres personnes travaillent-elles dans ce dossier ? ».
- `referentiel.etat` : `existant` | `a_creer` | `aucun` | `inconnu`. Posé au maillon 1 ; l'étape 3b le fait passer de `aucun` ou `inconnu` à `a_creer` puis `existant` sur accord.
- `referentiel.chemin` : `""` tant que `etat` ne vaut pas `existant`. Sinon il est égal à une racine déclarée ou situé sous l'une d'elles, et cette racine figure dans `partagees`. `cortex_config.py` refuse tout autre cas.
- `process` dans `donnees.structurants` : toléré avec un avertissement et exclu de la liste effective (A6). Le refus vit dans `copie_structurant.py`.
- `sante.max_gestes_rangement` : entier, 120 par défaut.

Une racine ajoutée à l'étape 3b (l'espace partagé où créer le dossier commun) suit la règle du cadrage : elle se demande, s'ouvre une fois, s'écrit en forme `~`, jamais devinée.

## 2. `federation.yaml` : clé nouvelle

```yaml
version: 1
nom: "Ateliers Exemple"
referentiel: "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel"
membres:
  - { slug: camille, export: "~/Cortex/camille/_export/camille" }
```

`referentiel` vaut `""` ou est absente quand le groupe n'en a pas. C'est une décision de groupe : fixée au cadrage du premier rédacteur, reprise telle quelle par les suivants. `federe.py` écrit alors `<commun>/50 - Ressources/Référentiel commun.md` (§7) et une ligne dans `00 - Centre/Centre.md`. Sans la clé, rien de plus qu'en 2.2.0.

## 3. `_cortex/03-rangement.json`

```json
{
  "format": "cortex/rangement",
  "version": 1,
  "genere_le": "2026-10-04T15:00:00",
  "racines": ["~/Documents/Travail", "~/Library/CloudStorage/OneDrive-Exemple/Commun"],
  "bornes": {"gestes": 37, "plafond": 120, "depassement": false, "ecartes": 0},
  "operations": [
    {"id": "r001", "geste": "renommer", "de": "~/Documents/Travail/Clients/Nouveau document (3).docx",
     "vers": "~/Documents/Travail/Clients/Accueil d'un nouveau client - 2026-03-12.docx",
     "motif": "nom illisible ; titre lu dans le document", "partage": false, "lot": 1, "classe": ""},
    {"id": "r002", "geste": "creer_dossier", "vers": "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel/Procédures",
     "motif": "dossier commun des procédures", "partage": true, "lot": 5, "classe": ""},
    {"id": "r003", "geste": "deplacer", "de": "~/Library/CloudStorage/OneDrive-Exemple/Commun/Divers/Process facturation.docx",
     "vers": "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel/Procédures/Facturation d'une affaire - 2025-11-04.docx",
     "motif": "procédure établie pour toute l'entreprise", "partage": true, "lot": 5, "classe": "entreprise"},
    {"id": "r004", "geste": "manuel", "de": "~/Documents/Travail/Process relance.docx",
     "vers": "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel/Procédures/Relance d'un impayé - 2026-01-20.docx",
     "motif": "deux espaces différents : à déplacer dans l'interface de l'outil", "partage": true, "lot": 6, "classe": "entreprise"},
    {"id": "r005", "geste": "ecrire_index", "vers": "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel/AGENTS.md",
     "motif": "sommaire pour les IA", "partage": true, "lot": 6, "classe": ""}
  ],
  "signalements": [
    {"type": "doublon_probable", "chemins": ["~/Documents/Travail/A/tarifs.xlsx", "~/Documents/Travail/B/tarifs.xlsx"], "motif": "même nom, même taille"},
    {"type": "en_ligne_seulement", "chemins": ["~/Library/CloudStorage/OneDrive-Exemple/Commun/Scan_0042.pdf"], "motif": "non ouvert ; nom à demander"}
  ],
  "base": [
    {"objet": "propriété Statut", "constat": "11 valeurs dont 4 synonymes", "proposition": "réduire à Idée, En cours, En attente, Clos"}
  ]
}
```

- `geste` ∈ `renommer` | `deplacer` | `creer_dossier` | `ecrire_index` | `publier` | `manuel`.
- `classe` ∈ `""` | `personnelle` | `entreprise` | `a_demander`. Une ligne `a_demander` ne s'applique pas avant la réponse ; la skill réécrit la classe puis la ligne.
- `partage` vaut `true` dès que `de` ou `vers` est sous une racine de `collecte.partagees`.
- `manuel` : `de` et `vers` relèvent de deux racines déclarées différentes. Jamais exécuté par le script.
- Ordre des `operations` : déterministe (tri par racine, puis chemin d'origine). Deux `--proposer` sur le même arbre et la même config rendent le même fichier, `genere_le` excepté.
- Aucun champ `contenu` ; aucun texte extrait au-delà du titre proposé dans `vers`.

## 4. `_cortex/03-rangement-journal.jsonl`

Une ligne par geste tenté, ajoutée, jamais réécrite :

```json
{"id": "r001", "geste": "renommer", "de": "~/…/Nouveau document (3).docx", "vers": "~/…/Accueil d'un nouveau client - 2026-03-12.docx", "taille": 48213, "mtime": 1741773600.0, "resultat": "fait", "erreur": "", "renforce": false, "fait_le": "2026-10-04T15:12:03"}
```

`resultat` ∈ `fait` | `echec` | `annule`. Une annulation ajoute une ligne `annule` pour l'`id`, elle n'efface pas la ligne `fait`. Pour `ecrire_index` et `publier`, `taille` et un champ `sha256` portent l'empreinte du fichier écrit par Cortex.

## 5. `range.py` : interface

```
range.py --atelier <_cortex> --proposer
range.py --atelier <_cortex> --appliquer --ids r001,r003 [--renforce]
range.py --atelier <_cortex> --verifier
range.py --atelier <_cortex> --annuler [--ids r003]
range.py --atelier <_cortex> --publier <fichier SKILL.md de l'atelier> --nom <assistant> --renforce
range.py --autotest
```

Codes de sortie : `0` fait ; `1` erreur ou écart constaté ; `2` usage ; `3` garde levée, rien n'a bougé.

Gardes, chacune testée par l'auto-test et par la recette :
- G1. Destination existante : code 3, rien ne bouge. Testée juste avant le geste, sur tous les systèmes.
- G2. Ligne `partage: true` sans `--renforce` : code 3.
- G3. Ligne `manuel`, ou `de` et `vers` sous deux racines différentes : code 3.
- G4. Chemin hors des racines déclarées (après résolution des liens symboliques) : code 3.
- G5. Origine changée depuis la proposition (taille ou date) : code 3, la ligne se repropose.
- G6. Fichier « en ligne seulement » : jamais ouvert ni haché ; seuls ses métadonnées et son nom se lisent.
- G7. `AGENTS.md` présent sans le marqueur `<!-- cortex-3b-rangement: index -->` : code 3, la skill montre l'écart et demande.
- G8. `classe: a_demander` : code 3.
- G9. Plafond `sante.max_gestes_rangement` : la proposition s'arrête, `bornes.depassement: true`, `ecartes` compté.

Interdits dans le code : `os.remove`, `os.unlink`, `shutil.rmtree`, `shutil.copy*`, `shutil.move`, `os.replace`, `os.chdir`. Seules exceptions, à l'annulation uniquement : `os.rmdir` d'un dossier créé par Cortex et resté vide ; retrait d'un fichier écrit par Cortex dont le `sha256` n'a pas changé depuis le journal.

`--verifier` relit le journal : pour chaque `fait` non annulé, `vers` existe avec la même taille et la même date, `de` n'existe plus (sauf `creer_dossier`, `ecrire_index`, `publier`). Il constate aussi les gestes `manuel` : quand `vers` existe et que `de` n'existe plus, il ajoute au journal une ligne `fait` avec `renforce: true` ; sinon la ligne reste en attente et s'affiche comme telle.

## 6. Nomenclature

Détail dans `skills/cortex-3b-rangement/references/nomenclature.md`. Le contrat fixe :
- Nom illisible : nom par défaut d'un logiciel (`Nouveau document`, `Sans titre`, `Untitled`, `Document1`, `Classeur1`), sortie d'appareil (`Scan_0001`, `IMG_1234`, `DSC…`), suffixe de copie ou de version (`(1)`, `copie de`, `final`, `def`, `v2` sans objet), nom fait de chiffres seuls.
- Nom parlant et daté : `<Objet en clair> - AAAA-MM-JJ.<ext>`. La date est celle de la version (dans le nom d'origine s'il en porte une, sinon la date de modification). L'extension ne change jamais.
- Caractères refusés, pour Windows : `/ \ : * ? " < > |`, espace ou point final ; 120 caractères au plus.
- Jamais renommé ni déplacé : un fichier caché, un dossier qui est un dépôt git ou s'y trouve, un paquet d'application, un vault Obsidian (`.obsidian/`), l'atelier, le vault.
- Le vocabulaire d'un domaine décidé au maillon 3 sert au nom quand il s'applique ; aucun préfixe de code imposé.

## 7. Index et notes

`AGENTS.md` à la racine du référentiel :

```markdown
# Dossier commun de <Organisation>

Ce dossier porte les documents de référence de l'organisation : procédures, charte graphique, signatures, modèles, assistants. Toute IA qui travaille pour l'organisation lit ce sommaire avant de répondre sur l'un de ces sujets, puis le document lui-même.

<!-- cortex-3b-rangement: index 2026-10-04 -->

## Documents

| Document | Objet | Propriétaire | Date |
|---|---|---|---|
| [Facturation d'une affaire - 2025-11-04.docx](Procédures/Facturation%20d'une%20affaire%20-%202025-11-04.docx) | De la commande signée à la facture envoyée | Non renseigné | 2025-11-04 |

## Assistants

| Assistant | Ce qu'il fait | Fichier |
|---|---|---|
| lecteur-de-baux | Relève échéances, loyers et clauses d'un bail | [SKILL.md](assistants/lecteur-de-baux/SKILL.md) |

## Règles
- Une procédure par fichier ; le nom dit l'objet et la date de version.
- Une version nouvelle remplace l'ancienne au même endroit ; l'ancienne va dans `Archives/`.
```

Note du vault, `50 - Ressources/Référentiel commun.md`, écrite par le maillon 5 quand `referentiel.etat` vaut `existant`, par `federe.py` dans le commun :

```yaml
---
type: ressource
ressource: referentiel
chemin: "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel"
index: "AGENTS.md"
visibilite: commun
---
```

Corps : dix lignes au plus, ce que le dossier contient, la règle « lire le sommaire d'abord », un lien vers `00 - Centre` et vers chaque domaine concerné (pas d'orphelin).

Procédure personnelle : `50 - Ressources/Procédures/<Objet>.md`, `type: ressource`, `ressource: procedure`, `source_path` en forme `~`, résumé de dix lignes au plus, lien vers son domaine. Aucune note par procédure d'entreprise.

Gabarit `CLAUDE.md` du vault : le marqueur `{{REFERENTIEL}}` devient le chemin en forme `~` ; sans référentiel, la règle se remplace par « Aucun dossier commun déclaré. » Aucun `{{…}}` ne survit au scaffold.

## 8. `etat.py`

Entrée nouvelle entre 3 et 4 : numéro `"3b"`, maillon `cortex-3b-rangement`, nom « Rangement », artefact `03-rangement.md`. `etat.json.etapes` compte dix entrées. Phrase : « rangeons mes dossiers ».

| Situation | État de 3b | Phrase suivante après le maillon 3 |
|---|---|---|
| `03-rangement.md` absent | `a_faire` | « rangeons mes dossiers » |
| `statut: refuse` ou `rien_a_ranger` | `arbitre`, raison écrite | « construis mon second cerveau » |
| journal avec des `fait` et des lignes acceptées non faites | `en_cours` | « rangeons mes dossiers » |
| `statut: applique` | `faite` | « construis mon second cerveau » |

Le maillon 4 refuse de construire tant que 3b vaut `en_cours`, et le dit dans les mots de la personne. `03-rangement.md` absent ne bloque pas le maillon 4.

## Invariants

- I-R1. Le nombre de fichiers de la personne sous les racines est le même avant et après `--appliquer`, et après `--annuler`. Seuls s'ajoutent un dossier créé ou un `AGENTS.md`.
- I-R2. Appliquer puis annuler rend un arbre identique : chemins, tailles, dates de modification.
- I-R3. Aucun octet de fichier de la personne n'est lu pour vérifier un geste.
- I-R4. Aucune écriture dans une base en ligne.
- I-R5. Aucune procédure dans `50 - Ressources/Structurants/`.
- I-R6. Zéro chemin absolu, zéro marque, dans tout ce qui est livré (contrôles existants de la recette).

## Amendements du chef d'orchestre (2026-10-04, questions de la lane)

- A1. Après un rangement appliqué, la skill 3b rejoue `scan.py` sur le même `01-inventaire.json`, sans modifier `scan.py` ; le rejeu garde `mail`, `bases`, `resume` et `preuve_de` par `source_id`. Le maillon 5 lit le journal pour traduire tout chemin ancien cité par `02-ontologie.md` ou `00-cadrage.md`.
- A2. Étape 3b absente alors qu'un artefact aval existe (`04-ingest.md` et suivants) : `arbitre`, raison « passée sans rangement ».
- A3. L'accord sur une ligne s'inscrit dans le frontmatter de `03-rangement.md` (`acceptees: [...]`) au moment de `--appliquer` ; c'est ce qui rend visible « acceptée non faite ».
- A4. Une ligne `manuel` n'entre jamais dans `acceptees`. Un geste manuel en attente ne bloque pas le maillon 4 ; le maillon 5 ne crée aucune note-pointeur pour une source qui en porte un, il l'inscrit dans `04-ingest.md` comme « en attente de déplacement ». Une fois le geste constaté par `--verifier`, la source reçoit sa note (contrôle de recette, cas positif et négatif).
- A5. `--annuler --ids` sur une ligne acceptée jamais faite la retire, par une ligne `annule` au journal.
- Suivi hors périmètre : le rejeu de `scan.py` relance l'extraction des candidats structurants, y compris sur un fichier en ligne seulement. Défaut préexistant de `scan.py`, noté au rapport, non corrigé.
- A6. Arbitrage après la livraison : `process` dans `donnees.structurants` d'une config existante n'est plus une erreur. `cortex_config.py` l'accepte avec l'avertissement « type 'process' retiré en 2.3.0, ignoré » et l'exclut de la liste effective ; le cadrage et `config.example.yaml` ne l'écrivent plus ; `copie_structurant.py --type process` refuse. Motif : les vaults livrés avant 2.3.0 portent `process` et tomberaient au lint.
- A7. Après l'audit : `--verifier` constate un geste manuel quand `vers` existe, que `de` a disparu et que la taille est celle de la proposition ; la date de modification n'est pas comparée, un déplacement par l'interface d'un outil peut la changer.
- A8. Après la reprise 1 : la note `50 - Ressources/Référentiel commun.md` du vault est écrite par l'installation (`scaffold.py`) dès que `referentiel.etat` vaut `existant` ; le maillon 5 vérifie qu'elle existe au lieu de l'écrire. Le commun fédéré la reçoit toujours de `federe.py`.
