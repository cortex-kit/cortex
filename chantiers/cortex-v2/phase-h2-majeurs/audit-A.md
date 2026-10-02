# Audit à froid : lane A (code), Phase H2

Auditeur Opus 5.5, session neuve, 2026-10-02. Worktree `~/Dev/cortex--h2a`, branche `lane/h2a` (`e6a8350`), base `fix/phase-h` (`158d6c0`, merge-base vérifiée). Rien modifié hors de ce fichier, rien commité. Ancien code joué depuis `git archive fix/phase-h` dans `$TMPDIR/old`, chaque fichier vérifié identique au blob de `fix/phase-h` (`git hash-object`) avant lecture des rouges.

## Verdict

**Lane mergeable.** Les quatorze critères cochables de `06-verification.md` (lane A) et les quatre critères « ne mentent pas » passent, remesurés par moi. Aucun bloquant. Un majeur à traiter avant la lane C (M1, faux bloquant du lint sur un commun ouvert dans le Finder) ; il découle du texte du §9 du contrat, donc la décision revient au chef d'orchestre. Onze mineurs et dix points d'information, aucun ne bloque le merge.

## Tableau de replay

| # | Critère (06, lane A) | Commande rejouée | Résultat | Témoin / contre-épreuve | Statut |
|---|---|---|---|---|---|
| 1 | Recette complète, > 117 | `/usr/bin/python3 …/parcours_blanc.py` (3.9.6) ; aussi `python3` 3.14 et sur `git archive HEAD` | sortie 0, 139 passés, 0 échec, les trois fois | `fix/phase-h` : 117, sortie 0 | PASS |
| 2 | Auto-tests | `/usr/bin/python3 <script> --autotest` sur poste, etat, lint_sante, federe, scaffold, scan, session_start, stop, rend_notice | 0 pour les neuf | sonde de code témoin `SystemExit(3)` lue 3 (ma première boucle lisait `$?` après `$(basename)`, invalide, rejouée) | PASS |
| 2b | `ast.parse` 3.9 | `/usr/bin/python3 -c "ast.parse(…)"` sur les 10 `.py` du diff | 10 OK | témoin `match x:` : `SyntaxError` sous 3.9 | PASS |
| 3 | A1 détection | `HOME=<tmp> PATH=/usr/bin:/bin poste.py --dry-run`, faux `graphify` 0755 dans `<tmp>/.local/bin` (montage listé) | graphify absent de la liste | sans binaire (0 fichier) : `graphify : absent → …` ; ancien code, binaire posé : listé absent | PASS |
| 4 | A1 non mesurable | vrai `uvx`/`uv` liés seuls dans un PATH temporaire, `UV_CACHE_DIR` sous un dossier `dr-xr-xr-x`, `command -v markitdown` vide | `markitdown : à vérifier (sonde uvx en échec : … Permission denied (os error 13))` | ancien code, même montage : `markitdown : absent → uv tool install "markitdown[all]"` | PASS |
| 5 | A2 voie | `poste.py --ecrire --atelier <tmp> --mail … --fournisseur m365 --no-open` | `voie: aucune`, `voie_proposee: softeria` ; avec `--voie softeria` : `softeria` | ancien : `voie: softeria` sans `--voie` | PASS |
| 6 | A3 options | même commande | `options_proposees: []` ; `--options aucune` : `[]` | ancien : `['wispr-flow', 'superwhisper', 'noota']` | PASS |
| 7 | A4 lint du commun | `federe.py --fixtures` puis `--config`, ligne ajoutée sous l'en-tête « généré » d'une note, `lint_sante.py --vault --config --json` | constat `{file, raison: MESSAGE_EMPREINTE}` | intact : `[]` ; ancien `lint_sante.py`, note éditée : `[]` (rouge). La recette C6 le joue sur des exports du vrai `export.py` | PASS |
| 8 | A4 une seule empreinte | `grep -n "def empreinte" …/federe.py` | code 1, aucune ligne | `fix/phase-h` : `184:def empreinte(commun):`. Ancien `federe.empreinte` et `lint_sante.empreinte_commun` sur un même commun : `fdca3d39…ba3c` tous deux, égal au sceau écrit | PASS |
| 9 | A5 inscription | `--inscrire helene` deux fois | un membre, `attendus: ["Karim Benali"]`, seul `federation.yaml` dans le commun | dossier étranger (2 fichiers) : sortie 1, sha256 identiques avant et après ; ancien code : option inconnue (code 2) ; mutation `if False and (…)` : C6 rouge `code 0, 6 fichiers` | PASS |
| 10 | A6 attendus | atelier `societe`/`federe`, 00 à 06 valides, `federation.yaml` à un membre remis et un attendu | `arbitre / en attente de Karim Benali / clôture` | ancien : `a_faire / None / relie les cerveaux` | PASS |
| 11 | A6 étape 8 | deux membres, `remis_le:` vide chez karim | `arbitre / en attente de karim / clôture` | les deux remis : `a_faire / relie les cerveaux` ; ancien : `a_faire / relie les cerveaux` dès un remis ; non inscrit : `arbitre / groupe non inscrit` | PASS |
| 12 | A6 statut | `07-federation.md` `statut: en_cours` | état `en_cours` (« En cours ») | ancien : `illisible` | PASS |
| 13 | A7 hooks | `scaffold.py --config template/config.example.yaml --out <tmp>`, grep `settings.json` ; `cd /tmp && CLAUDE_PROJECT_DIR=<vault> python3 <vault>/.claude/hooks/stop.py --autotest` ; commande SessionStart jouée par `sh -c` depuis `/tmp` | l. 36 et 46 ancrées ; `OK stop.py` code 0 ; `Contrôle de santé : 0 problème(s)…` code 0 | commande relative de `fix/phase-h` depuis `/tmp` : `can't open file '/private/tmp/.claude/hooks/stop.py'`, code 2 | PASS |
| 14 | A8 médias | `scan.py --racine <tmp> --out`, 3 `.jpg` dans `Divers/Photos`, 3 `.docx` dans `Divers/Notes` (6 fichiers listés) | un seul `dossier_sans_domaine`, celui des photos | ancien : `[]` ; mutation `docx` ajouté aux médias : C3 rouge, deux candidats ; `.HEIC`/`.MOV` majuscules et `.DS_Store` : candidat posé | PASS |
| 15 | Périmètre | `git diff --name-only fix/phase-h..HEAD` filtré par la liste de la lane | reste `05-execution.md` seul (cases de la lane A, autorisé par le pack) ; `rend_notice.py` ouvert à la lane par §1 et accord d'Evrard | filtre amputé de `poste.py` : les autres fichiers apparaissent | PASS |
| 15b | export.py, sandbox, poser_identite | `git diff … -- …/cloture/export.py \| wc -l` ; grep `sandbox\|poser_identite\|settings_json\|historique` sur les lignes ± | 0 ligne ; 1 seule occurrence, dans la prose de `rapport-A.md` | `a7b7678^..a7b7678` : 41 lignes ; `01955f6` : 3 | PASS |
| 15c | scaffold.py | diff complet | `HOOKS` et un commentaire, rien d'autre | | PASS |
| 16 | Silent-failure | agent `silent-failure-hunter` sur les sept fichiers | aucun `except` neuf qui avale sans trace hors le repli documenté de `dossier_outils_uv` ; sondes `uvx`/`gh` conformes (gh réel du bac à sable : nouveau `(None, '… token in keyring is invalid.')`, ancien `False`) ; deux agrégations restent (M-lint du §9, m3) | voir défauts | PASS avec réserves |

Critères « ne mentent pas » : 22 contrôles ajoutés (139 − 117), recette neuve jouée sur l'ancien code : 17 rouges, 5 verts. Les 5 verts sont 4 témoins voulus (graphify sans binaire, deux remis, `--options noota`, commun intact) et le contrôle de fumée `stop.py --autotest hors du vault`, non discriminant, déclaré tel par le rapport. Mutation du tri de rejeu de `scan.py` (`and False`) : la recette reste verte, seul l'auto-test de `scan.py` tombe ; ce comportement n'a pas de contrôle de recette.

Chiffres du rapport remesurés : 117 et 139, 22 contrôles (C1 12, C3 1, C4 4, C6 5), sortie 0, `fdca3d39…ba3c`, les rouges de contre-épreuve cités (A1, A2, A3, A4, A5, A6, A7, A8) : tous conformes. Vaults de la Phase H : 0 fichier modifié depuis le 2026-09-29 dans `~/Cortex/helene`, `karim`, `alcyon-commun` (témoin depuis le 2026-09-20 : 140, 126, 15).

Non calibré par moi : comportement sous Windows (M3 manuel) ; expansion réelle de `${CLAUDE_PROJECT_DIR}` par Claude Code (simulée par `sh -c`) ; contrôles manuels M1, M2, M4.

## Défauts

### Majeur

**M1. Un `.DS_Store` déposé par le Finder dans le commun déclenche un faux bloquant dans chaque vault membre.** `skills/cortex-4-installation/scripts/lint_sante.py:297`. `empreinte_commun` hache tout fichier hors `.cortex-genere`, `.git`, `.obsidian`. Reproduit : commun généré, lint `--bref` « 0 problème(s) bloquant(s) » ; un `.DS_Store` posé dans `20 - Projets/`, « 1 problème(s) bloquant(s) », `commun_edite_main` étant un contrôle DUR. Même effet attendu avec `Thumbs.db` ou `desktop.ini` sous Windows. Le hook SessionStart l'affiche à chaque session. Le texte du §9 prescrit exactement ces exclusions : la lane l'a suivi à la lettre, mais c'est elle qui rend la comparaison effective. Correctif probable : exclure les fichiers cachés (nom commençant par `.`) et les deux fichiers Windows, dans `empreinte_commun` seule, puisque `federe.py` l'appelle aussi. Demande un amendement du §9. Confiance haute.

### Mineurs

- **m1. `etat.py` plante sur un `federation.yaml` mal formé ou illisible.** `etat.py:141-142` et `155`. Seul `ValueError` est rattrapé. `membres: [helene]` (liste de chaînes) : `AttributeError: 'str' object has no attribute 'get'`, traceback, aucun `etat.json`, donc plus de notice pour tout l'atelier. Même chose pour un `PermissionError` sur `federation.yaml` ou sur un `06-passation.md` membre (`etat.py:124`), reproduit par l'agent. Le reste d'`etat.py` lit ses fichiers sans plus de garde, mais ce chemin est neuf. Confiance haute.
- **m2. `attendus` écrit en scalaire s'épelle lettre par lettre.** `etat.py:136`. `attendus: Karim` donne « en attente de K, a, r, i, m ». Confiance haute (reproduit).
- **m3. Un membre sans `export` se lit « en attente de <slug> ».** `etat.py:141-142`. La raison est la même que pour un rédacteur non remis, et le chemin testé devient un dossier voisin du commun. `federe.py --config` refuserait ce fichier, donc le défaut est borné. Confiance haute pour le message, basse pour le faux « remis ».
- **m4. `--inscrire` écrit tel quel un `--export` relatif.** `federe.py:409`. Lancé depuis `$D` avec `--export karim/vault/_export/karim`, le fichier porte `export: "karim/vault/_export/karim"`, que `federe.py` (l. 216) et `etat.py` résolvent par rapport au dossier du commun, donc vers un autre vault. Le §4 dit « le chemin s'écrit en forme `~` » : il suffit de résoudre le chemin avant `_tilde`. Confiance haute (reproduit).
- **m5. Un second `--ecrire` sans `--voie` efface l'accord donné.** `poste.py:278` et `367`. Après `--voie softeria`, un `--ecrire --options aucune` sans `--voie` réécrit `voie: aucune` et `mail_voie: aucune` dans `config.yaml` ; les options suivent la même règle. Les outils installés, eux, se conservent (`deja_par_cortex`). La lane B doit donc répéter `--voie` et `--options` à chaque `--ecrire`, sinon la réponse acquise (§8) se perd. Confiance moyenne sur l'usage réel, haute sur le comportement.
- **m6. Un commun sans `.cortex-genere` n'est jamais signalé.** `lint_sante.py:484`. Une fédération interrompue entre `vider()` et l'écriture du sceau, ou un sceau supprimé, laisse un commun partiel que le lint ne voit pas. Confiance moyenne (lecture de code).
- **m7. Un fichier illisible du commun fait planter le lint.** `lint_sante.py:290-305`, `read_bytes` sans garde ; la boucle `*.md` juste au-dessus avait déjà ce défaut. Reproduit par l'agent (`chmod 000`). Confiance haute.
- **m8. `dossiers_projets` non scalaire fait planter le scan.** `scan.py:338`, `Path(list)` lève `TypeError`. Confiance moyenne (non rejoué via un vrai `config.yaml`).
- **m9. Libellé du constat d'empreinte.** `lint_sante.py:504`. La sortie lisible annonce « 1 note(s) du vault commun editee(s) a la main » puis la racine du commun, en chemin absolu. Cosmétique. Confiance haute.
- **m10. La sonde markitdown laisse `:memory:.ses` dans le dossier temporaire du système.** `poste.py:83` et `126`, `cwd=tempfile.gettempdir()` partagé. Constaté : `/tmp/claude-501/:memory:.ses` daté de 21:40, pendant la lane. Un `TemporaryDirectory()` le supprimerait. Confiance haute.
- **m11. Traçabilité.** `05-execution.md` A10 annonce « recette 138/138 » alors que la branche en compte 139 (le contrôle de notice d'A9 vient après). A9, A10, A11 n'y portent pas de hash, et le rapport écrit « commit de clôture » et « ce commit » (`383f0b9`, `e6a8350`). Confiance haute.

### Information

- i1. `session_start.py:20`, `stop.py` : avec un `CLAUDE_PROJECT_DIR` qui pointe vers un dossier inexistant, les deux hooks se taisent (sortie vide, code 0), et `stop.py` confond ce cas avec un `git` absent sous son `except FileNotFoundError`. Comportement antérieur à la lane, Claude Code pose une valeur valide.
- i2. Un jeton gh réellement expiré se lit désormais `connecte: null` (« à vérifier ») et non `false`, conformément au §2.
- i3. Hors ligne, sans markitdown, le dry-run dit « à vérifier » au lieu de proposer l'installation, conformément au §2.
- i4. `etat.py:136-139` : quand des attendus existent, la raison ne nomme qu'eux, même si un membre inscrit n'est pas remis.
- i5. Interprétations du rapport (point 4) : `brouillon` lu « En cours » et groupe à un membre arbitré « en attente d'un second rédacteur ». Les deux sont cohérentes avec la règle générale du §3 et avec le refus de `federe.py` sous deux membres.
- i6. Sous un PATH réduit, `--dry-run` imprime `[prérequis] Homebrew absent → …`, que le motif de la recette C1 refuserait. La recette tourne avec brew présent, et ce comportement existait déjà.
- i7. `federation.yaml` entre dans l'empreinte (rapport, point 5) : une inscription après génération rend le commun « périmé », en contrôle DUR, jusqu'à la fédération suivante.
- i8. `recette/rejeu_profil.py:135` lit `present: null` comme absent (rapport, point 8).
- i9. `scan.py` ne regarde que les fichiers directs d'un dossier : un dossier de photos dont un sous-dossier contient des documents reste candidat.
- i10. `dossier_outils_uv` (`poste.py` l. 105) avale l'échec de `uv tool dir --bin` sans trace : repli du contrat, sans effet sur `present`.

## Agent silent-failure, confronté au critère

L'agent remonte dix constats ; le rapport de la lane en citait deux. Retenus ci-dessus : m1 (pour `PermissionError` et `membres` mal formé), m3, m6, m7, m8, i1, i10. L'agent classe m1 « critique » : je le classe mineur, parce que l'erreur sort en traceback visible et non en silence, et que `federation.yaml` n'est écrit que par `--inscrire`. Il classe i1 « majeur » : c'est le comportement de `fix/phase-h` (`os.environ.get("CLAUDE_PROJECT_DIR") or …` inchangé), donc pas une régression. Le message d'empreinte qui réunit deux causes est fixé mot pour mot par le §9.
