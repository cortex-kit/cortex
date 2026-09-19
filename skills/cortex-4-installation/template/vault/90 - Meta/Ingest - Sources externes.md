---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Ingest - Sources externes

Remonte vers [[Centre]]. Procédure répétable de l'opération **Ingest**, flux « source externe ». Complète [[Conventions]] et [[Architecture Mémoire]].

## Quand l'utiliser

Une source externe à intégrer : article, papier, podcast, vidéo, page d'un outil tiers, livre.

Critère d'éligibilité, et il est strict : **la source nourrit au moins un projet ou un domaine actif.** Sinon on n'ingère pas. Filtrer en amont coûte cinq secondes ; désencombrer un vault que la veille a rempli coûte une journée, et la plupart du temps on ne le fait jamais.

## Pré-requis

- Source localisée et accessible, avec une adresse stable.
- Domaine de rattachement identifié : un au minimum, plusieurs si le sujet est transverse.
- Au moins cinq minutes d'attention. **L'ingest n'est pas un signet.** Si le geste tient en un clic, ce n'est pas un ingest, c'est un report de décision.

## Procédure

### 1. Lecture

Lire la source intégralement, ou la consulter avec sa transcription si c'est de l'audio ou de la vidéo. Identifier : la thèse, trois à cinq concepts clés, les **contradictions avec ce que le vault contient déjà**, et les projets ou domaines impactés.

Les contradictions sont le point le plus précieux et celui qu'on saute le plus souvent. Une source qui confirme tout ce qu'on pense déjà n'apporte presque rien ; une source qui contredit une décision passée mérite d'être reliée à cette décision.

### 2. Filing

Note dans `50 - Ressources/Sources externes/`. Nom de fichier : `Titre court de la source.md` — pas de date dans le nom, elle est dans le frontmatter. Frontmatter conforme au `_README` du dossier.

### 3. Résumé en pointeur

**Maximum {{SEUIL_JOURNAL}} lignes.** C'est un contrôle dur du lint, pas une recommandation.

Format : liste de concepts, jamais de paragraphes recopiés. Citation textuelle réservée aux formulations vraiment marquantes, deux au maximum, entre guillemets.

La raison du plafond : la source reste accessible à son adresse. La recopier ne crée aucune valeur et crée deux problèmes — une version qui divergera de l'original, et un vault qu'on ne peut plus parcourir. Ce qui a de la valeur, c'est **pourquoi cette source compte ici**, et ça tient en dix lignes.

### 4. Cross-références

Lier `[[ ]]` vers le ou les domaines concernés, les projets impactés, les autres notes ressource sur le même sujet, les décisions liées.

**Une source sans aucun lien sortant est un ingest manqué.** Elle ne sera jamais retrouvée, donc elle n'existe pas.

### 5. Mise à jour des notes liées

- Si la source change l'analyse d'un projet : une puce datée sous `## Décisions` de la fiche projet, pointant vers la note ressource.
- Si elle provoque une bascule de stratégie : une note `type: decision` dans `60 - Journal/`.

### 6. Log

Une entrée dans le `## Historique` du `_README` du dossier : `- YYYY-MM-DD - [[Titre]] - impact en une ligne`.

## Garde-fous

- **Pointeur jamais copie.** Au-delà de {{SEUIL_JOURNAL}} lignes recopiées, c'est un anti-pattern, et le lint le refuse.
- **Pas d'ingest de complaisance.** Si la source ne change rien à un projet ou domaine actif, ne pas l'ingérer. La veille décorative alourdit le graphe et fait baisser la confiance dans tout le reste.
- **Le jugement reste humain.** Le résumé peut être rédigé par un agent, mais il doit refléter ce que {{REDACTEUR}} estime digne d'être retenu. Un résumé générique produit par un modèle est indistinguable d'un résumé qu'on n'a pas lu.
- **`statut: obsolete` plutôt que suppression.** Si une source disparaît ou se périme, basculer son statut. Supprimer la note casse les liens entrants et efface la trace de la décision qu'elle avait influencée.

## Cas particulier : une page d'un outil tiers comme source

Le substrat externe reste canonique. La note du vault pointe via `source_url`. Si la page bouge, basculer la note en `statut: obsolete` et en créer une nouvelle sur la nouvelle adresse — plutôt que de corriger l'URL en place, ce qui effacerait le fait que la source a changé.

Pour un **espace pivot** (une base de veille, un répertoire de ressources) : une note pivot unique qui sert d'INDEX, et des notes individuelles pour les seules sous-pages qui déclenchent un impact sur un projet. Indexer un espace entier note par note revient à le recopier.

## Outils

Les lectures se font avec ce dont l'agent dispose : lecture de page web, connecteur vers le substrat concerné, lecture de fichier local. Aucun outil particulier n'est requis par cette procédure.
