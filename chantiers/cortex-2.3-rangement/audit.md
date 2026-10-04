# Audit à froid de la lane rangement (Cortex 2.3.0)

Auditeur : Opus 5.5, effort high, session neuve. Date : 2026-10-04. Objet : worktree `~/Dev/cortex--rangement`, branche `lane/rangement`, HEAD `abc2449` (code à `2efc3e4`), base `2c1f289`. Aucun fichier du dépôt corrigé ; seul ce fichier est écrit.

## Verdict

**Lane à reprendre.** Un défaut bloquant, deux défauts majeurs de comportement, quatre majeurs sur les contrôles eux-mêmes ou sur le pack, une série de mineurs. Aucun geste observé ne supprime, n'écrase ni ne copie un fichier de la personne : les gardes de `range.py` tiennent, et 36 perturbations sur 42 font rougir l'auto-test ou la recette (les six vertes portent sur quatre gardes, détail en 3bis). Ce qui bloque est ailleurs : le sommaire du dossier commun ment dès qu'il y a plus d'une procédure d'entreprise à ranger, et un rangement appliqué mais non clos se fait effacer par la construction.

## Ce que j'ai relancé moi-même

| Mesure | Résultat | Sur quoi la commande a répondu |
|---|---|---|
| `git status` | propre, branche `lane/rangement` | worktree |
| `git log --oneline 2c1f289..HEAD` | 18 commits, dont 2 du chef d'orchestre sur le pack (`eb276bd`, `ce062ca`) | worktree |
| six `--autotest` | tous en 0 (codes relevés sans pipe) | scripts du worktree |
| `parcours_blanc.py` à HEAD | 192 passés, 0 en échec, sortie 0 ; C11 37/37 | `DEPOT` déduit de `__file__`, donc le worktree |
| `parcours_blanc.py` à `2c1f289` | 154 passés, 0 en échec, sortie 0 | `git archive 2c1f289` extrait dans le scratchpad |
| grep des appels interdits | 2 lignes, `os.remove` aux lignes 1059 et 1106, chacune commentée « exception 2 du contrat §5 » | `range.py` du worktree |
| témoin du grep | 3 lignes sur un jetable (`os.remove(`, `shutil.copy2(`, `os.replace(`) | fichier jetable |
| grep `cd` du SKILL.md | 0 ligne ; témoin `cd ~/Documents/Travail` : 1 ligne | SKILL.md 3b |
| section Notice | identique octet pour octet (363 octets) à celle de `cortex-3-ontologie` | deux SKILL.md |
| `copie_structurant.py --type process` | code 2, message « une procedure ne se copie jamais » ; `--type contrat` même source : 0, note écrite | vault jetable |
| proposition sur la fixture dirigeant | 11 changements (6 renommages, 2 procédures, 3 pour créer le dossier commun), signalements `en_ligne_seulement` et `doublon_probable` | copie de la fixture hors dépôt |
| `silent-failure-hunter` sur les six scripts | 11 findings, dont 6 dans le code de la lane, 5 préexistants (vérifié par `git blame`) | worktree |

Les chiffres du rapport (154 avant, 192 après, C11 à 37, 11 changements au contrôle manuel) sont remesurés et justes.

## Critères de 06-verification.md, un par un

### Script et gardes

| Critère | Statut | Preuve |
|---|---|---|
| `range.py --autotest` rend 0 | PASS | sortie 0, « auto-test OK » |
| Chaque garde G1 à G9 dans les deux sens, code 3, arbre identique | **FAIL partiel** | G1, G2, G3, G4, G5, G7, G8 : cas qui lève (code 3, `arbre()` comparé) et cas qui passe, prouvés par perturbation (voir 3bis). G9 n'est pas une garde à code 3, ses deux sens sont testés. G6 : seul le chemin « titre non lu » est testé, par conséquence sur le nom proposé. Le chemin à code 3 de G6 (`lire_index` sur un `AGENTS.md` présent seulement en ligne, ligne 729) n'est éprouvé ni par l'auto-test ni par la recette : désactivé, les deux restent verts. |
| I-R1 | PASS | auto-test : `len == n_avant + 1` (seul le sommaire s'ajoute) puis arbre d'avant après `--annuler` ; recette C11 idem |
| I-R2 | PASS | auto-test et recette comparent chemins, tailles, `mtime` ; perturbations « annuler ne renomme pas » et « rmdir sauté » : rouge |
| Déterminisme | PASS | auto-test et recette ; perturbation par tri aléatoire : rouge (« deux propositions divergent ») |
| Grep des appels interdits | PASS | deux lignes, toutes deux exceptions commentées ; témoin à 3 lignes. Angle mort noté en mineur m1 |

### Config, état, maillons

| Critère | Statut | Preuve |
|---|---|---|
| `cortex_config.py` refuse `process`, un `referentiel.chemin` hors racine, une `partagees` non incluse ; accepte `config.example.yaml` | **FAIL à la lettre** | hors racine et `partagees` : refusés (auto-test, recette, perturbations rouges). `process` : accepté avec avertissement, par l'arbitrage T5 amendé de `2efc3e4`. Le pack n'a pas suivi : `01-cadrage.md` T5, `03-backlog-technique.md`, `04-contrat.md` §1 et ce critère disent toujours « refusé ». Voir majeur M5 |
| `copie_structurant.py --type process` en erreur nommant la règle ; `contrat` réussit | PASS | relancé à la main, voir plus haut ; perturbation : rouge |
| `etat.py --autotest` couvre les quatre lignes du §8 ; dix étapes | PASS | auto-test lignes 373 à 381 ; recette « etat.json compte dix étapes » ; perturbations `en_cours` et A2 : rouge |
| Maillon 4 refuse quand 3b vaut `en_cours` | PASS | recette C11 (journal avec un `fait` et `r999` accepté non fait, `scaffold.py` sort 2, aucun vault) ; perturbation de `rangement_inacheve` : rouge. Trou de couverture : voir majeur M2 |
| `scaffold.py` : aucun `{{`, chemin `~` du référentiel | PASS | recette et auto-test ; perturbation `{{REFERENTIEL}}` non substitué : rouge |
| `federe.py` : note et ligne du Centre avec la clé, rien sans, deux générations identiques | PASS | auto-test et recette ; perturbations note et ligne du Centre : rouge |
| Notice identique octet pour octet | PASS | 363 octets identiques |
| Doctrine : un `^## 12`, amendement daté au §5 | PASS | ligne 162 ; amendement 2026-10-04 ligne 86 |

### Recette

| Critère | Statut | Preuve |
|---|---|---|
| Recette à 0, plus de contrôles qu'avant | PASS | 154 puis 192, remesurés des deux côtés |
| White-label et chemin absolu couvrent `skills/cortex-3b-rangement/` | PASS | recette ; perturbation (chemin `/Users/…` ajouté à `nomenclature.md`) : C9 rouge |
| `cd` seulement pour l'interdire | PASS, vacuité notée | 0 ligne trouvée, la seule mention est entre accents graves (« par `cd` ») ; témoin positif à 1 ligne |

### Sécurité

| Critère | Statut | Preuve |
|---|---|---|
| Aucun secret, aucun nom réel | PASS, confiance moyenne | noms ajoutés : « Ateliers Roumier », « Malbrun », « Ateliers Exemple », déjà fictifs avant la lane ; aucun secret. Je ne peux pas prouver qu'un nom est fictif |
| G4 résout les liens symboliques | PASS | auto-test r900 ; perturbation `realpath` remplacé par `abspath` : rouge |

### Silent-failure

| Critère | Statut | Preuve |
|---|---|---|
| Aucun `except` vide, aucun repli qui agrège, aucun geste en échec qui continue | **FAIL partiel** | aucun `except` vide, aucun lot qui continue après un échec (`appliquer` et `annuler` s'arrêtent et journalisent). Mais le code de la lane agrège : `range.py:1104` (trois causes, « modifié ou absent », message faux pour un fichier seulement en ligne), `range.py:950` (trois erreurs d'usage, un message), `range.py:262` (`KeyError` d'un `.docx` sans `word/document.xml` rendu `""`, sans signalement). Voir majeur M6 et mineurs |

### Témoins (verifier-avant-de-croire)

| Critère | Statut | Preuve |
|---|---|---|
| Garde prouvée mordante, G1 désactivée, consigné au rapport | PASS | reproduit : code 1, `[Errno 17] File exists` (le renommage exclusif tient seul) |
| Témoin du grep | PASS | 3 lignes sur jetable |
| Témoin « aucun `{{` » | PASS faible | la recette teste la regex sur un texte, pas la chaîne de scaffold. Ma perturbation de `substitutions` fait rougir l'auto-test de `scaffold.py` : le contrôle mord, mais par mon témoin, pas par le sien |
| Témoin I-R2 par `touch` | PASS | recette C11 |
| Chaque assertion négative porte une positive sur le même objet | **FAIL partiel** | « pas de procédure copiée » / « un contrat copié existe » : tenu. « Pas de note par procédure d'entreprise » : testé seulement dans le commun (`not Procédures exists`), où `federe.py` ne recopie jamais `50 - Ressources` des exports (ligne 291) : l'assertion ne peut pas rougir. Côté vault, aucun contrôle (le maillon 5 écrit par conduite) |

### Contrôle manuel consigné

| Critère | Statut | Preuve |
|---|---|---|
| « rangeons mes dossiers » en session ouverte : skill, lot de quatre, refus total | **Non recalibré** | je n'ai pas ouvert de session Claude Code imbriquée. Le rapport le consigne en mode `claude -p`, non interactif, où la question à cases ne s'affiche pas. La partie scriptée (11 changements, statut `refuse` sur refus) est remesurée par moi |

## 3bis. Les contrôles eux-mêmes

Méthode : copie de HEAD par `git archive` dans le scratchpad ; pour chaque perturbation, le motif est compté (exactement une occurrence, sinon non posée), le fichier relu différent de l'original, puis restauré.

| Perturbation | Contrôle | Résultat |
|---|---|---|
| G1 dans `controler` | auto-test | rouge |
| G2 dans `controler`, G2 dans `publier` | auto-test | rouge, rouge |
| G3 manuel, G3 deux racines | auto-test | rouge, rouge |
| G4 hors racines, G4 sans résolution des liens | auto-test | rouge, rouge |
| G5 | auto-test | rouge |
| G6 détection, G6 titre lu malgré « en ligne » | auto-test | rouge, rouge |
| **G6 dans `lire_index`** | auto-test et recette | **vert, vert** |
| G7 `controler`, G7 `ecrire_index` | auto-test | rouge, rouge |
| G8 | auto-test | rouge |
| G9 sans troncature, `depassement` forcé à faux | auto-test | rouge, rouge |
| I-R2 (`rmdir` sauté, annuler sans renommer) | auto-test | rouge, rouge |
| I-R3 (lecture d'un octet dans `_identique`) | auto-test | rouge |
| Déterminisme (tri aléatoire) | auto-test | rouge |
| `renamex_np` sans `RENAME_EXCL` | auto-test | rouge |
| Retrait du sommaire sans contrôle sha | auto-test | rouge |
| Garde « dépôt git » dans `controler` | auto-test | rouge |
| **`--clore applique` sans la garde « appliqué en partie »** | auto-test et recette | **vert, vert** |
| **`ecrire_index` en mode `w` au lieu de `x`** | auto-test | **vert** |
| **`publier` sans la garde G1** | auto-test | **vert** (le mode `x` protège encore, mais aucun cas ne publie sur un assistant existant) |
| `marquer_construction` retiré | recette | rouge |
| `pas_apres_construction` neutralisé | recette | rouge |
| `--verifier` ne constate plus le manuel | recette | rouge |
| `--clore` n'inscrit plus le référentiel | recette | rouge |
| `etat.py` `en_cours`, A2 | auto-test | rouge, rouge |
| `scaffold.py` garde, `{{REFERENTIEL}}` | auto-test | rouge, rouge |
| `cortex_config.py` `partagees`, référentiel hors racine | auto-test | rouge, rouge |
| `copie_structurant.py` `process` | auto-test | rouge |
| `federe.py` note, ligne du Centre | auto-test | rouge, rouge |
| chemin absolu dans `nomenclature.md` | recette C9 | rouge |

Critères que je n'ai pas pu calibrer : le contrôle manuel en session interactive ; la détection réelle d'un fichier « en ligne seulement » (`st_flags & 0x40000000`, simulée par `CORTEX_RECETTE_EN_LIGNE` partout) ; la fenêtre de course de `renommer_exclusif` sous charge d'un client de synchronisation.

## 4. Non-objectifs, sur tout le diff

| Non-objectif | Constat |
|---|---|
| Supprimer | `os.remove` du sommaire et d'un assistant publié, `os.rmdir` d'un dossier resté vide : seulement à l'annulation, sur ce que Cortex a créé, après comparaison sha256. Conforme |
| Écraser | `renommer_exclusif` (`renamex_np RENAME_EXCL`, `renameat2 RENAME_NOREPLACE`), `open(…, "x")`. Le sommaire marqué se réécrit, son texte d'avant part au journal : prévu par G7 et §7. Conforme |
| Dupliquer | aucun appel de copie. Observation : `--publier` laisse le brouillon `_cortex/assistants/<nom>/SKILL.md` à côté de l'exemplaire publié, deux exemplaires du même assistant (sanctionné par le contrat §5) |
| Écrire dans une base | `base_en_ligne` lit l'inventaire et écrit une proposition. Conforme |
| Déplacer entre deux espaces | G3 recalcule les racines au moment du geste ; un renommage système ne copie jamais (`EXDEV` lève). Conforme |
| Lire un fichier seulement en ligne | gardé dans `titre_local`, `lire_index`, `_description`, l'annulation. Dérive acceptée par A1 : la skill fait rejouer `scan.py`, qui peut télécharger un candidat structurant en ligne (suivi noté au rapport) |
| `cd` vers une racine | aucun |
| Fichiers hors possession | aucun fichier de la liste « Ne pas toucher ». Hors du tableau de `03-backlog-technique.md` : `template/vault/.claude/skills/lint/SKILL.md` (une phrase, « copie de process » devient « copie de contrat ») |
| Défaut préexistant corrigé | aucun ; mais les cinq défauts préexistants relevés par la chasse aux échecs silencieux ne sont pas notés au rapport (mineur m9) |

## 5. Conduite du SKILL.md face à D2, D5, D6, D7 et aux mots interdits

- **D2** (lots de quatre, ligne par ligne, journal, annulable) : tenu dans le texte (§3, §5, « Défaire »). Contredit dans les faits par le bloquant B1 : le premier lot partagé n'est pas applicable seul.
- **D5** (accord renforcé à part, phrase sur les liens, liste des gestes) : tenu mot pour mot (§5). Le script fait foi sur le champ `partage` écrit dans la liste au moment de proposer, sans le recalculer depuis `config.yaml` au moment du geste (mineur m4).
- **D6** (personnelle pointée, d'entreprise au dossier commun, question en cas de doute) : tenu (§4). Une procédure nommée « Mon process … » dans un dossier partagé est classée d'entreprise sans question (`range.py:527`) ; la ligne reste à cocher (mineur m5).
- **D7** (création proposée à tous, « voyez avec qui de droit » ; existant adopté) : tenu (§6) ; `range.py` ne propose rien dans un dossier commun existant.
- **Mots** : aucun mot interdit dans les textes destinés à la personne (citations, message de clôture). La liste du SKILL.md ligne 27 omet « JSON » (mineur m6). Le dossier créé par défaut s'appelle `Référentiel`, mot interdit devant la personne, qui le verra dans ses dossiers ; c'est la forme du contrat §1 (observation).

## Findings, classés

Chaque finding porte une confiance (haute, moyenne, basse).

### Bloquant

**B1. Le sommaire du dossier commun ment dès que les procédures d'entreprise débordent d'un lot, et le premier lot partagé échoue en code 3.** Confiance haute, reproduit.
Les lignes se trient par chemin d'origine : les `deplacer` depuis `Commun/Divers/…` passent avant `creer_dossier` et `ecrire_index` sous `Commun/Référentiel`. Avec cinq procédures, le lot 1 porte quatre `deplacer`, le lot 2 le cinquième plus la création et le sommaire. Suivre la skill (« lot par lot ») : lot 1 en code 3 (« le dossier d'arrivée n'existe pas »), lot 2 en 0, lot 1 rejoué en 0, `--clore applique` en 0. Résultat : `AGENTS.md` ne liste qu'une procédure sur cinq, et rien ne le régénère. D8 (« un `AGENTS.md` qui donne pour chaque document son objet ») est faux sans signal. Le SKILL.md §6 promet « un même lot renforcé » pour création, rangement et sommaire, ce que `attribuer_lots` ne fait pas au-delà de quatre lignes. La recette ne le voit pas : sa fixture n'a qu'une procédure d'entreprise.
Reproduction : scratchpad `x3`, cinq `Process <X>.md` dans `Commun/Divers`, `--proposer`, puis `--appliquer` lot par lot avec `--renforce`.

### Majeurs

**M1. Un rangement appliqué en entier mais non clos est effacé par la construction.** Confiance haute, reproduit.
Cinq gestes faits (dont la création du dossier commun et une procédure déplacée dedans), `--verifier` à 0, pas de `--clore` (session interrompue, ou étape §9 sautée). `etat.py` rend 3b `a_faire` (aucune ligne acceptée en suspens), le maillon 4 construit, `marquer_construction` écrit `statut: passee` et « passée sans rangement » (faux : cinq changements faits), `config.yaml` garde `referentiel.etat: aucun`, `CLAUDE.md` du vault dit « Aucun dossier commun déclaré. » alors qu'il existe et porte la procédure. Ensuite `--clore` et `--annuler` refusent (code 3, construit) : rien ne rattrape. D6 est rompu (le vault ne pointe pas vers le dossier commun). Le rapport déclare l'état « `propose` sans ligne en suspens : `a_faire` » comme écart, sans cette conséquence.
Reproduction : scratchpad `x1`.

**M2. La garde « appliqué en partie » de `--clore applique` n'est éprouvée par rien.** Confiance haute. Neutralisée, auto-test et recette restent verts. L'effet est contenu (`etat.py` donne `en_cours` et le maillon 4 bloque), mais le rapport présente cette garde comme une protection.

**M3. G6 à code 3 non éprouvée** (`lire_index`, sommaire présent seulement en ligne). Confiance haute. Critère 2 de `06` non tenu pour G6.

**M4. Une assertion négative sans objet possible.** Confiance haute. « Aucune note par procédure d'entreprise » ne peut pas rougir dans le commun et n'est pas contrôlée dans le vault (critère « assertions négatives » de `06`).

**M5. Le pack contredit le code sur T5.** Confiance haute. L'arbitrage du chef d'orchestre (process toléré avec avertissement) vit dans le message de `2efc3e4`, le rapport, la doctrine et `config.example.yaml`. `01-cadrage.md` T5, `03-backlog-technique.md`, `04-contrat.md` §1 et `06-verification.md` disent encore « refusé par `cortex_config.py` ». Le contrat se dit « définitif pour la 2.3.0 » : il n'a pas reçu d'amendement A6. Document de référence faux à la fusion.

**M6. Le critère silent-failure n'est pas tenu dans le code de la lane.** Confiance haute pour la ligne 1104, moyenne pour la 262. `range.py:1104` agrège trois causes (en ligne seulement, absent, modifié) dans « assistant modifié ou absent » (faux pour la première), alors que `_defaire_index` juste au-dessus les distingue. `range.py:262` : un `.docx` sans `word/document.xml` rend `""` et ne produit pas de `titre_illisible`.

### Mineurs

- **m1.** Le grep des appels interdits ne voit ni `Path.unlink`, ni `Path.rename`/`replace`, ni `os.rename`. Le code de production n'en porte pas (vérifié à la main, hors auto-test) ; la sonde garde l'angle mort. Confiance haute.
- **m2.** `ecrire_index` (mode `x` à la création) et `publier` sur un assistant existant (G1) : aucun cas de test ; perturbés, l'auto-test reste vert. Confiance haute.
- **m3.** `notice.md` (texte du LISEZ-MOI) dit « Les neuf étapes » et ne décrit pas le rangement, sous un tableau qui en compte dix. Confiance haute.
- **m4.** G2 lit `partage` dans la liste figée à la proposition, sans le recalculer depuis `collecte.partagees` au moment du geste. Confiance moyenne.
- **m5.** Une procédure au nom personnel (« Mon … ») dans un dossier partagé est classée d'entreprise sans la question de D6. Confiance moyenne.
- **m6.** La liste des mots interdits du SKILL.md omet « JSON » (02, « Mots »). Confiance haute.
- **m7.** G9 tronque la liste triée par la fin : au-delà du plafond, les lignes de création du dossier commun et du sommaire partent les premières, et des `deplacer` vers un dossier sans ligne de création restent proposés (bloqués en code 3). Lu dans le code, non reproduit. Confiance moyenne.
- **m8.** `--verifier` constate un geste manuel dès que `vers` existe et `de` a disparu, sans comparer taille et date à la proposition (T3). Conforme à la lettre du §5. Confiance moyenne.
- **m9.** Défauts préexistants relevés par `silent-failure-hunter`, absents du rapport : `etat.py` `_frontmatter` « illisible » sans raison et `generer` qui jette le message de config illisible ; `copie_structurant.py` `texte_de` qui agrège binaire absent, délai et échec, et jette `stderr` ; `scaffold.py` couleur invalide grisée sans avertissement ; `federe.py` `KeyError` brut sur un `index.json` mal formé. Confiance haute (`git blame` : aucun commit de la lane).
- **m10.** Messages d'erreur de la lane qui agrègent : `range.py:950` (trois erreurs d'usage), `en_ligne_seulement` et `_identique` qui changent un échec de `stat` en « local » ou « changé » sans trace, repli muet de `renommer_exclusif` si la libc manque. Confiance moyenne à basse.
- **m11.** Le maillon 6 affiche une commande coupée (`--atelier <…>       --publier`, barre oblique perdue). Confiance haute.
- **m12.** `scaffold.py` cherche l'atelier dans le dossier de `--config` ; lancé avec une config ailleurs, la garde du rangement ne voit rien. Confiance basse.
- **m13.** Hors du tableau de `03-backlog-technique.md` : `template/vault/.claude/skills/lint/SKILL.md` touché (une phrase). Confiance haute, sans effet.

## Pour reprendre

1. B1 : grouper en un lot renforcé unique la création, les rangements vers le dossier commun et le sommaire, ou régénérer le sommaire à chaque geste qui touche le dossier commun et à `--clore` ; ajouter à la fixture au moins cinq procédures d'entreprise et contrôler que le sommaire les liste toutes.
2. M1 : traiter « des gestes faits, rien en suspens, pas clos » comme `en_cours` pour le maillon 4, ou faire clore par `marquer_construction` au lieu d'écrire « passée sans rangement » ; contrôle de recette sur ce cas.
3. M2, M3, m2 : un cas d'auto-test par garde non éprouvée.
4. M4 : une assertion positive sur le même objet (un export portant une note de procédure, et le constat qu'elle n'entre pas), ou retirer l'assertion vide.
5. M5 : amendement A6 dans `04-contrat.md`, et mise à jour de T5 et du critère de `06`.
6. M6 : distinguer les trois causes à la ligne 1104, signaler le `.docx` sans corps.
