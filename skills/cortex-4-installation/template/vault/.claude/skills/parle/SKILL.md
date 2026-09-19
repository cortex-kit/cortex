---
name: parle
description: Répond à une question sur le travail de la personne à partir du vault, en citant les notes. Charge le Centre, puis les domaines que la question vise, puis les notes liées à ces domaines, jusqu'au plafond sante.max_notes_parle ; au-delà, délègue la recherche au sous-agent chercheur-vault. N'écrit jamais. Déclencher quand la personne dit "parle", "qu'est-ce qu'on sait sur", "où en est", "rappelle-moi", "explique-moi", "qui est", ou pose une question sur un projet, un interlocuteur, une décision, un domaine. Ne PAS utiliser pour écrire (cloture), auditer (lint), créer (nouveau-projet) ni intégrer une source (ingest).
---

# parle : le vault répond, et cite

La personne pose une question dans ses mots. La skill lit ce qu'il faut, pas plus, et répond en citant les notes d'où vient chaque affirmation. Une réponse sans citation n'est pas vérifiable, donc pas fiable.

## 1. Charger, dans cet ordre

1. **`00 - Centre/Centre.md`**, toujours. C'est la carte : les domaines, les gestes, l'inbox.
2. **La ou les notes de domaine** que la question vise, dans `10 - Domaines/`. Une question sur un client, un projet ou un sujet appartient à un domaine ; l'identifier d'abord évite de lire tout le vault.
3. **Les notes liées à ces domaines**, dont le frontmatter correspond à la question : `domaine: "[[Nom]]"`, puis `client`, `statut`, `type`. Chercher d'abord dans les propriétés, ensuite dans les liens `[[ ]]`, en dernier dans le plein texte.

Le compte s'arrête à **`sante.max_notes_parle`** notes (douze par défaut, valeur dans [[Configuration]]). Au-delà, la question déborde le fil principal : **déléguer** la recherche au sous-agent `chercheur-vault` avec la question telle quelle, et bâtir la réponse sur sa synthèse, qui porte les chemins.

Pourquoi un plafond : lire quarante notes dans le fil principal coûte le contexte de toute la session, et la réponse devient plus longue que ce que la personne demandait. Le sous-agent lit large et rend dix lignes.

Pour une fiche projet, lire la fiche **complète** : frontmatter, `## Actions`, dernière entrée de `## Journal`. Une fiche lue à moitié donne un état sans sa raison.

## 2. Répondre

- **Citer** chaque affirmation par un lien `[[Nom de la note]]`. Le lien est la preuve ; il doit résoudre vers une note existante du vault.
- **Distinguer** le constaté de l'inféré : ce qui est déduit porte `[déduction]`, ce qui est incertain porte `[?]`.
- **Un trou est une réponse.** « Aucune note ne dit pourquoi ce fournisseur a été écarté » est une information, souvent la plus utile. Ne jamais combler par une supposition plausible.
- **Court.** Trois à huit lignes pour une question simple. Pointer vers le substrat canonique (`url_canonique`, `dossier_local`) quand le détail y vit : le vault pointe, il ne stocke pas.
- **En régime copie**, une réponse peut s'appuyer sur `50 - Ressources/Structurants/`. Si le lint signale ce structurant `structurant_perime`, le dire : la copie a divergé de la source.

Forme :

```
<réponse en quelques lignes, chaque fait suivi de sa note [[ ]]>
Où vit le détail : <pointeur canonique, ou « nulle part dans le vault »>
Ce qui manque : <les trous constatés, ou rien>
```

## 3. Ne jamais écrire

Aucune création, aucune modification, aucun classement, aucun commit. Si la conversation fait apparaître une chose à écrire, le **dire**, et laisser la personne le faire par la skill qui écrit.

Ce n'est pas de la prudence : un vault dans lequel on ne sait plus si une ligne a été voulue ou supposée a perdu sa valeur de mémoire.

## 4. Finir

Si l'échange a produit une **décision** ou a levé un **blocage**, terminer par une proposition, sans l'exécuter :

```
Cet échange a tranché quelque chose. Dites « clôture » pour en garder la raison dans la fiche.
```

Sinon, s'arrêter à la réponse.

## Interdits

- **Jamais de réponse sans lien `[[ ]]`** vers une note lue.
- **Jamais plus de `sante.max_notes_parle` notes** dans le fil principal.
- **Jamais recopier** une note en entier : résumer et pointer.
- **Jamais écrire**, ni dans le vault, ni ailleurs.
- **Jamais inventer** un projet, un acteur, une raison. En cas de doute, dire ce qui manque.
