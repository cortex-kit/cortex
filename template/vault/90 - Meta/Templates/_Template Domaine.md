---
type: domaine
statut: actif
tags:
  - d/CODE
---
# {{title}}

Description courte du domaine, deux lignes maximum.

Centre de gravité secondaire. Remonte vers [[Centre]].

## Ce qui rattache une note à ce domaine

Une note appartient à ce domaine par sa propriété `domaine: "[[{{title}}]]"`, pas
par son emplacement. Un projet de ce domaine et un projet d'un autre vivent tous
deux dans `20 - Projets` : le domaine est une propriété, jamais un dossier. C'est
ce qui permet de réaffecter sans déplacer de fichier.

## Comment voir ce qui vit ici

Sans aucun plugin à installer :

- **Les projets** — recherche globale `domaine: "[[{{title}}]]"`, ou ouvrir
  `20 - Projets` et trier sur la colonne `domaine` dans le panneau Propriétés.
- **Les acteurs et tout ce qui pointe ici** — le panneau **Liens entrants**
  (plugin core) de cette note les liste déjà. Ne pas le réimplémenter.
- **Les actions ouvertes** — recherche `task-todo: #d/CODE`.
- **La carte** — le Graph View colore ce domaine automatiquement d'après son
  tag, les groupes de couleur étant générés depuis la configuration.

Un vault qui a besoin d'un plugin tiers pour se lire est un vault qui ne se lit
pas : chez le prédécesseur de ce produit, une vingtaine de blocs de requête
s'affichaient en code brut depuis des mois, faute de plugin installé. Les
requêtes équivalentes restent disponibles, regroupées et optionnelles, dans
[[Vue Obsidian (Dataview, optionnel)]].

## Projets structurants

- _Non renseigné — à compléter._

## Notes

-
