# Doctrine Cortex — pour qui exécute la chaîne

Ce fichier est destiné au **consultant**, pas au client. Il porte ce qui vaut dans les neuf maillons et qui n'a donc sa place dans aucun : le vocabulaire, les invariants, et la raison de chaque garde-fou.

Il ne redit pas la doctrine du vault livré. Celle-ci vit dans le gabarit — `cortex-4-installation/template/vault/90 - Meta/` : `Conventions.md` pour le contrat de données, `Architecture Mémoire.md` pour les quatre couches, `Architecture - Vue d'ensemble.md` pour l'entrée. La règle vaut pour ce fichier comme pour le reste : **pointeur jamais copie**.

## 1. Ce qu'on installe

Un **second cerveau** : la mémoire longue et le pilotage léger d'une organisation. Du markdown et du YAML dans un dossier, lisibles sans logiciel, versionnés par git, pilotés par une couche d'agents.

Il **pointe, il ne stocke pas**. C'est la phrase à dire au premier rendez-vous, pas au moment de la remise. Un client qui a compris ça au cadrage ne demandera pas au maillon 5 qu'on « mette tous les documents dedans » ; un client qui l'apprend à la remise a acheté autre chose que ce qu'il reçoit.

Ce n'est **pas** : un wiki d'équipe, une gestion documentaire, un gestionnaire de tâches, un CRM, ni un double du substrat métier. Chacune de ces quatre choses existe déjà chez le client et fait le travail mieux. Le vault est ce qui relie et ce qui se souvient — le reste reste où il est.

## 2. Le vocabulaire

Ces mots ont un sens précis dans la chaîne. Les employer autrement devant un client crée une attente qu'un maillon plus loin devra démentir.

| Terme | Sens |
|---|---|
| **substrat** | un outil du client qui porte du canon — l'espace de fichiers, la base de projets, le dépôt de code, l'agenda. Déclaré au maillon 1, parcouru au 2 |
| **canon** | la source de vérité d'un type de fait. Un fait, un propriétaire, jamais deux |
| **pointeur canonique** | l'adresse du canon dans une note : `url_canonique`, `repo`, ou `dossier_local` relatif. Une note sans pointeur est un doublon en devenir |
| **domaine** | un centre de gravité du travail réel. Entre 1 et 6, décidés au maillon 3 sur preuve chiffrée |
| **cycle** | le vocabulaire de phases d'un type de projet. Les mots du client, pas les tiens |
| **atelier** | `_cortex/`, le dossier de travail du consultant. Ne part jamais chez le client |
| **white-label** | l'absence, dans le livrable, de ta marque, de tes outils et **des clients que tu as déjà servis** |
| **kit générique** | les 6 skills et 2 sous-agents livrés par le maillon 4, identiques chez tous |
| **agent métier** | un sous-agent sur mesure, conçu au maillon 6 sur un vault déjà peuplé, avec une date de péremption |

## 3. La chaîne, et pourquoi elle est coupée là

| Maillon | Nature | Coût de rejeu |
|---|---|---|
| 0 poste | équipement | une réinstallation d'outil |
| 1 cadrage | collecte | le temps du client — le plus cher de la chaîne |
| 2 inventaire | mesure | un accès et de la patience |
| 3 ontologie | **jugement** | un arbitrage à re-litiger |
| 4 installation | matérialisation | une seconde |
| 5 ingest | application | des jetons, incrémental grâce au registre |
| 6 agents métier | conception | une spec à revalider |
| 7 passation | régénération | nul, à tout moment |
| 8 fédération | agrégation | nul, le commun se jette et se refait |

Trois coupures portent tout le reste.

**Collecter n'est pas juger** (2 ≠ 3). Le maillon 2 compte, localise, relève ; il ne qualifie rien d'important. C'est ce qui permet de rejouer une source qui a échoué — et elles échouent souvent — sans rejouer l'arbitrage des domaines.

**Juger n'est pas matérialiser** (3 ≠ 4). L'analyse est chère et subjective, la matérialisation est gratuite et mécanique. Les mélanger interdirait de relancer la seconde sans re-payer la première. C'est ce qui fait de `rm -rf` puis relance un geste normal au maillon 4, et non un incident.

**Peupler précède concevoir** (5 avant 6). Un agent métier conçu sur un vault vide encode ce que le consultant suppose du métier ; conçu sur un vault peuplé, il part des documents réels et des répétitions observées. L'écart entre les deux est l'écart entre un agent qu'on utilise et un agent de démonstration.

**Aucun maillon n'invoque le suivant.** Entre deux maillons, il se passe des choses dans le monde réel : obtenir un accès, faire signer, laisser le client essayer. Une chaîne qui s'enchaîne toute seule traverse ces attentes sans les voir.

*Amendement 2026-09-19, arbitrage final : il remplace celui du 2026-08-23.* La phrase s'applique telle quelle dans les deux modes de conduite. Aucun maillon n'enchaîne sur le suivant, ni en consultant, ni en solo, ni après un accord explicite. Il termine par la régénération de la notice, qui affiche l'étape suivante et la phrase à prononcer ; la personne la prononce quand elle veut. Ce que le mode solo raccourcit, c'est le délai entre deux maillons, pas la condition d'entrée du suivant ni la décision de continuer : un prérequis manquant se dit et arrête la chaîne, en solo comme en consultant. Les attentes du monde réel n'ont pas disparu en solo (retrouver un mot de passe, réactiver un compte, finir autre chose d'abord), et une chaîne qui les traverserait sans les voir produirait un inventaire partiel dont personne ne saurait ce qui a manqué.

## 4. La garde formelle

Chaque maillon écrit un fichier d'atelier dont le frontmatter porte `statut` et une liste de `controles`. Le maillon suivant le lit en étape 0 et **s'arrête sans repli** si un contrôle n'est ni `passe` ni explicitement `arbitre` avec motif.

| Fichier `_cortex/` | Produit par |
|---|---|
| `00-cadrage.md` (+ `config.yaml`, `README.md`) | 1 cadrage |
| `01-inventaire.json` + `01-inventaire.md` | 2 inventaire |
| `02-ontologie.md` | 3 ontologie |
| — | 4 installation |
| `04-ingest.md` | 5 ingest |
| `05-agents-metier.md` | 6 agents métier |
| `06-passation.md` | 7 passation |

**Le trou en `03` est voulu.** La sortie du maillon 4 est le vault lui-même, et sa preuve est le lint qui sort en 0 depuis ce vault. Lui fabriquer un fichier d'état n'ajouterait aucune information et donnerait à croire que l'installation est un jugement à valider.

C'est la seule garde formelle de la chaîne, et elle vaut mieux qu'une consigne : une consigne se contourne par bonne volonté un jour de retard, un contrôle d'étape 0 ne se contourne pas sans mentir par écrit.

## 5. Les cinq invariants

Ils valent dans les neuf maillons. Chacun a coûté quelque chose à quelqu'un.

**Pointeur jamais copie.** Une copie diverge de sa source, et le jour où elles se contredisent, personne ne sait laquelle croit. La parade n'est pas une règle en prose : le schéma d'inventaire n'a pas de champ `contenu`, et le plafond de résumé est un contrôle dur. S'il n'y a pas d'endroit où mettre la copie, la copie ne se fait pas.

**Un vault, un rédacteur nommé.** Pas une équipe, pas une fonction. Git sur du markdown à plusieurs produit des conflits sur `## Journal` à chaque clôture concurrente, à résoudre par des gens qui ne sont pas développeurs. Plusieurs personnes ⇒ plusieurs vaults, et l'agrégation plus tard.

**Ne jamais inventer une valeur manquante.** `_Non renseigné — à compléter_` et `Non observé dans l'inventaire` sont des réponses. Une supposition plausible, une fois écrite, devient indistinguable d'un constat — et elle sera crue, d'autant plus qu'elle est plausible.

**Ce qui est écarté se déclare.** Une troncature silencieuse se lit comme une couverture complète. Le maillon suivant conclura sur un corpus dont il ignore qu'il est amputé, et le trou deviendra un domaine oublié.

**L'atelier ne part pas chez le client.** Il contient l'inventaire brut, les hypothèses écartées et les constats sur son organisation — dont ceux qu'on ne lui a pas dits en ces termes.

*Amendement 2026-08-23 — en mode solo, cet invariant perd son objet sans perdre sa fonction.* Le client est l'installateur : l'atelier lui appartient déjà, et il n'y a rien à lui cacher de ses propres constats. `_cortex/` reste ce qu'il est — le dossier de travail de la chaîne, et l'endroit naturel où vit le tableau de bord — mais il n'en devient pas un dossier à publier ou à transmettre : ce qui vaut pour un vault vaut pour son atelier.

## 6. Ce qui ne se négocie pas avec le client

Quatre points. Ils se posent au cadrage, quand ils sont abstraits et coûtent une phrase ; les poser plus tard coûte un arbitrage contre une attente déjà formée.

**Les plafonds** — 6 domaines, 60 projets, 80 acteurs au jour 1. Ce ne sont pas des limites techniques. Au-delà de 6 domaines, chaque note hésite entre deux rattachements et le classement cesse de porter de l'information. Au-delà des volumes, on livre un annuaire, et personne n'ouvre un annuaire — c'est la seule façon dont l'outil peut échouer. Un client qui en demande quinze reçoit un **constat de sous-segmentation à discuter**, pas une case supplémentaire.

*Amendement 2026-08-23 — en mode solo, les plafonds n'ont plus d'avocat.* Personne ne défend les 6 domaines contre l'envie d'en avoir quinze. Ils ne bougent pas pour autant : ce sont eux qui empêchent l'outil d'échouer, et l'absence de contradicteur les rend plus nécessaires, pas moins. La défense change seulement de forme — au maillon 3, les trois seuils qui invalident deviennent explicatifs : quand un domaine proposé ne tient pas son seuil, le dire et expliquer pourquoi, au lieu de le retirer en silence.

**Zéro plugin requis.** Markdown, YAML, et les greffons du cœur. Un vault dont les vues n'existent qu'après installation d'un composant tiers non signé est un vault cassé à l'ouverture, et un obstacle d'achat en entreprise.

**La messagerie, agrégats seuls.** `domaine expéditeur → volume`, jamais un objet, jamais un corps, jamais une adresse individuelle, et jamais sans accord tracé. C'est le meilleur signal de la chaîne — l'organigramme déclare qui compte, la messagerie constate qui compte — et c'est le seul endroit où une erreur est irréversible : une donnée personnelle lue sans base légale ne se dé-lit pas.

**Aucune donnée sensible dans le vault.** Un vault est synchronisé, sauvegardé, indexé et parfois lu par un agent. Chacune de ces quatre propriétés est utile, et chacune est une voie de fuite. Il est conçu pour être facilement lisible ; c'est incompatible avec le stockage d'un secret.

## 7. Le geste qui décide de tout

À la remise, un seul geste compte : le client lance `cloture` à la fin de chaque bloc de travail. Trois à dix fois par jour, moins de trente secondes.

Un vault sans clôture se remplit une fois, à l'installation, puis meurt — personne ne retourne écrire ce qui s'est décidé, et six mois plus tard il ne reste qu'une photographie périmée du jour de la livraison.

D'où la forme de la remise : **montrer `cloture` sur une vraie session**, pas faire un tour du propriétaire. Ce qu'on veut, c'est qu'il le lance le lendemain, pas qu'il ait vu tous les dossiers.

## 8. Les mots qui ne se disent pas

Le vocabulaire du §2 et les clés de `config.yaml` décrivent la mécanique de la chaîne. Ils servent à qui la construit, pas à qui la traverse. Devant la personne, cliente ou consultant qui installe pour un client, ils se traduisent : une personne qui entend « mode consultant » ou « je dois trancher quatre écarts » apprend que l'outil parle de lui-même, et cesse d'écouter ce qu'il dit d'elle.

| Mot de la chaîne | Ce qu'on dit à la place |
|---|---|
| consultant, conduite, mode, solo, fédéré | « vous installez pour quelqu'un d'autre » ; « pour vous seul » ; « chacun le sien dans l'équipe » |
| profil, employé, dirigeant, société, parcours dirigeant ou employé | ce que la personne a répondu : « vous dirigez », « vous travaillez pour un responsable », « vous êtes plusieurs » |
| régime, pointeur, copie | « votre outil reste la référence, le second cerveau y renvoie » ; « les documents de fond sont recopiés ici » |
| substrat, rédacteur | « vos dossiers et vos outils » ; « la personne qui écrit dedans » |
| écart, écart candidat | « un point à éclaircir », « une question sur ce dossier » |
| maillon N, nom d'un skill ou d'un script | la phrase d'entrée de l'étape (« faisons le cadrage ») ou son nom ordinaire (« le cadrage ») |
| clé ou valeur de configuration (`mail_optin`, `visibilite_defaut`, `mentions_interdites`, `arbitre`) | sa traduction, en une phrase |

La règle couvre tout ce que la personne voit : le texte des messages, les questions, les options et leurs descriptions, les aperçus, les récapitulatifs, les messages de clôture. Elle ne couvre pas les fichiers de l'atelier, qui gardent les clés du contrat, ni les commandes affichées pour être copiées.

## 9. Ce que la chaîne lit

Cinq endroits, pas un de plus : l'atelier `_cortex/` du rédacteur en cours, son vault, les racines déclarées au cadrage, les fichiers du plugin sous `${CLAUDE_SKILL_DIR}`, et le dossier du commun au maillon 8. Le second rédacteur d'un groupe lit en plus `00-cadrage.md` et `config.yaml` dans l'atelier du premier, pour reprendre les décisions de groupe ; rien d'autre de ses notes ni de son vault. Pour savoir si un atelier existe déjà, le maillon 0 lit les noms des dossiers de `~/Cortex/`, leurs noms seuls.

Le reste du poste ne se lit jamais : `~/Documents`, `~/Desktop`, `~/OneDrive*`, `~/Library`, les dépôts de code, les dossiers de travail du consultant, la mémoire de Claude (`~/.claude/projects/*/memory`), l'historique des sessions, le dépôt source du plugin hors de `${CLAUDE_SKILL_DIR}`. On n'y cherche ni nom, ni marque, ni indice pour deviner une réponse. Ce que la personne n'a pas dit se demande.

La raison tient en deux phrases. Le poste du consultant porte ses autres clients : une session qui fouille pour deviner les ramène dans l'atelier d'un client. Le poste d'un client porte sa vie privée : une session qui fouille la lit.

D'où la règle des racines : une racine se demande, elle ne se propose pas depuis un parcours du disque. `~/Documents` et `~/Desktop` ne sont jamais des racines par défaut, ce sont les dossiers où le privé et le travail se mêlent le plus ; la personne qui les nomme elle-même les déclare comme n'importe quelle racine. Le fournisseur de messagerie oriente la question (« vos fichiers de travail sont-ils dans un OneDrive ? »), il ne fournit pas de chemin. Une racine nommée s'ouvre une fois, pour vérifier qu'elle répond, avant d'être écrite.

## 10. Ce qui se valide se voit

Une question qui demande de valider, signer ou confirmer un contenu (un récapitulatif, le bloc d'identité, le cahier des charges d'un agent, la carte des domaines, une liste de noms) porte ce contenu à l'écran : dans le texte du message qui la précède, ou dans l'aperçu de l'option qui le valide. « Ci-dessus » ne renvoie qu'à un texte écrit dans la conversation.

La personne ne voit que les messages. Un contenu préparé dans le raisonnement n'est pas affiché, et le faire valider produit une signature sans objet ; la trace qui s'en écrit ensuite dans l'atelier ment.

## 11. Accord, réponse acquise, marque, atelier existant

**Accord.** Rien ne s'installe ni ne se branche sur le poste sans une question qui dit ce que cela y pose. Le choix vaut accord, son absence vaut refus. La voie de messagerie softeria se propose ainsi : elle pose un petit serveur local et l'outil node, et donne accès à la boîte sans passer par l'administrateur du compte. Un refus s'écrit `--voie aucune` ; la messagerie reste alors hors de l'inventaire.

**Réponse acquise.** Une réponse donnée ne se repose pas, ni pour la faire confirmer, ni pour recommander l'inverse. Si elle a une conséquence que la personne doit connaître, la conséquence se dit une fois, dans le récapitulatif, sans question. Une réponse qui rend une question sans objet (« aucun », « rien ») la retire du lot.

**Marque.** La liste des noms à ne jamais faire apparaître dans un vault livré ne contient que les marques du consultant : son nom, sa société, ses outils internes. Il la saisit lui-même. Aucun nom d'un autre client ne s'y propose et aucun ne se cherche sur le poste : proposer ce nom dans l'atelier d'un client, c'est déjà l'y écrire. Le vault reste propre des autres clients par la lecture bornée du §9, pas par une liste qui les transporterait d'atelier en atelier. En groupe, la liste est une décision de groupe : fixée au cadrage du premier rédacteur, reprise telle quelle chez les suivants et annoncée dans leur récapitulatif, jamais redemandée.

**Atelier existant.** Au maillon 0, dès qu'un atelier existe sur le poste, la première question demande le nom court ; les ateliers existants y figurent comme options, à côté d'un nouveau nom. Un atelier trouvé n'est jamais présumé celui de la personne qui parle, et son contenu ne se lit pas pour le décrire.
