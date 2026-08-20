---
type: meta
tags:
  - doctrine
  - optionnel
cree: {{DATE}}
maj: {{DATE}}
---
# Vue Obsidian (Dataview, optionnel)

Rattachée à [[Architecture Mémoire]] (couche VUE). Contrat de données : [[Conventions]].

**Cette note est la seule du vault à dépendre d'un plugin.** Aucune autre note ne pointe vers elle — c'est un cul-de-sac délibéré, pour que rien ne casse si le plugin n'est jamais installé. Elle pointe en revanche vers la doctrine qui la justifie : une note sans lien sortant serait injoignable, et le lint la refuserait à juste titre.

## Pourquoi c'est optionnel, et pourquoi c'est isolé ici

Le vault est conçu **sans aucun plugin communautaire**. Markdown, YAML, et les plugins livrés avec Obsidian — recherche, liens entrants, propriétés, graphe, templates. C'est ce qui lui permet de fonctionner dans un éditeur de texte, dans un `grep`, dans une session d'agent, et de s'installer en entreprise sans demander la validation d'une extension tierce non signée.

Cette décision vient d'un constat, pas d'une préférence. Dans l'installation qui a servi de modèle à ce produit, une vingtaine de blocs de requête étaient répartis dans le tableau de bord et trois templates — et le plugin n'avait jamais été installé. Ces blocs s'affichaient en code brut depuis des mois. Le système fonctionnait très bien : la vue réelle était ailleurs. Pire, les templates fautifs avaient essaimé **quarante blocs morts** dans les notes de contenu qu'ils avaient servi à créer.

D'où le rangement : les requêtes existent, elles sont regroupées, elles sont génériques, et elles sont dans un cul-de-sac. Si tu installes Dataview, elles marchent. Sinon, tu ne les vois jamais.

## Une propriété utile de ces requêtes

Aucune ne contient de nom de domaine en dur. Elles utilisent `GROUP BY domaine`, ce qui les rend valides quelle que soit la configuration — et évite la duplication d'une même requête par domaine, qui est ce qui avait fait gonfler le tableau de bord d'origine à onze blocs pour sept formes réelles.

## Les projets actifs, groupés par domaine

```dataview
TABLE WITHOUT ID file.link AS "Projet", phase AS "Phase", priorite AS "Prio", echeance AS "Échéance", client AS "Client"
FROM "20 - Projets"
WHERE type = "projet" AND statut = "actif"
GROUP BY domaine
SORT priorite ASC
```

## Les acteurs, groupés par domaine et catégorie

```dataview
TABLE WITHOUT ID file.link AS "Acteur", categorie AS "Catégorie", statut AS "Statut", dernier_contact AS "Dernier contact"
FROM "40 - Acteurs"
WHERE type = "acteur"
GROUP BY domaine
SORT dernier_contact DESC
```

## Les échéances à sept jours

```dataview
TABLE WITHOUT ID file.link AS "Projet", domaine AS "Domaine", echeance AS "Échéance", priorite AS "Prio"
FROM "20 - Projets"
WHERE type = "projet" AND statut = "actif"
  AND echeance >= date(today) AND echeance <= date(today) + dur(7 days)
SORT echeance ASC
```

## Les actions ouvertes, groupées par domaine

```dataview
TASK
FROM "20 - Projets"
WHERE !completed
GROUP BY domaine
```

## Les projets dont le journal dort

Le complément de la métrique de santé : un projet actif dont personne n'a écrit la raison de son état depuis deux semaines.

```dataview
TABLE WITHOUT ID file.link AS "Projet", domaine AS "Domaine", dernier_journal AS "Dernier journal", phase AS "Phase"
FROM "20 - Projets"
WHERE type = "projet" AND statut = "actif"
  AND (!dernier_journal OR dernier_journal < date(today) - dur(14 days))
SORT dernier_journal ASC
```

## Ce que ces requêtes ne remplacent pas

Le lint. Une requête affiche, elle ne bloque pas — et la leçon centrale de ce produit est que **la détection sans blocage ne protège pas** : les deux pires dérives du système d'origine étaient affichées en avertissement pendant des mois sans que rien ne les empêche. Les contrôles qui comptent sont dans `.claude/skills/lint/`, avec un code de retour.
