# Backlog produit : Phase H2

## Valeur utilisateur

La personne qui reçoit un second cerveau n'a pas de compétence technique. Elle doit entendre ses mots, jamais ceux de la chaîne ; valider ce qu'elle voit ; ne jamais retrouver sur son poste une trace du consultant ou d'un autre client ; et ne recevoir d'installation ni de branchement qu'elle n'a pas acceptés. Le consultant, lui, doit pouvoir mener un groupe de rédacteurs sans que le tableau de bord lui propose de relier les cerveaux avant que tout le monde soit remis.

## Ce que la personne vit autrement, défaut par défaut

| # | Avant (parcours du 2026-09-27) | Après |
|---|---|---|
| 1 | « Mode consultant, organisation à plusieurs rédacteurs », « je dois trancher quatre écarts », « Accepter l'écart » | Des phrases ordinaires : « Vous installez pour quelqu'un d'autre, dans une équipe de plusieurs personnes », « quatre points à éclaircir avec vous » |
| 2 | La liste des noms interdits revient après « retirez », puis revient chez Karim avec les clients en « Recommandé » | Une réponse donnée tient. Chez le second rédacteur, la marque de l'organisation est reprise telle quelle et dite, pas redemandée |
| 3 | La session fouille le dépôt du plugin, les dossiers personnels et la mémoire de Claude pour « deviner » ; elle propose `~/Documents` comme racine par défaut | La chaîne lit l'atelier, le vault, les racines déclarées et les fichiers du plugin, rien d'autre. Les racines se demandent, elles ne se proposent pas depuis un parcours du disque |
| 4 | Six noms d'autres clients proposés pour l'atelier d'Hélène | La liste proposée ne contient que les marques du consultant, qu'il complète lui-même |
| 5 | « Le cahier des charges est-il juste ? » sans cahier à l'écran | Tout contenu à valider est affiché dans le message ou dans l'aperçu de l'option, avant la question |
| 6 | La voie softeria s'écrit sans qu'on la propose | Une question explique ce que la voie installe (un petit serveur local, l'outil node) ; un refus vaut « aucune » |
| 7 | « graphify absent » alors qu'il vient d'être installé ; une question de développeur posée à la cliente | Un outil installé est vu comme présent ; un outil qu'on ne peut pas mesurer se dit « à vérifier », jamais « absent » |
| 8 | Rien n'avertit qu'un Windows natif laisse Bash hors confinement | Le README, la fiche des outils et le guide de remise le disent, WSL2 recommandé pour un poste sensible |
| 9 | Étape 8 « à faire » et « relie les cerveaux » proposé alors que Karim n'est pas cadré ; au maillon 0, l'atelier `evrard` pris pour celui d'Hélène | Étape 8 « arbitrée, en attente de Karim » jusqu'à sa remise, puis « relie les cerveaux » ; au maillon 0, le nom court se demande toujours quand un atelier existe |
| 10 | Une note du commun modifiée à la main passe le lint | Le lint signale un commun qui ne correspond plus à son empreinte |

## Décisions métier actées dans cette phase

- Le groupe se déclare dans `federation.yaml` dès le cadrage de chaque rédacteur (décision 2 du cadrage).
- La fédération se lance depuis l'atelier ; depuis un vault, elle rend la main avec la commande de mise à jour de la notice (décision 3).
- Retrait silencieux d'une note repassée en privé (décision 5).

## Hors scope produit

Voir `01-cadrage.md`, section « Exclus ».
