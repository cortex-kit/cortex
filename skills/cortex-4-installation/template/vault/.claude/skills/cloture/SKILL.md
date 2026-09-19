---
name: cloture
description: Réflexe de micro-clôture du vault. À déclencher dès la fin d'un bloc de travail cohérent (mission, chantier, tâche, sous-tâche), autant de fois par jour que nécessaire, typiquement 3 à 10. Détecte les notes touchées, patche la fiche projet concernée (## Journal daté en tête avec le POURQUOI, ## Actions, frontmatter dernier_journal et blocages_actifs), retire les cases soldées, file les décisions structurantes en note dédiée, vérifie la santé par le lint, exporte ce qui part au commun, puis commit local et push si un remote existe. Idempotent, moins de trente secondes. Déclencher quand la personne dit "cloture", "clôture", "j'ai fini X", "termine la tâche", "patche la fiche", "fin de mission", "consolide", ou dès qu'un bloc de travail se termine. Ne PAS utiliser pour créer un projet (nouveau-projet), auditer (lint), répondre (parle) ni faire le point (bilan).
---

# cloture : le réflexe qui fait vivre le vault

C'est **la** skill du produit. Un vault sans clôture se remplit une fois, à l'installation, puis meurt : personne ne retourne écrire ce qui s'est décidé. Avec elle, il se remplit tout seul, un bloc de travail à la fois.

## Positionnement

- **Réflexe haute fréquence.** Plusieurs déclenchements par jour, pas un rituel de fin de semaine.
- **Moins de trente secondes.** Au-delà, elle ne sera pas déclenchée, et une skill qu'on n'appelle pas ne sert à rien. Cette contrainte gouverne tous les arbitrages ci-dessous.
- **Granularité libre** : mission, chantier, tâche, sous-tâche.
- **Idempotente.** Dix relances le même jour ne produisent aucun doublon.
- **Tolérante à l'échec.** Le vault est patché en premier ; si le lint, l'export ou le commit tombent, on le signale et on continue. La source de vérité est déjà écrite.
- **Aucune écriture hors du vault.** Ni base externe, ni dossier de travail, ni messagerie. Sens unique, toujours.

## Étape 0 : prérequis

Le vault a un `config.yaml` à sa racine. Sinon, s'arrêter et le dire : sans configuration, ni les enums ni les seuils ne sont connus, et toute écriture serait à l'aveugle.

## 1. Détecter les notes touchées

Par ordre de fiabilité :

1. `git status --porcelain` : les notes modifiées depuis la dernière clôture. C'est la détection la plus sûre, et la première à faire.
2. Un dossier de projet ouvert dans la session, recoupé avec les `dossier_local` du vault.
3. Un nom de projet ou d'interlocuteur cité explicitement.
4. Les fichiers du vault édités qui ressemblent à `20 - Projets/<CODE> - <nom>.md`.
5. Les fichiers `90 - Meta/` édités, cas du chantier interne.

**Plusieurs candidats** : les lister et demander de confirmer. **Aucun candidat** : demander, en proposant un rapprochement approximatif depuis `20 - Projets/`.

**Ne jamais deviner.** Patcher la mauvaise fiche est pire que ne rien patcher : l'information devient fausse à deux endroits au lieu d'être absente à un seul.

## 2. Construire le delta : le routage sémantique

C'est le cœur de la skill, et c'est là que se joue la qualité du vault à trois semaines.

| Ce qui s'est passé | Où ça va |
|---|---|
| une décision, un contexte, la raison d'une avancée, un blocage levé ou créé | `## Journal`, **le POURQUOI** |
| une tâche créée | `## Actions`, case `- [ ]` |
| une tâche terminée | **la case disparaît** de `## Actions` ; la trace vit dans git |
| un changement de phase ou de progression | le frontmatter |
| une décision **structurante** ou transverse | une **note dédiée** dans `60 - Journal/` |

### Le critère de granularité

**Si la session est un cluster cohérent avec des décisions** (« troisième entretien fait, on saute le quatrième, l'accès au dossier partagé est débloqué ») : 1 à 3 puces de journal, centrées sur le pourquoi.

**Si la session est une tâche isolée sans contexte décisionnel** (« j'ai relancé la compta », « j'ai déposé le document ») : la case est **retirée** de `## Actions`, et **aucune puce de journal**.

Ce second cas est celui qu'on traite mal, et c'est lui qui décide de tout. Un journal où chaque geste laisse une ligne devient illisible en un mois, donc n'est plus relu, donc ne sert plus. Le journal doit rester lisible à trois semaines : c'est le seul moment où on l'ouvre, et c'est pour y chercher une raison, pas un inventaire.

Le seuil est simple : **si tu ne peux pas écrire « parce que », ça ne va pas au journal.**

### Le plafond de lignes

Une entrée de journal fait **au maximum `config.sante.max_lignes_entree_journal`** lignes, dix par défaut. Contrôle dur du lint.

Au-delà, ce n'est plus une décision : c'est un compte rendu, et un compte rendu appartient au substrat canonique du projet. Un vault dont les fiches portent des comptes rendus est devenu un double du substrat.

### En régime copie

`donnees.regime: copie` ne change rien à la clôture : **elle ne copie jamais un document**. Les structurants entrent par `ingest`, un par un, sur accord. Si le lint de l'étape 6 signale un `structurant_perime`, le dire au récap et proposer `ingest` pour rafraîchir la copie ; ne pas le faire ici.

## 3. Valider, conditionnellement

**Delta non trivial** (au moins 2 puces de journal, ou un changement de `phase` / `progression`, ou une décision) : afficher un résumé et attendre un mot.

```
[<fiche>]
État : <phase> · <progression> %
Fait (pourquoi) : <1-3 puces>
Décidé : <0-2 puces, ou rien>
Tâches : +N créées · M soldées · blocage <levé / créé / rien>
```

**Delta trivial** (une seule case soldée, sans changement de journal ni de frontmatter) : **écrire directement**, sans demander, et le mentionner dans le récap.

Cette asymétrie tient la cible des trente secondes. Demander une validation pour solder une case ferait abandonner la skill en trois jours ; ne pas en demander pour une décision ferait écrire des choses que personne n'a voulues.

## 4. Patcher la fiche

1. **Lire le fichier en entier** avant d'éditer. Sans exception.
2. Calculer la date du jour.
3. **Frontmatter**, n'amender que les champs concernés :
   - `dernier_journal: AAAA-MM-JJ` ;
   - `blocages_actifs: <N>`, **recompté** depuis les `#blocage` du corps **après** application du delta, jamais incrémenté à l'aveugle ;
   - `phase` et `progression` seulement si validés. `phase` doit appartenir à l'enum de son `cycle` (voir [[Configuration]]), refuser sinon.
4. **`## Journal`** :
   - section en paragraphe libre : insérer une entrée `### AAAA-MM-JJ` **en tête**, l'existant intact dessous. Migration douce, on ne réécrit pas l'historique ;
   - section déjà datée : si l'entrée du jour existe, **fusionner avec déduplication textuelle stricte** ; sinon insérer en tête.
5. **`## Actions`** :
   - nouvelle tâche : `- [ ] Intitulé #d/<code> 📅 AAAA-MM-JJ` ;
   - tâche soldée : **retirer la ligne**. Le commit de clôture garde la trace, et une liste qui ne contient que l'ouvert se lit d'un coup d'œil.
6. **`## Décisions`** : puce datée `- AAAA-MM-JJ : <décision>`. Créer la section si nécessaire, **avant `## Journal`**.
7. **`## Pointeurs`** : **ne jamais toucher.**

**Idempotence** : avant tout ajout, vérifier qu'une puce textuellement identique n'existe pas déjà. Dix passes doivent produire le même fichier.

### La décision structurante

Un choix d'architecture, une bascule de stratégie, un abandon motivé ne vont **pas** dans le `## Décisions` local. Ils vont dans une note dédiée `60 - Journal/AAAA-MM-JJ - Titre court.md`, depuis `_Template Décision`, avec sa section **`## Arbitrage écarté`**.

Demander confirmation avant de créer la note : le seuil « structurant » est un jugement, et le prendre à la place de la personne remplit `60 - Journal/` de quotidien.

## 5. Contrôle de périmètre

Pour chaque projet retenu ayant un `dossier_local`, compter les `CLAUDE.md` :

```bash
find "<dossier résolu>" -name "CLAUDE.md" -type f 2>/dev/null | wc -l
```

**1** : silencieux. **0** : « aucun CLAUDE.md à la racine, projet créé sans `nouveau-projet` ? ». **Plus de 1** : « N CLAUDE.md détectés, attendu 1. Règle cardinale violée ».

Best-effort strict : aucun effet de bord, jamais d'arrêt. Le dossier de travail est en lecture seule pour l'agent, et c'est voulu.

## 6. Vérifier la santé

```bash
python3 .claude/skills/lint/lint_sante.py --vault .
```

Un contrôle dur en échec se **signale au récap**, sans bloquer : le vault est déjà patché et le patch n'est pas la cause. Ne jamais le taire.

## 7. Exporter ce qui part au commun

```bash
python3 .claude/skills/cloture/export.py --vault .
```

En mode `federe`, le script vide puis réécrit `<commun.export>/<slug>/` : `index.json` et la copie des notes de `10 - Domaines`, `20 - Projets`, `40 - Acteurs`, `60 - Journal` dont `visibilite` vaut `commun` (une note sans clé prend `commun.visibilite_defaut` ; `prive` ne sort jamais). Régénéré en entier : idempotent. En mode `solo`, il ne fait rien et le dit.

L'export est un dossier du vault, pas une écriture vers l'extérieur : c'est l'agrégateur du commun qui vient le lire.

## 8. Commit

Si le vault est sous git :

```bash
git add <chemins ciblés>          # jamais `add -A`
git commit -m "<message mono-sujet>"
git remote | grep -q . && git push    # seulement si un remote existe
```

`git add` ciblés : la configuration locale de l'éditeur produit du bruit qui n'a pas à être versionné avec la doctrine. L'export (`_export/`) fait partie des chemins ciblés en mode `federe`.

**Jamais `--force`, jamais `--no-verify`.** Si le push échoue, le signaler et s'arrêter là : le commit local existe, rien n'est perdu.

## 9. Récap, 7 lignes maximum

```
✓ Fait : <ce qui a été synthétisé>
✎ Modifié : <fiches patchées>
✎ Périmètre : <warning CLAUDE.md, ou rien>
⚠ Lint : <contrôles durs en échec, structurants périmés, ou rien>
↻ Export : <N notes, ou « solo »>
↻ Commit : <empreinte, push fait ou « aucun remote », ou raison de l'absence>
→ Suite : <prochaine action, ou rien>
```

Ne pas dépasser. Un récap long ne sera pas lu, et un récap non lu ne permet pas de rattraper une erreur d'écriture, ce qui est sa seule fonction.

## Interdits

- **Jamais d'écriture hors du vault.** Ni base externe, ni dossier de travail, ni messagerie.
- **Jamais copier un document** dans le vault, quel que soit le régime.
- **Jamais de note satellite** : une seule fiche canonique par projet.
- **Jamais toucher `## Pointeurs`.**
- **Jamais deviner** un projet, une phase, une décision. En cas de doute, demander.
- **Jamais inventer un succès.** Si le lint, l'export ou le push échouent, le dire.
- **Jamais recopier** ce que le substrat canonique porte déjà.
