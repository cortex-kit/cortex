# Profil employé : une personne dans une organisation qu'elle ne dirige pas

Ce profil s'applique quand la personne travaille pour un employeur, rend compte à quelqu'un, et porte des dossiers dont une partie lui est confiée plutôt que choisie. Son second cerveau couvre son poste, pas l'entreprise.

Ce qui le distingue des deux autres profils : la frontière du périmètre passe entre « mon travail » et « le travail des autres », et cette frontière est floue pour la personne elle-même. Le cadrage sert d'abord à la tracer.

## Les questions, en langage ordinaire

À poser par lots de quatre, options fermées plus « autre ». Une question à la fois épuise l'attention, un lot de quatre la tient. Ne jamais prononcer « substrat », « domaine », « rédacteur », « régime ».

| Sujet | Question telle qu'elle se pose | Ce que la réponse alimente |
|---|---|---|
| Métier | « En une phrase, que faites-vous dans cette organisation ? » | `organisation.nom`, le secteur (`secteurs.md`), le vocabulaire à écouter |
| N+1 | « À qui rendez-vous compte ? Une personne, pas un service. » | premier acteur déclaré, à confronter au volume mail au maillon 3 |
| Collègues | « Avec qui travaillez-vous chaque semaine ? Trois à six noms. » | acteurs internes déclarés |
| Parties prenantes | « Qui, hors de votre équipe, compte sur votre travail ou vous sollicite ? Clients internes, prestataires, autres services. » | acteurs externes déclarés, base de l'écart `correspondant_non_declare` |
| Projets portés | « Quels dossiers portez-vous en ce moment ? Ceux dont vous seriez le nom si on demandait qui s'en occupe. » | projets déclarés, base de l'écart `projet_non_declare` |
| Projets subis | « Quels dossiers vous tombent dessus sans que vous les ayez choisis ? Une charge héritée, un remplacement, une réunion qu'on vous a confiée. » | projets déclarés avec `subi: true`, souvent absents du disque |
| Outils | « Où suivez-vous l'état de vos dossiers : un tableau, un outil en ligne, votre boîte mail, votre tête ? » | `substrats.base_projets`, et donc le régime de donnée |
| Rituels | « Quelles réunions reviennent chaque semaine ou chaque mois ? » | agenda déclaré, base de l'écart `reunion_recurrente_sans_projet` |

La question sur les projets subis est celle qui rapporte le plus. Un employé déclare spontanément ce qu'il a choisi et oublie ce qu'on lui a confié, alors que c'est souvent là que vit la moitié de son temps.

## Les substrats attendus

- Un espace de fichiers personnel ou d'équipe : `~/Documents`, un lecteur réseau, un dossier synchronisé de l'entreprise.
- Une boîte mail professionnelle, souvent la seule mémoire réelle des échanges.
- Souvent aucune base de projets déclarée, alors qu'un outil d'équipe existe et que la personne y a un accès. Le poser deux fois : « et votre équipe, elle suit ça où ? ».
- Rarement du code.

## Les racines proposées

À proposer telles quelles, puis à confirmer une par une. Forme `~` obligatoire.

- `~/Documents`
- `~/Desktop`
- Le dossier synchronisé de l'employeur s'il existe, deviné depuis `_cortex/poste.json` : fournisseur `gmail` suggère un dossier de type Drive, `m365` un dossier de type OneDrive ou SharePoint. Proposer, ne jamais supposer.

Jamais le dossier personnel entier : la vie privée y côtoie le travail, et le maillon 2 la verrait.

## Les plafonds

Plus bas que le défaut, parce que le périmètre est un poste, pas une entreprise.

| Plafond | Valeur | Pourquoi |
|---|---|---|
| domaines | 5 | un poste tient rarement six centres de gravité |
| projets | 30 | au-delà, ce sont les projets des autres |
| acteurs | 40 | l'équipe, le N+1, les parties prenantes, les prestataires |
| profondeur d'arbre | 3 | |
| dossiers | 200 | |
| mois de mail | 12 | |

## Les domaines de départ

Des hypothèses à confronter à l'inventaire au maillon 3, jamais des décisions. Le maillon 3 les teste en premier, avec ses seuils, et les remplace par ce que l'inventaire montre.

- `prj` Projets portés
- `sub` Projets subis et charges héritées
- `equ` Équipe et hiérarchie
- `fon` Fonction, le métier lui-même : process, référentiels, fiches de poste

## Les pièges

- **Confondre le périmètre du poste et celui de l'entreprise.** Un employé qui déclare « la stratégie commerciale » comme dossier porte en général une partie d'un projet qu'un autre porte. Demander : « si vous partiez demain, qui reprendrait ce dossier ? ».
- **Le dossier fourre-tout.** Un `Divers/` ou `Perso/` sous la racine. Le maillon 2 le voit, le maillon 3 demande s'il relève du travail. La réponse « non » le sort du périmètre, sans le supprimer.
- **La base d'équipe non déclarée.** Un export d'outil en ligne dans un dossier de projet trahit une base que la personne consulte sans la considérer comme sienne. C'est elle qui fixe le régime : dès qu'elle est nommée, le régime passe à `pointeur`.
- **Les données des collègues.** Une fiche de poste, un entretien annuel, un organigramme sont des documents structurants du poste, pas des données sur des personnes. Un dossier RH nominatif d'autrui ne se copie jamais, quel que soit le régime.

## Bloc config proposé

Le bloc que le maillon 1 propose avant confirmation. Il est lu tel quel par `cortex_config.charger_texte` : mapping à un niveau, listes inline, pas de commentaire sur une ligne de liste.

```yaml
profil: employe
mode: solo
donnees:
  regime: copie
collecte:
  racines: ["~/Documents", "~/Desktop"]
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  plafond_projets: 30
  plafond_acteurs: 40
  plafond_domaines: 5
domaines:
  - { code: prj, nom: "Projets portés", couleur: "#1c42da" }
  - { code: sub, nom: "Projets subis", couleur: "#c9a227" }
  - { code: equ, nom: "Équipe et hiérarchie", couleur: "#0f8a6a" }
  - { code: fon, nom: "Fonction", couleur: "#8a3c0f" }
cycles:
  - { cycle: projet, phase: "Cadrage", progression: 20 }
  - { cycle: projet, phase: "En cours", progression: 60 }
  - { cycle: projet, phase: "Livré", progression: 90 }
  - { cycle: projet, phase: "Clos", progression: 100 }
```
