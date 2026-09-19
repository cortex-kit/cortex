---
name: ingest
description: Transforme une source externe en note-pointeur dans le vault — article, papier, podcast, vidéo, page d'un outil tiers, livre, rapport. Produit un résumé plafonné, des cross-références obligatoires, et met à jour les notes que la source impacte. Déclencher quand l'utilisateur dit "ingère ça", "ajoute cette source", "note cet article", "intègre ce papier", ou partage un lien avec l'intention de le garder. Ne PAS utiliser pour un simple signet, ni pour importer le contenu d'un document dans le vault.
---

# ingest — une source externe devient un pointeur

Procédure complète et raisonnée : [[Ingest - Sources externes]]. Cette skill l'exécute.

## Le test d'éligibilité, avant tout

**La source nourrit-elle au moins un projet ou un domaine actif ?**

Si non, ne pas ingérer. Le dire, et proposer un signet ordinaire.

Ce refus est la partie la plus utile de la skill. Filtrer coûte cinq secondes ; désencombrer un vault que la veille a rempli coûte une journée, et personne ne la passe jamais — on cesse simplement de faire confiance au dossier.

Second test, aussi discriminant : **cinq minutes d'attention sont-elles disponibles ?** Si le geste attendu tient en un clic, ce n'est pas un ingest, c'est un report de décision, et le résultat sera une note que personne ne relira.

## 1. Lire

Lire la source **intégralement**, ou la consulter avec sa transcription. Identifier :

- la thèse ;
- trois à cinq concepts clés ;
- **les contradictions avec ce que le vault contient déjà** ;
- les projets ou domaines impactés.

Les contradictions sont le point le plus précieux et le plus souvent sauté. Une source qui confirme tout ce qu'on pense n'apporte presque rien ; une source qui contredit une décision passée mérite d'être reliée à cette décision — c'est ce qui permettra plus tard de savoir que l'arbitrage a été réexaminé.

## 2. Écrire la note

Dans `50 - Ressources/Sources externes/`, nommée `Titre court.md` — pas de date dans le nom, elle est au frontmatter.

Frontmatter : `type: ressource`, `domaine`, `statut: actif`, `source_url`, `source_type`, `date_ingest`, `tags`.

**Le résumé ne dépasse pas `config.sante.max_lignes_entree_journal` lignes**, dix par défaut. Contrôle dur.

Format : une liste de concepts, jamais des paragraphes recopiés. Citation textuelle réservée aux formulations vraiment marquantes — deux au maximum, entre guillemets.

La source reste à son adresse. La recopier ne crée aucune valeur et crée une version qui divergera de l'original. Ce qui a de la valeur, c'est **pourquoi elle compte ici**, et ça tient en dix lignes.

## 3. Relier — obligatoire

Des liens `[[ ]]` vers : le ou les domaines, les projets impactés, les autres notes ressource sur le même sujet, les décisions concernées.

**Une source sans lien sortant est un ingest manqué.** Elle ne sera jamais retrouvée, donc elle n'existe pas — autant ne pas l'avoir ingérée. Le lint la refusera comme orpheline.

## 4. Répercuter

- La source change l'analyse d'un projet → une puce datée sous `## Décisions` de sa fiche, pointant vers la note ressource.
- Elle provoque une bascule de stratégie → une note `type: decision` dans `60 - Journal/`.

Une source ingérée qui ne change rien nulle part est une source qui ne méritait pas l'étape 1.

## 5. Journaliser

Une ligne dans le `## Historique` du `_README` du dossier : `- AAAA-MM-JJ - [[Titre]] - impact en une ligne`.

## Régime copie : les structurants

Deux régimes de donnée cohabitent, fixés au cadrage dans `config.yaml`, clé `donnees.regime`.

En régime `pointeur`, tout ce qui précède s'applique et rien d'autre : la source reste à son adresse, le vault la désigne.

En régime `copie`, un second geste existe pour une famille restreinte de documents, les structurants : organigramme, process, fiche de poste, contrat, projet, acteur, tenants et aboutissants, fil de messagerie structurant. Ceux-là sont recopiés dans `50 - Ressources/Structurants/<type>/`, parce qu'ils fondent la compréhension et qu'un lien mort vers un fichier déplacé vaut zéro. La liste exacte vit dans `donnees.structurants`, le plafond dans `sante.max_structurants`.

Le geste, depuis la racine du vault :

    python3 .claude/skills/ingest/copie_structurant.py --vault . --source <fichier> --type process --domaine "Ops"

La copie porte `type: structurant`, `structurant`, `domaine`, `source_path` en forme `~`, `hash` (sha256 de la source) et `copie_le`. Le script rejoué ne duplique pas : même hash, il ne touche rien ; hash différent, il rafraîchit ; note écrite à la main, il refuse et le dit.

## Rafraîchir un structurant périmé

Le lint compare le `hash` du frontmatter à la source et lève `structurant_perime` : la source a changé depuis la copie, ou elle a disparu. C'est une dette, pas un blocage, et le lint reste à 0.

Devant un `[i] structurant(s) dont la source a change depuis la copie` :

1. Lire la ligne du constat : elle donne le fichier du vault et le `source_path`.
2. Source toujours là, changement voulu : rejouer la commande ci-dessus sur la même source, avec le même `--type` et le même `--domaine`. La copie se rafraîchit, le hash suit, le constat tombe.
3. Source déplacée : la copier de nouveau depuis sa nouvelle adresse, puis supprimer l'ancienne note si le titre a changé.
4. Source supprimée à dessein : garder la copie et l'assumer, elle est devenue la seule trace ; ou la retirer du vault si elle n'a plus d'objet.

Un structurant périmé qu'on laisse est un choix, pas un oubli, du moment qu'il est vu. Le bilan le redit à chaque passage.

## Idempotence

Avant de créer, vérifier qu'une note ne pointe pas déjà vers la même `source_url`. Si oui : **mettre à jour** plutôt que dupliquer, et le signaler.

## Interdits

- **Plus de dix lignes de résumé.** Contrôle dur.
- **Aucun contenu de la source recopié** au-delà de deux citations courtes.
- **Aucune note sans lien sortant.**
- **Ne jamais inventer** un impact sur un projet pour justifier l'ingest. Si la source n'impacte rien, c'est le constat qui compte.
- Une source périmée passe en `statut: obsolete` ; elle ne se supprime pas. Supprimer casse les liens entrants et efface la trace de la décision qu'elle avait influencée.
