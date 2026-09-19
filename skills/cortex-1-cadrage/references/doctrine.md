# Doctrine Cortex — pour qui exécute la chaîne

Ce fichier est destiné au **consultant**, pas au client. Il porte ce qui vaut dans les sept maillons et qui n'a donc sa place dans aucun : le vocabulaire, les invariants, et la raison de chaque garde-fou.

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
| **kit générique** | les 4 skills et 2 sous-agents livrés par le maillon 4, identiques chez tous |
| **agent métier** | un sous-agent sur mesure, conçu au maillon 6 sur un vault déjà peuplé, avec une date de péremption |

## 3. La chaîne, et pourquoi elle est coupée là

| Maillon | Nature | Coût de rejeu |
|---|---|---|
| 1 cadrage | collecte | le temps du client — le plus cher de la chaîne |
| 2 inventaire | mesure | un accès et de la patience |
| 3 ontologie | **jugement** | un arbitrage à re-litiger |
| 4 installation | matérialisation | une seconde |
| 5 ingest | application | des jetons, incrémental grâce au registre |
| 6 agents métier | conception | une spec à revalider |
| 7 passation | régénération | nul, à tout moment |

Trois coupures portent tout le reste.

**Collecter n'est pas juger** (2 ≠ 3). Le maillon 2 compte, localise, relève ; il ne qualifie rien d'important. C'est ce qui permet de rejouer une source qui a échoué — et elles échouent souvent — sans rejouer l'arbitrage des domaines.

**Juger n'est pas matérialiser** (3 ≠ 4). L'analyse est chère et subjective, la matérialisation est gratuite et mécanique. Les mélanger interdirait de relancer la seconde sans re-payer la première. C'est ce qui fait de `rm -rf` puis relance un geste normal au maillon 4, et non un incident.

**Peupler précède concevoir** (5 avant 6). Un agent métier conçu sur un vault vide encode ce que le consultant suppose du métier ; conçu sur un vault peuplé, il part des documents réels et des répétitions observées. L'écart entre les deux est l'écart entre un agent qu'on utilise et un agent de démonstration.

**Aucun maillon n'invoque le suivant.** Entre deux maillons, il se passe des choses dans le monde réel : obtenir un accès, faire signer, laisser le client essayer. Une chaîne qui s'enchaîne toute seule traverse ces attentes sans les voir.

*Amendement 2026-08-23 — cette phrase se qualifie par mode de conduite.* En mode **consultant**, elle s'applique telle quelle : ce qui attend entre deux maillons appartient à des tiers — un DSI qui ouvre un accès, un dirigeant qui signe — et rendre la main est la seule façon de voir ces attentes. En mode **solo** — la même personne conduit la chaîne et en bénéficie, choix fait au maillon 1 et mémorisé dans la configuration — la personne qui répond et la personne qu'on attendrait sont la même. Chaque maillon peut donc proposer le suivant et l'enchaîner après un accord explicite, jamais sans. Ce que le mode solo supprime, c'est le **délai** entre les maillons, pas la **condition d'entrée** du suivant : un prérequis manquant arrête l'enchaînement et se dit, en solo comme en consultant. Les attentes du monde réel n'ont pas disparu en solo — retrouver un mot de passe, réactiver un compte, finir autre chose d'abord — et une chaîne qui les traverserait sans les voir produirait un inventaire partiel dont personne ne saurait ce qui a manqué.

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

Ils valent dans les sept maillons. Chacun a coûté quelque chose à quelqu'un.

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
