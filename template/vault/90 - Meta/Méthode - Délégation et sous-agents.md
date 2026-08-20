---
type: meta
tags:
  - hub
cree: 2026-05-31
maj: 2026-05-31
---
# Méthode - Délégation et sous-agents

Remonte vers [[Centre]]. Comment le travail hors-scope est traité sans polluer le fil principal. Complète [[Runbook - Nouveau Projet]] et [[Architecture Mémoire]].

## Principe : tâche déléguée en session isolée

Quand un sujet utile surgit mais sort du périmètre de la session en cours (correction dans un autre repo, dette repérée, faille de sécurité vue au passage), on ne l'exécute pas dans le fil : on le **flague comme tâche déléguée**. Elle part dans :
- une **session d'agent séparée**, dédiée au sujet ;
- un **worktree git** (copie isolée du repo, bac à sable) : le vrai dossier reste intact tant que rien n'est validé ;
- avec une **consigne autoportante** : la session déléguée ne connaît pas la conversation d'origine, donc la consigne contient tout le contexte nécessaire.

Validation par **diff** : on relit la modification proposée avant de l'intégrer. Rien n'est mergé sans accord.

## Quand l'utiliser

- Correction hors-sujet du changement courant (ne pas mélanger deux intentions dans un même commit).
- Travail dans un autre repo que celui de la session.
- Vulnérabilité ou bug repéré avec confiance pendant une autre tâche.
- Dette technique à isoler pour rester concentré sur la fondation.

## Bénéfice

Le fil principal garde une seule intention claire. Les à-côtés ne sont ni oubliés (ils deviennent une tâche traçable) ni intrusifs (ils s'exécutent ailleurs). C'est l'équivalent opérationnel de la règle « 1 changement cohérent à la fois ».

## Capacités plus larges (réserve, sur demande explicite)

- **Sous-agents parallèles** : plusieurs agents lancés en éventail pour explorer/chercher dans beaucoup de fichiers à la fois, puis synthèse. Utile pour les recherches larges.
- **Workflows** : orchestration multi-agents déterministe (boucles, vérification adverse, fan-out) pour les gros chantiers (audit exhaustif, migration). Coûteux en tokens, donc uniquement sur demande explicite.

Par défaut : une seule session, déléguer les à-côtés. Mobiliser les capacités larges seulement quand l'ampleur du travail le justifie et que tu l'as demandé.
