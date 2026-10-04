# Profil société : plusieurs personnes, plusieurs vaults, un commun généré

Ce profil s'applique quand plusieurs personnes d'une même organisation veulent un second cerveau et attendent d'y voir ce que les autres savent. La doctrine ne bouge pas : un vault, un rédacteur. La réponse est donc plusieurs vaults, un par personne, et un vault commun généré que personne n'édite.

Ce profil n'est pas un quatrième parcours. Chaque rédacteur suit la chaîne seul, maillon par maillon, avec son propre profil de questions (employé ou dirigeant selon son poste) et une clé qui change tout à la fin : `mode: federe`. Le maillon 8, `cortex-8-federation`, assemble ensuite les exports.

## Ce que le cadrage décide en plus

Quatre choses, avant toute question individuelle, avec la personne qui porte la démarche pour le groupe.

1. **La liste des rédacteurs.** Nom, poste, et pour chacun le profil de questions qu'il suivra. Trois à huit personnes est l'ordre de grandeur raisonnable ; au-delà, commencer par un noyau.
2. **L'emplacement du commun.** Un dossier hors de tout vault individuel, forme `~`, par exemple `~/Cortex/commun`. Il sera régénéré à chaque fédération et ne se modifie jamais à la main.
3. **Le défaut de visibilité.** Ce qu'une note devient quand son auteur n'a rien précisé : `prive` (rien ne sort sans geste explicite) ou `commun` (tout sort sauf mention contraire). Le défaut recommandé est `prive` : une note qui fuit coûte plus qu'une note qui manque.
4. **Le dossier commun de l'entreprise**, où vivent la charte, les signatures, les procédures et les assistants établis pour tous. Existant, il se demande et s'ouvre une fois ; absent, le rangement proposera de le créer. Chaque vault y pointe, aucun ne le recopie.

Ces quatre réponses s'écrivent dans chaque `config.yaml` individuel (`mode`, `commun.racine`, `commun.visibilite_defaut`, bloc `referentiel`). La liste des rédacteurs va aussi dans `federation.yaml`, qui vit dans le commun : chaque cadrage y inscrit son rédacteur par `federe.py --inscrire`, avec les autres noms du groupe comme attendus (`cortex-1-cadrage` §5). Pour les rédacteurs suivants, ces décisions se reprennent du premier cadrage et s'annoncent ; elles ne se reposent pas.

## Les questions, en langage ordinaire

Les mêmes que pour chaque rédacteur selon son poste, plus les questions de groupe (visibilité, dossier commun). Par lots de quatre, options fermées plus « autre ».

| Sujet | Question telle qu'elle se pose | Ce que la réponse alimente |
|---|---|---|
| Métier | « Que fait votre organisation, et qui parmi vous tiendra son propre outil ? » | `organisation.nom`, la liste des rédacteurs |
| N+1 | « Qui rend compte à qui, parmi ces personnes ? » | acteurs internes, croisés au maillon 8 |
| Collègues | « Sur quels dossiers deux d'entre vous travaillent-ils ensemble ? » | projets partagés, ceux que le commun devra dédoublonner |
| Parties prenantes | « Qui, dehors, parle à plusieurs d'entre vous ? » | acteurs présents chez plusieurs rédacteurs, fusionnés au maillon 8 |
| Projets portés et subis | par rédacteur, selon son profil | projets déclarés, avec leur porteur |
| Outils | « Avez-vous un outil commun où vit l'état des dossiers ? » | `substrats.base_projets`, régime de donnée, identique pour tous si l'outil est commun |
| Rituels | « Quelles réunions réunissent plusieurs d'entre vous ? » | agenda commun |
| Visibilité | « Par défaut, ce que chacun note reste-t-il chez lui, ou passe-t-il aux autres ? » | `commun.visibilite_defaut` |
| Dossier commun | « Votre entreprise a-t-elle un dossier commun où l'on range la charte graphique, les signatures de mail, les procédures ? » | bloc `referentiel`, décision de groupe : fixée au premier cadrage, reprise par les suivants, comme la visibilité |

## Les substrats attendus

- Un espace de fichiers partagé, avec des dossiers d'affaires ou de projets que plusieurs rédacteurs ouvrent.
- Une boîte mail par personne, jamais mutualisée dans un vault.
- Souvent un outil commun de suivi ; s'il existe, le régime est `pointeur` pour tout le monde, et le commun n'a rien à copier.
- Parfois un dépôt de code partagé.

## Les racines à demander

Par rédacteur, celles de son profil, plus le dossier partagé. Deux rédacteurs peuvent déclarer la même racine : chacun la parcourt pour lui, et le commun fusionne ce qui se recoupe.

À demander, jamais à proposer depuis un parcours du disque (`../doctrine.md` §9). La question : « où sont vos dossiers de travail sur cet ordinateur ? ». Chaque réponse s'ouvre une fois pour vérifier qu'elle répond, puis s'écrit en forme `~`. `~/Documents` et `~/Desktop` ne se proposent jamais par défaut ; la personne qui les nomme elle-même les déclare comme une autre racine.

Pour chaque dossier nommé : « d'autres personnes travaillent-elles dans ce dossier ? ». Un oui l'inscrit dans `collecte.partagees` ; le rangement facultatif y demandera une confirmation à part, parce que les liens des collègues casseront.

- Le dossier partagé de l'organisation, demandé comme pour les autres profils : le fournisseur de messagerie oriente la question, il ne donne pas de chemin.

## Les plafonds

Par vault, ceux du profil de chaque rédacteur. Le commun n'a pas de plafond propre : il est généré, il ne se lit pas comme un vault de travail. Un commun qui dépasse six domaines fusionnés signale que les rédacteurs ne parlent pas la même langue, et c'est un constat à remonter au maillon 8, pas à corriger dans un vault.

## Les domaines de départ

Ceux du profil de chaque rédacteur. Le commun fusionne les domaines par nom : deux rédacteurs qui appellent la même chose « Affaires » obtiennent un domaine commun, deux qui l'appellent « Affaires » et « Chantiers » en obtiennent deux. Aligner le vocabulaire au cadrage, quand il coûte une phrase, épargne une fusion manuelle au maillon 8.

## Le cycle de départ

Celui du profil de poste de chaque rédacteur. Le commun ne fusionne pas les cycles : chaque vault garde le sien, et le maillon 8 n'agrège que domaines, projets et acteurs.

## Les pièges

- **Le vault partagé.** Le groupe demande un seul dossier « où tout le monde écrit ». C'est un produit différent, et c'est celui qui échoue : conflits sur le journal à chaque clôture, résolus par des gens qui ne sont pas développeurs. Refuser, expliquer, proposer le commun généré.
- **Le rédacteur absent.** Un membre qui n'a pas suivi la chaîne n'a pas d'export ; le commun ne le voit pas, et ses collègues croient qu'il ne fait rien. Le dire avant : le commun montre ceux qui clôturent.
- **La fuite par défaut.** `visibilite_defaut: commun` avec une note qui contient un constat sur un collègue. Le défaut `prive` protège ; l'auteur marque `visibilite: commun` note par note.
- **Le commun édité à la main.** Quelqu'un corrige une fiche dans le commun ; la fédération suivante l'écrase. Le `README.md` généré le dit, la clôture ne s'y lance jamais.

## Le passage en `mode: federe` et le rôle du maillon 8

Chaque rédacteur, à son cadrage, reçoit `mode: federe`, `commun.racine` et `commun.visibilite_defaut`, identiques pour tout le groupe. Sa clôture écrit alors `<vault>/_export/<slug>/` : les notes dont la visibilité vaut `commun`, avec `source_vault` et `exporte_le`, et un `index.json`. Une note `visibilite: prive` ne sort jamais.

Le maillon 8, `cortex-8-federation`, lit `federation.yaml` dans le commun (la liste des membres et le chemin de leur export), vide le commun et le régénère : Centre, domaines fusionnés par nom, projets et acteurs avec `source_vault`, un acteur présent chez deux rédacteurs devient une note unique. Deux fédérations sur les mêmes exports ne diffèrent que par la date. Le commun porte un `README.md` « généré, ne pas éditer » et une empreinte.

Le maillon 8 ne se lance qu'une fois tous les rédacteurs de `federation.yaml` remis (maillon 7 fait) et aucun attendu restant. Avant, l'étape reste `arbitre` dans la notice, avec la raison « en attente de <noms> », et la notice ne propose pas « relie les cerveaux ».

## Bloc config proposé

Le bloc de chaque rédacteur, par-dessus celui de son profil de poste. Lu tel quel par `cortex_config.charger_texte`. Le rejeu de la recette prend un rédacteur au profil employé.

```yaml
profil: societe
mode: federe
commun:
  racine: "~/Cortex/commun"
  export: "_export"
  visibilite_defaut: prive
donnees:
  regime: copie
collecte:
  racines: []
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  partagees: []
  plafond_projets: 60
  plafond_acteurs: 80
  plafond_domaines: 6
referentiel:
  etat: inconnu
  chemin: ""
```

Ce bloc ne porte ni `domaines` ni `cycles` : ils se décident au maillon 3, sur preuve tirée de l'inventaire. `config.yaml` sort du maillon 1 avec `domaines: []` et `cycles: []`, et `valider_installable` signale alors leur absence, ce qui est attendu (`04-contrat.md` §2).

