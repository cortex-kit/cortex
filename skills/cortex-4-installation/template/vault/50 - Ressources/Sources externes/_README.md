# Sources externes — contrat du dossier

Les sources externes ingérées : article, papier, podcast, vidéo, page d'un outil tiers, livre.

Procédure complète : [[Ingest - Sources externes]].

## Frontmatter obligatoire

```yaml
type: ressource
domaine: "[[Nom du domaine]]"
statut: actif           # actif | obsolete
source_url: ""          # l'adresse stable de la source
source_type: ""         # article | papier | video | podcast | page | livre
date_ingest: AAAA-MM-JJ
tags:
  - d/<code>
```

## Les deux règles qui comptent

**Dix lignes de résumé au maximum.** Contrôle dur. La source reste à son adresse : la recopier ne crée aucune valeur et crée une version qui divergera. Ce qui a de la valeur, c'est pourquoi elle compte ici.

**Aucun lien sortant = ingest manqué.** Une source qui ne pointe vers aucun domaine ni projet ne sera jamais retrouvée, donc elle n'existe pas. Autant ne pas l'avoir ingérée.

## Historique

- AAAA-MM-JJ - [[Titre]] - impact en une ligne
