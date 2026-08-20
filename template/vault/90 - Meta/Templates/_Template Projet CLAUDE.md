# CLAUDE.md — {{NOM_PROJET}}

Chargé automatiquement pour toute session d'agent lancée depuis ce dossier.

Ce fichier ne duplique **ni** ce qui vit dans le substrat canonique (l'état opérationnel), **ni** ce qui vit dans la fiche de vault (la direction et le pourquoi). Il porte les pointeurs et les règles d'entrée en session, et rien d'autre.

## Mémoire transverse

L'état, les décisions et les pointeurs de ce projet vivent dans le vault, pas ici.

- Vault : {{CHEMIN_VAULT}}
- Fiche de ce projet : `20 - Projets/{{PREFIX}} - {{NOM_PROJET}}.md`
- Contrat de données : `90 - Meta/Conventions.md`

Lire la fiche de ce projet, et ses liens, avant toute action de fond.

## Identité

| Champ | Valeur |
|---|---|
| Projet | {{NOM_PROJET}} |
| Client | {{CLIENT}} |
| Domaine | {{DOMAINE}} |
| Cycle | {{CYCLE}} |
| Phase courante | voir le frontmatter de la fiche de vault (miroir) |
| Responsable | {{RESPONSABLE}} — {{COURRIEL_VISIBLE}} |
| Interlocuteur principal | {{INTERLOCUTEUR}} |
| Démarrage | {{DATE_DEBUT}} |
| Échéance | {{DATE_ECHEANCE}} |

La phase n'est pas recopiée ici. Une valeur d'état présente à deux endroits finit par différer, et celle du CLAUDE.md sera la périmée — parce que personne ne pense à mettre à jour un fichier de contexte.

## Pointeurs canoniques

| Substrat | Rôle | Adresse |
|---|---|---|
| Substrat métier | canon de l'état et des travaux | {{URL_CANONIQUE}} |
| Fiche de vault | direction, journal, actions macro | `20 - Projets/{{PREFIX}} - {{NOM_PROJET}}.md` |
| Espace documents client | documents **fournis** par le client, immuables | {{ESPACE_DOCUMENTAIRE}} |
| Dossier de travail | ce que **nous** produisons | `./` |

La distinction entre les deux dernières lignes est celle qui compte le plus au quotidien : elle sépare ce qui est source de ce qui est notre production. Les mélanger fait perdre la trace de ce qui est vérifié.

## Règle d'entrée en session

1. **Lire le substrat canonique avant toute proposition d'action.** C'est lui qui porte l'état à jour.
2. Restituer un état de 5 à 8 lignes : phase, dernier delta, actions macro, blocage.
3. **Ne rien exécuter sans validation explicite.**

## Interlocuteurs

- {{INTERLOCUTEUR_1}} — {{ROLE_1}}
- À compléter à chaque nouveau contact identifié. Une entité mentionnée mérite une note dans `40 - Acteurs` du vault ; une personne se mentionne, elle n'a pas de fiche.

## Interdictions et garde-fous

- Aucune action hors du périmètre de {{NOM_PROJET}}.
- **Aucune modification visible par le client sans validation explicite.**
- **Aucune duplication du contenu du substrat** dans ce dossier ni dans le vault. Un résumé de plus de {{SEUIL_JOURNAL}} lignes est une copie déguisée.
- **Aucun sous-CLAUDE.md dans les sous-dossiers.** Un seul par racine de projet : plusieurs fichiers de contexte dans une même arborescence produisent des consignes qui divergent en silence, et l'agent applique celle qu'il a lue en dernier.
- {{REGLES_SPECIFIQUES}}

## Statut

Instancié le {{DATE_PROJET}}. À mettre à jour à chaque changement de phase ou d'interlocuteur — un CLAUDE.md périmé est plus nuisible qu'absent, parce qu'il est cru.
