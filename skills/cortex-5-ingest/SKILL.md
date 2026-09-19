---
name: cortex-5-ingest
description: Cinquième maillon de la chaîne Cortex. Transforme le catalogue d'inventaire en notes-pointeurs dans le vault installé — projets, acteurs, ressources — avec un résumé plafonné et une écriture idempotente. Tient un registre source vers note qui rend les relances incrémentales. Déclencher quand le consultant dit "maillon 5", "on peuple le vault", "ingest de l'inventaire", ou dispose d'un vault installé et d'un 01-inventaire.json validé. Ne PAS confondre avec la skill `ingest` livrée au client, qui traite une source externe à la fois en mode maintenance.
---

# cortex-5-ingest — peupler sans recopier

Cinquième des sept. C'est le seul maillon qui **survit à l'installation** : sa procédure devient la skill `ingest` que le client garde et lance à chaque nouvelle source.

## Positionnement

Ce maillon ne décide rien : les domaines sont arrêtés au maillon 3, l'arborescence au maillon 4. Il applique.

Il **ne rapatrie aucun document**. Il crée des notes qui pointent.

## Étape 0 — bloquante

1. Le vault existe et son lint sort en 0.
2. `_cortex/01-inventaire.json` et `02-ontologie.md` en `statut: valide`.
3. **Le vault est vide de contenu** — hors doctrine et templates. Si des notes ont été écrites à la main entre-temps, le signaler : elles seront traitées comme des conflits à arbitrer, pas écrasées.

**Lire aussi la clé `conduite` du `config.yaml`** — absente ⇒ `consultant`, comportement actuel à l'identique. En `solo`, le fond ne change pas : trier, pointer, ne jamais recopier. Changent l'adresse des arbitrages — ce qui déborde les plafonds se présente à la personne elle-même, dans ses mots : « voilà ce que je propose d'écarter, et pourquoi » — et le message de clôture, qui propose la suite au lieu de rendre la main.

## 1. Trier avant d'écrire

Toutes les entrées du catalogue ne deviennent pas des notes. La sélection est le vrai travail de ce maillon.

| Devient une note | Ne devient rien |
|---|---|
| un dossier ou une base qui porte un travail en cours | un vestige : peu de fichiers, rien depuis deux ans |
| une entité avec laquelle il se passe quelque chose | un contact sans trace de travail commun |
| une source externe qui a changé une décision | un signet |

**Un vault peuplé de tout ce qui existe est un annuaire**, et personne n'ouvre un annuaire. Les plafonds de `config.collecte` — 60 projets, 80 acteurs — ne sont pas des limites techniques : au-delà, l'outil cesse d'être consulté, ce qui est la seule façon dont il peut échouer.

Si le catalogue déborde, présenter **ce qui est écarté et pourquoi**, et faire arbitrer. Jamais tronquer en silence.

## 2. Écrire des notes-pointeurs

Depuis les templates du vault. Chaque note porte :

**Où prendre les valeurs.** Le catalogue du maillon 2 porte les *schémas* des bases, jamais leurs lignes — c'est ce qui garantit qu'aucun contenu n'a été rapatrié. Mais écrire une fiche demande la valeur de `phase` de chaque entrée, donc les lignes. Ce maillon **suit donc le pointeur et relit la source**, pour les seuls champs à énumération fermée : jamais un texte libre, jamais un corps de page. Les inventer serait pire — une phase devinée est indistinguable d'une phase lue.


- son `domaine`, un des domaines arrêtés ;
- **au moins un pointeur canonique** — `url_canonique`, `repo` ou `dossier_local` relatif ;
- un résumé de **`config.sante.max_lignes_entree_journal` lignes au maximum**, dix par défaut ;
- des liens `[[ ]]` vers son domaine et vers les entités concernées.

Une note sans lien sortant est orpheline, donc introuvable, donc inutile — le lint la refuse.

Le plafond de résumé est un contrôle dur. La source reste à son adresse : la recopier crée une version qui divergera, et un vault qu'on ne peut plus parcourir.

## 3. Écriture idempotente — le diagnostic en trois branches

Avant d'écrire une note, regarder si elle existe :

| Cas | Détection | Action |
|---|---|---|
| **absente** | pas de fichier | créer, avec le marqueur de provenance |
| **présente avec marqueur** | `<!-- cortex-5-ingest: <source_id> <date> -->` | montrer le diff, demander confirmation |
| **présente sans marqueur** | quelqu'un l'a écrite à la main | **s'arrêter sur cette note et arbitrer** |

La troisième branche est celle qui compte. Écraser une note écrite à la main détruit un travail humain sans trace — et c'est exactement ce qu'un batch fait par défaut si on ne l'en empêche pas.

Le **registre** `_cortex/04-ingest.md` tient la table `source_id → note`. C'est lui qui rend les relances incrémentales : une seconde passe ne retouche que ce qui a changé.

## 4. Validation — par lot de source

Les douze projets venus de la base, puis les trente acteurs venus des agrégats de messagerie. Pas note par note.

Le coût de régénération est élevé en jetons mais le registre rend la relance incrémentale : c'est la granularité qui minimise le nombre d'allers-retours sans jamais imposer de tout rejouer.

## 5. Vérifier

```bash
python3 <vault>/.claude/skills/lint/lint_sante.py --vault <vault>
```

**Doit sortir en 0.** Un vault peuplé qui ne passe pas le lint ne doit pas être remis : les écarts se corrigent ici, pendant qu'ils sont peu nombreux et récents.

## 6. Écrire l'état

```yaml
maillon: 5
produit_par: cortex-5-ingest
statut: valide
controles:
  lint_vert: passe
  aucune_note_ecrasee: passe
  tous_pointeurs_canoniques: passe
  resumes_sous_plafond: passe
  ecartes_declares: passe        # ou `arbitre` avec motif
```

## Message de clôture

```
Vault peuplé pour <organisation>.

- <N> projets, <M> acteurs, <K> ressources
- écartés : <N> entrées, motifs dans 04-ingest.md
- lint : vert
- conflits arbitrés : <N ou aucun>

Pour toi :
1. Ouvre le vault et vérifie trois notes au hasard : le pointeur mène-t-il
   au bon endroit ?
2. Fais tourner `cloture` sur une vraie session de travail.
3. Puis `cortex-6-agents-metier`, si le cadrage a identifié un besoin.
4. Enfin `cortex-7-passation`.

L'étape 1 n'est pas une formalité. Un pointeur faux est indétectable par
le lint — il vérifie la présence, pas la destination — et c'est la seule
erreur de ce maillon qui ne se voit qu'à l'usage, des semaines plus tard.
```

**En mode solo :**

```
Votre second cerveau est rempli.

- <N> projets, <M> interlocuteurs, <K> ressources — des fiches qui
  pointent vers vos vrais dossiers, jamais des copies
- écarté : <N> éléments, motifs notés — rien n'a été laissé de côté
  en silence
- contrôle de santé : vert

Avant d'aller plus loin, ouvrez trois fiches au hasard : le lien
mène-t-il au bon endroit ? C'est la seule erreur d'ici qui, sinon,
ne se verrait que des semaines plus tard.

La suite examine s'il vous faut des assistants sur mesure. Sa
condition d'entrée : l'outil rempli et sain — c'est fait. Réponse
honnête probable : « pas encore », et c'est une bonne réponse.

On enchaîne ?
```

Sur accord, lancer `cortex-6-agents-metier` — après les trois fiches vérifiées : c'est le geste qui ne se saute pas, personne d'autre ne le fera.

## Interdits

- **Jamais plus que le plafond de lignes** dans un résumé.
- **Jamais de note sans pointeur canonique ni lien sortant.**
- **Jamais écraser une note sans marqueur de provenance.**
- **Jamais tronquer en silence.** Ce qui est écarté se déclare avec son motif.
- **Jamais de personne physique** dans `40 - Acteurs`.
- **Jamais annoncer une écriture réussie sans l'avoir vérifiée.** Si une écriture échoue, le dire — un rapport de succès non vérifié empêche de savoir qu'il y a quelque chose à rattraper.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
