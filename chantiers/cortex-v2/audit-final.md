# Audit à froid final — Cortex v2, `main` (2026-09-19)

Auditeur : session neuve, Opus 5, effort `high`. Commit audité : `7d7f62a`, arbre propre avant et après.
Aucun fichier du dépôt modifié. Ce rapport est le seul livrable.

## 1. Replay

| # | Critère | Commande | Sortie | Verdict | Confiance |
|---|---|---|---|---|---|
| 1 | Recette verte, 113 contrôles | `python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?` | `113 contrôle(s) passé(s), 0 en échec.` / `Recette verte.` / `EXIT=0` ; `grep -c '[ok]'` = 113 ; 2,7 s | vert | haute |
| 2 | Grep white-label | `grep -rniE 'evrard\|marcon\|mister ?ia\|misteria\|devprom\|voies? d.egypte\|\bvde\b\|cosmos\|claudia\|kockpit\|evrardmarcon' skills/ notice/ outils/ README.md fabricant/` | zéro ligne, `EXIT=1`. Témoin posé : les 12 empreintes de `MARQUES_EMPREINTES` détectent bien ces 12 formes (script de contrôle exécuté, 14 formes testées, 12 détectées, `cortex` et un faux témoin non détectés) | vert | haute |
| 3 | Chemins absolus | `grep -rnE '/Users/[A-Za-z0-9._-]+/\|/home/[A-Za-z0-9._-]+/\|\b[A-Z]:\\[A-Za-z]' skills/ notice/ outils/ README.md fabricant/` | zéro ligne, `EXIT=1`, sans aucune exclusion, `fabricant/` compris | vert | haute |
| 4 | `ast.parse` sous 3.9 | `/usr/bin/python3` (3.9.6), `ast.parse` de chaque `.py` hors `.git` | `17 fichiers, 0 en echec` | vert | haute |
| 5 | Auto-tests | `python3 <script> --autotest` sur les 16 scripts qui portent l'option | 16 scripts, `rc=0` partout (`fabrique`, `poste`, `scan`, `parcours_blanc`, `rejeu_profil`, `cortex_config`, `etat`, `lint_sante`, `notice`, `rend_notice`, `scaffold`, `session_start`, `stop`, `export`, `copie_structurant`, `federe`). `fixtures.py` n'a pas d'`--autotest` ; la recette le couvre | vert | haute |
| 6 | Scaffold pointeur, copie, `--outillage-seul` | `scaffold.py --config <cfg-pointeur\|cfg-copie> --out <vault>` puis `lint_sante.py --vault <vault>` ; puis `py_compile` d'un hook du vault et du gabarit, et `--outillage-seul` | pointeur : `47 fichier(s)`, `1 racine(s)`, `2 regle(s) deny`, `2 hooks`, `rc=0` ; lint `[OK] Vault sain.` `rc=0`. Copie : idem, lint `rc=0`. `__pycache__` dans `<vault>/.claude/hooks/` : `✓ Outillage rafraichi : 15 fichier(s)`, `rc=0`. `__pycache__` dans le gabarit : idem, `rc=0`. Gabarit remis propre | vert | haute |
| 7 | Fédération, deux générations, lint du commun | `federe.py --fixtures <tmp>` puis `federe.py --config <commun>/federation.yaml` deux fois, `diff -r`, `lint_sante.py --vault <commun>` | `3 membres`, `35 notes`, `14 projets`, `11 acteurs (2 fusionnés)`, `2 domaines`, `rc=0`. `diff -r` : 2 lignes, toutes deux `genere_le` dans `README.md`. Lint du commun `[OK] Vault sain.` `rc=0` | vert | haute |
| 8 | Paquet | `python3 fabricant/scripts/fabrique.py --sortie <tmp>/cortex.zip` | `OK — … : 10 dossiers (9 maillons + 1 annexe), LISEZ-MOI.html, PROVENANCE.md`. Inspection du zip : 10 dossiers racine, 2 fichiers racine, `0` entrée contenant `recette` | vert | haute |
| 9 | Plugin | `claude plugin details cortex@cortex-kit` | `cortex 2.0.0-rc.1`, `Skills (10)` : les 9 maillons plus `stop-slop`, `Agents 0`, `Hooks 0`, `MCP 0` | vert | haute |

Les neuf critères de replay passent. Les mesures ci-dessous sont rejouables telles quelles.

## 2. Défauts

### Majeur

**M-1. L'invariant I10 est contredit à l'intérieur du produit, et la recette ne le voit pas.**
`skills/cortex-1-cadrage/SKILL.md:28` pose que « chaque maillon **propose** le suivant et l'enchaîne après un accord explicite », et `skills/cortex-1-cadrage/references/doctrine.md:53` (amendement daté 2026-08-23) le qualifie en doctrine. Cinq messages de clôture en mode solo se terminent donc par `On enchaîne ?` : `cortex-1-cadrage/SKILL.md:199`, `cortex-3-ontologie/SKILL.md:188`, `cortex-4-installation/SKILL.md:151`, `cortex-5-ingest/SKILL.md:167`, `cortex-6-agents-metier/SKILL.md:139`.
En face, `01-cadrage.md` liste I10 « aucun maillon n'invoque le suivant », `04-contrat.md` (amendement 2026-09-19) écrit « seule la section Notice propose la suite », `cortex-0-poste/SKILL.md:26` et `:129` posent « Aucun maillon n'invoque le suivant » et « Ne jamais enchaîner sur le maillon 1 », et les neuf sections Notice, identiques et conformes au §10, disent « Elle ne l'exécute jamais ».
L'amendement du contrat est postérieur de vingt-sept jours à celui de la doctrine et n'a pas été reporté. `parcours_blanc.py:633` vérifie la présence de la section Notice, jamais l'absence d'enchaînement : les cinq lignes passent la recette.
Effet pour la personne : elle lit `On enchaîne ?`, répond « oui », et obtient deux comportements selon la ligne que l'agent retient. Un agent qui suit I10 lui renvoie la notice alors qu'elle vient de dire oui.

**M-2. Quatre maillons nomment une skill au lieu de la phrase canonique dans leur message de clôture.**
`cortex-1-cadrage/SKILL.md:178` « lance `cortex-2-inventaire` », `cortex-3-ontologie/SKILL.md:163` « Puis lance `cortex-4-installation` », `cortex-4-installation/SKILL.md:129` « lance `cortex-5-ingest` », `cortex-5-ingest/SKILL.md:140-141` « Puis `cortex-6-agents-metier` … Enfin `cortex-7-passation` ».
`cortex-2-inventaire` et `cortex-6-agents-metier` font l'inverse et donnent la phrase : `cortex-2-inventaire:165` « Dis « décidons mes domaines » », `cortex-6-agents-metier:120` « Dis « prépare la remise » ». `cortex-0-poste:104` fait de même. Le produit tient donc deux conventions à la fois. La table `PHRASES` d'`etat.py:63-74` est correcte et la notice rend bien la bonne phrase à chaque état (vérifié : atelier à deux étapes faites, `phrase_suivante` = « lance l'inventaire », rendue dans `notice.html`).

### Moyen

**Y-1. Le zip renvoie à un README qu'il ne contient pas.** `LISEZ-MOI.html` embarqué dans le zip, geste 1 : « collez la ligne d'installation du paquet, donnée dans le fichier README du paquet ». Le zip porte `LISEZ-MOI.html` et `PROVENANCE.md`, rien d'autre à la racine (vérifié sur le zip produit). La personne qui reçoit le zip seul ne trouve pas la ligne d'installation. Le repli « Sans terminal » la débloque, la référence reste morte.

**Y-2. Le vault livré se décrit faux.** `skills/cortex-4-installation/template/vault/90 - Meta/Architecture - Vue d'ensemble.md:70` annonce « `.claude/` 4 skills + 2 sous-agents ». `scaffold.py` pose six skills (`bilan`, `cloture`, `ingest`, `lint`, `nouveau-projet`, `parle`), deux sous-agents et deux hooks, conformes au contrat §9 (vérifié sur le vault scaffoldé). Même compte périmé dans `cortex-1-cadrage/references/doctrine.md:28` et `cortex-6-agents-metier/SKILL.md:42`. La description de `cortex-4-installation`, elle, dit bien « 6 skills, 2 sous-agents, 2 hooks ».

**Y-3. `06-verification.md` décrit un état que `main` a dépassé.** Le fichier ouvre sur « **111 contrôles passés, 2 en échec, sortie 1** », porte C4 à « 14/16 rouge » et décrit l'écart `outillage_seul` comme ouvert. Sur `main`, la recette rend 113/0 et les deux contrôles C4 passent (mesuré). Le lecteur du seul livrable de vérification apprend que la recette est rouge.

**Y-4. M4 manque au tableau imprimé par la recette.** `parcours_blanc.py:94-96` déclare trois contrôles manuels ; `grep -c 'M4'` sur le script rend 0. `06-verification.md:7` annonce « les contrôles manuels M1 à M4 » et documente M4 en fin de fichier. Un opérateur qui se fie à la sortie du script ignore le quatrième contrôle manuel.

### Mineur

**N-1. Comptes périmés hérités de la v1.** `cortex-5-ingest/SKILL.md:8` « Cinquième des sept » ; `doctrine.md:3` et `:75` « les sept maillons » ; la table de `doctrine.md:33-41` liste sept maillons, sans le 0 ni le 8.

**N-2. Ordinaux incohérents entre maillons.** `cortex-0:8` « Premier des neuf » et `cortex-3:8` « Quatrième des neuf, le maillon 0 compris » comptent la position ; `cortex-2:8` « Deuxième des neuf maillons » et `cortex-4:8` « Quatrième maillon » comptent le numéro. Deux conventions pour la même phrase d'ouverture.

**N-3. Vocabulaire d'atelier dans un message adressé à la personne.** `cortex-6-agents-metier/SKILL.md:131` et `:134` emploient « maillon » dans le bloc solo. La notice dit « étape » seize fois et « maillon » zéro fois ; `cortex-1` interdit par ailleurs de prononcer « profil », « régime » ou « pointeur » devant la personne.

**N-4. Forme nue de markitdown dans la prose.** `cortex-2-inventaire/SKILL.md:49` et `scan.py:12` écrivent « `uvx markitdown` », `parcours_blanc.py:96` (libellé M2) aussi. L'amendement §3 du contrat impose `uvx --from "markitdown[all]" markitdown`, « le paquet nu ne lit ni pdf ni docx ». Le code est juste (`scan.py:129`, `poste.py:46-47`) ; seule la prose induit en erreur.

**N-5. `stop-slop` est livré en anglais.** Corps de `skills/stop-slop/SKILL.md` et les trois fichiers de `references/`. La décision 18 dit « Français seul » et les non-objectifs réservent l'anglais à une v2.1. Seule la description est en français. La licence MIT autorise la traduction ; `PROVENANCE.md` couvre l'emprunt.

**N-6. Le contrôle white-label bloquant du maillon 7 n'a pas de garde sur liste vide.** `cortex-7-passation/SKILL.md:63` : `grep -rwiE "<config.marque.mentions_interdites, en alternance>" "$V"`. Avec une liste vide, l'alternance est vide et `grep -rwiE ""` rend toutes les lignes du vault. Le §solo du même fichier dit que la liste est pré-remplie au maillon 1, sans instruction pour le cas où elle ne l'est pas.

**N-7. Le compteur solo ne nomme pas l'étape arbitrée.** `etat.py` `main()` imprime « 8/9 étape(s) faite(s), conduite solo » (mesuré sur un atelier solo complet), là où §5 amendé parle de « 8 faites et 1 arbitrée ». Déjà consigné en observation dans `06-verification.md`, toujours ouvert. La notice HTML, elle, rend « Tout est installé » et la pastille « Arbitré » : la personne n'est pas trompée, l'opérateur si.

**N-8. Trace de v1 dans une note livrée.** `template/vault/90 - Meta/Architecture - Vue d'ensemble.md:78` et `:94` portent « hors v1 », vocabulaire de chantier dans le vault du client.

## 3. Lecture novice, ce qui tient

Les neuf sections Notice sont identiques au caractère près (md5 unique sur les neuf extraits) et conformes au §10. Les neuf phrases canoniques figurent chacune dans la `description` de son maillon, dans les termes de `PHRASES`. La notice hors ligne ne porte aucune URL, dit ce que l'outil ne fait jamais, et affiche à chaque état l'étape courante avec la phrase à prononcer. `cortex-0-poste` est le maillon le mieux tenu du lot : il donne la phrase suivante en clair et interdit explicitement d'enchaîner. `README.md` tient en trois gestes. `outils/OUTILS.md` donne une ligne par outil avec sa commande par OS, sa licence et son verdict. `PROVENANCE.md` couvre l'emprunt unique et reproduit sa notice MIT.

Rien dans le parcours ne laisse la personne sans savoir quoi dire, à condition qu'elle ouvre la notice. Le défaut M-1 la met en revanche devant un produit qui lui pose une question (`On enchaîne ?`) dont la réponse « oui » n'a pas de comportement unique.

## 4. Verdict

Prêt pour la Phase H sous réserve de M-1 et M-2, qui portent sur l'invariant I10 et se corrigent en prose sur six fichiers : trancher entre « la notice propose » et « le maillon enchaîne en solo », reporter l'arbitrage dans `doctrine.md:53` et `cortex-1-cadrage/SKILL.md:28`, remplacer les cinq `On enchaîne ?` et les quatre appels de skill par la phrase canonique de `PHRASES`, et poser dans `parcours_blanc.py` le contrôle qui manque pour que la recette attrape la récidive ; Y-1 à Y-4 se corrigent dans la même passe et n'engagent aucun script. Les mineurs N-1 à N-8 ne bloquent pas le parcours réel et peuvent attendre la Phase I.
