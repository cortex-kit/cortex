---
name: miroir
description: Fait descendre la phase et le statut des projets depuis la base de projets (Notion) vers les fiches du vault, en sens unique ; constat par défaut, écriture sur accord. Déclencher quand la personne dit "miroir", "recale les fiches", "aligne sur Notion", "mets à jour les phases", ou en début de clôture quand un miroir est configuré. Ne PAS utiliser pour écrire dans la base : rien ne remonte jamais du vault vers la base.
---

# miroir : la base fait foi, le vault se recale

La base de projets porte l'état des affaires ; la fiche du vault en garde un reflet léger (phase, statut) pour que le vault réponde sans ouvrir la base. Ce reflet dérive dès qu'on change une phase dans la base sans clôture. Le miroir le recale.

**Devant la personne** : ses mots, jamais ceux de l'outil (ni le nom d'un script, ni une clé de `config.yaml`) ; et tout ce qu'on lui demande de valider s'affiche en entier avant la question.

## Prérequis

Le bloc `miroir` de `config.yaml` : `outil: notion`, le chemin du fichier qui contient le jeton d'intégration (jamais le jeton lui-même dans le vault), les noms des propriétés `phase` et `statut` dans la base, et la table `miroir_statuts` qui traduit chaque statut de la base en statut du vault. La page Notion de chaque projet doit être partagée avec l'intégration. Sans bloc `miroir`, le script le dit et ne fait rien.

## Le geste

```bash
python3 .claude/skills/miroir/miroir.py --vault .            # constat
python3 .claude/skills/miroir/miroir.py --vault . --ecrire   # après accord
```

1. Lancer le constat, montrer la liste des changements telle quelle (fiche, champ, avant, après) et les signalements.
2. Sur accord, relancer avec `--ecrire`, puis dire « clôture » pour l'enregistrer.

## Ce qu'il ne fait jamais

- Écrire dans la base. Le sens montant est un lien interdit.
- Recopier une phase hors du vocabulaire du cycle de la fiche : il la signale, la personne tranche (ajouter la phase au cycle, ou corriger la base).
- Toucher un autre champ que `phase`, `progression` (dérivée de la phase) et `statut`.
