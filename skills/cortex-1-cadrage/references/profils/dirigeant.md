# Profil dirigeant : une personne qui porte une organisation

Ce profil s'applique quand la personne dirige une structure, seule ou avec quelques associés, et que son travail est l'entreprise elle-même : les affaires, les clients, l'argent, les gens, les fournisseurs. Son second cerveau couvre l'organisation vue de son poste, pas le poste de chacun.

Ce qui le distingue : rien ne lui est « subi » au sens de l'employé, tout lui remonte. Le cadrage sert à séparer ce qu'elle tient elle-même de ce qu'elle délègue et ne fait que suivre.

## Les questions, en langage ordinaire

Par lots de quatre, options fermées plus « autre ». Un dirigeant décroche à la cinquième question sans réponse écrite en face. Ne jamais prononcer « substrat », « domaine », « rédacteur », « régime ».

| Sujet | Question telle qu'elle se pose | Ce que la réponse alimente |
|---|---|---|
| Métier | « Que vend votre entreprise, à qui, et à combien de personnes ? » | `organisation.nom`, secteur, effectif, ordre de grandeur des plafonds |
| N+1 | « À qui devez-vous rendre des comptes ? Associés, conseil, banque, actionnaire, personne. » | acteurs de gouvernance, souvent absents du disque et présents dans le mail |
| Collègues | « Sur qui vous appuyez-vous au quotidien ? Les trois à six personnes sans qui rien ne tourne. » | acteurs internes, base d'une future fédération |
| Parties prenantes | « Qui, dehors, pèse sur vos décisions ? Clients principaux, fournisseurs, expert-comptable, banque, assureur. » | acteurs externes déclarés, base de l'écart `correspondant_non_declare` |
| Projets portés | « Quelles affaires ou quels chantiers suivez-vous vous-même en ce moment ? » | projets déclarés |
| Projets subis | « Qu'est-ce qui vous occupe sans être une affaire : une mise en conformité, un recrutement, un litige, un déménagement ? » | projets transverses, ceux qu'on oublie de nommer parce qu'ils ne facturent pas |
| Outils | « Où vit l'état de vos affaires : un logiciel de gestion, un tableur, un outil en ligne, un cahier ? » | `substrats.base_projets`, régime de donnée |
| Rituels | « Quelles réunions reviennent : point hebdo, revue de chantier, comité, conseil ? » | agenda déclaré, base de l'écart `reunion_recurrente_sans_projet` |

La question sur les outils décide du régime. Un dirigeant qui suit ses affaires dans un logiciel de gestion a une base déportée, même s'il ne l'appelle pas ainsi : régime `pointeur`. Celui qui les suit dans un tableur sur son disque n'en a pas : régime `copie`, et le tableur devient un structurant candidat.

## Les substrats attendus

- Un espace de fichiers d'entreprise : dossier partagé, serveur, dossier synchronisé, avec une arborescence par affaire ou par client.
- Une boîte mail très chargée, seul lieu où les fournisseurs, la banque et l'expert-comptable existent.
- Souvent un logiciel de gestion ou de devis, parfois un tableur qui en tient lieu.
- Un agenda tenu par la personne ou par une assistante.
- Rarement du code, sauf société technologique.

## Les racines proposées

À proposer telles quelles, puis à confirmer une par une. Forme `~` obligatoire.

- `~/Documents`
- Le dossier partagé de l'entreprise, deviné depuis `_cortex/poste.json` : `gmail` suggère un dossier de type Drive, `m365` un dossier de type SharePoint ou OneDrive. Proposer, ne jamais supposer.
- Le dossier des affaires s'il vit ailleurs, par exemple `~/Affaires`.

## Les plafonds

Les défauts du contrat. Une PME tient dedans ; au-delà, c'est une société à plusieurs rédacteurs, et c'est le profil `societe`.

| Plafond | Valeur | Pourquoi |
|---|---|---|
| domaines | 6 | plafond dur de la doctrine |
| projets | 60 | au-delà, on livre un annuaire |
| acteurs | 80 | clients, fournisseurs, équipe, gouvernance |
| profondeur d'arbre | 3 | |
| dossiers | 200 | |
| mois de mail | 12 | |

## Les domaines de départ

Des hypothèses à confronter à l'inventaire au maillon 3, jamais des décisions. Le piège de ce profil est de reproduire l'organigramme (§`secteurs.md`) ; ces quatre familles suivent la nature du travail.

- `aff` Affaires, ce qui se vend et se livre
- `cli` Clients et marché
- `fou` Fournisseurs et partenaires
- `adm` Administration, finance, personnel

Une menuiserie d'agencement fictive, sur laquelle la recette rejoue ce profil, montre le cas typique : les affaires captent tous les projets datés, tandis que le bureau d'études, les achats et l'atelier portent des acteurs, des ressources et des décisions sans porter un seul projet. Compter en notes, pas en projets (`secteurs.md` §Seuils).

## Le cycle de départ

Même statut que les domaines : une hypothèse pour le maillon 3, jamais une décision du maillon 1.

| Cycle | Phase | Progression |
|---|---|---|
| affaire | Devis | 10 |
| affaire | Signée | 30 |
| affaire | En cours | 60 |
| affaire | Réceptionnée | 100 |

## Les pièges

- **Le découpage par organigramme.** Le dirigeant propose « commercial, production, administratif » parce que c'est sa carte mentale. Un chantier traverse les trois. Suivre la nature du travail.
- **Tout est prioritaire.** Soixante affaires déclarées « en cours » dont quarante sont closes ou dormantes. Demander pour chacune : « un mail ou un fichier sur cette affaire ces trente derniers jours ? ». L'inventaire tranchera.
- **Les chiffres sensibles.** Comptabilité, paie, contrats de travail, polices d'assurance sont des structurants légitimes en régime `copie`, mais ils contiennent des données de personnes et des montants. Copier l'existence et la structure, jamais les montants ni les noms de salariés. La règle vaut aussi pour le résumé en régime `pointeur`.
- **La messagerie comme base de projets.** Un dirigeant qui répond « dans mes mails » à la question des outils n'a pas de base déportée : régime `copie`, et la messagerie reste soumise à l'accord tracé.
- **Les associés.** Deux dirigeants qui veulent « le même outil » sont deux rédacteurs : c'est le profil `societe`, pas un vault à deux.

## Bloc config proposé

Le bloc que le maillon 1 propose avant confirmation. Lu tel quel par `cortex_config.charger_texte`.

```yaml
profil: dirigeant
mode: solo
donnees:
  regime: copie
collecte:
  racines: ["~/Documents"]
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  plafond_projets: 60
  plafond_acteurs: 80
  plafond_domaines: 6
```

Ce bloc ne porte ni `domaines` ni `cycles` : ils se décident au maillon 3, sur preuve tirée de l'inventaire. `config.yaml` sort du maillon 1 avec `domaines: []` et `cycles: []`, et `valider_installable` signale alors leur absence, ce qui est attendu (`04-contrat.md` §2).

