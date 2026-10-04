# Second audit à froid de la lane rangement (Cortex 2.3.0), après la reprise 1

Auditeur : Opus 5.5, effort high, session neuve. Date : 2026-10-04. Objet : worktree `~/Dev/cortex--rangement`, branche `lane/rangement`, HEAD `ea6977e` (code à `d6c7b2f`, pack amendé jusqu'à A8), base `2c1f289`. Aucun fichier du dépôt corrigé ; seul ce fichier est écrit. Les essais ont tourné dans le scratchpad, sur des copies (`git archive HEAD`) et sous un `HOME` factice pour les scénarios qui construisent un vault.

## Verdict

**Lane à reprendre, reprise courte.** Aucun bloquant. Les sept findings bloquant et majeurs de `audit.md` sont levés, preuve à l'appui (B1 et M1 reproduits puis rejoués : le sommaire liste les cinq procédures, la construction refuse un rangement non clos). Restent trois majeurs neufs, petits à corriger :

1. **N1** : après des gestes faits, un échec du rafraîchissement du sommaire sort en code 3 avec « Rien n'a bougé », alors que les fichiers ont bougé et que le journal les porte `fait`. Reproduit.
2. **N2** : le rafraîchissement du sommaire à la clôture n'est éprouvé par rien (perturbé, auto-test et recette restent verts), alors qu'il est le seul à faire entrer au sommaire une procédure déplacée à la main.
3. **N3** : la garde d'empreinte qui précède le retrait d'un assistant publié (`os.remove` dans le dossier partagé) n'est éprouvée par rien.

Aucun geste observé ne supprime, n'écrase ni ne copie un fichier de la personne. Sur 48 perturbations posées, 43 font rougir l'auto-test ou la recette ; les cinq vertes sont listées en 3bis.

## Ce que j'ai relancé moi-même

| Mesure | Résultat | Sur quoi la commande a répondu |
|---|---|---|
| `git status` | propre, branche `lane/rangement`, HEAD `ea6977e` | worktree |
| `git log --oneline 2c1f289..HEAD` | 23 commits ; les commits de pack (`eb276bd`, `ce062ca`, `a10faaa`, `ea6977e`) sont du chef d'orchestre | worktree |
| `git diff --stat 2c1f289..HEAD` | 39 fichiers, +3538 −125 ; aucun fichier de la liste « Ne pas toucher » | worktree |
| six `--autotest` | tous en 0, codes relevés sans pipe | scripts du worktree |
| `parcours_blanc.py` à HEAD | 197 passés, 0 en échec, sortie 0 ; C11 42/42 | worktree (`DEPOT` déduit de `__file__`, ligne 40), puis une copie `git archive HEAD` : même résultat |
| `parcours_blanc.py` à `2c1f289` | 154 passés, 0 en échec, sortie 0 | copie `git archive 2c1f289` |
| grep des appels interdits (06) | 2 lignes, `os.remove` lignes 1112 et 1163, commentées « exception 2 du contrat §5 » | `range.py` du worktree |
| témoin du grep | 2 lignes sur un jetable (`os.remove(`, `shutil.copy2(`) | fichier jetable |
| grep `cd` (06) | 0 ligne, sortie 1 ; témoin `cd ~/Documents` : 1 ligne | `cortex-3b-rangement/SKILL.md` |
| section Notice | sha256 identique (363 octets) ; témoin à un octet près : empreinte différente | deux SKILL.md |
| `cortex_config.valider_installable` | config 2.2 avec `process` : aucune erreur, avertissement « type 'process' retiré en 2.3.0, ignoré », liste effective sans `process` ; `partagees` hors racines : refusée ; dossier commun hors racine : refusé ; `config.example.yaml` : accepté | configs jetables |
| `copie_structurant.py --type process` | code 2, « une procedure ne se copie jamais » ; `--type contrat` même source : 0, copie écrite | vault jetable en régime copie |
| proposition sur la fixture dirigeant | 15 changements (6 renommages, 5 déplacements, 2 créations, 1 manuel, 1 sommaire), 5 lots | copie de la fixture hors dépôt |
| `silent-failure-hunter` sur les six scripts | 1 finding neuf de la lane (rejoint N1), 3 messages agrégés résiduels (N7), 4 défauts préexistants inchangés (notés au rapport) | worktree |

Les chiffres du rapport (154 avant, 192 après la lane, 197 après la reprise 1, C11 à 42) sont remesurés et justes. Un chiffre est daté : les « 11 changements » du contrôle manuel datent d'avant la reprise 1 ; la même fixture en donne 15 aujourd'hui (voir N8).

## Les findings de audit.md, un par un

| Finding | Statut | Preuve |
|---|---|---|
| **B1**, sommaire incomplet au-delà d'un lot | **Levé** | Scénario `x3` rejoué (cinq `Process <X>.md` dans `Commun/Divers`, lots appliqués dans l'ordre avec `--renforce`) : quatre lots en 0, `--clore applique` en 0, `AGENTS.md` liste les cinq procédures. Le tri place `creer_dossier` en tête et `ecrire_index` en dernier (`range.py:593`). Perturbations : tri sans priorité de création, rouge (auto-test et recette) ; rafraîchissement après lot retiré, rouge (recette, contrôle « il liste les cinq »). Le rafraîchissement à la clôture, lui, n'est pas éprouvé (N2) |
| **M1**, rangement non clos effacé par la construction | **Levé** | Scénario sous `HOME` factice : tous les gestes faits, `--verifier` à 0, pas de clôture : `scaffold.py` sort 2 avec « Le rangement de vos dossiers n'est pas conclu », aucun vault écrit ; `etat.py` rend 3b `en_cours` « appliqué, pas encore conclu ». Après `--clore applique` : `referentiel.etat: existant`, chemin `~/Commun/Référentiel`, construction en 0, `CLAUDE.md` du vault nomme le dossier commun, note `Référentiel commun.md` écrite, lint à 0. Perturbation de la branche M1 d'`etat.py` : rouge |
| **M2**, garde « appliqué en partie » de `--clore` | **Levé** | Neutralisée (`if False`) : auto-test rouge, recette rouge |
| **M3**, G6 dans `lire_index` | **Levé** | Neutralisée : auto-test rouge (cas `--publier` sur sommaire simulé en ligne, `range.py:1465`) |
| **M4**, assertion négative sans objet | **Levé en partie** | Côté vault : la positive (note `Référentiel commun` présente) porte sur le même vault que la négative, et un témoin jetable montre que la sonde trouve une note de procédure. Perturbation de `note_referentiel` : rouge. Reste que le vault contrôlé sort du maillon 4, qui n'écrit jamais de note de procédure ; le maillon 5, qui le pourrait, écrit par conduite et n'est pas exercé. Côté commun, `federe.py` ne recopie jamais `50 - Ressources` des exports : la négative y reste incapable de rougir. Résidu : mineur N9 |
| **M5**, pack contredit par le code sur T5 | **Levé** | A6 ajouté au contrat (`04-contrat.md`), T5 amendé (`01-cadrage.md`), §1 du contrat et critère de `06` réécrits, ligne `lint/SKILL.md` ajoutée à `03` (diff `a10faaa`). Comportement remesuré, voir plus haut |
| **M6**, causes agrégées dans le code de la lane | **Levé pour les deux lignes citées** | Annulation d'une publication : trois messages distincts (disparu, en ligne seulement, modifié), `range.py:1157-1162`. `.docx` sans corps : `titre_local` rend `None`, `proposer` signale `titre_illisible` (`range.py:504`) ; perturbation vers `""` : rouge. Résidu : la même agrégation « a changé ou disparu » vit encore aux lignes 911, 1062 et 1137 (mineur N7) |
| **m1**, angle mort du grep | **Levé dans la recette** | La recette cherche aussi `Path.unlink`, `Path.rename`, `Path.replace`, `os.rename` ; perturbation qui remplace `renommer_exclusif` par un `os.rename` brut : le grep de la recette rougit. La commande de `06` reste l'ancienne, plus étroite (pack, hors lane) |
| **m2**, création exclusive et double publication | **Levé** | `open(…, "x")` passé en `"w"` : rouge ; G1 de `publier` neutralisée : rouge |
| **m3**, notice à neuf étapes | **Levé** | `notice.md` ligne 29 « Les dix étapes », ligne 50 « 3 bis. Rangement » ; `notice/LISEZ-MOI.html` régénéré porte « 3 bis. Rangement » et « dix étapes » |
| **m4**, G2 figé | **Levé** | `controler` recalcule `partage` (`range.py:903`) ; perturbation : rouge |
| **m5**, « Mon … » en dossier partagé | **Levé** | `range.py:528` rend `a_demander` ; auto-test `range.py:1332` |
| **m6**, « JSON » absent des mots interdits | **Levé** | SKILL.md, section « Devant la personne » |
| **m7**, troncature qui sacrifie création et sommaire | **Levé dans le code, non éprouvé** | Reproduit avec un plafond de 5 : les deux créations, le sommaire, un renommage et un déplacement restent, 4 écartés déclarés. Perturbation qui retire la priorité : auto-test et recette verts (mineur N4) |
| **m8**, A7 | **Levé** | `range.py:1078` compare la taille, pas la date ; perturbation : rouge |
| **m9**, défauts préexistants absents du rapport | **Levé** | Rapport, section « m9, défauts préexistants, en suivi sans correctif » ; la chasse les retrouve tous, inchangés, hors des commits de la lane |
| **m10**, messages agrégés | **Levé** | Quatre `Usage` distincts dans `publier` (`range.py:999-1006`) ; un `stat` refusé remonte (perturbation `except OSError` : rouge) ; le repli sans libc écrit un avertissement (`range.py:870-872`) |
| **m11**, commande coupée au maillon 6 | **Levé** | Commande sur deux lignes avec la barre oblique (`cortex-6-agents-metier/SKILL.md`, §3 bis) |
| **m12**, atelier de `scaffold.py` | **Levé** | Message « Aucun atelier à côté de … : l'état du rangement n'est pas vérifié » quand `config.yaml` n'a pas `02-ontologie.md` à côté |
| **m13**, `lint/SKILL.md` hors tableau | **Levé** | Ligne ajoutée à `03-backlog-technique.md`. Même écart, neuf : `notice.md` (observation N12) |

## Critères de 06-verification.md, un par un

### Script et gardes

| Critère | Statut | Preuve |
|---|---|---|
| `range.py --autotest` rend 0 | PASS | sortie 0 |
| G1 à G9 dans les deux sens, code 3, arbre identique | PASS | chaque garde neutralisée fait rougir l'auto-test (tableau 3bis), y compris G6 dans `lire_index`, G7 dans `publier`, G9 sans troncature. Le helper `garde()` de l'auto-test compare `arbre()` avant et après (`range.py:1350-1354`) |
| I-R1 | PASS | auto-test `range.py:1425` ; recette C11 |
| I-R2 | PASS | auto-test et recette ; témoin `touch` de la recette ; perturbations d'annulation : rouge |
| Déterminisme | PASS | auto-test et recette ; perturbation par mélange aléatoire des candidats : rouge |
| Grep des appels interdits | PASS | deux lignes commentées ; témoin positif |

### Config, état, maillons

| Critère | Statut | Preuve |
|---|---|---|
| `cortex_config.py` (A6, refus hors racine et `partagees`, accepte l'exemple) | PASS | remesuré par `valider_installable`. Le lancement `cortex_config.py <config>` ne valide pas, il affiche : c'est son rôle préexistant, la validation vit dans `valider_installable` |
| `copie_structurant.py --type process` refusé, `contrat` réussit | PASS | remesuré, voir plus haut |
| `etat.py --autotest` couvre le §8 ; dix étapes | PASS | auto-test lignes 442 à 469 ; recette « etat.json compte dix étapes » |
| Maillon 4 refuse quand 3b vaut `en_cours` | PASS | scénario M1 remesuré ; garde de `scaffold.py` neutralisée : recette rouge |
| `scaffold.py` : aucun `{{`, chemin `~` | PASS | vault construit sous `HOME` factice : `CLAUDE.md` porte `~/Commun/Référentiel`, aucun `{{…}}` hors `Templates` et code ; perturbation de la substitution : rouge |
| `federe.py` : note, ligne du Centre, rien sans la clé, idempotence | PASS | perturbations note et ligne du Centre : rouge (voir 3bis pour une perturbation à moi mal posée, refaite) |
| Notice identique octet pour octet | PASS | sha256 identique ; témoin |
| Doctrine `^## 12`, amendement daté au §5 | PASS | lignes 162 et 86 |

### Recette

| Critère | Statut | Preuve |
|---|---|---|
| Recette à 0, plus de contrôles qu'avant | PASS | 154 puis 197, remesurés des deux côtés |
| White-label et chemin absolu couvrent `skills/cortex-3b-rangement/` | PASS | `/Users/quelquun/x` ajouté à `nomenclature.md` d'une copie : C9 rouge |
| `cd` seulement pour l'interdire | PASS, vacuité notée | 0 ligne ; les deux mentions de `cd` sont entre accents graves et l'interdisent ; témoin positif |

### Sécurité

| Critère | Statut | Preuve |
|---|---|---|
| Aucun secret, aucun nom réel | PASS, confiance moyenne | aucun motif de secret dans le diff ; noms de fixture « Ateliers Roumier », « Ateliers Exemple », déjà fictifs avant la lane. Je ne peux pas prouver qu'un nom est fictif |
| G4 résout les liens symboliques | PASS | `realpath` remplacé par `abspath` : rouge |

### Silent-failure

| Critère | Statut | Preuve |
|---|---|---|
| Aucun `except` vide, aucun repli qui agrège, aucun geste en échec qui continue en silence | **FAIL partiel** | aucun `except` vide ; `appliquer` et `annuler` s'arrêtent et journalisent chaque échec de geste. Mais `rafraichir_index` n'est enveloppé d'aucun `try` (`range.py:987` et `:1242`) : son échec n'est pas journalisé et sort avec un message faux (N1, trouvé aussi par `silent-failure-hunter`). Agrégation résiduelle « a changé ou disparu » (N7) |

### Témoins

| Critère | Statut | Preuve |
|---|---|---|
| Garde prouvée mordante, consignée au rapport | PASS | G1 neutralisée : auto-test rouge, et le témoin de la recette (« G1 désactivée dans une copie jetable ») rouge aussi |
| Témoin du grep | PASS | rejoué |
| Témoin « aucun `{{` » | PASS | le témoin de la recette teste la regex sur un jetable ; ma perturbation de la substitution dans `scaffold.py` fait rougir auto-test et recette |
| Témoin I-R2 par `touch` | PASS | recette C11 |
| Chaque assertion négative porte une positive sur le même objet | **PASS partiel** | « pas de procédure copiée » / « un contrat copié existe » : tenu. « Aucune note par procédure d'entreprise » : positive sur le même vault et témoin, mais objet qui ne peut pas produire le défaut (N9) |

### Contrôle manuel consigné

| Critère | Statut | Preuve |
|---|---|---|
| « rangeons mes dossiers » en session ouverte | **Non recalibré, et daté** | je n'ai pas ouvert de session Claude Code imbriquée. Le rapport le consigne en `claude -p` (non interactif), avant la reprise 1 : « 11 changements », alors que la fixture en donne 15 aujourd'hui et que l'ordre des lots a changé. Il n'a pas été rejoué (N8) |

## 3bis. Les contrôles eux-mêmes

Méthode : copie `git archive HEAD` ; pour chaque perturbation, le motif est compté (exactement une occurrence, sinon « non posée »), le fichier relu différent de l'original, auto-test du script et recette lancés, puis l'original restauré et relu identique. Script : `scratchpad/perturb.py`.

| Perturbation | Auto-test | Recette |
|---|---|---|
| G1 `controler`, G1 `publier`, renommage exclusif remplacé par `os.rename` brut | rouge ×3 | rouge ×3 |
| G2 `controler`, G2 recalculé (m4), G2 `publier` | rouge ×3 | rouge ×3 |
| G3 manuel, G3 deux racines | rouge ×2 | rouge ×2 |
| G4 hors racines, G4 sans `realpath` | rouge ×2 | rouge ×2 |
| G5 | rouge | rouge |
| G6 détection, G6 titre lu malgré « en ligne », G6 `lire_index` | rouge ×3 | rouge ×3 |
| G7 `controler`, G7 `ecrire_index`, G7 `publier` | rouge ×3 | rouge ×3 |
| G8 | rouge | rouge |
| G9 sans troncature | rouge | rouge |
| **G9 sans priorité création et sommaire (m7)** | **vert** | **vert** |
| Clôture « appliqué en partie » (M2) | rouge | rouge |
| Création du sommaire en mode `w` (m2) | rouge | rouge |
| Rafraîchissement après lot (B1) | vert | rouge |
| **Rafraîchissement à la clôture (B1)** | **vert** | **vert** |
| Tri sans priorité de création (B1) | rouge | rouge |
| Garde « dépôt git » | rouge | rouge |
| `stat` refusé avalé | rouge | rouge |
| `.docx` sans corps rendu `""` | rouge | rouge |
| A7, taille non comparée | rouge | rouge |
| A5, retrait désactivé | rouge | rouge |
| Annulation de la mise à jour de config (`c001`) | rouge | rouge |
| `--clore` n'inscrit pas le dossier commun | rouge | rouge |
| `pas_apres_construction` neutralisée | rouge | rouge |
| Étape 0 (domaines signés) neutralisée | rouge | rouge |
| **Annulation d'une publication sans contrôle d'empreinte** | **vert** | **vert** |
| Annulation du sommaire sans contrôle d'empreinte | rouge | rouge |
| Déterminisme (mélange aléatoire) | rouge | rouge |
| `etat.py` branche M1, branche « appliqué en partie » | rouge, rouge | rouge, vert (couverte par l'auto-test) |
| **`etat.py` branche A2 avec `03-rangement.md` présent** | **vert** | **vert** |
| `scaffold.py` garde 3b | vert (l'auto-test appelle la fonction, pas `main`) | rouge |
| `scaffold.py` `marquer_construction` retiré | vert | rouge |
| **`scaffold.py` `marquer_construction` qui ignore un geste fait** | **vert** | **vert** |
| `scaffold.py` note du dossier commun retirée | vert | rouge |
| `scaffold.py` `{{REFERENTIEL}}` non substitué | rouge | rouge |
| `federe.py` note du dossier commun | rouge | rouge |
| `federe.py` ligne du Centre | rouge | rouge |
| Chemin absolu dans `nomenclature.md` | sans objet | rouge (C9) |

Une sonde à moi a menti avant de dire vrai : ma première perturbation de la ligne du Centre (`centre += [] or [...]`) ne retirait que le titre et laissait `[[Référentiel commun]]` ; recette verte. Refaite en retirant le lien lui-même : auto-test et recette rouges. Le contrôle mord ; ma perturbation ne détruisait pas l'information.

Critères que je n'ai pas pu calibrer : le contrôle manuel en session interactive ; la détection réelle d'un fichier « en ligne seulement » (`st_flags & 0x40000000`, simulée partout par `CORTEX_RECETTE_EN_LIGNE`) ; la fenêtre de course de `renommer_exclusif` sous un client de synchronisation actif.

## 4. Non-objectifs, sur tout le diff

| Non-objectif | Constat |
|---|---|
| Supprimer | `os.remove` du sommaire (`:1112`) et d'un assistant publié (`:1163`), `os.rmdir` d'un dossier resté vide (`:1150`, `:1167`) : à l'annulation seulement, sur ce que Cortex a créé, après comparaison d'empreinte. Conforme. La garde d'empreinte de `:1161` n'est pas éprouvée (N3) |
| Écraser | `renommer_exclusif` (`renamex_np RENAME_EXCL`, `renameat2 RENAME_NOREPLACE`), `open(…, "x")`. Le sommaire marqué se réécrit, son texte d'avant part au journal. Conforme |
| Dupliquer | aucun appel de copie. Le brouillon d'assistant reste dans l'atelier après `--publier` (sanctionné par le contrat §5, déjà noté) |
| Écrire dans une base | `base_en_ligne` lit l'inventaire et écrit une proposition dans `03-rangement.md`. Conforme |
| Déplacer entre deux espaces | G3 au moment du geste ; le geste devient `manuel`, constaté par `--verifier`. Conforme |
| Lire un fichier seulement en ligne | gardé dans `titre_local`, `lire_index`, `_description`, `_defaire_index`, l'annulation d'une publication. `texte_index` ne fait qu'un `stat`. Dérive acceptée par A1 : le rejeu de `scan.py` peut télécharger un candidat structurant en ligne (suivi au rapport, `scan.py` hors possession) |
| `cd` vers une racine | aucun |
| Fichiers hors possession | aucun fichier de la liste « Ne pas toucher ». Hors du tableau de `03` : `skills/cortex-4-installation/scripts/notice.md` (texte du LISEZ-MOI, touché pour m3) |
| Défaut préexistant corrigé | aucun ; les quatre défauts préexistants sont au rapport |

## 5. Conduite du SKILL.md face à D2, D5, D6, D7 et aux mots interdits

- **D2** (lots de quatre, ligne par ligne, journal, annulable) : tenu (§3, §5, « Défaire »), et tenu dans les faits depuis B1. Le §3 dit « Code 3 : une garde a levé, rien n'a bougé » : N1 rend cette phrase fausse dans un cas.
- **D5** (accord renforcé à part, phrase sur les liens, liste des gestes) : tenu mot pour mot (§5) ; G2 recalculé au geste dans le script.
- **D6** (personnelle pointée, d'entreprise au dossier commun, question en cas de doute) : tenu (§4) ; « Mon … » en dossier partagé passe par la question.
- **D7** (création proposée à tous avec « voyez avec qui de droit » ; existant adopté) : tenu (§6) ; `range.py` ne propose rien dans un dossier commun existant (`dans_ref`, `range.py:494-496`). Quand aucun dossier partagé n'est déclaré, la skill fait inscrire le nouveau dossier dans `collecte.racines` et `collecte.partagees` sans script : une édition de `config.yaml` par conduite (observation N13).
- **Mots** : aucun mot interdit dans les citations destinées à la personne ni dans les messages de clôture ; la liste porte « JSON ». Deux réserves : le sommaire montré avant l'accord sur un dossier commun existant est rédigé par l'agent d'après le gabarit, pas produit par le script (N10) ; le guide d'usage du maillon 7 nomme `AGENTS.md` devant la personne (N11). Le dossier créé par défaut s'appelle `Référentiel`, mot interdit que la personne verra dans ses dossiers : forme du contrat §1 (observation déjà portée par `audit.md`).

## Findings neufs, classés

Chaque finding porte une sévérité et une confiance.

### Majeurs

**N1. Un échec du rafraîchissement du sommaire, après des gestes faits, sort en code 3 « Rien n'a bougé » et ne se journalise pas.** Sévérité majeure, confiance haute, reproduit.
`appliquer` appelle `rafraichir_index` après la boucle des gestes, hors de tout `try` (`range.py:987`). `ecrire_index` y lève `Garde` (G7 si la marque a disparu, G6 si le sommaire est passé « en ligne seulement ») ou `OSError` (droits). L'exception remonte au `except Garde` de `main` (`range.py:1707`), qui imprime « [garde] … Rien n'a bougé. » et sort 3. Scénario `x4` : sommaire écrit au lot précédent, marque retirée à la main, puis `--appliquer --ids r006 --renforce` : sortie 3, message « Rien n'a bougé », alors que `Process Qualite.md` est dans `Procédures/` et que le journal porte `r006` en `fait`. Aucune ligne `echec` ne trace le rafraîchissement manqué. Le contrat §5 définit le code 3 comme « garde levée, rien n'a bougé », et le SKILL.md §3 fait dire à la personne que rien n'a bougé. Même défaut à `clore` (`:1242`), sans fichier déplacé. `silent-failure-hunter` l'a trouvé de son côté (classé critique).

**N2. Le rafraîchissement du sommaire à la clôture n'est éprouvé par rien.** Sévérité majeure, confiance haute.
Retiré (`range.py:1242`), auto-test et recette restent verts. Or c'est le seul chemin par lequel une procédure déplacée à la main (geste `manuel` constaté par `--verifier`, qui ne rafraîchit pas) entre au sommaire. Démontré sur `x6` : procédure `manuel` vers le dossier commun, déplacée à la main, constatée ; sommaire avant clôture : 0 occurrence ; après `--clore applique` : 1 (`i001`). Sans ce rafraîchissement, B1 revient pour les gestes manuels, sans signal.

**N3. Le contrôle d'empreinte qui précède le retrait d'un assistant publié n'est éprouvé par rien.** Sévérité majeure, confiance haute.
`range.py:1161` compare le sha256 du `SKILL.md` publié à celui du journal avant `os.remove` (exception 2 du contrat §5). Neutralisé, auto-test et recette restent verts : aucun cas ne modifie un assistant publié avant de défaire sa publication. C'est la seule garde qui empêche de supprimer, dans le dossier partagé, un assistant qu'un collègue a retouché.

### Mineurs

- **N4.** Priorité de la création et du sommaire à la troncature (m7) : juste dans le code (reproduit, plafond 5), non éprouvée (perturbation verte). Confiance haute.
- **N5.** Branches non éprouvées, d'effet limité : `etat.py`, A2 quand `03-rangement.md` existe sans geste fait (`_rangement`, `elif _aval`) ; `marquer_construction` qui n'écrit jamais `passee` après un geste fait (atteignable seulement quand tout a été défait, où `passee` serait d'ailleurs juste). Confiance haute pour l'absence de test, moyenne pour l'effet.
- **N6.** `--annuler --ids <déplacement vers le dossier commun>` après la clôture laisse le sommaire lister un document absent, jusqu'à la clôture suivante. Reproduit (`x3`, `r006` défait : `Procedure Qualite` toujours au sommaire). Effet contenu : l'étape repasse `en_cours` et la construction attend une nouvelle clôture, qui rafraîchit. Confiance haute.
- **N7.** Agrégation résiduelle de deux causes (absent, changé) dans le code de la lane : G5 (`range.py:911`), `--verifier` (`:1062`), annulation d'un déplacement (`:1137`). Aucune perte ; diagnostic moins précis sur le chemin le plus fréquent. Confiance haute.
- **N8.** Le contrôle manuel consigné date d'avant la reprise 1 (« 11 changements », fixture à deux procédures) ; la fixture en donne 15 aujourd'hui, en cinq lots, et l'ordre des lignes a changé. Non rejoué. Confiance haute.
- **N9.** Résidu de M4 : l'assertion « aucune note par procédure d'entreprise » porte sur le vault du maillon 4, qui n'en écrit jamais ; le maillon 5, qui pourrait en écrire, n'est pas exercé ; côté commun, la négative ne peut pas rougir. Confiance haute.
- **N10.** Dossier commun existant : le SKILL.md §6 fait « générer dans le message à partir de la liste » le sommaire montré avant l'accord. Le texte écrit ensuite vient de `texte_index`, qui liste tout le dossier : ce que la personne a vu peut différer de ce qui s'écrit (doctrine §10). Aucune commande ne rend le texte exact à l'avance. Confiance moyenne.
- **N11.** Le guide d'usage du maillon 7 dit « le sommaire `AGENTS.md` de ce dossier » ; `AGENTS.md` figure dans les mots interdits devant la personne (02, « Mots »). Confiance moyenne : dépend de ce que le guide d'usage est lu par la personne.
- **N12.** Le sommaire décoché mais des procédures rangées : `--clore` inscrit quand même `referentiel.etat: existant` (`range.py:1245-1252`), et le `CLAUDE.md` du vault renvoie à un `AGENTS.md` qui n'existe pas. Lu dans le code, non reproduit. Confiance moyenne.

### Observations

- **N13.** Sans dossier partagé déclaré, l'ajout du dossier où créer le dossier commun se fait par édition de `config.yaml` sous conduite, sans script, à rebours du motif donné par le rapport pour les extensions de `range.py`.
- Doctrine §12 : « renommer un fichier ou un dossier » ; le script ne renomme jamais un dossier (écart déclaré au rapport). Le texte promet plus que le code.
- `notice.md` modifié hors du tableau de `03` (même nature que m13, sans effet).
- `silent-failure-hunter` signale aussi, dans `scaffold.py`, un `except` unique autour de quatre commandes git ; hors de cette lane d'après `git blame`.

## Pour reprendre

1. N1 : envelopper les deux appels à `rafraichir_index` ; journaliser l'échec sous un id `i…` en `echec` ; sortir 1 avec un message qui dit que les gestes sont faits et que seul le sommaire n'a pas suivi. Cas d'auto-test : marque retirée entre deux lots.
2. N2 : un cas d'auto-test ou de recette où un geste manuel vers le dossier commun, constaté, n'entre au sommaire qu'à la clôture.
3. N3 : un cas d'auto-test qui modifie l'assistant publié puis défait la publication, et exige code 1 et fichier intact.
4. Mineurs au choix du chef d'orchestre ; N8 demande seulement de rejouer le contrôle manuel sur la fixture actuelle.
