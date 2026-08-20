---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Runbook - Nouveau Projet

Remonte vers [[Centre]]. Procédure répétable pour tout nouveau projet. Contrat de données : [[Conventions]].

Principe : ce runbook **aiguille vers les skills** quand elles couvrent une étape, il ne réécrit pas le process. Une procédure recopiée à côté de son exécutant finit par en différer.

## Point d'entrée : la skill `nouveau-projet`

Elle orchestre les trois créations, dans cet ordre, et fait ensuite le passage de relais :

1. **La fiche de vault** — `20 - Projets/<CODE> - <Nom>.md`, depuis `_Template Projet`.
2. **Le dossier de travail** — `{{DOSSIERS_PROJETS}}/<CODE>/<Nom>/`, avec l'arborescence adaptée au type.
3. **Le CLAUDE.md du projet** — depuis le template adapté, par substitution des placeholders, back-pointer vers le vault inclus.

La skill **détecte** le type de projet mais **ne dispense jamais de la question**. La détection sert à pré-cocher la réponse par défaut, pas à sauter la validation : un type mal deviné produit une arborescence et un CLAUDE.md qu'il faudra défaire, et personne ne les défait — on vit avec.

## Ce que porte la fiche de vault, sans exception

- `type: projet`, `domaine` en lien vers son centre de gravité, `statut`, `priorite`, `debut`.
- `cycle` — une clé de `config.cycles`, ou `aucun`. Et `phase` **dans l'enum de ce cycle**.
- `facturable`, et `payeur` / `vehicule` si ces axes sont activés.
- `client` en lien `[[ ]]` — créer l'entité dans `40 - Acteurs` si elle n'existe pas.
- **Au moins un pointeur canonique** : `url_canonique`, `repo` ou `dossier_local`. Contrôle dur du lint.
- Le tag de domaine `#d/<code>`.
- Les liens vers le domaine et le client : c'est ce qui donne à la fiche sa gravité et l'empêche d'être orpheline.

## La convention de destination, cardinale

Toute production destinée à un projet atterrit dans **son dossier de travail**, sous `{{DOSSIERS_PROJETS}}/<CODE>/<Nom>/`.

Jamais ailleurs : ni dans un dossier temporaire, ni sur le bureau, ni dans les téléchargements, ni dans le répertoire d'un outil. Une convention unique, appliquée dès le premier fichier.

La raison est qu'il n'y a pas de bonne façon de rattraper l'inverse. Un livrable produit hors convention est retrouvable le jour même et introuvable trois semaines plus tard, et sa recherche coûte davantage que sa reproduction — ce qui conduit à le refaire, donc à en avoir deux versions.

**Une seule convention, jamais des variantes par type de projet.** Dans le système dont ce produit est extrait, trois conventions de chemin coexistaient : celle que le runbook prescrivait, et deux autres réellement en usage. Aucune n'était fausse ; ensemble, elles rendaient tout chemin imprévisible.

### La frontière à tenir

| Type de document | Substrat canonique | Pointeur depuis le vault |
|---|---|---|
| ce que nous produisons | le dossier de travail | `dossier_local` |
| ce que le client fournit | l'espace documentaire déclaré | pointeur dans `## Pointeurs` |
| l'état détaillé, les travaux structurés | le substrat déclaré | `substrat_canonique` + `url_canonique` |
| le code | le dépôt | `repo`, `claude_md` |

**Périmètre strict du dossier de travail : ce que nous produisons.** Mélanger les documents reçus du client avec nos livrables fait perdre la seule distinction qui compte quand il faut savoir ce qui est vérifié et ce qui est source.

## Les branches par type

### Projet de mission ou de dossier client

1. Instancier l'espace dans le substrat métier — c'est lui qui portera les travaux.
2. Poser la fiche de vault et le dossier de travail par la skill `nouveau-projet`.
3. Récupérer l'adresse retournée par le substrat et **la reporter** dans `url_canonique` de la fiche.

L'étape 3 est le seul retour d'information amont de la chaîne, et c'est celle qu'on saute. Une fiche sans `url_canonique` oblige à rechercher l'espace à la main à chaque session — le lint la signale pour cette raison.

### Projet de code

1. Créer le dépôt.
2. Écrire le `CLAUDE.md` — cadre technique canonique — **et y poser le back-pointer** vers le vault. Voir [[Amorçage]].
3. Les secrets dans un fichier d'environnement exclu du suivi de version, dupliqués dans la plateforme d'hébergement. Jamais dans le dépôt : un secret commité reste dans l'historique après suppression, il faut le révoquer.
4. Fiche de vault avec `repo`, `claude_md`, et l'URL de production s'il y en a une.

### Projet interne ou non commercial

Fiche depuis `_Template Projet`, `facturable: false`, `cycle: aucun` si aucun vocabulaire de phase ne s'applique — et dans ce cas `phase` reste **vide**, ce que le lint vérifie.

## L'automatisation

**À standardiser avant d'automatiser.** Un process automatisé avant d'être stable est un process qu'on ne peut plus corriger sans casser l'automate, et le premier réflexe devient de contourner l'automate — ce qui laisse le pire des deux mondes.

Le candidat légitime est toujours le même : l'étape qu'on a exécutée dix fois à la main de la même façon.
