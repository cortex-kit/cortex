# Rapport de la lane rangement (Cortex 2.3.0)

Branche `lane/rangement`, worktree `~/Dev/cortex--rangement`, base `cf5912a` (2.2.1) plus les deux commits du chef d'orchestre sur le pack (`eb276bd`, `ce062ca`). Rien n'est fusionné, poussé ni tagué ; `.claude-plugin/` est intact.

## Recette

| | Contrôles | Sortie |
|---|---|---|
| Avant la lane (`ce062ca`) | 154 passés, 0 en échec | 0 |
| Après la lane (`76ce831`) | 191 passés, 0 en échec | 0 |

Le critère C11 (36 contrôles) couvre le rangement ; C1, C2 et C10 passent de neuf à dix étapes.

## Fait

| Tâche (05-execution) | Commit |
|---|---|
| 1. `range.py` : proposer, appliquer, vérifier, annuler, publier, gardes G1 à G9, auto-test | `00edd7f` |
| 2. `references/nomenclature.md` et gabarit `AGENTS.md` | `00edd7f` |
| 3. `SKILL.md` de `cortex-3b-rangement` | `00edd7f` |
| 4. Maillon 1, profils, `cortex_config.py`, `config.example.yaml` | `5b156e3` |
| 5. `etat.py` à dix étapes, notice, fin du maillon 3, garde du maillon 4 | `5210b6a` (prose), `18550be` (garde dans `scaffold.py`) |
| 6. Maillon 5 et `copie_structurant.py` | `8f5547e` |
| 7. Gabarit du vault et `scaffold.py` (`{{REFERENTIEL}}`) | `18550be` |
| 8. Maillon 6 | `180c3b2` |
| 9. Maillon 8 et `federe.py` | `3a53f7a` |
| 10. Maillon 7 | `67bd234` |
| 11. Doctrine §12, §5, §9 | `9b2e8a0` |
| 12. Fixtures et `parcours_blanc.py` | `29c30f3` |
| 13. Notice vierge régénérée (README inchangé : sa source ne cite pas les phrases d'étape) | `fd1beec` |
| Reprise après vérification | `787587b`, `76ce831` |

Amendements du chef d'orchestre appliqués : A1 à A5 de `04-contrat.md` (fin du fichier), sans les recopier ici.

## Écarts au contrat et leur motif

- **Extensions d'interface de `range.py`** (contrat §5) : `--classer`, `--nommer`, `--chemins`, `--clore applique|refuse`, `--referentiel` (sur `--proposer`), `--proprietaire` (sur `--appliquer`). Motif : la skill porte la conduite, le script porte les gardes ; sans elles, la réécriture d'une ligne `a_demander`, le nom donné par la personne, le statut final et les propriétaires de l'index auraient été des éditions à la main de fichiers que le script relit. `--clore applique` refuse tant qu'une ligne acceptée n'est pas faite, et inscrit le dossier commun créé dans `config.yaml` (`referentiel.etat: existant`, chemin `~`).
- **Champs ajoutés aux opérations de `03-rangement.json`** (contrat §3) : `taille` et `mtime` de l'origine. G5 (« origine changée depuis la proposition ») ne se teste pas sans eux.
- **Journal** (contrat §4) : `creer_dossier` porte `taille: 0` ; `ecrire_index` porte `cree` (vrai si Cortex a créé le fichier, condition de son retrait à l'annulation, T4) ; `publier` porte `dossiers_crees`, `index_cree`, `index_sha256`. Une ligne `annule` de retrait (A5) a `geste: ""`. Un `annule` qui laisse un fichier en place le dit dans `erreur` (« sommaire modifié depuis son écriture : laissé tel quel »).
- **Titre d'un document** : lu en stdlib (première ligne d'un texte, premier paragraphe d'un `.docx` par `zipfile`, objet d'un `.eml`), pas par `markitdown`. Motif : hors ligne, déterministe, sans conversion ; le backlog technique le citait comme possibilité, pas comme obligation. Un `.pdf` ou un `.xlsx` prend le nom de son dossier.
- **Doublon probable** : signalé quand un même nom à la même taille se trouve à exactement deux endroits (« deux endroits », contrat 2.3 et produit). Au-delà, c'est une convention de nommage (`devis.pdf` dans chaque dossier d'affaire), pas une copie.
- **Ce que le script ne propose pas** : renommer un dossier, sortir des fichiers d'un dossier « Divers » vers un domaine. Ces gestes demandent un jugement que la proposition déterministe ne porte pas ; la nomenclature le dit. Les procédures, elles, se rangent.
- **Comparaison d'arbre (I-R2)** : chemins, tailles et dates des fichiers, liste des dossiers. La date d'un dossier bouge à chaque renommage dans le dossier ; elle n'est pas comparée.
- **État `propose` sans ligne en suspens** : `a_faire` (ou `arbitre` « passée sans rangement » si un artefact aval existe, A2). Le tableau du contrat §8 ne nomme que les quatre cas ; celui-ci ne bloque pas le maillon 4.
- **Mise à jour d'un vault déjà livré** : `cortex_config.valider_installable` refuse désormais `process` dans `donnees.structurants` (T5). Le lint d'un vault installé avant 2.3.0 lit cette fonction ; après un `--outillage-seul`, son `config.yaml` (qui porte `process`) passe en `contrat_config_invalide`. Voir les suivis.

- **L'installation écrit dans l'atelier** (décision de lane, à valider par le chef d'orchestre) : après une construction réussie, `scaffold.py` inscrit `construit_le` dans `_cortex/03-rangement.md`, et `statut: passee` (arbitré « passée sans rangement ») si le rangement n'a pas été conclu ; il ne le fait que dans un atelier (présence de `02-ontologie.md`). Motif : sans trace de la construction, `etat.py` proposait « rangeons mes dossiers » juste après le maillon 4 et `range.py` aurait renommé des fichiers que le vault venait de pointer (D3). `range.py` refuse ensuite `--proposer`, `--appliquer`, `--classer`, `--nommer`, `--clore` et `--annuler` (code 3 ; 02-backlog : « défaire, à tout moment avant la construction ») ; `--publier` (maillon 6), `--verifier` et `--chemins` restent ouverts. Le trou en 03 de la doctrine §4 reste vrai pour l'étape 4 elle-même.
- **Config du dossier commun journalisée** : `--clore applique` inscrit `referentiel.etat: existant` par une ligne de journal `c001` (`geste: referentiel`, avec la valeur d'avant) ; l'annulation la rend. Sans cela, un rangement défait laissait au vault un sommaire fantôme.
- **Statut et signalements ajoutés** : `statut: passee` dans `03-rangement.md` ; signalements `dossier_commun_a_choisir` (plusieurs dossiers partagés), `racine_dans_un_depot`, `titre_illisible`, `index_etranger`, `racine_absente`.
- **Codes de sortie** : une commande mal formée rend 2 ; un journal ou un inventaire illisible rend 1 (erreur), jamais 2. `scaffold.py` refuse aussi de construire quand l'étape 3b est illisible.
- **A4 vit dans la prose du maillon 5** : le remplissage écrit ses notes par conduite, sans code d'écriture où loger la garde. Le code fournit la décision (`range.py --chemins`, fonction `note_autorisee`), la recette la prouve dans les deux sens ; l'appel reste une consigne du SKILL.md du maillon 5.

## Valeurs attendues dans des fichiers hors possession

- `.claude-plugin/plugin.json` : `"version": "2.3.0"` (actuellement `2.2.1`).
- `.claude-plugin/marketplace.json`, description : « … inventaire, ontologie, rangement, installation, peuplement, agents, passation, fédération. »
- `chantiers/cortex-v2/04-contrat.md` §5 et §11 : « neuf étapes » devient « dix étapes, dont l'étape facultative 3b » (le contrat 2.3 §8 l'étend sans le réécrire ; à porter si le chef d'orchestre veut un seul texte de référence).
- `notice/LISEZ-MOI.html` affiche « paquet 2.0.0 », comme avant la lane : la version affichée suit le geste de fabrication du chef d'orchestre.

## Vérification

Deux passes à contexte frais (sous-agents), puis une chasse aux échecs silencieux sur les six scripts. Défauts relevés et suite donnée :

| Défaut | Suite |
|---|---|
| `rapport.md` absent, Statut du README (la passe a tourné avant leur écriture) | écrits |
| `os.rename` écrase sous POSIX si la destination apparaît entre la garde et le geste | `renommer_exclusif` (macOS `renamex_np RENAME_EXCL`, Linux `renameat2 RENAME_NOREPLACE`, Windows refuse déjà) ; auto-test dédié |
| une racine dans un dépôt git est rangée | racine et parents testés (`.git`, `.obsidian`), signalement `racine_dans_un_depot` |
| racines imbriquées : G2 contourné, lignes en double | « partagé » = sous n'importe quelle racine partagée ; une racine interne se parcourt une fois |
| un sommaire marqué, complété à la main, perdu à l'annulation | le texte d'avant part au journal et revient mot pour mot |
| annuler le lendemain d'une publication échoue (marque datée) | comparaison au dernier sommaire écrit par Cortex, réécritures d'annulation comprises |
| ranger après la construction reste possible | `construit_le` posé par l'installation, gardes de `range.py` |
| dossier commun créé sans sommaire : config non mise à jour | `--clore applique` l'inscrit dès qu'un geste fait y a posé quelque chose |
| G3 (deux racines) et G7 non éprouvées par la ligne de commande | cas ajoutés à l'auto-test ; perturbations : l'auto-test rougit |
| publication en échec : restes non journalisés, « rien n'a bougé » faux | `restes` au journal et dans le message, `Garde` rattrapée |
| inventaire ou titre illisibles avalés | erreur nommée (code 1) ; signalement `titre_illisible` |
| fichiers du dossier commun lus sans test « en ligne seulement » | `lire_index` refuse un sommaire présent seulement en ligne ; description d'un assistant non lue |
| un dossier commun créé au rangement n'atteint pas `federation.yaml` | §9 de la skill : `federe.py --inscrire … --referentiel` en groupe |
| la note `Référentiel commun` du commun ne lie que le Centre | liens vers les domaines du commun |
| skill : `dossier_commun_absent` émis aussi avec plusieurs dossiers partagés ; noms de dossier et §8 | type `dossier_commun_a_choisir` ; un nom affiché est une donnée |
| étape 0 (domaines signés) en prose seulement | `--proposer` la vérifie (code 3) |

Seconde passe sur `787587b` : cinq défauts corrigés, deux en partie, un nouveau. Repris dans `76ce831` :

| Défaut | Suite |
|---|---|
| un dossier partagé qui est un dépôt git recevait encore le dossier commun et son sommaire | aucun dossier commun proposé dans un dépôt ; `controler` refuse tout geste dans un dépôt (auto-test et perturbation) |
| publication d'un SKILL.md illisible : fichier vide et dossiers laissés sans trace | la source se lit avant tout geste ; illisible, rien ne s'écrit (code 2) |
| après un rangement défait, la config gardait `referentiel: existant` vers un dossier supprimé | la mise à jour de la config se journalise et se défait |
| `--annuler` restait ouvert après la construction | fermé (code 3), comme le reste |
| G3, cas `manuel` seul, non éprouvé | l'auto-test vérifie le message propre au geste manuel ; perturbation : il rougit |

Rien de ce que les deux passes ont essayé n'a supprimé, écrasé ni copié un fichier de la personne.

## Contrôle manuel consigné

Session `claude -p --plugin-dir <dépôt>` ouverte sur un atelier de recette (fixture dirigeant et son dossier partagé, maillons 0 à 3 valides), 2026-10-04.

- Tour 1, « rangeons mes dossiers » : la skill `cortex-3b-rangement` se déclenche, lance la proposition, annonce « 11 changements possibles : 6 noms illisibles, 2 procédures à regrouper dans un dossier commun qui n'existe pas encore, 3 changements pour le créer avec son sommaire », signale le doublon `tarifs.xlsx` sans y toucher, puis affiche le premier lot de quatre lignes en entier (avant, après, raison) et demande de cocher. Aucune permission refusée.
- Tour 2, « je refuse tout » : `03-rangement.md` porte `statut: refuse`, `raison: "refusé"` ; `etat.py` rend l'étape 3b `arbitre` « refusé » et la phrase suivante « construis mon second cerveau ». Aucun fichier de la fixture n'a bougé.
- Écart vu : en mode `-p`, la question à cases ne s'affiche pas ; la skill l'a dit et demandé les numéros en texte. Ce mode n'existe pas dans une session interactive.

## Garde prouvée mordante

G1 désactivée dans une copie jetable de `range.py` (`if False and …` sur la garde de `controler`) : l'auto-test rougit. Sortie avant la reprise :

```
AssertionError: (['--appliquer', '--ids', 'r001'], 0, "fait  r001 renommer …/Nouveau document (3).md -> …/Accueil d'un nouveau client - 2026-03-12.md\n", '')
```

Sous macOS, sans la garde, `os.rename` avait écrasé la destination occupée et sorti 0. Depuis la reprise (`renommer_exclusif`, voir « Vérification »), la même perturbation donne :

```
AssertionError: (['--appliquer', '--ids', 'r001'], 1, '', '[échec] r001 : [Errno 17] File exists: "…/Accueil d\'un nouveau client - 2026-03-12.md". Le lot s\'arrête ; …')
```

Le renommage refuse lui-même la destination occupée : deux barrières au lieu d'une. Le témoin tourne aussi dans la recette (C11).

## Suivis notés, non traités

- **Rejeu du scan après rangement** (A1) : `scan.py` relance l'extraction des candidats structurants, y compris sur un fichier présent seulement en ligne, qu'il téléchargerait. Défaut préexistant de `scan.py`, hors possession.
- **Vaults livrés avant 2.3.0** : leur `config.yaml` porte `process` dans `structurants`. À la mise à jour de l'outillage, retirer `process` de leur config (ou faire tolérer la clé par le lint jusqu'à une migration). Décision du chef d'orchestre.
- **Renommage exclusif hors macOS et Linux** : sous Windows, `os.rename` refuse déjà une destination existante ; sur une autre plateforme POSIX sans `renamex_np` ni `renameat2`, la garde rejouée juste avant le geste reste la seule barrière (fenêtre de deux appels système).
- **Rangement après la remise** : hors périmètre (01-cadrage). Défaire après la construction casserait les liens du vault ; la skill le dit avant d'agir.
