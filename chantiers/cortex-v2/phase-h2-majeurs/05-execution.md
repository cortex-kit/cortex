# Exécution : Phase H2

Cocher chaque case avec le hash du commit qui la porte.

## Préparation (chef d'orchestre)

- [ ] `git -C ~/Dev/cortex worktree add ~/Dev/cortex--h2a -b lane/h2a fix/phase-h`
- [ ] `git -C ~/Dev/cortex worktree add ~/Dev/cortex--h2b -b lane/h2b fix/phase-h`
- [ ] Recette verte sur `fix/phase-h` avant de lancer : `python3 skills/cortex-4-installation/recette/parcours_blanc.py`, sortie 0.

## Lane A : code (worktree `~/Dev/cortex--h2a`)

Commits sur `lane/h2a`, messages « Lane H2A : … ». Un correctif, un commit, son contrôle de recette dans le même commit.

- [x] A1. (`65a1267`) `poste.py` détection (§2) : binaire, dossier des outils de `uv`, puis sonde ; `present: null` avec `raison` quand la sonde échoue sans prouver l'absence ; `--dry-run` dit « à vérifier ». Auto-test mis à jour.
- [x] A2. (`50106cc`) `poste.py` voie mail (§2) : `--voie`, `voie_proposee`, aucune voie qui installe sans `--voie`. Auto-test : `m365` non admin sans `--voie` écrit `aucune` et `voie_proposee: softeria`.
- [x] A3. (`6408268`) `poste.py` options (§2) : liste vide sans `--options` ou avec `aucune`. Recette l. 348 alignée.
- [x] A4. (`59c040e`) `lint_sante.empreinte_commun()` et `federe.py` qui l'appelle (§9) ; `commun_edite_main` compare à `.cortex-genere`. Recette : un commun généré puis une note éditée en gardant son en-tête doit être signalé.
- [x] A5. (`5c14e50`, puis `e763585` : `--attendu` déjà membre ignoré avec un message, consigne du chef d'orchestre) `federe.py --inscrire` (§4), auto-test : création, ajout, remplacement, `attendus` ajoutés puis retirés à l'inscription du même nom, idempotence, refus sur dossier étranger ; `cortex_config.charger` relit le fichier.
- [x] A6. (`2a11809`) `etat.py` étape 8 (§3) et statut `en_cours`. Auto-test : groupe non inscrit, un attendu restant, un membre non remis, tous remis, commun validé.
- [x] A7. (`72ed49a`) Hooks (§10) : `HOOKS` de `scaffold.py`, `session_start.py` et `stop.py`. Recette : `settings.json` porte `${CLAUDE_PROJECT_DIR}` ; `stop.py --autotest` lancé depuis un autre dossier que le vault sort en 0.
- [x] A8. (`cc28331`, puis `2e2253b` : retrait au rejeu, retour du contrôle silent-failure) `scan.py` : dossier de médias seuls hors projets en `dossier_sans_domaine`. Auto-test ou recette C3 : trois `.jpg` dans `Divers/Photos` donnent le candidat.
- [x] A9. (rien pour `present: null`, aucun lecteur dans la notice ; `e6a8350` : libellé de l'étape 8 en groupe, sur accord d'Evrard du 2026-10-02) `rend_notice.py` seulement si nécessaire pour `present: null`.
- [x] A10. (recette 139/139, contre-épreuves dans `rapport-A.md`, `383f0b9`) Recette complète verte, puis contre-épreuves de `06-verification.md` (lane A) jouées et consignées.
- [x] A11. (`rapport-A.md`, `383f0b9`) `rapport-A.md` : fichiers touchés, hashes, sortie de chaque commande d'acceptation, contre-épreuves, points en attente.

## Lane B : conduite (worktree `~/Dev/cortex--h2b`)

Commits sur `lane/h2b`, messages « Lane H2B : … ».

- [x] B1. `doctrine.md` : sections §5 (mots), §6 (lecture), §7 (validation visible), §8 (accord, réponse acquise, marque, atelier existant), en prose de la doctrine, sans recopier le contrat mot pour mot. Fait : `69b87fe`.
- [x] B2. Chaque SKILL.md des maillons 0 à 8 renvoie à ces sections dans ses règles, en une ligne. Fait : `0b9562d`.
- [x] B3. Maillon 0 : nom court demandé dès qu'un atelier existe ; question softeria avec ce qu'elle pose, `--voie` selon la réponse ; `--options` porte le choix de la personne ; outil « à vérifier » dit comme tel, sans question de développeur (pas de proposition de modifier un script ou la configuration du shell). Fait : `96bbf21`, `bc51816`.
- [x] B4. Maillon 1 : aucune phrase avec un mot du §5 ; racines demandées, jamais proposées depuis le disque ; liste de marque sans nom de client, décision de groupe reprise et annoncée chez le second rédacteur ; récapitulatif affiché avant chaque validation ; `federe.py --inscrire` en fin de cadrage en groupe, avec `--redacteur` et un `--attendu` par autre rédacteur nommé (`04-contrat.md` §4). Fait : `b4b331e`.
- [x] B5. Maillons 2 à 7 : chaque phrase fautive relevée au parcours corrigée (liste dans `06-verification.md`, lane B) ; tout « … est-il juste ? » précédé du contenu ou porté par un aperçu. Fait : `4c9d8fd`, `bc51816`.
- [x] B6. Maillon 7 : la limite Windows dans le guide de remise. Fait : `2885e04`.
- [x] B7. Maillon 8 : lancement depuis l'atelier ; depuis un vault, commun généré et commande `notice.py` donnée ; contrôle 3 qui exclut la ligne « Généré par ». Fait : `836ad9b`.
- [x] B8. `README.md` et `outils/OUTILS.md` : la limite Windows, WSL2 recommandé pour un poste sensible. Fait : `b515da2`.
- [x] B8bis. Skills du vault (`template/vault/.claude/skills/*/SKILL.md`) : une ligne par skill pour les mots (§5) et la validation visible (§7), sans renvoi à la doctrine, absente du vault. Fait : `fd5d932`.
- [x] B9. Recette complète verte sur `lane/h2b` (elle vérifie tailles, Notice, marques, chemins), plus les greps de `06-verification.md`, lane B. Fait : `45a2da9` (recette 117 verts sur `bc51816`, sorties dans `rapport-B.md`).
- [x] B10. `rapport-B.md`. Fait : `45a2da9`.

## Points d'arrêt

- **Fin de A et fin de B** : rapport au chef d'orchestre, puis arrêt. Pas de merge.
- **Audit à froid** de chaque lane, session neuve (`08-prompt-verification.md`). Une lane à reprendre repart dans sa session d'origine avec la liste de l'audit.
- **Merge** par le chef d'orchestre : `lane/h2a` puis `lane/h2b` dans `fix/phase-h`, recette verte après chaque merge, plugin passé en 2.0.0-rc.7.
- **Lane C** lancée seulement ensuite, sur accord d'Evrard.

## Lane C : parcours (session pilote, `~/Cortex`)

- [ ] C1. Préparation de l'annexe : mémoire du pilote neutralisée, bac à sable neuf, vaults et commun de la Phase H supprimés sur accord.
- [ ] C2. Parcours complet selon `annexe-parcours-alcyon.md`.
- [ ] C3. `~/Cortex-test/verdict-phase-h2.md` rempli, défauts par gravité, décision selon la règle.
