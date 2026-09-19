# 50 - Ressources / Structurants : les copies validées, en régime copie seulement

Ce dossier ne sert qu'en **régime copie** (`donnees.regime: copie` dans [[Configuration]]) : aucune base déportée ne porte le canon, le vault garde donc une copie markdown des documents structurants, validés un par un à l'ingest. En régime pointeur, il reste vide.

Un sous-dossier par type : `organigramme/`, `process/`, `fiche_de_poste/`, `contrat/`, `projet/`, `acteur/`, `tenants_aboutissants/`, `fil_structurant/`.

Chaque copie porte dans son frontmatter `type: structurant`, `structurant: <type>`, `source_path` (forme `~`), `hash` (sha256 de la source) et `copie_le`. Le lint ne lui applique pas le plafond de lignes, et lève `structurant_perime` dès que la source a changé depuis la copie : la copie ne se met jamais à jour toute seule, elle se rafraîchit par `ingest`, sur accord.

Un fil de messagerie n'entre ici qu'en **résumé anonymisé** (`fil_structurant`), jamais en corps de mail.

Le plafond est `sante.max_structurants`. Au-delà, le vault cesse d'être un index et devient un second disque.
