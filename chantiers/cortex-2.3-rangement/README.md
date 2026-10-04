# Cortex 2.3.0 : rangement de l'existant et référentiel commun

**Statut** : livrée, à auditer après la reprise 2 (code au commit `b898688`, recette 199 contrôles à 0 ; rapport dans `rapport.md`). Écrit le 2026-10-04 ; lane `lane/rangement` dans `~/Dev/cortex--rangement`
**Objectif en une phrase** : avant de construire le vault, Cortex propose de ranger les dossiers de travail de la personne (noms parlants, arborescence, index lisible par toute IA) et l'applique sur son accord, de façon réversible ; les procédures et assistants établis pour toute l'entreprise vivent dans un dossier partagé de référence vers lequel chaque vault pointe ; aucune procédure n'est jamais copiée.
**Modèle exécutant (07)** : Opus 5.5
**Modèle auditeur (08)** : Opus 5.5
**Effort recommandé** : exécution `high` (une étape neuve, un script qui écrit hors du vault, six maillons retouchés, la recette), audit `high`
**Base** : `main` à `cf5912a` (2.2.1, recette 154 contrôles à 0) ; le pack lui-même est le commit `2c1f289`

## Ordre de lecture
1. `01-cadrage.md` : pourquoi, inclus, non-objectifs, décisions actées
2. `02-backlog-produit.md` : ce que la personne vit, mot pour mot
3. `03-backlog-technique.md` : fichiers, composants, commandes
4. `04-contrat.md` : clés, formats, gestes, invariants
5. `05-execution.md` : plan de tâches
6. `06-verification.md` : critères d'acceptation
7. `07-prompt-execution.md` : à coller dans la session ouverte sur le worktree
8. `08-prompt-verification.md` : à coller dans une session neuve pour l'audit

Contrat de référence toujours en vigueur : `chantiers/cortex-v2/04-contrat.md` et ses amendements. Ce pack l'étend, il ne le réécrit pas.

## Ce que cette phase livre
- Une étape facultative « 3 bis » entre la décision des domaines et la construction : skill `cortex-3b-rangement`, phrase « rangeons mes dossiers », script `range.py` (proposer, appliquer par lot, vérifier, annuler).
- Le référentiel commun : déclaré au cadrage, adopté s'il existe, proposé s'il manque, indexé par un `AGENTS.md` à sa racine.
- Les procédures et les assistants classés en personnels (pointés depuis le vault) ou d'entreprise (rangés dans le référentiel, pointés depuis chaque vault et depuis le commun fédéré).
- La doctrine : une section « Ce que la chaîne écrit hors du vault », la procédure retirée des types copiables.
- La recette étendue, verte.

## Contexte de suite
Avant : 2.2.0 sait adopter un vault existant ; la convergence phase 1 a été auditée et reprise en 2.2.1, acceptée le 2026-10-04. Le 2026-10-04, le commanditaire a confronté son schéma en six étapes à la chaîne : le régime de donnée 2.2.0 est maintenu (pointeur si une base existe, copie des documents de fond sinon), Cortex ne crée aucune base, mais il range l'existant et sépare le personnel du commun.
Après : fusion sur `main` par le chef d'orchestre une fois l'audit à froid de cette lane accepté (la condition D10 sur la convergence est remplie depuis la 2.2.1) ; montée de `plugin.json` en 2.3.0 et tag par le chef d'orchestre. Hors périmètre ici : rangement proposé après la remise, création de bases.
