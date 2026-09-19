---
name: cortex-5-ingest
description: Cinquième maillon de la chaîne Cortex. Transforme le catalogue d'inventaire en notes-pointeurs dans le vault installé — projets, acteurs, ressources — avec un résumé plafonné et une écriture idempotente. Tient un registre source vers note qui rend les relances incrémentales. Déclencher quand le consultant dit "maillon 5", "on peuple le vault", "ingest de l'inventaire", ou dispose d'un vault installé et d'un 01-inventaire.json validé. Phrase d'entrée de la notice : « remplis mon second cerveau ». Ne PAS confondre avec la skill `ingest` livrée au client, qui traite une source externe à la fois en mode maintenance.
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

**Lire la clé `donnees.regime` du `config.yaml`** : `pointeur` (une base déportée porte le canon, rien n'est copié, comportement v1 à l'identique) ou `copie` (aucune base déportée : les documents structurants validés un par un sont copiés, §2 bis). Le régime a été fixé au maillon 1 ; ce maillon ne le change pas.

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

## 2 bis. Régime copie : les structurants, par lots de quatre

En régime `copie`, le vault garde une copie markdown des documents **structurants** : ceux qui décrivent comment l'organisation tourne, et que personne ne retrouvera s'ils restent dans un dossier parmi mille. Les types éligibles sont ceux de `donnees.structurants` : `organigramme`, `process`, `fiche_de_poste`, `contrat`, `projet`, `acteur`, `tenants_aboutissants`, `fil_structurant`. Rien d'autre.

**Candidats.** Les `signal_ontologique.structurant_candidat` de `01-inventaire.json`, plus ce que le cadrage a nommé. Les classer par type, puis par importance déclarée.

**Validation par lots de quatre.** Une question par lot (AskUserQuestion, choix multiple) : « Ces quatre documents décrivent-ils comment vous travaillez ? Cochez ceux qu'on garde. » Chaque proposition nomme le fichier, son type, le domaine de rattachement proposé. Lot suivant seulement après réponse. Aucune copie sans un « oui » explicite sur le document lui-même.

**Plafond.** `sante.max_structurants`, quarante par défaut. Atteint, on s'arrête et on le dit : au-delà, le vault devient un second disque, et un second disque ne se consulte pas plus que le premier. Ce qui reste se déclare écarté, avec son motif.

**La copie**, par le script, jamais à la main :

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/copie_structurant.py" --vault <vault> \
    --source "~/Documents/.../PROCESS-affaire.md" --type process --domaine "Ops"
```

Il convertit le document (`uvx --from "markitdown[all]" markitdown` pour les formats bureautiques, depuis un dossier temporaire ; lecture directe pour le texte), écrit `50 - Ressources/Structurants/<type>/<nom>.md` avec le frontmatter du contrat (`type: structurant`, `structurant`, `domaine`, `source_path` en forme `~`, `hash` sha256 de la source, `copie_le`) et un marqueur de provenance. Rejoué, il ne duplique pas : même hash, rien ; source changée, copie rafraîchie ; note écrite à la main, refus. Le lint suspend le plafond de lignes sur ce dossier et lève `structurant_perime` dès que la source diverge de la copie.

**Les fils de messagerie** (`fil_structurant`) n'entrent **jamais en corps de mail**. Un fil validé se copie en **résumé anonymisé** : objet, période, nombre de messages, participants réduits à leur rôle ou à leur domaine (« le cabinet comptable », « un fournisseur »), dix lignes de substance. Le résumé passe par `--texte <fichier>` sans `--source`. Le même fil s'inscrit dans `mail.fils_structurants` de `01-inventaire.json` : `{fil_id, objet, participants_anonymises, periode, messages, resume}`.

**Après la remise**, le même script vit dans le vault, déposé par `scaffold.py` en `.claude/skills/ingest/copie_structurant.py`. C'est lui que la personne rejoue pour rafraîchir une copie périmée, plugin installé ou non : la skill `ingest` du vault porte le mode d'emploi.

**En régime `pointeur`**, cette section ne s'applique pas : le dossier `Structurants/` reste vide, et une demande de copie se refuse en nommant le régime.

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
  structurants_valides_un_par_un: passe   # regime copie ; `arbitre` motif « regime pointeur » sinon
  aucun_corps_de_mail_copie: passe
```

## Message de clôture

```
Vault peuplé pour <organisation>.

- <N> projets, <M> acteurs, <K> ressources
- structurants copiés : <N> sur <plafond> (régime copie), ou « aucun, régime pointeur »
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

Vérifier les trois fiches avant de proposer la suite : c'est le geste qui ne se saute pas, personne d'autre ne le fera.

## Interdits

- **Jamais plus que le plafond de lignes** dans un résumé.
- **Jamais de note sans pointeur canonique ni lien sortant.**
- **Jamais écraser une note sans marqueur de provenance.**
- **Jamais tronquer en silence.** Ce qui est écarté se déclare avec son motif.
- **Jamais de personne physique** dans `40 - Acteurs`.
- **Jamais une copie en régime pointeur**, jamais un type hors `donnees.structurants`, jamais au-delà de `sante.max_structurants`.
- **Jamais un corps de mail** dans le vault, quel que soit le régime. Un fil structurant entre en résumé anonymisé, ou n'entre pas.
- **Jamais annoncer une écriture réussie sans l'avoir vérifiée.** Si une écriture échoue, le dire — un rapport de succès non vérifié empêche de savoir qu'il y a quelque chose à rattraper.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
