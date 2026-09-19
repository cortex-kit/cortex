# Audit à froid de la lane F (Opus 5, effort high, 2026-09-19)

Worktree `~/Dev/cortex--F`, branche `lane/F`, protocole `06-prompt-review.md`.
Rien n'a été modifié dans la lane. Ce fichier n'est pas committé.

## 1. Périmètre réel de la lane

`git diff main --stat` liste six fichiers, mais trois sont l'avance de `main`,
pas des écritures de F :

    merge-base : 2e0ee29
    main..HEAD : 677c554, 05075fc, c968705
    HEAD..main : 0c09255, 98463af, 6fe114a   (03-backlog, 04-contrat, README)

Écritures réelles de la lane, par commit :

    c968705  chantiers/cortex-v2/consignes-F.md              |   6 +
    05075fc  skills/cortex-8-federation/SKILL.md             | 157 +
             skills/cortex-8-federation/scripts/federe.py    | 489 +
    677c554  skills/cortex-8-federation/SKILL.md             |  13 +-
             skills/cortex-8-federation/scripts/federe.py    |  25 +-

`chantiers/cortex-v2/rapport-F.md` est non suivi : il ne partira pas au merge.

Conséquence : `lane/F` n'a jamais vu `04-contrat.md` amendé (commit `98463af`).
Les trois exigences de l'amendement §6 sont pourtant appliquées, relayées par
`consignes-F.md`.

## 2. Tableau de replay

| Critère | Commande | Sortie (extrait) | Verdict | Confiance |
|---|---|---|---|---|
| Fichiers touchés dans la colonne « Possède » | `git diff main --stat` + `git show --stat` par commit | voir §1 : deux fichiers possédés, plus `consignes-F.md` | passe sauf `consignes-F.md` | haute |
| Trois exports fictifs donnent un commun | `federe.py --fixtures $T` puis `federe.py --config $T/commun/federation.yaml` | `membres : camille, marc, yasmine` / `notes lues: 35 (dont 3 de journal)` / `domaines 2   projets 14   acteurs 11 (dont 2 fusionnés)` / `empreinte 78b994c617dffbd9ca189eaf14110a918262bd48bacd67684e31c951aca055da`, exit 0 | passe | haute |
| `diff -r` de deux générations hors `genere_le` | `diff -r commun-1 commun \| grep '^[<>]' \| grep -vc genere_le` | `0`, et `diff -r` brut vide | passe | haute |
| Note `visibilite: prive` absente du commun | `grep -rl 'visibilite: prive' $T/commun \| wc -l` | `0` | passe | haute |
| `README.md` généré présent | `ls -a $T/commun` | `.cortex-genere  00 - Centre  10 - Domaines  20 - Projets  40 - Acteurs  60 - Journal  config.yaml  federation.yaml  README.md` | passe | haute |
| Commun vert au lint v1 de `main` | `lint_sante.py --vault $T/commun; echo $?` | `[OK] Vault sain.` puis `exit=0` ; un seul `[i]` mou, 11 `dernier_journal` périmés | passe | haute |
| `--help` sort 0 | `federe.py --help` | usage complet, `exit=0` | passe | haute |
| Auto-test | `federe.py --autotest` | `OK : commun de 14 projets, 11 acteurs (2 fusionnés), 2 domaines, identique sur deux générations, lint v1 vert`, exit 0 | passe | haute |
| Imports stdlib seuls | `grep -nE "^import\|^from" federe.py` | 9 lignes stdlib, plus `32:import cortex_config` et `33:import lint_sante` | **échoue** | haute |
| Marques interdites | `grep -rwiE "evrard\|marcon\|evrardmarcon\|mister ?ia\|misteria\|devprom\|voies d.?egypte\|vde\|cosmos\|claudia\|kockpit" skills/ chantiers/ README.md` | une seule ligne, `skills/stop-slop/SKILL.md` (« quand Evrard dit »), identique sur `main`, hors lane | passe pour F | haute |
| Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\" skills/cortex-8-federation/` | aucune ligne | passe | haute |
| Frontmatter, moins de 300 lignes, section Notice | `wc -l`, puis `diff` de la section contre `main:skills/cortex-7-passation/SKILL.md` | 156 lignes ; `name` et `description` présents ; section Notice **identique** | passe | haute |
| Phrase canonique (amendement §5) | lecture `SKILL.md:3` | `il relie les cerveaux` et déclencheur `"relie les cerveaux"` | passe | haute |
| Amendement §6 : config.yaml du commun, journal, liens neutralisés | lecture plus sortie | `config.yaml` généré, `60 - Journal/<SLUG> - <titre>.md` (3 notes), `1 neutralisés (Note interne)` | passe | haute |
| Contrat §2 : `societe` implique `mode: federe` | témoin, voir défaut 2 | config généré : `profil societe / mode solo`, aucun bloc `donnees` | **échoue** | haute |
| Refus sans toucher le commun | un seul membre ; export absent ; note prive indexée | `exit=1` dans les trois cas, `commun intact apres refus` | passe | haute |
| Note prive **non indexée** dans un export | dépôt hors `index.json` puis `federe.py --config` | `exit=0`, note ni refusée ni signalée, et non copiée | échoue partiellement | haute |
| Critères 3 et 4 sur `notice/` et `outils/` | `ls -d notice outils` | `No such file or directory` (lane B non mergée) | non mesurable | haute |
| Invariants I4, I5, I6, I10 | lecture `SKILL.md` et du code | aucun sous-agent, aucun appel du maillon suivant, commun généré et sans rédacteur | passe | moyenne |

Reproductibilité : les six chiffres et l'empreinte `78b994c6…` du rapport de la
lane se reproduisent au caractère, depuis un dossier temporaire neuf et depuis
un `cwd` étranger au dépôt. Le rapport de la lane est exact.

## 3. Défauts par sévérité

### Bloquant

Aucun.

### À corriger avant merge

**Défaut 1 — dépendance de code vers un fichier de la lane E.**
`skills/cortex-8-federation/scripts/federe.py:33`

    31  sys.path.insert(0, str(_CORTEX4 / "scripts"))
    32  import cortex_config  # noqa: E402
    33  import lint_sante  # noqa: E402

Quatre entrées de `lint_sante.py` sont consommées :

    federe.py:76   lint_sante.parse_frontmatter(texte)
    federe.py:123  lint_sante.en_liste(fm.get("tags"))
    federe.py:127  lint_sante.liens_sortants(str(fm.get("domaine") or ""))
    federe.py:427  lint_sante.lint(commun, ...)        (auto-test)
    federe.py:428  lint_sante.DURS                      (auto-test)

`cortex_config.charger` est imposé par `05-prompt-execution-F.md` (« lit
`federation.yaml` par `cortex_config.charger` »). `lint_sante` ne l'est pas, et
`04-contrat.md` §1 l'attribue à la lane E, qui le réécrit en parallèle
(`lint_sante.py` conditionnel au régime). Le critère 5 de `06-prompt-review.md`
(« ne montre que la stdlib ») échoue mécaniquement, et l'auto-test de F casse
si E renomme une de ces cinq entrées.

**Défaut 2 — le `config.yaml` du commun contredit le contrat §2.**
`skills/cortex-8-federation/scripts/federe.py:158-176`, fonction `config_commun`

Lignes 160-166, telles qu'écrites :

    160  lignes = ["# généré par federe.py, ne pas éditer : ce que lint_sante.py doit connaître du commun",
    161            "version: 1", "conduite: consultant", "profil: societe",
    162            "organisation:", f'  nom: "{nom}"', "  code: commun", '  redacteur: ""', '  courriel: ""',
    163            "mode: solo", "commun:", '  racine: ""', '  export: "_export"', "  visibilite_defaut: commun",
    164            "chemins:", '  dossiers_projets: ""',
    165            "marque:", '  produit_nom: "Cortex"', "  mentions_interdites: []",
    166            "domaines:"]

Deux écarts dans ces sept lignes :

1. `profil: societe` (ligne 161) avec `mode: solo` (ligne 163). `04-contrat.md`
   §2, sémantique de `profil` : « `societe` implique `mode: federe` pour chaque
   rédacteur ». Le commun n'est pas un rédacteur, l'intention se comprend
   (éviter que le lint du commun reboucle sur `commun_edite_main`), mais la
   paire écrite est celle que le contrat interdit.
2. Aucun bloc `donnees` n'est écrit, donc pas de `donnees.regime`.
   `04-contrat.md` §2 le liste parmi les clés de la v2, enum
   `pointeur | copie`.

Mesure des clés réellement produites :

    cles de premier niveau : ['agents', 'chemins', 'collecte', 'commun', 'conduite',
                              'cycles', 'domaines', 'marque', 'mode', 'organisation',
                              'profil', 'sante', 'version']
    bloc donnees present ? -> False
    profil / mode -> societe / solo

Pourquoi c'est un défaut avant merge, et pas une remarque de style : la chaîne
de contrôle est déjà branchée sur `valider_installable`.

    skills/cortex-4-installation/scripts/lint_sante.py:253
        f["contrat_config_invalide"] = cortex_config.valider_installable(conf)

    skills/cortex-4-installation/scripts/lint_sante.py:60-73
        DURS = (
            "contrat_config_invalide",      <-- première entrée
            ...
        )

    skills/cortex-4-installation/scripts/lint_sante.py:445
        return 1 if any(f.get(k) for k in DURS) else 0

Or `03-backlog.md` ligne C annonce exactement l'ajout qui déclenchera cette
entrée : « `cortex_config.py` valide `profil` et `donnees.regime` dans
`valider_installable` », acceptation « refuse `profil: autre` et
`regime: mixte` avec un message qui nomme la clé ». Et l'ordre de merge est
B, C, D, E, F : la lane C passe avant F.

Témoin exécuté, `valider_installable` enrichi des deux contrôles annoncés par
C, puis lint du commun généré :

    DURS en echec -> {'contrat_config_invalide': [
        'donnees.regime: absent ou hors enum (pointeur | copie)',
        'profil societe implique mode: federe']}

Aujourd'hui, sur `lane/F` seule, le lint est vert :

    $ python3 skills/cortex-4-installation/scripts/lint_sante.py --vault $T/commun
    [OK] Vault sain.
    exit=0

    $ python3 - ...  # valider_installable de main, non modifié
    valider_installable -> []

Donc l'acceptation de F est vraie sur sa branche et fausse sur sa cible de
merge. Ce que `consignes-F.md` exige (« Le vault commun genere doit passer
`lint_sante.py`  ») ne tiendra plus une fois C mergée.

Ce que la lane F doit trancher, sans que l'audit le code : `config_commun`
produit-il un `config.yaml` qui satisfait le contrat §2 (donc un bloc
`donnees` avec un `regime`, et une paire `profil`/`mode` cohérente), ou le
commun cesse-t-il d'être décrit comme `profil: societe` ? Les deux lèvent le
défaut ; le choix appartient à la lane, et son effet sur
`commun_edite_main` doit être remesuré, puisque ce contrôle ne se déclenche
que sur `mode == "federe"` avec un `commun.racine` non vide
(`lint_sante.py:367-371`).

### Mineur

**3.** `federe.py:337-392` — `fixtures()` importe `recette/fixtures.py`, possédé
par la lane G, encore ouverte. L'auto-test grave les valeurs qui en dépendent :

    federe.py:417  assert b2["projets"] == 14 and b2["acteurs"] == 11 and b2["fusionnes"] == 2
    federe.py:418  ... "40 - Acteurs" / "Malbrun.md"
    federe.py:420  ... "40 - Acteurs" / "Vinci.md"
    federe.py:422  ... "CAMILLE - AFF - 2025-002 Aménagement bureau Kervran.md"

Un changement de `CLIENTS` (`recette/fixtures.py:243`) met l'auto-test de F au
rouge sans qu'une ligne de F ait bougé.

**4.** `federe.py:59-80` — `lire_export` n'itère que sur `idx["notes"]`. Une note
`visibilite: prive` déposée dans l'export mais absente d'`index.json` n'est ni
refusée ni signalée. Mesure : `exit=0`, et `grep -rl "secret industriel"` sur le
commun rend `0`. Pas de fuite, la note n'est pas copiée ; écart au libellé du
livrable, « refuse une note `visibilite: prive` trouvée dans un export ».

**5.** `federe.py:59-80` — aucun contrôle que `idx["slug"]` corresponde au `slug`
du membre dans `federation.yaml`. Un `export:` mal recopié attribue
silencieusement les notes au mauvais rédacteur, ce que l'invariant I4 vise.

**6.** `federe.py:312-319` — le README généré dit « Généré par `federe.py`, ne pas
éditer », la date vivant dans `genere_le`. `04-contrat.md` §6 cite « généré par
federe.py le `<date>`, ne pas éditer ».

**7.** `federe.py:148-153` — `empreinte()` écarte toute ligne **contenant** la
sous-chaîne `genere_le`, pas la seule clé :

    151  for ligne in p.read_bytes().splitlines(keepends=True):
    152      if b"genere_le" not in ligne:
    153          h.update(ligne)

Une note dont le corps mentionne `genere_le` sort du sceau sans bruit.

**8.** `federe.py:485-486` — unités mélangées dans la même ligne de sortie :
`liens_renommes` compte des occurrences (`len(renommes)`, ligne 325),
`liens_neutralises` des cibles distinctes (`sorted(set(neutralises))`, ligne
325). Affiché « 3 renommés, 1 neutralisés ».

**9.** `federe.py:279` — la fusion d'acteurs rétrograde les titres d'un cran :

    279  c = re.sub(r"^(#{1,5}) ", r"#\1 ", c, flags=re.M)  # un cran sous « Vu par »

Un `## Journal` devient `### Journal`, et le motif `^##\s+Journal\s*$` de
`lint_sante.py:195` ne le reconnaît plus : les contrôles de journal cessent de
s'appliquer aux notes d'acteur fusionnées.

**10.** `federe.py` — la clé `version` de `federation.yaml` et celle d'`index.json`
ne sont jamais lues, alors que `04-contrat.md` §6 les déclare toutes deux.

### Hors lane, pour le chef d'orchestre

**11.** `chantiers/cortex-v2/consignes-F.md`, commit `c968705`, est hors de la
colonne « Possède » de F (`04-contrat.md` §1 attribue `chantiers/cortex-v2/`
hors 06-verification au chef d'orchestre). Le motif est uniforme sur les six
branches et les commits sont signés du chef :

    lane/B  1f50907 Lane B : consignes du chef d orchestre
    lane/C  7608921 Lane C : consignes du chef d orchestre
    lane/D  dcd2852 Lane D : consignes du chef d orchestre
    lane/E  a1fcd17 Lane E : consignes du chef d orchestre
    lane/F  c968705 Lane F : consignes du chef d orchestre
    lane/G  6a96212 Lane G : consignes du chef d orchestre

C'est une livraison du chef sur la branche, pas un débordement de la lane.
À arbitrer une fois pour les six, pas lane par lane.

**12.** `lane/F` est en retard de trois commits sur `main` et n'a jamais lu
`04-contrat.md` amendé. Les trois exigences de l'amendement §6 sont appliquées
quand même, relayées par `consignes-F.md`.

**13.** `skills/stop-slop/SKILL.md` porte le prénom du fabricant. Identique sur
`main` (`git show main:skills/stop-slop/SKILL.md | grep -c "Evrard"` rend `1`).
Annexe conservée par la décision `2e0ee29` ; relève de la lane B et de
`PROVENANCE.md`.

**14.** Tous les commits de `main` et des six lanes portent un seul auteur :

    Evrard Marcon <264784665+voiesdegypte@users.noreply.github.com>

Le dépôt est public (décision 9) et le grep white-label porte sur les fichiers,
pas sur l'historique. La forme `evrardmarcon` figure dans la liste des marques
interdites de l'amendement §11.

## 4. Verdict

**Mergeable, sous condition.**

Le merge lui-même est propre : F ne touche que ce qu'elle possède, aucun
conflit n'est possible sur `skills/cortex-8-federation/`, ses quatre critères
d'acceptation se reproduisent à l'identique et l'idempotence est exacte au
sceau près. Le code est sobre, stdlib, les refus sont vérifiés et ne touchent
jamais le commun.

Ce qui bloque la déclaration « vert » n'est pas dans la lane mais entre les
lanes : les défauts 1 et 2 sont des couplages vers E et C, qui mergent avant F.
Avant de merger F :

1. La lane F tranche le défaut 2 et patche `config_commun`
   (`federe.py:158-176`), puis rejoue `--autotest` et le lint du commun.
2. Le défaut 1 est arbitré : soit `lint_sante` reste importé et la lane E est
   prévenue que quatre entrées sont publiques, soit F cesse d'en dépendre.
3. `--autotest` et `lint_sante.py --vault <commun>` sont remesurés sur l'arbre
   fusionné B+C+D+E+F, pas sur `lane/F` seule.
