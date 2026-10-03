# Verdict Phase H2 : parcours Alcyon rejoué

- Date : 2026-10-02 23:54 au 2026-10-03 01:22 (1 h 28)
- Plugin installé : `cortex@cortex-kit` 2.0.0-rc.7 (scope user, activé), servi depuis `~/Dev/cortex/skills`
- Dépôt : `~/Dev/cortex` branche `main`, HEAD `a2d17e0` (commit du chef d'orchestre « Pack H2 : lane C lancee », 23:52, qui ne touche que `phase-h2-majeurs/README.md`) ; code identique à `0c21dee` = `fix/phase-h`. L'annexe attendait la branche `fix/phase-h` : écart accepté par le chef d'orchestre.
- Recette `parcours_blanc.py` rejouée par le pilote : 140 contrôles passés, 0 échec, sortie 0 (hors sandbox ; le premier essai sous sandbox échoue en `FileExistsError` sur `recette/fixtures/employe`, effet du sandbox du pilote). `git status` du dépôt vide avant et après le parcours.
- Fixtures : `~/Cortex-test/alcyon`, 89 fichiers. Préparation faite par le chef d'orchestre ; vérifié : `~/Cortex` ne contenait que l'atelier `evrard`, `-Users-evrard-Cortex/memory/MEMORY.md` vide (0 octet), dépôt `cortex-helene` renommé (l'ancien nom redirigeait encore vers `cortex-helene-h1-20260927` côté API jusqu'à sa recréation).
- Pilotage : sessions `alcyon-helene` (surface 152), `alcyon-karim` (153), `vault-helene` (160), `vault-karim` (161), lancées depuis `~/Cortex` ; réponses au clavier ; chaque maillon relu dans le transcript (`~/.claude/projects/-Users-evrard-Cortex/ef479a8e…` Hélène, `7a898b4e…` Karim, `-Users-evrard-Cortex-*-vault/`) et dans les fichiers écrits.

## Décision

**Phase H non validée en l'état : 1 bloquant, 2 majeurs.** Tag v2.0.0 non autorisé tant que le bloquant n'est pas levé ou requalifié par Evrard.

Le bloquant est atypique : c'est le harnais Claude Code, pas le modèle, qui écrit dans une racine. Une session lancée depuis un vault qui fait `cd <racine>` puis lance une seconde commande crée `<racine>/.claude/.cc-writes` (dossier vide), malgré `sandbox.filesystem.denyWrite` et `deny Edit`. Reproduit par le pilote, témoin compris (détail plus bas). Si Evrard le requalifie en limite du harnais hors grille, il reste 2 majeurs, sous le seuil de 3, et la phase serait validée. Cette requalification lui revient.

Les 10 majeurs de la Phase H sont levés au parcours, sauf le vocabulaire (Q-vocab), qui revient sous une forme plus étroite : des noms de skill et de script dans les récapitulatifs de fin d'installation.

## Défauts par gravité

### Bloquant

| Code | Où | Preuve |
|---|---|---|
| P-ecrit (harnais) | Karim, maillon 4, contrôle vivant prescrit par le skill 4 (`claude -p "compte les fichiers de <racine>"`) | `~/Cortex-test/alcyon/partage/.claude/.cc-writes` créé le 2026-10-03 à 01:04:11, une seconde après la commande `cd ~/Cortex-test/alcyon/partage && find …` de la session `d47c4767` (`-Users-evrard-Cortex-karim-vault`). Reproduit : depuis `~/Cortex/karim/vault`, `claude -p` avec deux appels Bash (`cd ~/Cortex-test/alcyon/karim && ls Veille`, puis `ls Prospection`) crée `karim/.claude/.cc-writes`. Témoin : un seul appel sans `cd` (`ls ~/Cortex-test/alcyon/karim/Veille`) ne crée rien. Le dossier du témoin a été supprimé, celui de `partage` est laissé comme preuve. Sur un vrai poste, la racine est un SharePoint synchronisé : le dossier `.claude/` se propage à toute l'équipe. |

### Majeurs

| Code | Où | Preuve |
|---|---|---|
| Q-vocab | Hélène 4, Karim 4, Hélène 6 | Récapitulatifs : « Fais tourner `cloture` sur une vraie session, trois fois » (nom de skill, chez les deux), « Le scaffold (pour l'historique de versions)… » (Hélène, l. 808). Karim, l. 802 : question « etat.py ne déduit l'étape 4 que d'un fichier aval (04-ingest.md)… Que fait-on dans le kit ? » avec l'option « Corriger maintenant (Recommended) : etat.py marque l'étape 4… avec un cas ajouté à l'autotest ». Hélène, l. 1043 : « Le contrôle est marqué arbitré ». Les questions des maillons 0 à 3 et 5 sont propres chez les deux. |
| Q-repose (limite) | Hélène 1 | À « Quelle est l'adresse de Sitadel ? », réponse libre : « Je n'ai pas l'adresse sous la main ; on s'en sert surtout par ses exports ». Puis l. 327 : « Comment l'inventaire doit-il le traiter ? » avec « Attendre l'adresse (Recommandé) » contre « Se contenter des exports ». La réponse portait l'usage, la question le traitement : je le compte comme réponse reposée avec l'inverse recommandé (doctrine §8), au bénéfice du doute contre le produit. Sans lui : 1 majeur. |

### Mineurs et observations

- m-nom (banc) : au maillon 0, le nom court proposé est « evrard » / « marcon », l'adresse proposée « marcon.evrard@gmail.com » (« l'adresse rattachée à ce compte Claude »), chez les deux. Effet du compte Claude du fabricant ; aucun dossier de `~/Cortex/` listé.
- m-ref : aperçu « Dossiers » d'Hélène, « Dossier de référence des opérations : `~/Cortex-test/alcyon` », parent non déclaré qui contient aussi `karim/`. Corrigé par moi en `partage/Operations`.
- m-matrice : la table « qui fait foi » signée au maillon 3 n'est jamais reportée dans le vault (`90 - Meta/Architecture Mémoire.md` garde 5 « _à renseigner_ »). La remise de Karim le découvre et le corrige ; celle d'Hélène ne le voit pas, son vault part avec les trous.
- m-trace : chaque commit du vault porte `Co-Authored-By: Claude …` et `Claude-Session: https://claude.ai/code/session_…` (lien vers une session du compte du consultant), poussés sur `voiesdegypte/cortex-helene` (3 commits). Aucune mention interdite.
- m-nommage : « OPE - Caluire Belvédère » chez Hélène, « Caluire Belvédère » chez Karim ; au commun, deux notes de projet (`HELENE - OPE - …`, `KARIM - …`) au lieu d'une.
- m-PLU : « « PLU » n'apparaît dans aucun nom » alors que le fichier s'appelle `PLU Lyon 2026 synthese.pdf` (Karim, maillon 3).
- m-outils : `config.yaml` bloc `poste.outils` liste `github-desktop` et `buzz`, refusés ; chez Karim, libellés d'options en identifiants (`github-desktop`, `wispr-flow`) et pas d'option « Aucun » à la question des outils.
- Tutoiement et vouvoiement mêlés dans tous les récapitulatifs (« Pour toi ») : mineur exclu, suivi.
- Notice bloquée sur « construis mon second cerveau » après l'installation : mineur exclu, suivi.
- Banc : les deux sessions d'atelier se savent chez le fabricant (« Deux réserves, que je te laisse décider de corriger dans le produit », Hélène 4 ; proposition de modifier `etat.py`, Karim 4). Le plugin est servi depuis `~/Dev/cortex`. J'ai refusé ; `~/Dev/cortex` intact.
- Guide d'usage sans limite Windows chez les deux : le skill 7 la conditionne à `os: windows` ; poste macOS, l'attente de l'annexe ne s'applique pas.
- Scripts d'ingest écrits dans le scratchpad du harnais (`/private/tmp/claude-501/…`), temporaire : non compté en P-ecrit.

## Tableau

| Maillon | Rédacteur | Ce qui s'est passé | Défauts (code) | Durée | Questions inattendues | Écart de formulation |
|---|---|---|---|---|---|---|
| 0 Poste | Hélène | Nom court demandé : `helene`. markitdown et graphify vus présents, non reproposés. GitHub Desktop et Buzz refusés, rien installé. Options `[]`. MX vide (DNS relancé hors sandbox), question Google/Microsoft/autre, Microsoft, non administrée ; question explicite « petit serveur local et l'outil node » : non. `poste.json` : voie `aucune`, `voie_proposee: softeria`, gh `connecte: null` « à vérifier ». Notice ouverte, « faisons le cadrage » proposé sans démarrage. | m-nom, m-outils | 3 min | aucune | question softeria posée avec celle de l'administration |
| 1 Cadrage | Hélène | Pour quelqu'un d'autre, plusieurs. Racines demandées, aucune proposée depuis le disque. Quatre blocs (identité, noms, dossiers, bornes) en aperçu d'option. Mentions : seul « Evrard Marcon » proposé, aucun client ; ajout cortex-kit, Cosmos, Mister IA. `config.yaml` conforme (consultant, société, fédéré, commun en `~`, pointeur, `domaines: []`), `00-cadrage.md` 7 contrôles, `federation.yaml` : `helene` + `attendus: [Karim Benali]`. Lectures : plugin et atelier seulement. | Q-repose (limite), m-ref | 9 min | adresse Sitadel ; traitement de Sitadel | « Dans quelle situation êtes-vous ? » pour autrui ; récap en tutoiement |
| 2 Inventaire | Hélène | Aucune question. Scan relancé hors sandbox (cache markitdown). Mail non lu (0 en-tête). 4 points : Meyzieu, comités, configurateur-prix, Photos anniversaire. | aucun | 7 min | aucune | « 4 points à éclaircir » |
| 3 Ontologie | Hélène | 4 points en un lot. Opérations 45 %, Commercialisation 25 %, Administration et finance 30 %, preuves chiffrées en aperçu ; matrice, interdits, écartés et carte signée en aperçu. `02-ontologie.md` 8 contrôles. | aucun | 12 min | aucune (trésorerie dite par moi en note) | aucune fiche de service proposée |
| 4 Installation | Hélène | Vault conforme : 00 à 99, 6 skills, 2 sous-agents, hooks `${CLAUDE_PROJECT_DIR}`, `deny` en `Edit` seul, bloc `sandbox`, identité git d'Hélène, lint 0. Dépôt privé `cortex-helene` créé et poussé. Contrôle vivant : lecture OK, `Write` refusé. Sonde du pilote en mode bypass depuis le vault : Python vers `partage` EPERM, vers le vault et le commun OK. | Q-vocab | 6 min | aucune | « Deux réserves… corriger dans le produit » ; réserve fausse « le blocage vient des permissions, pas du sandbox » (ma sonde montre le contraire) |
| 5 Ingest | Hélène | 8 phases demandées en 2 lots ; 3 lots de fiches en aperçu ; 21 notes (8 projets, 6 acteurs, 7 ressources), 0 copie, 0 chemin absolu, lint 0, `04-ingest.md` valide. | m-trace | 5 min | aucune | « Direction commerciale » ajoutée à ma demande |
| 6 Agents métier | Hélène | Spec `lecteur-promesses-de-vente` complète en aperçu avant validation. Promesses de 2 octets : agent non écrit, contrôle arbitré. Résumé des mails refusé et expliqué (canal, pas type de document ; messagerie hors du champ). | Q-vocab (« arbitré ») | 3 min | test sur 3 promesses réelles | aucun |
| 7 Passation | Hélène | 5 contrôles automatiques et 3 liens en aperçu, vérifiés par moi sur disque. White-label fichiers et `git log --all -p` : 0. `remis_le` posé. Guide d'usage et Reprise. Étape 8 : `arbitre`, « en attente de Karim Benali », phrase suivante « clôture ». | m-matrice | 3 min | qui garde le dépôt GitHub | aucun |
| 0 Poste | Karim | Nom court demandé : `karim`. Rien à installer, aucun outil « absent » à tort, options `[]`. Microsoft, non administrateur, softeria refusé : voie `aucune`. | m-nom, m-outils | 2 min | aucune | libellés en identifiants |
| 1 Cadrage | Karim | Second du groupe : lit `config.yaml` et `00-cadrage.md` d'Hélène, rien d'autre. Commun, visibilité et marque repris et affichés (« REPRIS DU GROUPE »), non reposés. Ni `~/Documents` ni `~/Desktop`. Plafonds 5/30/40 en aperçu. `federation.yaml` : 2 membres, `attendus: []`. | aucun | 5 min | aucune | nom d'organisation redemandé |
| 2 Inventaire | Karim | Aucune question, mail non lu, 7 points dont Photos anniversaire. | aucun | 2 min | aucune | aucun |
| 3 Ontologie | Karim | Opérations (même nom et code qu'Hélène, 57 %) et Développement foncier (43 %), preuves en aperçu ; carte signée en aperçu. « je ne lis pas le second cerveau d'Hélène, seulement son cadrage ». | m-PLU | 6 min | Saint-Priest ; PLU | « Direction commerciale » ajoutée à ma demande |
| 4 Installation | Karim | Vault conforme, lint 0, pas de dépôt distant. Contrôle vivant : `Write` refusé. Question de modification d'`etat.py` : refusée. | **P-ecrit (harnais)**, Q-vocab | 3 min | corriger le kit | « Fais tourner `cloture` » |
| 5 Ingest | Karim | Étapes demandées ; 8 fiches en un aperçu ; 4 projets, 1 acteur, 3 ressources ; lint 0. | m-nommage | 3 min | PLU sans étapes | aucun |
| 6 Agents métier | Karim | « Aucun besoin » : zéro agent, dit en rendez-vous, sans question de volume. | aucun | 1 min | aucune | aucun |
| 7 Passation | Karim | Matrice reportée dans le vault (aperçu), 3 liens vérifiés par moi, white-label 0, `remis_le`. Étape 8 `a_faire` et « relie les cerveaux » dans les deux ateliers. | aucun | 3 min | reporter la table « qui fait foi » | 3 liens non désignés |
| 8 Fédération | Hélène + Karim | Voir ci-dessous : 7 tests conformes. | m-nommage | 8 min | régénérer depuis le vault de Karim (refusé, relancé depuis l'atelier) | aucun |

## Fédération

| Test | Résultat |
|---|---|
| 1. `visibilite: commun` sur Caluire et Direction commerciale, clôture dans chaque vault | `_export/helene/` et `_export/karim/` avec `index.json`, 2 notes chacun ; sessions de vault ouvertes sans avertissement de règle |
| 2. « relie les cerveaux » depuis l'atelier d'Hélène | `federe.py` sortie 0 ; Opérations en une note ; Direction commerciale en une note à deux sections « Vu par » ; README « ne pas éditer » ; `.cortex-genere` ; `07-federation.md` valide ; notice 9 sur 9 |
| 3. Relance | `diff -r` contre la copie d'avant : seules les 2 lignes de date du README changent ; empreinte `673b38a6…` identique ; contrôle 3 du skill : 0 |
| 4. Caluire de Karim repassée en `prive`, clôture, relance | sortie 0, `KARIM - Caluire Belvédère` sort du commun, aucune note `prive` au commun (le même grep trouve les 2 notes `commun`) |
| 5. Note privée glissée à la main dans l'export de Karim, hash dans `index.json` | `[X] karim : … porte visibilite: prive`, sortie 1 ; empreintes de tous les fichiers du commun identiques avant et après ; export restauré |
| 6. Ligne ajoutée à `Direction commerciale.md` du commun, en-tête intact | lint d'Hélène : sortie 0 avant, sortie 1 après, « le commun ne correspond plus à son empreinte » ; restauré par relance |
| 7. « relie les cerveaux » depuis `vault-helene` | commun régénéré, commande `notice.py --atelier ~/Cortex/helene/_cortex` donnée ; ateliers intacts (empreintes avant et après) ; fichiers modifiés : le commun seul |

## Points tranchés seul pendant le test

- Adresse Sitadel : « pas sous la main, on s'en sert par ses exports » ; puis « Se contenter des exports ».
- Dossier de référence des opérations corrigé en `partage/Operations`.
- Mentions interdites : ajout de cortex-kit, Cosmos, Mister IA.
- Fiche de service « Direction commerciale » demandée chez les deux (aucune proposée), nécessaire au test de fédération.
- Dépôt GitHub d'Hélène : « transférer à Hélène » (noté, rien exécuté).
- Karim : PLU « en attente » ; modèles hors de sa carte ; matrice reportée ; modification d'`etat.py` refusée.
- Régénération proposée depuis le vault de Karim : « attendre », relance faite depuis l'atelier selon l'annexe.

## Nettoyage (donné, non exécuté)

```bash
rm -rf ~/Cortex/helene ~/Cortex/karim ~/Cortex/alcyon-commun
rm -rf ~/Cortex-test/alcyon            # dont la preuve partage/.claude/.cc-writes
gh repo delete voiesdegypte/cortex-helene --yes
cmux close-surface --surface surface:152; cmux close-surface --surface surface:153
cmux close-surface --surface surface:160; cmux close-surface --surface surface:161
# transcripts à garder jusqu'à lecture du verdict, puis :
rm -rf ~/.claude/projects/-Users-evrard-Cortex-helene-vault ~/.claude/projects/-Users-evrard-Cortex-karim-vault \
       ~/.claude/projects/-Users-evrard-Cortex-helene--cortex ~/.claude/projects/-Users-evrard-Cortex-karim--cortex
```
