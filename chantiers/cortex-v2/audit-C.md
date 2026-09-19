# Audit à froid de la lane C (session neuve, 2026-09-19)

Worktree `~/Dev/cortex--C`, branche `lane/C`, merge-base `2e0ee29`, HEAD `99d9437`.
Rien n'a été modifié dans la lane. Ce fichier est le seul écrit de l'audit, non committé.

Lu : `README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ligne C), `04-contrat.md` en entier
**y compris les amendements du chef** (`98463af`, présents sur `main`, absents du merge-base de la lane),
`05-prompt-execution-C.md`, `rapport-C.md`.

## Tableau de rejeu

| Critère | Commande | Sortie (extrait) | Verdict | Confiance |
|---|---|---|---|---|
| 1. Fichiers hors « Possède » | `git diff main --stat` puis `git diff 2e0ee29..HEAD --stat` | `chantiers/cortex-v2/consignes-C.md \| 6 +` (commit `7608921`) + 9 fichiers tous dans la colonne C | **échoue** (1 fichier) | haute |
| C1 refus `profil`/`regime` | `valider_installable` sur un yaml `profil: autre` / `donnees.regime: mixte` | `profil: 'autre' n'est pas dans ['dirigeant', 'employe', 'societe']…`<br>`donnees.regime: 'mixte' n'est pas dans ['copie', 'pointeur']…` | passe | haute |
| C2 trois rejeux acceptés | `rejeu_profil.py --profil {employe,dirigeant,societe} --racine <fixture> --atelier <_cortex>` | `valider_installable : accepte` × 3, `rc=0` × 3 | **vert sur la forme, invalide sur le fond** (bloquant 1) | haute |
| C3 cinq écarts → cinq `[?]` | `json.load(fixtures/employe/ECARTS.json)` puis `grep -c '^\[?\]' 02-ontologie.md` | `5` / `5` | passe | haute |
| 3. Marques interdites | `grep -rwiE "evrard\|marcon\|mister ?ia\|misteria\|devprom\|voies\|egypte\|vde\|cosmos\|claudia\|kockpit" skills/ chantiers/ notice/ outils/ README.md` | 2 lignes : `template/vault/CLAUDE.md` (« trois voies de fuite », faux positif) ; `skills/stop-slop/SKILL.md` (« Evrard », déjà sur `main`) | passe pour C, échoue hors lane | haute |
| 4. Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\"` sur les fichiers C | `rc=1` (vide). Les 5 occurrences du dépôt sont les motifs de grep eux-mêmes (`lint_sante.py`, `parcours_blanc.py`, `cortex-7/SKILL.md`) et `notice.md` (lane B, `C:\Users\VOTRE_NOM`) | passe | haute |
| 5a. `rejeu_profil.py` | `--help` ; `--autotest` | `rc=0` ; `OK : rejeu des trois profils, écarts en [?], régime pointeur sur base déportée` `rc=0` | passe | haute |
| 5b. `cortex_config.py --help` | idem | `FileNotFoundError: config introuvable : --help`, `rc=1` | **échoue** (identique sur `main`) | haute |
| 5c. Imports stdlib | `grep -nE "^import\|^from"` | `argparse json re sys datetime pathlib` + `import cortex_config` (module du dépôt, chargé par `sys.path.insert`) | passe | haute |
| 6. SKILL.md | `wc -l`, frontmatter, section Notice | `cortex-1` 221 l., `cortex-3` 209 l. ; `name` et `description` présents ; section Notice identique mot pour mot au §10 dans les deux | passe | haute |
| 7. Conformité au contrat | amendements `98463af` §2 vs config produit par le rejeu | contrat : « `config.yaml` garde `domaines: []` jusqu'au maillon 3 ». Config produit : 4 domaines, 4 cycles | **échoue** | haute |
| 7bis. Phrases canoniques §5 | `grep` dans les `description` | « faisons le cadrage » (maillon 1), « décidons mes domaines » (maillon 3) | passe | haute |
| 7ter. `agents.skills` / `hooks` | `git diff` sur `config.example.yaml` | `skills: [cloture, nouveau-projet, ingest, lint, parle, bilan]`, `hooks: [session-start, stop]` = §2 du contrat. Correction d'une divergence réelle, dans le droit de C | passe | haute |
| 8. Invariants | grep sous-agents/`Write`, `lancer \`cortex-` | aucun agent créé par C ; deux lignes héritées « Sur accord, lancer `cortex-N` » (`cortex-1:202`, `cortex-3:191`), encadrées par « le consultant lance » et par la section Notice | passe, réserve mineure | moyenne |
| Merge | `git merge-tree main HEAD` | merge propre, aucun conflit. `main` n'a touché aucun fichier de C depuis le merge-base | passe | haute |
| Recette v1 | `parcours_blanc.py` | `rc=1` sur `lane/C` **et** `rc=1` sur `main`, même cause : `[erreur] skill presentation introuvable dans skills/` | non imputable à C | haute |

## Défauts par sévérité

### Bloquant

**1. Les domaines de départ entrent dans `config.yaml` au maillon 1.**
`skills/cortex-1-cadrage/references/profils/employe.md:70-98`, `dirigeant.md:72-100`, `societe.md:69-100` —
la section « Bloc config proposé », présentée comme « le bloc que le maillon 1 propose avant confirmation »,
porte `domaines:` et `cycles:` remplis. `skills/cortex-1-cadrage/scripts/rejeu_profil.py:80-83` fusionne
ce bloc entier dans `config.yaml`.

Le contrat amendé (`04-contrat.md`, §2 des amendements) dit : « les domaines de départ du profil vont dans
`00-cadrage.md` seulement ; `config.yaml` garde `domaines: []` jusqu'au maillon 3 ».
La lane le répète elle-même, deux fois : `skills/cortex-1-cadrage/SKILL.md:88` (« Les domaines de départ du
profil ne s'écrivent pas dans `config.yaml` ») et `SKILL.md:135` (« `domaines: []` et `cycles: []` restent
vides : ils sont au maillon 3 »). Les artefacts livrés contredisent la prose livrée.

Conséquence sur la preuve : `valider_installable` refuse un `domaines: []` (`domaines: aucun domaine declare`).
Le critère C2 « trois `config.yaml` que `valider_installable` accepte » n'est donc vert que parce que la règle
est enfreinte. Un vrai config.yaml de sortie de maillon 1 ne peut pas passer ce critère — le SKILL.md le dit
d'ailleurs ligne 135 : « `valider_installable` le refusera encore, c'est attendu tant que les domaines manquent ».
Le critère du backlog et le contrat amendé sont incompatibles ; c'est un arbitrage du chef, pas de la lane.

**Arbitrage du 2026-09-19, option 1.** Les trois blocs profil ne gardent que `profil`, `mode`, `commun`,
`donnees.regime`, `collecte`. Les domaines de départ restent en prose, section « Les domaines de départ »,
destinés à `00-cadrage.md` seulement. Le critère C2 de `03-backlog.md` est réécrit par le chef : `charger`
relit les trois `config.yaml` sans erreur, et `valider_installable` ne signale que l'absence de domaines.
La correction est portée par une session de reprise `fix/C` sur l'arbre fusionné, pas par la lane C.

**2. Fichier hors de la colonne « Possède ». — Clos par le chef, motif accepté.**
`chantiers/cortex-v2/consignes-C.md` (commit `7608921`). `chantiers/cortex-v2/` appartient au chef d'orchestre
(`04-contrat.md` §1). Circonstances : fichier écrit par le chef, `main` porte déjà `consignes-G2.md` au même
endroit, merge propre, risque nul. **Arbitrage du 2026-09-19 : livraison du chef, pas un écart de la lane.
Le point est fermé, il ne bloque pas le merge.**

### À corriger avant merge

**3. Le rejeu fabrique une validation.**
`skills/cortex-1-cadrage/scripts/rejeu_profil.py:113-119` — `md_cadrage` estampille `statut: valide` et les sept
contrôles à `passe`, dont `racines_confirmees`, `plafonds_acceptes` et `mail_optin_trace`, sur un cadrage rejoué
sans personne pour confirmer quoi que ce soit. `md_ontologie` (`rejeu_profil.py:160-172`) est honnête au même
endroit : `statut: brouillon`, contrôles à `arbitre`, avec le motif « rejeu sans personne ». L'invariant I11
(« un artefact `_cortex/` non validé arrête la chaîne ») repose entièrement sur ce frontmatter.

**4. Dossier `scripts/` hors arborescence cible, et outil de recette livré dans le plugin.**
`skills/cortex-1-cadrage/scripts/` est nouveau. `02-arbo.md` donne à `cortex-1-cadrage` : `SKILL.md`,
`references/{doctrine,secteurs}.md`, `references/profils/*.md` — pas de `scripts/`. Deux effets : un outil de
recette part dans le plugin installé chez le novice, et il écrit `02-ontologie.md`
(`rejeu_profil.py:160`, artefact du maillon 3) depuis le dossier du maillon 1.

### Mineur

**5.** `skills/cortex-4-installation/scripts/cortex_config.py:352,358` — `valider_installable` lève
`AttributeError: 'str' object has no attribute 'get'` sur un `config.yaml` parseable mais mal formé
(`donnees: copie`, `substrats: x`). Traceback au lieu d'un message qui nomme la clé, dans un produit destiné à
quelqu'un sans compétence technique. Le raccourci existe déjà ligne 296 (`collecte`) ; la lane en ajoute deux.

**6.** `skills/cortex-4-installation/scripts/cortex_config.py:462` — `--help` part en `FileNotFoundError`, `rc=1`.
Pré-existant sur `main`, mais le fichier est désormais possédé par C et le critère 5 de l'audit porte dessus.

**7.** `skills/cortex-3-ontologie/SKILL.md:9` — « Troisième des neuf ». Avec le maillon 0, `cortex-3` est le
quatrième des neuf. Le titre de `cortex-1` a été corrigé au même endroit (« Maillon 1, après l'équipement du
poste »), pas celui-ci.

**8.** `skills/cortex-4-installation/scripts/cortex_config.py:341-360` — messages d'erreur non accentués
(« redacteur », « depart », « genere », « regime », « anterieure ») dans un produit français seul, alors que le
reste du fichier accentue (« Complétude », « décidés »).

**9.** `skills/cortex-1-cadrage/SKILL.md:44` — un tiret cadratin conservé sur une ligne héritée modifiée d'un mot
(« six maillons suivants » → « maillons suivants »). Seule occurrence dans tout le diff de la lane ; déclarée
telle quelle dans `rapport-C.md`.

**10.** `chantiers/cortex-v2/rapport-C.md:2` — la ligne « modifiés » omet `references/profils/*.md` et
`scripts/rejeu_profil.py` comme créations ; la ligne `✎ Modifié` du récap les couvre. Aucune surestimation ailleurs.

### Hors lane, à remonter au chef

**11.** `skills/stop-slop/SKILL.md` porte « Evrard », présent sur `main` depuis `2e0ee29` — le commit qui a
justement réduit le kit d'annexes à cette seule skill. L'exception « les quatre annexes internes connues » du
prompt d'audit n'en couvre plus qu'une, et elle fuit. Le grep white-label de la recette G restera rouge tant
que cette ligne vit. **Arbitrage du 2026-09-19 : le prénom est retiré sur `lane/B`.**

## Arbitrages rendus par le chef d'orchestre (2026-09-19)

| Point | Décision | Qui porte |
|---|---|---|
| Bloquant 1, `domaines`/`cycles` dans `config.yaml` | Option 1. Les blocs profil ne gardent que `profil`, `mode`, `commun`, `donnees.regime`, `collecte`. Domaines de départ en prose, pour `00-cadrage.md`. Critère C2 réécrit : `charger` relit les trois config sans erreur, `valider_installable` ne signale que l'absence de domaines | session de reprise `fix/C` sur l'arbre fusionné ; C2 réécrit par le chef |
| Bloquant 2, `consignes-C.md` | Livraison du chef, motif accepté. Point clos, ne bloque pas le merge | néant |
| Défaut 11, « Evrard » dans `stop-slop` | Prénom retiré | `lane/B` |

## Verdict

**Mergeable, sous réserve de la reprise `fix/C`.**

Au moment de l'audit, la lane portait un défaut bloquant de fond : les blocs `domaines` et `cycles` écrits dans
`config.yaml` au maillon 1, contre l'amendement §2 du contrat et contre la doctrine que la lane écrit elle-même.
Le chef l'a arbitré en option 1 et a porté la correction sur une session de reprise `fix/C` après fusion, pas
sur la lane. Le second bloquant est clos comme livraison du chef. Il ne reste donc aucun bloquant qui s'oppose
au merge de `lane/C` ; la dette de correction est nommée, affectée et datée.

Restent à traiter après merge, par `fix/C` : les défauts 3 et 4 (le rejeu qui estampille `statut: valide` sans
personne pour valider, et le dossier `scripts/` hors arborescence cible qui part dans le plugin), puis les
mineurs 5 à 9.

Le reste est propre, mesuré et honnêtement rapporté : les trois critères d'acceptation tournent, la section
Notice est conforme au mot près, zéro chemin absolu, zéro marque interdite dans les fichiers de la lane, stdlib
seule, merge sans conflit, et `rapport-C.md` ne surestime rien — il déclare même ses propres écarts (tiret
cadratin hérité, recette rouge hors lane).
