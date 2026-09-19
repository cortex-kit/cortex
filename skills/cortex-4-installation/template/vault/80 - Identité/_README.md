# 80 - Identité — immatriculations

Type `identite`. Données d'immatriculation **semi-publiques** de l'organisation, pour remplir un formulaire administratif en lisant le frontmatter plutôt qu'en ressaisissant.

## LIGNE ROUGE — aucune donnée sensible en clair

Interdits, sans exception et sans cas particulier :

- coordonnées bancaires,
- mots de passe et clés d'API,
- identifiants fiscaux, sociaux, de déclaration,
- numéros de sécurité sociale,
- scans de pièces d'identité.

Ces éléments vivent **hors du vault** — gestionnaire de mots de passe ou dossier chiffré. La fiche n'en porte qu'un pointeur textuel indiquant où les trouver.

Le motif est mécanique, pas procédural. Un vault est synchronisé entre machines, sauvegardé, indexé par un moteur de recherche, versionné, et parfois lu intégralement par un agent. Chacune de ces propriétés est ce qui le rend utile, et chacune est une voie de sortie pour un secret. Le vault est conçu pour être facilement lisible : c'est structurellement incompatible avec le stockage d'un secret.

En cas de doute sur un élément, il ne va pas dans le vault. Le doute est la réponse.

## Le champ des données à porter

Il dépend du pays et de la forme juridique, et c'est pourquoi ce produit ne livre pas de schéma : une table de champs valable dans une juridiction est trompeuse dans une autre. À définir à l'installation, avec pour seule contrainte la ligne rouge ci-dessus.
