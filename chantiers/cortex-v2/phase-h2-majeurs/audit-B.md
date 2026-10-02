# Audit à froid de la lane B : Phase H2, conduite

Auditeur : Opus 5.5, session neuve, 2026-10-02. Worktree `~/Dev/cortex--h2b`, branche `lane/h2b`, HEAD `e824037`, base `fix/phase-h` = `158d6c0` (= merge-base, vérifié). Méthode : `08-prompt-verification.md` appliqué à la lane B, skill `verifier-avant-de-croire` chargée. Aucun fichier modifié hors ce rapport ; les montages ont tourné dans le scratchpad de la session (copie `git archive`, commun temporaire).

## Verdict

**Lane à reprendre, reprise courte.** Recette verte, périmètre propre, tous les critères cochables de `06-verification.md` passent et les sondes mordent. Mais trois résidus reproduisent directement les majeurs 1 et 4 que le parcours C va mesurer, dans des fichiers de la lane, à quelques lignes des corrections : D1, D2, D3. Une demi-heure de patch, sans toucher au reste. Les autres défauts (D4 à D14) ne bloquent pas le merge.

## Tableau de replay (`06-verification.md`, lane B)

| # | Critère | Commande rejouée | Résultat | Témoin / contre-épreuve | Statut |
|---|---|---|---|---|---|
| 1 | Recette complète | `python3 skills/cortex-4-installation/recette/parcours_blanc.py` sur `e824037` | rc=0, 117 passés, 0 en échec, C1 à C10 VERT | Copie `git archive HEAD` perturbée (cadrage à 319 lignes, `/Users/evrard/...` dans le maillon 0, section Notice retirée du maillon 8) : rc=1, C2 10/12 ROUGE, C8 0/1 ROUGE, C9 1/2 ROUGE, 113 passés, 4 en échec | PASS, calibré |
| 2 | Doctrine | `grep -n "^## " .../doctrine.md` | §8 mots, §9 lecture, §10 validation visible, §11 accord | `git show fix/phase-h:...doctrine.md \| grep "^## "` : s'arrête à §7 | PASS |
| 3 | Renvois des 9 maillons | `grep -L 'doctrine.md\` §8 à §11' skills/cortex-[0-8]-*/SKILL.md` | liste vide ; 9 fichiers sondés, 1 occurrence chacun (`grep -c`) | `git grep -L` même motif sur `fix/phase-h` : les 9 fichiers | PASS |
| 4 | Skills du vault | `grep -L "Devant la personne"` sur les 6 `SKILL.md` du gabarit ; idem `"s'affiche en entier avant la question"` | listes vides ; 6 fichiers, 1 occurrence chacun | `git grep -L` sur `fix/phase-h` : les 6 fichiers | PASS |
| 5 | Maillon 0 | grep des motifs (ateliers en options, `--voie softeria`, `--voie aucune`, petit serveur local, `exactement cette liste`, `à vérifier (<raison>)`) ; grep `zshrc\|bashrc\|export PATH\|modifier un script` | 8 occurrences ; seule mention de script/PATH : l'interdit l. 44 et l. 131 | même grep sur `fix/phase-h` : 0 | PASS |
| 6 | Maillon 1 | grep `~/Documents\|~/Desktop`, `racines:`, `clients que tu as déjà servis`, `--inscrire` | `~/Documents` seulement dans des interdits ; `racines: []` ×3 ; « clients déjà servis » absent du SKILL ; `--export "~/Cortex/<slug>/vault/_export/<slug>"` conforme au §4 | `fix/phase-h` : 8 lignes `~/Documents`/`~/Desktop` dans les profils, « clients que tu as déjà servis » l. 102 | PASS (voir D1 : la phrase survit dans `doctrine.md` l. 27) |
| 7 | Phrases fautives | grep des 7 phrases + « est-il juste » sur `skills/**/*.md` | présentes seulement comme contre-exemples ou dans la doctrine ; le rapport cite le passage qui encadre chacune | **`fix/phase-h` : 0 occurrence pour les 8 motifs.** Les phrases n'étaient pas écrites dans les skills, le modèle les a produites. La sonde « absente » ne discrimine rien | PASS sur la lettre (passage cité), **non calibrable** par grep |
| 8 | Maillon 8, contrôle 3 | montage : 2 exports `export_fictif` (camille, yasmine), `federe.py --config` ×2 à 2 s d'écart, copie témoin, 15 fichiers de chaque côté vérifiés avant lecture | nouveau contrôle 3 : **0** | ancien contrôle 3 (texte `fix/phase-h`) : **2** ; témoin positif, ligne ajoutée dans `20 - Projets/YASMINE - MAG - 2026-002 Gamma.md` : **1** ; angle mort, ligne ajoutée contenant « Généré par » : **0** (D8) | PASS, calibré |
| 9 | Windows | `grep -n -i windows README.md outils/OUTILS.md skills/cortex-7-passation/SKILL.md \| grep -i wsl` | 3 lignes : README l. 12, OUTILS l. 5, passation l. 38 | `git grep -i wsl fix/phase-h -- <3 fichiers>` : rc=1, vide | PASS |
| 10 | Périmètre | `git diff --stat fix/phase-h..HEAD` ; `git diff --name-only ... \| grep -v '\.md$'` | 23 fichiers, tous `.md` ; rc=1 sur le filtre `.py` ; 21 fichiers de la lane + `rapport-B.md` + `05-execution.md` (cochage demandé par le prompt B) ; `README.md` du pack (Statut) non touché | sans témoin (zéro hors périmètre : la liste des 23 a été lue fichier par fichier) | PASS |
| 11 | Prose | `git diff fix/phase-h..HEAD \| grep "^+" \| grep -c "—"` | **0** ; demi-cadratin `–` ajoutés : 0 | même sonde sur les lignes retirées : **5** | PASS |
| 12 | `git status` | `git status --short` | vide avant et après l'audit | sans objet | PASS |
| 13 | Tailles | `wc -l skills/cortex-[0-8]-*/SKILL.md` | 148 à 239, total 1686, identique au rapport | C2 rouge sur la copie perturbée (ligne 1) | PASS |
| 14 | `rejeu_profil.py --autotest` (cité au rapport) | rejoué | rc=0, « OK : rejeu des trois profils… » | sans objet | PASS |

Non-objectifs (`01-cadrage.md`, Exclus) : aucun `.py` touché, donc `export.py`, le bloc `sandbox`, `poser_identite()` intacts ; le diff de `cortex-7-passation/SKILL.md` a trois hunks (limite Windows, une ligne du message de clôture, l'interdit doctrine) et ne touche pas le contrôle d'historique. Titres `^#` identiques avant et après dans 18 des 21 fichiers ; les trois écarts sont des renommages voulus (« Les racines proposées » → « à demander » ×3, « 1. Créer » → « 1. Relire » au maillon 8). Aucune étape déplacée. Questions ajoutées : la question d'accord softeria/mcp-email (exigée par §8) ; voir D13.

Chiffres du rapport remesurés : 117 contrôles (rejoué sur `e824037`, le rapport l'a mesuré sur `bc51816`, seuls des fichiers du chantier diffèrent), 21 fichiers / 187+ 87-, tailles, contrôle 3 « 2 / 0 / 1 » : tous identiques. Un écart : « Dix commits » (l. 3 du rapport), il y en a 12 sur la branche, 11 au commit du rapport (D11).

Interfaces de la lane A citées par la lane B, confrontées à `lane/h2a` (HEAD `e763585`) : `--voie` avec les choix `connecteur|softeria|mcp-email|imap|aucune`, `voie_proposee`, la ligne `<outil> : à vérifier (<raison>)`, `--options` vide sur « aucune », `--inscrire` avec `expanduser` sur `--config`. Concordantes. Sur `lane/h2b` seule, `poste.py` n'a pas `--voie` : la commande du §4 du maillon 0 y échoue (D14).

## Défauts, par sévérité

### Bloquants pour le merge (reprise courte)

**D1. La doctrine définit encore le white-label par « les clients que tu as déjà servis ».** `skills/cortex-1-cadrage/references/doctrine.md:27`, table du §2 : « l'absence, dans le livrable, de ta marque, de tes outils et **des clients que tu as déjà servis** ». Le §11 du même fichier, écrit par la lane, dit l'inverse (décision 6). La session lit le §2 avant le §11. Sur `fix/phase-h`, deux textes portaient cette consigne, `cortex-1-cadrage/SKILL.md:102` et ce §2 ; la lane a corrigé le premier et laissé le second, alors qu'ensemble ils ont produit les six noms d'autres clients chez Hélène (majeur 4). Correctif : une ligne. Sévérité majeure, confiance haute.

**D2. La clôture du vault dit « solo » et « Lint » au client, à chaque clôture.** `skills/cortex-4-installation/template/vault/.claude/skills/cloture/SKILL.md:162-163`, gabarit du récap : `⚠ Lint : <contrôles durs en échec, …>` et `↻ Export : <N notes, ou « solo »>`. La ligne « Devant la personne » ajoutée l. 10 du même fichier l'interdit, comme la doctrine §8 (« solo », nom de skill). Le récap s'affiche trois à dix fois par jour. Même fichier, l. 120 : les avertissements « projet créé sans `nouveau-projet` ? » et « Règle cardinale violée » restent dans le texte que la lane vient d'encadrer par « en phrase ordinaire » (la source de « Accepter l'écart »). Sévérité majeure, confiance haute.

**D3. En mode consultant, le cadrage garde le jargon que l'Interdit proscrit.** `skills/cortex-1-cadrage/SKILL.md:61-74` : la collecte se pose « sous forme de liste compacte » et la liste porte « **Qui porte ce vault** », « Les **substrats existants** ». La traduction n'est donnée qu'en solo (l. 93-99, « Seul le vocabulaire change »), ce qui dit en creux qu'en consultant le jargon se pose tel quel. Contradictoire avec l. 228 (« Ne jamais prononcer … « substrat » ») et avec `04-contrat.md` §5 (« qu'elle soit client ou consultant »). H1 et K1 étaient des cadrages en mode consultant. Même schéma : `skills/cortex-2-inventaire/SKILL.md:32` (« En `solo` … « vos dossiers », pas « les substrats du client » »). Correctif : dire que la traduction vaut dans les deux modes. Sévérité majeure, confiance moyenne (la règle des Interdits peut l'emporter, rien ne le garantit).

### Mineurs

**D4. Noms d'outil et clés dans les messages de clôture des maillons.** Doctrine §8 (« nom d'un skill ou d'un script », clé de config, « rédacteur » ajouté par la lane l. 122) : `cortex-4-installation/SKILL.md:122` « lint : vert », `:123` « 6 skills, 2 sous-agents, 2 hooks » ; `cortex-5-ingest/SKILL.md:133` « lint : vert », alors que la lane a réécrit l. 144 en « contrôle de santé » ; `cortex-7-passation/SKILL.md:138` « kit de 6 skills », `:144-145` « Archive _cortex/ … sauf la ligne remis_le (§6) » ; `cortex-8-federation/SKILL.md:144` « Lint vert, empreinte », `:151` « rédacteur » ; `cortex-2-inventaire/SKILL.md:156` « structurants » ; `cortex-3-ontologie/SKILL.md:155-159` « Ontologie arrêtée », « matrice d'ownership ». Messages lus par le consultant ; le contrat les couvre. Confiance haute, sévérité mineure.

**D5. Le contrôle 1 du maillon 7 promet ce qu'il ne peut plus attraper.** `cortex-7-passation/SKILL.md:91` : « Un vault livré … qui contient le nom d'un autre client … c'est une fuite », sous le contrôle 1 dont la liste ne porte plus que les marques du consultant (décision 6). Le rapport (point 2) assume l'écart de fond, pas la phrase restée. Hors fichiers de la lane, non signalés au rapport : `template/config.example.yaml:70` (« 1. les CLIENTS déjà servis », lu par le cadrage hérité, `cortex-1-cadrage/SKILL.md` §5) et le commentaire `scaffold.py:533` (lane A). Confiance haute, sévérité mineure à moyenne.

**D6. Lectures que la doctrine §9 n'autorise pas.** `doctrine.md:131` ne permet le commun qu'« au maillon 8 », mais `cortex-1-cadrage/SKILL.md:170` exige de savoir qui est « déjà membre de `federation.yaml` » (lecture du commun au cadrage), et `cortex-8-federation/SKILL.md:23` lit `_cortex/06-passation.md` dans le vault des autres membres. `cortex-1-cadrage/SKILL.md:55` fait lire l'atelier du premier rédacteur sans dire comment le trouver : risque de parcours de `~/Cortex`. Le dernier commit de la lane A (`e763585`, `--attendu` déjà membre ignoré) rend la lecture de l. 170 inutile. Confiance moyenne, sévérité mineure.

**D7. Inscription au commun avant la validation des blocs.** `cortex-1-cadrage/SKILL.md:163` place `federe.py --inscrire` en §5, « une fois l'atelier écrit », avant §6 (validation par bloc, l. 172). L'appel crée le dossier commun et `federation.yaml` hors de l'atelier avant que l'identité et l'emplacement du commun soient validés. Confiance moyenne, sévérité mineure.

**D8. Le contrôle 3 du maillon 8 a un angle mort, et son commentaire n'a pas suivi.** `cortex-8-federation/SKILL.md:96` : `grep -vc "Généré par"` écarte toute ligne qui contient ces mots, pas seulement la ligne datée du README. Montage : une édition à la main « Généré par erreur, corrigé à la main » rend 0. Un motif ancré (`"^[<>] Généré par \`federe.py\` le "`) suffit. `:131` garde « diff -r hors genere_le vide ». Confiance haute, sévérité faible (le lint par empreinte de la lane A couvre l'édition).

**D9. Le retrait d'un attendu dépend de l'orthographe exacte.** `cortex-1-cadrage/SKILL.md:170` : `--redacteur` doit égaler la chaîne de `attendus` (contrat §4), le skill ne dit pas de reprendre le nom tel qu'il figure dans la liste du groupe. « Karim BENALI » contre « Karim Benali » laisse l'étape 8 arbitrée pour toujours. Confiance moyenne, sévérité mineure.

**D10. Noms des ateliers d'autres clients proposés en options au maillon 0.** `cortex-0-poste/SKILL.md:34` liste les dossiers de `~/Cortex/` comme options. Sur le poste du consultant, ce sont ses autres clients, affichés dans la session d'un client. Conforme à `04-contrat.md` §8 : risque du contrat, pas faute de la lane, à observer en lane C. Sévérité mineure.

**D11. Rapport : « Dix commits ».** `rapport-B.md:3`. 12 sur la branche. Sans effet.

**D12. Exemple `~/Documents` restant.** `cortex-5-ingest/SKILL.md:70` : `--source "~/Documents/.../PROCESS-affaire.md"`. Suggère la racine que la doctrine §9 bannit par défaut. Très faible.

**D13. Question implicite ajoutée.** `cortex-0-poste/SKILL.md:72` : « ne proposer la connexion que si la personne dit ne pas l'avoir faite » suppose de le lui demander. Dérive légère du non-objectif « aucune question ajoutée ». Très faible.

**D14. Dépendance d'ordre de merge.** Sur `lane/h2b` seule, le §4 du maillon 0 appelle `--voie`, absent de `poste.py` : erreur argparse. Le plan (A puis B) le couvre ; ne jamais merger B sans A.

## Critères non calibrables

- **Phrases fautives du parcours** (critère 7) : aucune n'existait dans le texte de `fix/phase-h`, la sonde « absente » rend 0 des deux côtés. Seul le parcours C dira si la conduite a changé.
- **Lecture bornée (§9), validation visible (§10), accord (§11)** : contrôles de texte seulement. La recette ne mesure pas la conduite (`01-cadrage.md`, Risques).
- **Interfaces de la lane A** : vérifiées par lecture du code de `lane/h2a`, pas exécutées depuis les skills de la lane B.

## Ce qui est bien fait

Les sections §8 à §11 de la doctrine sont fidèles au contrat sans le recopier. Les renvois sont uniformes et sondables. Le maillon 0 couvre les quatre points (nom court, accord softeria, `--options`, « à vérifier ») sans réécriture. Les profils ne proposent plus aucune racine. Le contrôle 3 corrigé tient au montage, et le rapport donne pour chaque critère qui attend zéro le témoin qui rend non-zéro.

## Reprise demandée

1. `doctrine.md:27` : white-label = marques et outils du consultant, sans « clients déjà servis ».
2. `cloture/SKILL.md:162-163` et `:120` : récap sans « Lint », sans « solo » ; avertissements en phrase ordinaire, sans nom de skill.
3. `cortex-1-cadrage/SKILL.md:61-74` et `:95`, `cortex-2-inventaire/SKILL.md:32` : la traduction du vocabulaire vaut dans les deux modes.

Puis recette et greps de `06-verification.md` rejoués. D4 à D9 à traiter dans le même passage s'ils coûtent une ligne, sinon à suivre.
