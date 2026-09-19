# Rapport de la reprise C2 (session `fix/C`, 2026-09-19)

Worktree `~/Dev/cortex--C2`, branche `fix/C`, issue de `main` après merge des six lanes.
Aucun push, aucun merge. Un commit : `dc5d4b8`.

## 1. Ce qui a changé

| Point de `consignes-C2.md` | Fichier | Geste |
|---|---|---|
| Bloquant 1, option 1 | `references/profils/{employe,dirigeant,societe}.md` | le « Bloc config proposé » ne garde que `profil`, `mode`, `commun`, `donnees.regime`, `collecte` ; `domaines` et `cycles` retirés, une note sous le bloc dit pourquoi |
| Bloquant 1, prose | idem | les domaines de départ restaient déjà en prose (`## Les domaines de départ`) ; une section `## Le cycle de départ` leur est ajoutée, même statut d'hypothèse |
| Bloquant 1, config | `recette/rejeu_profil.py` | `cadrage()` pose `domaines: []` et `cycles: []` (le gabarit en porte pour l'exemple) ; `domaines_profil()` lit les domaines dans la **prose** du profil et les écrit dans `00-cadrage.md` |
| Critère C2 réécrit | idem | `ATTENDUS = ("domaines:", "cycles:")` et `inattendus()` ; `main` sort en 0 tant que rien d'autre n'est signalé, et distingue `[attendu]` de `[refus]` |
| Défaut 3 | idem, `md_cadrage()` | `statut: brouillon` ; `racines_confirmees`, `plafonds_acceptes`, `mail_optin_trace` à `arbitre` avec le motif « rejeu sans personne ». Les quatre contrôles mécaniques (`redacteur_unique_nomme`, `profil_pose`, `regime_fixe`, `substrats_declares`) restent à `passe` : le rejeu les remplit vraiment |
| Défaut 4 | `git mv` vers `cortex-4-installation/recette/` | `ICI`/`INSTALLATION`/`CADRAGE` recalculés ; dossier `cortex-1-cadrage/scripts/` supprimé ; `cortex-1/SKILL.md:10` le nomme comme outil de recette hors des maillons livrés |
| Mineur 5 | `scripts/cortex_config.py` | helper `mapping(cle)` dans `valider_installable` : un bloc mal formé (`donnees: copie`, `substrats: x`, `collecte: 3`) rend un message qui nomme la clé. `domaines` non-liste est couvert aussi. Les trois blocs sont relus **une fois en tête**, donc un `substrats` mal formé se signale même en régime `pointeur`, où l'ancienne branche ne le lisait pas |
| Mineur 6 | idem, `main()` | `--help` et `-h` impriment `USAGE` et sortent en 0 ; `--autotest` explicite ; sans argument, `--autotest` comme avant |
| Mineur 7 | `cortex-3/SKILL.md:8` | « Troisième des neuf » → « Quatrième des neuf, le maillon 0 compris » |
| Mineur 8 | `scripts/cortex_config.py` | tous les messages de `valider_installable` accentués (les clés, elles, restent ASCII : `parcours_blanc.py`, `scaffold.py` et `lint_sante.py` testent des préfixes de clé, pas des phrases) |
| Mineur 9 | `cortex-1/SKILL.md:44` | tiret cadratin retiré, plus les deux lignes que la reprise touchait par ailleurs |
| I10 | `cortex-1/SKILL.md:202`, `cortex-3/SKILL.md:191` | « Sur accord, lancer `cortex-N` » retiré ; la Notice suffit |

Un seul commit plutôt que cinq : les cinq points se recouvrent sur `rejeu_profil.py` et
`cortex-1/SKILL.md`, et un découpage par fichier aurait raconté une histoire que le travail n'a pas eue.

## 2. Sorties

### Critère C2 réécrit, les trois profils sur les fixtures

```
$ python3 skills/cortex-4-installation/recette/rejeu_profil.py --profil employe   --racine .../fixtures/employe         --atelier /tmp/c2/employe/_cortex
  [attendu] domaines: aucun domaine déclaré. Ils se décident au maillon 3, sur preuve chiffrée tirée de l'inventaire. Installer sans eux produit un vault où rien ne se classe.
  [attendu] cycles: aucun cycle déclaré. `phase` n'aurait alors aucun vocabulaire fermé, et le contrôle qui la vérifie ne pourrait plus rien refuser.
  employe : config.yaml, 00-cadrage.md, 02-ontologie.md écrits dans /tmp/c2/employe/_cortex ; valider_installable : ne signale que ce qui se décide au maillon 3
  rc=0
$ ... --profil dirigeant --racine .../fixtures/dirigeant       --atelier /tmp/c2/dirigeant/_cortex   → mêmes deux [attendu], rc=0
$ ... --profil societe   --racine .../fixtures/societe/camille --atelier /tmp/c2/societe/_cortex     → mêmes deux [attendu], rc=0
```

`charger` relit les trois sans erreur :

```
$ python3 skills/cortex-4-installation/scripts/cortex_config.py /tmp/c2/<profil>/_cortex/config.yaml
employe   : charger rc=0   domaines=[] cycles=[] profil=employe   mode=solo   regime=copie
dirigeant : charger rc=0   domaines=[] cycles=[] profil=dirigeant mode=solo   regime=copie
societe   : charger rc=0   domaines=[] cycles=[] profil=societe   mode=federe regime=copie
```

### `cortex_config.py --autotest` et `--help`

```
$ python3 skills/cortex-4-installation/scripts/cortex_config.py --autotest
OK — config.example.yaml : 2 domaine(s), 2 cycle(s), mode solo
rc=0

$ python3 skills/cortex-4-installation/scripts/cortex_config.py --help
cortex_config.py — chargeur de config.yaml pour Cortex.

    python3 cortex_config.py <chemin/config.yaml>   charge et imprime les clés lues
    python3 cortex_config.py --autotest             rejoue le gabarit config.example.yaml
    python3 cortex_config.py --help                 ce message

Sans argument : --autotest.
rc=0
```

L'auto-test gagne quatre assertions : `donnees`, `substrats`, `collecte`, `domaines` mal formés
doivent rendre un message qui commence par le nom de la clé, jamais un traceback.

### `rejeu_profil.py --autotest`

```
$ python3 skills/cortex-4-installation/recette/rejeu_profil.py --autotest
OK : rejeu des trois profils, cadrage en brouillon, domaines hors config.yaml, écarts en [?], régime pointeur sur base déportée
rc=0
```

Il vérifie en plus, pour chaque profil : `inattendus(erreurs)` vide, `domaines:` bien signalé,
`config.yaml` à `domaines: []` et `cycles: []`, `00-cadrage.md` en `statut: brouillon` avec les
trois contrôles humains à `arbitre`, et les domaines de départ présents dans le cadrage.

### Les cinq blocs `[?]` sur la fixture employé

```
$ grep -c '^\[?\]' /tmp/c2/employe/_cortex/02-ontologie.md
5
$ python3 -c "import json;print(len(json.load(open('.../fixtures/employe/ECARTS.json'))))"
5
```

### Frontmatter du cadrage rejoué (défaut 3)

```
---
maillon: 1
produit_par: cortex-1-cadrage
statut: brouillon
controles:
  redacteur_unique_nomme: passe
  profil_pose: passe
  regime_fixe: passe
  racines_confirmees: arbitre        # rejeu sans personne : nul n'a confirmé la racine
  substrats_declares: passe
  plafonds_acceptes: arbitre         # rejeu sans personne : plafonds repris du profil, non acceptés
  mail_optin_trace: arbitre          # rejeu sans personne : aucun accord de collecte tracé
---
```

### Contrôles de non-régression

```
$ python3 -c "ast.parse(..., feature_version=(3,9))"   cortex_config.py  ok
                                                        rejeu_profil.py   ok
$ grep -rniE "evrard|marcon|mister ?ia|misteria|devprom|egypte|kockpit|cosmos|claudia" <fichiers C>   (aucune)
$ grep -rnE "/Users/|/home/|[A-Z]:\\"                                                   <fichiers C>   (aucun)
$ python3 fabricant/scripts/fabrique.py <zip> --version recette ; entrées "recette" dans le zip : 0
```

Le zip de repli n'embarque pas `recette/` : le déplacement de `rejeu_profil.py` le sort donc
bien du kit installé chez le novice, ce qui était l'objet du défaut 4.

### Recette complète, avant et après

```
$ python3 skills/cortex-4-installation/recette/parcours_blanc.py        # fix/C, depuis ~/Dev/cortex--C2
101 contrôle(s) passé(s), 4 en échec.   rc=1
  C2  Trois profils, régime, section Notice   lane C   11/11 VERT
EN ÉCHEC : C1 le compteur annonce 9/9 quand les neuf lignes sont faites (lane B)
           C1 le tableau de bord vierge affiche neuf lignes à faire (lane B)
           C4 SessionStart lance le lint bref, Stop rappelle la clôture (lane E)
           C10 LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante (lane B)
```

Témoin sur `main`, même commande : `98 contrôle(s) passé(s), 7 en échec`, `C2 11/11 VERT`.
Les quatre échecs ci-dessus y sont déjà, à l'identique. Les trois de plus sur `main` sont
`C3 scan <profil> : chemins en forme ~`, artefact du témoin lancé hors de `~` (§4 des
amendements : « un dépôt cloné hors de `~` produit des chemins absolus, et la recette ne
l'exige alors pas » — le contrôle ne fait pas encore cette exception). Aucun échec, ni avant
ni après, n'est imputable à la lane C ; la reprise fait passer C2 de « vert sur la forme,
invalide sur le fond » à vert sur le fond.

## 3. Points en attente, pour le chef d'orchestre

1. **`06-verification.md` et `03-backlog.md` portent encore l'ancien chemin.** `rapport-C.md`
   (lignes 11 à 30) cite `skills/cortex-1-cadrage/scripts/rejeu_profil.py`. Ces fichiers
   appartiennent au chef et à la lane G ; la reprise ne les a pas touchés.
2. **`skills/cortex-4-installation/SKILL.md:152`, `cortex-5-ingest/SKILL.md:168`,
   `cortex-6-agents-metier/SKILL.md:142` portent encore « Sur accord, lancer `cortex-N` ».**
   L'invariant I10 les vise aussi ; ces trois fichiers sont possédés par la lane E. Valeur
   attendue : la phrase retirée, la section Notice conservée telle quelle.
3. **Les quatre échecs de `parcours_blanc.py` restent ouverts** sur `main` comme sur `fix/C`
   (deux lane B, un lane E, un lane B). Ils ne concernent pas C, et la reprise n'y a pas touché.
4. **Aucune décision n'a manqué.** Les cinq points des consignes ont été exécutés en entier.
