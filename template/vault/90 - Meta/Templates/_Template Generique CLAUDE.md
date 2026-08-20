# CLAUDE.md — {{NOM_PROJET}}

Chargé automatiquement pour toute session d'agent lancée depuis ce dossier.

## Identité projet

| Champ | Valeur |
|---|---|
| Nom | {{NOM_PROJET}} |
| Domaine | {{DOMAINE}} |
| Objet | {{OBJET_EN_UNE_LIGNE}} |
| Responsable | {{RESPONSABLE}} |

## Pointeurs canoniques

| Substrat | Adresse |
|---|---|
| Fiche vault | `20 - Projets/{{PREFIX}} - {{NOM_PROJET}}.md` |
| Substrat canonique | {{URL_CANONIQUE_OU_NA}} |
| Dossier livrables | `./` |

Le substrat canonique porte l'état détaillé et les documents. La fiche vault
porte le **pourquoi** et les pointeurs. Aucun des deux ne recopie l'autre.

## Règle d'entrée en session

Lire la fiche vault si le contexte est ambigu, puis restituer l'objet et la
prochaine action avant d'agir.

## Interdictions

- Aucune action hors du périmètre de {{NOM_PROJET}}.
- Aucun sous-CLAUDE.md dans les sous-dossiers. Règle cardinale : **un seul
  CLAUDE.md par racine de projet**. Plusieurs fichiers de contexte dans une même
  arborescence produisent des consignes qui divergent en silence, et l'agent
  applique celle qu'il a lue en dernier.
- Ne jamais recopier dans la fiche vault ce que le substrat canonique porte
  déjà. Un résumé de plus de {{SEUIL_JOURNAL}} lignes est une copie déguisée.

## Statut

Projet instancié le {{DATE_PROJET}}.
