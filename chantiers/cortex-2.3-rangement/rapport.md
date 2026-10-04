# Rapport de la lane rangement (Cortex 2.3.0)

Branche `lane/rangement`, worktree `~/Dev/cortex--rangement`, base `cf5912a` (2.2.1) plus les deux commits du chef d'orchestre sur le pack (`eb276bd`, `ce062ca`). Rien n'est fusionné, poussé ni tagué ; `.claude-plugin/` est intact.

## Recette

| | Contrôles | Sortie |
|---|---|---|
| Avant la lane (`ce062ca`) | 154 passés, 0 en échec | 0 |
| Après la lane (`2efc3e4`) | 192 passés, 0 en échec | 0 |
| Après la reprise 1 (`d6c7b2f`) | 197 passés, 0 en échec | 0 |
| Après la reprise 2 (`b898688`) | 199 passés, 0 en échec | 0 |

Le critère C11 (42 contrôles après la reprise 1) couvre le rangement ; C1, C2 et C10 passent de neuf à dix étapes.

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
| Arbitrage du chef d'orchestre (T5 amendé, A4 en étape, doctrine §4) | `2efc3e4` |

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
- **T5 amendé par le chef d'orchestre (2026-10-04)** : `process` dans `donnees.structurants` n'est plus refusé par `cortex_config.py`. Une config antérieure à 2.3.0 qui le porte reste installable et verte au lint ; `avertissements()` dit « type retiré en 2.3.0, ignoré » (imprimé par `scaffold.py` et par `cortex_config.py <config>`), `structurants_effectifs()` l'exclut. Le refus vit là où la copie se fait : `copie_structurant.py --type process`. Le cadrage et `config.example.yaml` ne l'écrivent plus. La recette porte les deux faces (config 2.2 installée et lint à 0 avec l'avertissement ; copie d'une procédure refusée).

- **L'installation écrit dans l'atelier** (décision de lane, à valider par le chef d'orchestre) : après une construction réussie, `scaffold.py` inscrit `construit_le` dans `_cortex/03-rangement.md`, et `statut: passee` (arbitré « passée sans rangement ») si le rangement n'a pas été conclu ; il ne le fait que dans un atelier (présence de `02-ontologie.md`). Motif : sans trace de la construction, `etat.py` proposait « rangeons mes dossiers » juste après le maillon 4 et `range.py` aurait renommé des fichiers que le vault venait de pointer (D3). `range.py` refuse ensuite `--proposer`, `--appliquer`, `--classer`, `--nommer`, `--clore` et `--annuler` (code 3 ; 02-backlog : « défaire, à tout moment avant la construction ») ; `--publier` (maillon 6), `--verifier` et `--chemins` restent ouverts. Le trou en 03 de la doctrine §4 reste vrai pour l'étape 4 elle-même.
- **Config du dossier commun journalisée** : `--clore applique` inscrit `referentiel.etat: existant` par une ligne de journal `c001` (`geste: referentiel`, avec la valeur d'avant) ; l'annulation la rend. Sans cela, un rangement défait laissait au vault un sommaire fantôme.
- **Statut et signalements ajoutés** : `statut: passee` dans `03-rangement.md` ; signalements `dossier_commun_a_choisir` (plusieurs dossiers partagés), `racine_dans_un_depot`, `titre_illisible`, `index_etranger`, `racine_absente`.
- **Codes de sortie** : une commande mal formée rend 2 ; un journal ou un inventaire illisible rend 1 (erreur), jamais 2. `scaffold.py` refuse aussi de construire quand l'étape 3b est illisible.
- **A4, accepté pour la 2.3.0** : le remplissage écrit ses notes par conduite. L'appel est une étape numérotée du SKILL.md du maillon 5, avant chaque note-pointeur : `range.py --atelier <_cortex> --autorise "<chemin>"` (0 et le chemin rangé, ou 3 « en attente de déplacement »). La recette et l'auto-test prouvent la décision dans les deux sens.

## Valeurs attendues dans des fichiers hors possession

- `.claude-plugin/plugin.json` : `"version": "2.3.0"` (actuellement `2.2.1`).
- `.claude-plugin/marketplace.json`, description : « … inventaire, ontologie, rangement, installation, peuplement, agents, passation, fédération. »
- `chantiers/cortex-v2/04-contrat.md` §5 et §11 : « neuf étapes » devient « dix étapes, dont l'étape facultative 3b » (le contrat 2.3 §8 l'étend sans le réécrire ; à porter si le chef d'orchestre veut un seul texte de référence).
- Ces trois valeurs sont portées par le chef d'orchestre à la fusion.
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
- **Garde de lint sur A4** : une note-pointeur écrite vers une source qui attend un déplacement manuel n'est vue par aucun contrôle du vault. Prévue en 2.3.x, dans `lint_sante.py`, hors de cette lane.
- **Renommage exclusif hors macOS et Linux** : sous Windows, `os.rename` refuse déjà une destination existante ; sur une autre plateforme POSIX sans `renamex_np` ni `renameat2`, la garde rejouée juste avant le geste reste la seule barrière (fenêtre de deux appels système).
- **Rangement après la remise** : hors périmètre (01-cadrage). Défaire après la construction casserait les liens du vault ; la skill le dit avant d'agir.

## Reprise 1

Après l'audit à froid (`audit.md`, `a10faaa`) et les amendements A6 et A7. Recette à 197 contrôles, sortie 0 (C11 : 42). Chaque garde ajoutée ou éprouvée ici a sa perturbation : neutralisée dans une copie jetable, l'auto-test ou la recette rougit.

| Finding | Correction | Commit |
|---|---|---|
| B1, sommaire incomplet | La liste range la création du dossier commun avant toute ligne qui en dépend, le sommaire en dernier. Le sommaire se régénère après chaque lot qui touche le dossier commun et à `--clore` (lignes `i…` au journal, défaites comme les autres). Fixture à cinq procédures d'entreprise ; la recette passe la liste lot par lot comme la skill, avec une procédure acceptée après le sommaire, et exige les cinq. Perturbation du rafraîchissement : rouge | `a54e392`, `d6c7b2f` |
| M1, rangement non clos effacé par la construction | Des gestes faits sans clôture : `etat.py` rend 3b `en_cours` (« appliqué, pas encore conclu »), le maillon 4 refuse avec « rangeons mes dossiers ». `marquer_construction` n'écrit jamais `passee` quand le journal porte un geste fait. `--clore` inscrit `referentiel.etat` et `referentiel.chemin`. Contrôle de recette sur le scénario x1 | `a54e392` |
| M2, clôture appliquée en partie | cas d'auto-test (code 3) ; perturbation : rouge | `a54e392` |
| M3, G6 sur `lire_index` | cas d'auto-test : sommaire simulé en ligne, `--publier` en code 3 ; perturbation : rouge | `a54e392` |
| m2, création exclusive et publication en double | `creer_exclusif` testé sur un fichier existant ; `--publier` deux fois : G1, code 3 ; perturbations : rouge | `a54e392` |
| M4, assertion négative vide | L'installation écrit `50 - Ressources/Référentiel commun.md` quand le dossier commun existe (le maillon 5 la vérifie). Sur le même vault de recette : la note existe, aucune note ne porte une des cinq procédures, lint à 0 ; témoin sur un vault jetable qui en porte une | `a54e392` |
| M6, m10, causes agrégées | Annulation d'une publication : trois messages (disparu, en ligne seulement, modifié). Un `.docx` sans corps donne `titre_illisible`. `--publier` distingue ses trois erreurs d'usage. Un `stat` refusé remonte au lieu de devenir « local » ou « changé » (auto-test). Le repli de `renommer_exclusif` sans libc le dit sur la sortie d'erreur | `a54e392` |
| m1, grep des appels interdits | La recette voit aussi `Path.unlink`, `Path.rename`, `Path.replace`, `os.rename` ; chaque ligne trouvée est une exception commentée ou un geste de l'auto-test ; témoin à quatre appels sur un jetable, `str.replace` exclu | `a54e392` |
| m3, notice à neuf étapes | `notice.md` décrit dix étapes, rangement compris ; `notice/LISEZ-MOI.html` régénéré | `a54e392`, clôture |
| m4, G2 figé | `partage` se recalcule depuis `collecte.partagees` au moment du geste ; cas d'auto-test | `a54e392` |
| m5, « Mon … » en dossier partagé | classe `a_demander` ; cas d'auto-test | `a54e392` |
| m6, « JSON » | ajouté à la liste des mots du SKILL | `a54e392` |
| m7, troncature | au-delà du plafond, la création du dossier commun et le sommaire restent, les dernières lignes ordinaires partent | `a54e392` |
| m8, A7 | `--verifier` constate un geste manuel sur la taille de la proposition, sans la date ; auto-test dans les deux sens | `a54e392` |
| m11, commande du maillon 6 | affichée entière, sur deux lignes avec la barre oblique | `a54e392` |
| m12, atelier de `scaffold.py` | l'atelier est le dossier de `config.yaml` qui porte `02-ontologie.md` ; sinon le script le dit et n'inscrit rien | `a54e392` |
| M5, m13 | réglés côté pack (A6) | — |

Écart nouveau, déclaré : la note `Référentiel commun` du vault est écrite par l'installation, plus par le maillon 5 seul (contrat §7). Motif : elle ne dépend que de la config, et c'est ce qui donne à l'assertion « aucune note par procédure d'entreprise » un objet vérifiable.

### m9, défauts préexistants, en suivi sans correctif

- `etat.py` : `_frontmatter` rend « illisible » sans raison ; `generer` jette le message d'une config illisible.
- `copie_structurant.py` : `texte_de` agrège binaire absent, délai dépassé et échec de conversion, et jette `stderr`.
- `scaffold.py` : une couleur de domaine invalide est grisée sans avertissement.
- `federe.py` : un `index.json` mal formé lève un `KeyError` brut.

## Reprise 2

Après le second audit (`audit-2.md`, `e7d098c`) et l'amendement A8. Recette à 199 contrôles, sortie 0 (C11 : 44). Pour chaque cas ajouté, la garde ou le chemin qu'il vise a été neutralisé dans le code : l'auto-test ou la recette rougit (N1, N2, N3, N4, N5 ×2, N6, N10, N12 : rouges).

| Finding | Correction | Commit |
|---|---|---|
| N1, échec du rafraîchissement sorti en code 3 | Les deux appels (après un lot, à la clôture) passent par `rafraichir_ou_dire` : un échec se journalise sous un id `i…` en `echec` et sort 1, avec « … sont faits ; seul le sommaire du dossier commun n'a pas suivi ». Le code 3 garde le sens « rien n'a bougé ». Auto-test : marque retirée entre deux lots, code 1, geste fait, ligne d'échec au journal | `b8969cd` |
| N2, rafraîchissement de la clôture non éprouvé | Recette : la procédure déplacée à la main vers le dossier commun, constatée, est absente du sommaire avant la clôture et présente après | `b8969cd` |
| N3, empreinte avant retrait d'un assistant | Auto-test : assistant publié puis retouché, `--annuler --ids p…` rend 1, fichier intact | `b8969cd` |
| N4, priorité de la troncature | Auto-test au plafond 3 : la création du dossier commun et le sommaire restent, un renommage part | `b898688` |
| N5, branches non éprouvées | `etat.py` : liste proposée, rien de fait, suite faite : arbitré « passée sans rangement » ; témoin sans la suite. `scaffold.py` : `marquer_construction` n'écrit pas `passee` après un geste fait ; témoin sans geste | `b8969cd` |
| N6, annulation partielle | `--annuler --ids` qui touche le dossier commun rafraîchit le sommaire, journalisé `i…` ; auto-test | `b8969cd` |
| N7, absent et changé agrégés | `ecart_identite` : « a disparu » ou « a changé (taille ou date) » à G5, à `--verifier` et à l'annulation d'un déplacement | `b8969cd` |
| N8, contrôle manuel ancien | rejoué, voir ci-dessous | `b898688` (fixture actuelle) |
| N10, sommaire montré et écrit différents | `--montrer-index --ids <lot> [--proprietaire …]` imprime le texte exact que le lot écrira, sans rien écrire (projection des déplacements du lot). Le SKILL l'affiche en entier avant l'accord. Auto-test : texte montré égal au fichier écrit, arbre inchangé par la commande | `b8969cd` |
| N11, `AGENTS.md` dans le guide d'usage | « le sommaire pour les IA de ce dossier (ou, sans sommaire, le dossier lui-même) » | `b8969cd` |
| N12, sommaire refusé, procédures rangées | Le dossier commun reste inscrit. `CLAUDE.md` du vault et la note `Référentiel commun` ne renvoient à `AGENTS.md` que s'il existe ; sinon au dossier lui-même (`index: ""`). `parle` suit la même règle. Recette sur les deux faces | `b8969cd` |
| N13, dossier partagé ajouté sans validation | le SKILL exige `cortex_config.py <config>` avant tout geste, puis une nouvelle proposition | `b8969cd` |
| N9 | en suivi, ci-dessous | — |

### Contrôle manuel rejoué (N8)

`claude -p --plugin-dir <dépôt>` sur un atelier de recette tiré de la fixture actuelle (dirigeant et son dossier partagé, maillons 0 à 3 valides), 2026-10-04.

- Tour 1, « rangeons mes dossiers » : « 15 changements possibles : 6 noms illisibles à renommer, 6 procédures à regrouper dans un dossier commun, 3 lignes pour créer ce dossier commun et son sommaire pour les IA », doublon `tarifs.xlsx` signalé et laissé, puis le premier lot de quatre lignes en entier (avant, après, raison). Aucune permission refusée.
- Tour 2, « je refuse tout » : message de clôture du refus mot pour mot ; `03-rangement.md` en `statut: refuse`, `raison: "refusé"` ; `etat.py` : étape 3b arbitrée « refusé », phrase suivante « construis mon second cerveau » ; aucun fichier n'a bougé, aucun dossier commun créé.
- Limite du mode `-p` : les questions à cocher ne s'y affichent pas, la skill l'a dit et demandé les numéros en texte.

### Suivi

- **N9** : l'assertion « aucune note par procédure d'entreprise » porte sur le vault du maillon 4. Le maillon 5, seul à pouvoir en écrire, est conduit par la prose et n'a pas de code à exercer ; son contrôle viendra avec un outillage du remplissage (et avec la garde de lint prévue en 2.3.x).
