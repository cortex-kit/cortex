---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Runbook - Chantiers (phase packs)

Remonte vers [[Architecture Mémoire]] (couche PLAYBOOK). Cycle standard de TOUT chantier **interne** au vault — infrastructure, agents, scripts, ontologie — distinct de [[Runbook - Nouveau Projet]] qui couvre les projets et les missions métier.

Un chantier interne n'est pas un projet : il n'a pas de client, sa valeur n'est pas facturable, et il change le système avec lequel on travaille pendant qu'on travaille. C'est pourquoi il mérite un cycle à lui, plus contraignant sur la preuve que sur le délai.

## Cycle de vie (7 étapes)

1. **Cadrage.** Si le chantier découle d'une décision structurante : note `type: decision` dans `60 - Journal/` d'abord. Sinon cadrage direct dans le pack.
2. **Pack.** Dossier `90 - Meta/passation/<chantier>/<phase>/` (README + `01-cadrage` → `08-prompt-verification`). Un pack = une phase autonome, exécutable par n'importe quelle session sans autre contexte. Le pack transmet TOUT : **la session d'origine peut mourir.** C'est le test à appliquer avant de le considérer fini — si sa lecture seule ne suffit pas à exécuter, il est incomplet.
3. **Exécution.** Une session = un périmètre = un exécutant. Adds ciblés, commits mono-sujet, essai à blanc avant toute opération destructive.
4. **Preuves.** Chaque item fini = une commande et sa sortie réelle, consignées dans le `06-verification` du pack. **La vérité est l'ÉTAT** — journal git, comptages, fichiers — jamais les déclarations, y compris celles d'autres sessions ou de {{REDACTEUR}} sur ce que d'autres auraient « fini ». Un agent qui rapporte un succès n'est pas une preuve de succès.
5. **Audit à froid** (chantiers à risque : infrastructure, purge, sécurité, exposition de données). Session **indépendante** via `08-prompt-verification`, verdict GO / NO-GO avec conditions numérotées. Chaque condition doit être vérifiable par une commande. Les conditions du GO se consignent dans le README du pack et se soldent une à une. L'auditeur ne lit pas le compte rendu de l'exécutant : il constate.
6. **Merge.** Sur mandat explicite de {{REDACTEUR}}. Idempotence : avant d'exécuter ou de merger, constater si c'est déjà fait — déjà fait = skip constaté, jamais re-exécuté.
7. **Clôture.** Statuts du pack mis à jour (`05-execution` coché avec les empreintes de commit). Si le chantier continue au-delà de la session, régénérer le prompt de reprise : le rôle est une chaîne, pas une personne.

## Invariants transverses

- Un seul exécutant par périmètre. Concurrence détectée = arrêt et arbitrage, jamais de course.
- `git add` ciblés, jamais `add -A` sur le vault : la configuration locale de l'éditeur produit du bruit qui n'a pas à être versionné avec la doctrine.
- Force-push et suppression de branche distante = mandat explicite, jamais d'initiative.
- Arbitrages : question courte **avec recommandation**, puis attendre. Pas de question dont la réponse est déjà dans le pack.
- Écriture impossible depuis l'environnement courant = fournir le geste exact à coller, jamais improviser un contournement.
- Un instrument de mesure fait partie de ce qui est audité. Le rejouer et lire ce qu'il classe sont deux contrôles distincts, et aucun ne remplace l'autre.

## Pointeurs

- Sessions de travail : [[Runbook - Sessions de travail]].
- Ontologie et contrat de données : [[Conventions]].
