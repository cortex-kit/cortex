# Cadrage : Phase H2

## Pourquoi cette phase existe

Le parcours réel du 2026-09-27 a joué la chaîne complète pour deux rédacteurs fictifs d'Alcyon Promotion (Hélène, présidente ; Karim, foncier), puis la fédération. Les trois bloquants (hash export/fédération, identité git du consultant dans l'historique, écriture de Bash hors du vault) sont corrigés sur `fix/phase-h` en trois commits (`12a4b24`, `a7b7678`, `01955f6`) et rejoués avec succès. Restent dix majeurs : la règle de la Phase H invalide la phase au-delà de trois. Ils tiennent presque tous à la conduite du modèle devant la personne (ce qu'il dit, ce qu'il lit, ce qu'il décide seul), plus quatre défauts de scripts.

## Inclus

Les dix majeurs, numérotés comme dans le verdict :

1. **Vocabulaire interdit à l'écran** : « consultant », « profil », « parcours dirigeant/employé », « écart », « maillon N », noms de skills, dits à la personne.
2. **Question reposée** : la liste des mentions interdites reposée après une réponse (H1), reproposée à Karim avec des noms de clients en « Recommandé » (K1).
3. **Lectures hors périmètre** : `grep` dans `~/Dev/cortex` sur le nom du client, `ls ~/Documents ~/Desktop ~/OneDrive ~/PRO`, lecture de la mémoire de Claude, `~/Documents` et `~/Desktop` proposés comme racines « par défaut ».
4. **Confidentialité** : les noms d'autres clients du consultant, glanés sur le poste, proposés dans l'atelier d'un client.
5. **Validation à l'aveugle** : une question demande de valider un contenu jamais affiché (cahier des charges au maillon 6, bloc identité au maillon 1).
6. **Voie softeria sans accord** : `poste.py` la déduit de « Microsoft, non administrateur » et l'écrit sans question.
7. **Détection des outils** : `poste.py` cherche dans le PATH seul (`~/.local/bin` absent), sonde markitdown par `uvx` bloqué par le sandbox, lit `gh` « expiré » dans le sandbox. Il confond « absent » et « non mesurable ».
8. **Windows sans sandbox** : sous Windows natif, Bash n'est pas confiné au vault.
9. **Étape 8 et atelier existant** : l'étape 8 vaut « à faire » au lieu d'« arbitrée » tant qu'un rédacteur n'est pas remis, et la notice propose « relie les cerveaux » trop tôt ; au maillon 0, un atelier existant est pris pour celui de la personne au lieu de demander le nom court.
10. **Lint du commun** : une édition à la main qui garde l'en-tête « généré » n'est pas signalée.

Mineurs embarqués parce qu'ils coûtent peu :

- hook Stop et SessionStart en chemin relatif (cassent après un `cd`) ;
- statut `en_cours` lu « illisible » par `etat.py` ;
- contrôle 3 du skill 8 : la ligne « Généré par … le <date> » du README compte comme un écart ;
- `options_proposees` vaut les trois options quand la personne répond « Aucun » ;
- un dossier de photos (3 fichiers, hors travail) n'est jamais candidat à l'écart.

Puis le parcours Alcyon complet rejoué (Phase C).

## Exclus (non-objectifs)

- Toucher `export.py`, le bloc `sandbox` de `settings_json()`, `poser_identite()` ou le contrôle d'historique du maillon 7 : c'est le correctif des bloquants, rejoué et vert.
- Réécrire un SKILL.md en entier, changer l'ordre des étapes d'un maillon, ajouter un maillon ou une question qui n'existe pas.
- Élargir le sandbox du vault (pas d'atelier en `allowWrite`, décision 3).
- Bloquer l'installation sous Windows natif (décision 4).
- Toucher `fixtures.py` de la recette, les fixtures Alcyon, ou les vaults de test `~/Cortex/helene`, `~/Cortex/karim`, `~/Cortex/alcyon-commun` pendant les lanes A et B.
- Les autres mineurs du verdict (question Sitadel au maillon 2, emplacement du vault absent du skill 4, notice à 4/9 après installation, conflit de porteur non détecté, tutoiement et vouvoiement mêlés hors vocabulaire interdit) : suivis, pas traités.
- Pousser, merger, taguer. Le chef d'orchestre merge, l'humain décide du push et du tag.

## Décisions actées (ne pas requestionner)

1. Découpage : lane A code, lane B conduite, en parallèle, fichiers disjoints ; lane C parcours après merge. (Evrard, 2026-09-27)
2. La liste des rédacteurs d'un groupe vit dans `<commun>/federation.yaml`, inscrite dès le cadrage de chaque rédacteur ; `etat.py` y lit les membres et cherche `remis_le` dans le vault de chacun. Aucune clé de config nouvelle. (Evrard)
3. Le maillon 8 se lance depuis la session de l'atelier. Lancé depuis un vault, il produit le commun et donne la commande `notice.py` à jouer côté atelier ; le sandbox du vault ne s'élargit pas. (Evrard)
4. Windows natif : la limite se documente (README, `OUTILS.md`, guide de remise) avec WSL2 recommandé pour un poste sensible ; rien ne bloque l'installation. (Evrard)
5. Une note repassée en privé sort du commun par retrait silencieux à la clôture suivante, sortie 0. Le refus (sortie 1, commun intact) ne vaut que pour une note privée présente dans un export. (Evrard, 2026-09-27)
6. Les mentions interdites d'un atelier client ne contiennent que les marques du consultant, qu'il saisit lui-même ; aucun nom d'un autre client n'y figure, et rien ne se glane sur le poste. (Evrard, réponse au cadrage d'Hélène)
7. Un défaut se note pendant un test, il ne se répare pas ; chaque correctif porte son contrôle de recette et une contre-épreuve rouge sur l'ancien code.

## Risques et hypothèses

- **Banc de test** : le parcours tourne sur la machine du fabricant. Les sessions testées voient `~/Dev/cortex`, l'identité git et la mémoire du pilote. La lane B réduit ce que le modèle va lire ; la lane C doit neutraliser la mémoire du pilote (annexe, « Préparation »).
- La conduite du modèle ne se prouve pas par la recette : les lanes A et B la bornent par le texte et par des contrôles de grep, la preuve reste le parcours C.
- Hypothèse : `~/.local/bin` est l'emplacement des outils posés par `uv tool install` ; la lane A le lit par `uv tool dir --bin` quand `uv` répond, et retombe sur `~/.local/bin` sinon.

## Modèle cible et effort

Exécutant des lanes A, B et C : Opus 5.5, effort `high` (plusieurs sous-systèmes, conduite fine). Auditeur : Opus 5.5, effort `high`, session neuve par lane.
