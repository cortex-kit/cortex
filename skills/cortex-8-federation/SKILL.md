---
name: cortex-8-federation
description: Maillon 8 de la chaîne Cortex, réservé au profil société : il relie les cerveaux. Relie plusieurs vaults (un par rédacteur) à un vault commun généré par federe.py depuis leurs exports _export/<slug>/, jamais édité à la main, régénéré à l'identique à chaque passage. Déclencher quand la personne dit "maillon 8", "fédération", "relie les cerveaux", "relie nos cerveaux", "le commun", "regénère le commun", ou quand au moins deux vaults membres ont fait une clôture. Ne PAS utiliser pour un vault solo (l'étape vaut alors « arbitrée »), ni pour écrire dans un vault membre.
---

# cortex-8-federation : plusieurs cerveaux, un commun

Une société, ce sont plusieurs personnes, donc plusieurs vaults : un vault, un rédacteur, toujours. Ce maillon les relie sans mélanger les mains. Chaque rédacteur garde son vault et décide, note par note, de ce qui part au commun. Le commun est un dossier généré par `federe.py`, en lecture seule, que l'on peut jeter et refaire à tout moment.

## Positionnement

- **Le commun n'a pas de rédacteur.** Personne n'y écrit. Un fait s'y corrige en corrigeant le vault qui le possède, puis en relançant la fédération.
- **Le commun est régénérable à coût nul.** Deux passages sur les mêmes exports rendent les mêmes fichiers, à `genere_le` près. C'est l'invariant I5 de la v1, rendu exécutable.
- **Rien de privé n'y entre.** Une note `visibilite: prive` trouvée dans un export arrête la génération avant que le commun soit touché.

## Étape 0 : quand la fédération commence

Quatre conditions, toutes vérifiables :

1. Le profil est `societe` : chaque rédacteur a un vault installé (maillon 4) avec `mode: federe` et le même `commun.racine` dans son `config.yaml`, en forme `~`.
2. **Au moins deux vaults membres sont remplis** et ont fait une clôture : `<vault>/_export/<slug>/index.json` existe chez chacun. L'export est écrit par la skill `cloture`, jamais à la main.
3. Le dossier commun est accessible en lecture par tous les membres : dossier synchronisé, ou dépôt git privé (federe.py conserve `.git` et `.obsidian` quand il vide le dossier).
4. **Tout le groupe est remis** : chaque membre de `federation.yaml` porte `remis_le` dans `<vault>/_cortex/06-passation.md`, et la liste `attendus` est vide. C'est la règle du tableau de bord : tant qu'un rédacteur manque, l'étape vaut « arbitrée, en attente de <noms> » et la notice ne propose pas « relie les cerveaux ».

Sans la condition 2 ou la condition 4, s'arrêter et dire, en mots ordinaires, qui manque encore : une fédération à un seul membre n'est qu'une copie, et `federe.py` la refuse ; un commun relié avant que tout le groupe soit remis montre une équipe incomplète comme si elle était entière.

**Où se lance ce maillon.** Depuis la session de l'atelier, dans `~/Cortex/<slug>/` de la personne qui tient le commun : c'est là que vivent `_cortex/07-federation.md` et la notice. Une session ouverte dans un vault est confinée en écriture au vault et au commun ; elle ne peut pas écrire l'atelier, et son confinement ne s'élargit pas pour ça. Lancé depuis un vault, le maillon génère le commun (§2), le vérifie (§3), rend le résumé, puis s'arrête sans écrire l'état : il dit de relancer « relie les cerveaux » depuis la session de l'atelier, où la régénération est identique à `genere_le` près et où l'état s'écrit, et il donne la commande de la notice à jouer côté atelier, chemin du plugin résolu :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier ~/Cortex/<slug>/_cortex

En mode `solo`, ce maillon ne s'exécute pas. L'étape 8 du tableau de bord vaut `arbitre` avec la raison « vault solo » ; rien d'autre à faire.

## 1. Relire `federation.yaml` dans le commun

C'est le seul fichier du commun qui ne se régénère pas, et il vit là parce qu'il n'appartient à aucun rédacteur (contrat 04 §6). Il existe déjà : le cadrage de chaque rédacteur l'a créé ou complété par `federe.py --inscrire` (`cortex-1-cadrage` §5). Le relire et vérifier qu'il nomme tout le groupe ; un rédacteur absent s'inscrit par la même commande, jamais à la main. Sa forme :

```yaml
version: 1
nom: "Ateliers Roumier"
referentiel: "~/Library/CloudStorage/OneDrive-Exemple/Commun/Référentiel"
membres:
  - { slug: camille, redacteur: "Camille Roumier", export: "~/Cortex/camille/vault/_export/camille" }
  - { slug: yasmine, redacteur: "Yasmine Haddad", export: "~/Cortex/yasmine/vault/_export/yasmine" }
attendus: ["Marc Lefort"]
```

Règles :

- `slug` est le code du rédacteur, identique au nom de son dossier d'export. Il devient le préfixe des projets et des notes de journal dans le commun : `20 - Projets/<SLUG> - <titre>.md`, `60 - Journal/<SLUG> - <titre>.md`.
- `export` pointe le dossier `_export/<slug>/` du membre, en forme `~`. Un chemin relatif se lit depuis le dossier du commun.
- `redacteur` et `attendus` servent au tableau de bord : un nom dans `attendus` est un rédacteur annoncé au cadrage et pas encore cadré. `federe.py --config` les ignore pour générer le commun.
- `referentiel` est le dossier commun de l'entreprise (procédures, charte, signatures, modèles, assistants), en forme `~`. C'est une décision de groupe : le premier rédacteur qui le déclare au cadrage le pose par `federe.py --inscrire … --referentiel "<chemin>"`, les suivants le reprennent tel quel, et un autre chemin donné plus tard est ignoré avec un message. Vide ou absent, le groupe n'en a pas, et le commun reste ce qu'il était. Présent, `federe.py` écrit `50 - Ressources/Référentiel commun.md` (le chemin et son sommaire `AGENTS.md`) et une ligne « Dossier commun » dans `00 - Centre/Centre.md` ; aucune procédure n'entre dans le commun, il y renvoie.
- Un membre s'ajoute par `federe.py --inscrire`, au cadrage. Un membre se retire par la suppression de sa ligne : ses notes disparaissent du commun au passage suivant.
- Le fichier se lit avec le même parseur que `config.yaml` : une ligne par membre, dict inline, pas de commentaire en fin de ligne.

Ne rien mettre d'autre dans le commun. Tout ce qui n'est pas `federation.yaml`, `.git` ou `.obsidian` est effacé à chaque génération.

## 2. Générer, ou régénérer

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/federe.py" --config "<commun>/federation.yaml"
```

Le script lit chaque `index.json`, vérifie le hash de chaque note exportée, refuse toute note privée, puis vide le commun et le réécrit :

| Dans le commun | Contenu |
|---|---|
| `00 - Centre/Centre.md` | index par rédacteur, puis par domaine |
| `10 - Domaines/<nom>.md` | domaines fusionnés par nom, avec `source_vault: [a, b]`, la liste des projets et des acteurs rattachés |
| `20 - Projets/<SLUG> - <titre>.md` | la note du membre telle quelle, `source_vault: <slug>` ; jamais fusionnée, deux rédacteurs qui suivent la même affaire donnent deux notes |
| `40 - Acteurs/<nom>.md` | un acteur présent chez deux rédacteurs donne une note unique, `source_vault: [a, b]`, chaque vue sous un titre « Vu par <slug> » |
| `60 - Journal/<SLUG> - <titre>.md` | les décisions partagées, telles quelles, `source_vault: <slug>` ; dossier ignoré par le lint |
| `config.yaml` | dérivé des exports (domaines, cycles), pour que `lint_sante.py` puisse lire le commun |
| `README.md` | « Généré par `federe.py` le <date>, ne pas éditer », et `genere_le` dans l'en-tête |
| `.cortex-genere` | sha256 de l'ensemble hors `genere_le` : deux générations identiques donnent la même empreinte |

Ce que le script fait aux liens : un lien vers un projet ou une note de journal du même rédacteur suit le renommage ; un lien vers une note qui n'est pas dans le commun (note privée, note de méthode) devient du texte simple. Le titre d'une note privée ne voyage pas dans un dossier partagé, et le commun ne porte jamais un lien mort.

Relancer après chaque clôture d'un membre, ou une fois par jour. Idempotent : dix passages ne changent que `genere_le`.

Le script refuse et sort en 1, sans rien effacer, quand : un membre manque d'export, un hash ne correspond plus (relancer la clôture du membre), une note porte `visibilite: prive`, la `version` de `federation.yaml` ou d'un `index.json` n'est pas 1, le `slug` d'un `index.json` ne nomme pas le membre que `federation.yaml` lui attribue, ou le dossier cible n'est pas vide et ne porte pas `.cortex-genere` (ce n'est pas un commun, rien n'est touché).

Il signale sans refuser une note trouvée dans un export mais absente de son `index.json` : elle n'est jamais copiée, et sa présence dit que l'export du membre est périmé. Relancer la clôture chez lui.

## 3. Vérifier

```bash
C="<commun>"

# 1. Le commun passe le lint tel quel, avec le config.yaml généré
python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/lint_sante.py" --vault "$C"   # attendu : exit 0

# 2. Rien de privé
grep -rl "visibilite: prive" "$C"                                                             # attendu : vide

# 3. Deux générations identiques hors genere_le
cp -R "$C" "$C-temoin" && python3 "${CLAUDE_SKILL_DIR}/scripts/federe.py" --config "$C/federation.yaml"
diff -r "$C-temoin" "$C" | grep "^[<>]" | grep -v genere_le | grep -vc '^[<>] Généré par `federe.py` le '   # attendu : 0
rm -r "$C-temoin"

# 4. Le sceau
test -f "$C/.cortex-genere" && test -f "$C/README.md"
```

Le contrôle 3 ignore les deux lignes datées, `genere_le` et « Généré par … le <date> » du `README.md` : elles changent à chaque passage par construction.

Chez chaque membre, le lint en `mode: federe` ajoute un contrôle : toute note du commun sans la marque « généré » est signalée comme éditée à la main, et un commun qui ne correspond plus à son empreinte `.cortex-genere` aussi, même quand l'en-tête est resté en place. C'est le filet contre la dérive la plus tentante, corriger sur place.

## 4. Ce que le commun ne fait jamais

- **Être édité.** Une correction faite dans le commun disparaît au passage suivant, sans avertissement : c'est le fonctionnement voulu, pas un accident. Le README le dit, chaque note le porte en tête.
- **Porter une note privée.** `cloture` n'exporte pas une note `visibilite: prive` ; si une telle note arrive quand même dans un export, `federe.py` s'arrête avant d'écrire.
- **Devenir un vault de travail.** Pas de clôture, pas de `nouveau-projet`, pas d'agent qui y écrit. On l'ouvre dans l'éditeur de notes pour lire, on ferme.
- **Recopier une procédure.** Le dossier commun de l'entreprise garde le seul exemplaire ; le commun le cite par une note, rien de plus.
- **Fusionner des projets.** Deux rédacteurs sur la même affaire, ce sont deux points de vue, préfixés chacun par son slug. La fusion n'a lieu que pour les acteurs et les domaines, qui sont des référentiels.

## 5. Écrire l'état

`_cortex/07-federation.md`, dans l'atelier de la personne qui tient le commun, depuis la session de cet atelier (Étape 0, « Où se lance ce maillon ») :

```yaml
maillon: 8
produit_par: cortex-8-federation
statut: valide                      # valide | arbitre (motif obligatoire, ex. vault solo)
commun: "~/Cortex/commun"
membres: [camille, yasmine, marc]
genere_le: 2026-09-19T14:00:00
empreinte: "<contenu de .cortex-genere>"
controles:
  deux_membres_ou_plus: passe
  exports_coherents: passe          # hash de chaque note conforme à index.json
  aucune_note_privee: passe
  lint_vert_sur_commun: passe
  regeneration_identique: passe     # diff -r hors genere_le et ligne datée du README : vide
  readme_et_sceau_presents: passe
  aucune_note_hors_index: passe     # sinon, relancer la cloture du membre
  dossier_commun_cite: passe        # `arbitre` motif « le groupe n'a pas de dossier commun » sans `referentiel`
```

Un contrôle qui n'est ni `passe` ni `arbitre` avec motif laisse le maillon en `statut: en_cours`.

Sous le frontmatter, trois lignes suffisent : le nombre de projets, d'acteurs (dont fusionnés), de domaines et de notes de journal rendus par le script, et les liens neutralisés s'il y en a, pour que chaque rédacteur sache quelle note il pourrait passer en `visibilite: commun`.

## Message de clôture

```
Commun régénéré pour <nom> : <M> membres, <P> projets, <A> acteurs
(dont <F> fusionnés), <D> domaines, <J> décisions partagées. Contrôle de santé vert, empreinte <8 premiers
caractères>.

Le commun se lit, ne s'édite pas. Pour changer un fait : le vault qui
le possède, une clôture, puis « regénère le commun ».

Liens neutralisés : <liste ou aucun>. Chacun désigne une note que son
auteur peut rendre visible à l'équipe s'il veut qu'elle voyage.
```

## Interdits

- **Ne jamais parler, lire ni faire valider hors de la doctrine** : les mots devant la personne, ce que la chaîne lit, ce qui se valide à l'écran, ce qui demande un accord (`cortex-1-cadrage/references/doctrine.md` §8 à §11).
- **Jamais écrire dans le commun autrement que par `federe.py`.**
- **Jamais copier une note d'un vault membre à la main dans un autre.** Le seul chemin entre deux rédacteurs passe par l'export et le commun.
- **Jamais forcer une génération refusée.** Un refus nomme sa cause ; la corriger chez le membre, puis relancer.
- **Jamais déclarer un contrôle passé sans l'avoir lancé.**

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
