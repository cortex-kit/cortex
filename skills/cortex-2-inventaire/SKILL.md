---
name: cortex-2-inventaire
description: Deuxième maillon de la chaîne Cortex. Parcourt les substrats déclarés au cadrage — arborescences de fichiers, bases de projets, dépôts de code, agenda, messagerie si autorisée — et produit un catalogue de POINTEURS, jamais de contenu. Produit 01-inventaire.json et son rapport lisible. Déclencher quand le consultant dit "maillon 2", "inventaire", "on scanne l'existant", ou dispose d'un cadrage validé et des accès. Ne PAS confondre avec cortex-5-ingest, qui transforme ce catalogue en notes dans le vault.
---

# cortex-2-inventaire — cataloguer sans copier

Deuxième des sept. Il regarde ce que l'organisation a déjà, sans rien en rapatrier.

## Positionnement

Ce maillon **ne juge pas**. Il ne propose aucun domaine, ne qualifie rien d'important. Il compte, il localise, il relève des schémas. L'interprétation est le maillon 3, et les séparer est ce qui permet de rejouer une source sans rejouer l'arbitrage.

Il **ne rapatrie rien**. Voir §Le piège.

## Étape 0 — bloquante, sans repli

1. `_cortex/00-cadrage.md` en `statut: valide`.
2. **Chaque substrat déclaré répond.** Tester l'accès avant de commencer.

Si un substrat ne répond pas : **s'arrêter et le dire.** Ne pas inventorier les autres « en attendant ».

Un inventaire partiel est pire qu'absent, parce que le maillon 3 ne saura pas ce qui manque : il déduira une ontologie d'un corpus troué en le croyant complet, et le trou deviendra un domaine oublié. Mieux vaut attendre un accès trois jours.

**Lire aussi la clé `conduite` du `config.yaml` de l'atelier** — absente ⇒ `consultant`, comportement actuel à l'identique. En `solo`, le fond ne change pas : la mesure n'a pas d'interlocuteur. Changent l'adresse — « vos dossiers », pas « les substrats du client » — et le message de clôture, qui propose la suite au lieu de rendre la main. Un substrat qui ne répond pas s'annonce dans les mêmes termes qu'en consultant : dire lequel, et attendre. Retrouver un mot de passe ou réactiver un compte est une attente du monde réel ; l'inventaire ne passe pas par-dessus, en solo comme en consultant.

## Le piège — et sa parade structurelle

Le piège est unique et il est fatal : **recopier au lieu de pointer**. Un client le demandera, avec les meilleures raisons du monde : « mettez-nous les documents dedans, ce sera plus pratique ».

La parade n'est pas une règle en prose, c'est le schéma. **`01-inventaire.json` n'a pas de champ `contenu`.**

```json
{
  "source_id": "base-programmes",
  "substrat": "base_projets",
  "type": "base",
  "titre": "Programmes",
  "url": "…",
  "signal_ontologique": {
    "proprietes": ["Statut", "Ville", "Nb lots", "Date PC"],
    "enums": {"Statut": ["Étude", "PC déposé", "Chantier", "Livré"]}
  },
  "volume": 47,
  "derniere_maj": "2026-08-11",
  "resume": "≤ 10 lignes",
  "preuve_de": ["domaine:Promotion"]
}
```

S'il n'y a pas d'endroit où mettre la copie, la copie ne se fait pas. C'est la parade la moins coûteuse et la seule qui tienne dans le temps.

## Ce qu'on prend, et ce qu'on ne lit jamais

| Source | On extrait | On ne lit **jamais** |
|---|---|---|
| arborescences de fichiers | noms de dossiers, profondeur, nombre de fichiers, dates, extensions | le contenu des fichiers |
| **base de projets** | **schémas : noms de propriétés et options de listes**, titres, adresses | le corps des pages |
| dépôts de code | liste, langages, dernier commit, 20 premières lignes du README | le code |
| **messagerie** | **agrégats seuls** : `domaine expéditeur → volume sur 12 mois` | les objets, les corps, les adresses individuelles |
| agenda | titres de réunions **récurrentes** | le contenu des événements |
| registre légal public | forme, dirigeants, filiales, code d'activité | — |
| site public | offre, segments, vocabulaire commercial | — |

**Les schémas des bases sont le meilleur signal de toute la chaîne.** Les noms de propriétés et les options de listes déroulantes sont un vocabulaire déjà curé par le client et accepté par son équipe. Le maillon 3 s'en sert directement.

**L'agenda est le signal le plus sous-estimé.** Les réunions récurrentes révèlent la cadence réelle de l'organisation — ce qui se pilote toutes les semaines est un domaine, quoi qu'en dise l'organigramme.

## La messagerie — condition dure

**Si `collecte.mail_optin` est à `false`, ne pas ouvrir la messagerie.** Pas de contournement, pas de « juste pour voir ».

Si elle est autorisée : agrégats seuls, sur la fenêtre déclarée. Le résultat est une table `domaine → volume`, sans aucune adresse individuelle. Rien d'autre ne sort de cette source.

Une donnée personnelle lue sans base légale ne se dé-lit pas. C'est le seul endroit de la chaîne où une erreur est irréversible.

## Les bornes

Depuis `config.collecte`, jamais dépassées sans arbitrage écrit : profondeur 3, 200 dossiers, 12 mois de messagerie, README seul pour les dépôts.

Ce ne sont pas des précautions techniques. Au-delà, on produit un catalogue que le maillon 3 ne peut plus lire, donc qu'il survolera — et un inventaire survolé donne une ontologie devinée.

## Validation — par substrat

Un substrat, une validation. Pas par entrée.

C'est la bonne granularité pour une raison pratique : les échecs sont partiels et fréquents — limites de débit, permissions, expirations. On veut pouvoir rejouer **une** source sans rejouer les autres, et sans jamais rejouer le cadrage.

## Écrire

`_cortex/01-inventaire.json` (machine, consommé par les maillons 3 et 5) et `01-inventaire.md` (lisible).

```yaml
maillon: 2
produit_par: cortex-2-inventaire
statut: valide
controles:
  tous_substrats_repondent: passe
  aucun_contenu_rapatrie: passe
  bornes_respectees: passe
  mail_conforme_optin: passe
  volumes_sous_plafond: passe    # ou `arbitre` avec motif
```

Si un plafond est dépassé, **le dire au lieu de tronquer en silence.** Une troncature tacite se lit comme une couverture complète, et le maillon 3 conclura sur un corpus dont il ignore qu'il est amputé.

## Message de clôture

```
Inventaire terminé pour <organisation>.

- <N> substrats parcourus, <M> entrées cataloguées
- schémas relevés : <K> bases, <P> propriétés distinctes
- messagerie : <N domaines agrégés | hors périmètre>
- au-delà des bornes : <ce qui a été laissé de côté, ou rien>

Pour toi :
1. Relis 01-inventaire.md, surtout la section « au-delà des bornes ».
2. Lance `cortex-3-ontologie`.

Le maillon 3 est le seul qui juge. Il ne proposera aucun domaine sans
preuve chiffrée tirée de ce catalogue.
```

**En mode solo :**

```
Inventaire terminé.

- <N> endroits parcourus, <M> éléments repérés
- rien n'a été copié : tout est resté à sa place, l'outil a seulement
  noté où chaque chose vit
- laissé de côté : <ce qui dépasse les bornes, ou rien>

La suite décide les grandes familles de votre outil — sur ce que
l'inventaire vient de constater, pas sur des impressions.
Sa condition d'entrée : cet inventaire, complet et validé.

On enchaîne ?
```

Sur accord, lancer `cortex-3-ontologie`. Si un endroit déclaré n'a pas pu être parcouru, ou si une borne a été dépassée sans arbitrage : s'arrêter et dire ce qui manque — des familles décidées sur un inventaire troué seraient fausses, et personne ne saurait pourquoi.

## Interdits

- **Jamais de contenu rapatrié.** Le schéma l'interdit ; ne pas le contourner par un champ ajouté.
- **Jamais la messagerie sans opt-in tracé.**
- **Jamais d'inventaire partiel présenté comme complet.**
- **Jamais de troncature silencieuse.** Ce qui est laissé de côté se déclare.
- **Jamais de jugement ici.** « Ce dossier a l'air important » n'est pas un relevé. Compter, localiser, relever — le maillon 3 interprète.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
