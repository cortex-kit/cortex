---
name: cortex-1-cadrage
description: Maillon 1 de la chaîne Cortex, le cadrage. Pose le profil (employé, dirigeant, société) en langage ordinaire, fixe le régime de donnée (pointeur ou copie), propose les dossiers à parcourir et les plafonds depuis references/profils/<profil>.md, lit _cortex/poste.json pour pré-remplir le poste et la voie mail. Produit config.yaml et 00-cadrage.md dans _cortex/. Déclencher quand la personne dit "faisons le cadrage" (phrase de la notice), "cadre mon second cerveau", "on commence le cadrage", "maillon 1", "nouveau client Cortex", ou dispose d'un compte rendu de rendez-vous à exploiter. Ne PAS confondre avec cortex-3-ontologie, qui décide des domaines à partir de l'inventaire réel.
---

# cortex-1-cadrage — le maillon le plus cher

Maillon 1, après l'équipement du poste. Il consomme le temps du client, qui est la ressource la plus rare de toute la chaîne. Tout ce qui est mal cadré ici se paie six fois plus loin, quand le vault est déjà installé et peuplé.

Doctrine et vocabulaire : `references/doctrine.md`. Familles sectorielles : `references/secteurs.md`. Profils : `references/profils/{employe,dirigeant,societe}.md`. Rejeu sans personne : `cortex-4-installation/recette/rejeu_profil.py --profil <profil> --racine <dossier> --atelier <_cortex/>`, outil de recette, hors des maillons livrés (écrit config.yaml, 00-cadrage.md et la section « Ce que l'inventaire a révélé » de 02-ontologie.md depuis un ECARTS.json ; le cadrage rejoué sort en `statut: brouillon`, les contrôles qui demandent une personne restent à `arbitre`).

## La chaîne complète

| Maillon | Rôle |
|---|---|
| `cortex-0-poste` | le poste équipé, `_cortex/poste.json`, la notice ouverte |
| **`cortex-1-cadrage`** | **ce maillon — qui, quels substrats, quelles bornes** |
| `cortex-2-inventaire` | catalogue de pointeurs vers l'existant |
| `cortex-3-ontologie` | les domaines, avec preuve chiffrée. Le seul maillon de jugement |
| `cortex-4-installation` | le vault et sa couche d'agents |
| `cortex-5-ingest` | l'inventaire devient des notes-pointeurs |
| `cortex-6-agents-metier` | les agents sur mesure, une fois le vault peuplé |
| `cortex-7-passation` | guide de remise et recette d'acceptation |
| `cortex-8-federation` | le commun généré, quand plusieurs vaults se relient |

**Aucun maillon n'invoque le suivant.** Le consultant lance, parce qu'entre deux maillons il se passe des choses dans le monde réel : obtenir un accès, faire signer, laisser le client essayer.

En mode **solo** — choisi ici même, mémorisé dans la configuration — chaque maillon **propose** le suivant et l'enchaîne après un accord explicite, jamais sans, et jamais si sa condition d'entrée manque. Ce que le solo supprime, c'est le délai entre les maillons, pas la condition d'entrée du suivant. Qualification complète : `references/doctrine.md` §3, amendement 2026-08-23.

## Positionnement

Ce maillon **ne décide pas des domaines**. C'est le travail du maillon 3, et il a besoin de l'inventaire pour le faire honnêtement. Ici on collecte ce qu'on ne peut pas déduire : l'identité, les substrats, les autorisations, les bornes.

Il **ne promet rien sur le contenu**. Un client qui demande « et vous mettrez tous nos documents dedans » reçoit la réponse maintenant, pas au maillon 5 : non, le vault pointe, il ne stocke pas.

## Étape 0

Rien n'est requis. C'est le point d'entrée. Si un compte rendu de rendez-vous ou une transcription est fourni, **le lire avant de poser la moindre question** et pré-remplir tout ce qui s'y trouve. Faire ressaisir ce qui est déjà écrit est la meilleure façon de perdre l'attention d'un dirigeant.

**Le mode de conduite se fixe ici, une fois pour toutes.** Si `_cortex/config.yaml` existe déjà et porte la clé `conduite`, la lire et ne pas reposer la question — une session qui reprend au milieu du cadrage sait où elle est. Sinon, la toute première question du maillon est, telle quelle :

> « Installez-vous cet outil pour vous-même, ou pour quelqu'un d'autre ? »

En langage ordinaire, jamais « quel mode ». « Pour quelqu'un d'autre » ⇒ `conduite: consultant`, tout le comportement historique de ce maillon, à l'identique. « Pour moi-même » ⇒ `conduite: solo`. La personne qui répond est celle qui vivra avec l'outil : la collecte se reformule (§1), le white-label sort de la conversation (§2), et chaque message de clôture de la chaîne proposera la suite au lieu de rendre la main. La réponse s'écrit dans `config.yaml` à la création de l'atelier et n'est plus jamais reposée, ni ici ni dans les maillons suivants.

**Le profil se pose juste après, une seule fois.** Si `config.yaml` porte déjà `profil`, ne pas la reposer. Sinon, par AskUserQuestion, options fermées plus « autre », sans jamais prononcer « profil » ni les trois noms de l'enum :

> « Dans quelle situation êtes-vous ? »
> 1. Je travaille dans une organisation que je ne dirige pas, pour un responsable.
> 2. Je dirige une organisation, seul ou avec des associés.
> 3. Nous sommes plusieurs dans la même organisation à vouloir cet outil, chacun le sien.

1 ⇒ `profil: employe`, 2 ⇒ `profil: dirigeant`, 3 ⇒ `profil: societe`. Le profil choisit `references/profils/<profil>.md`, qui donne les questions, les substrats attendus, les racines, les plafonds, les domaines de départ et les pièges : le lire en entier avant la première question du §1. `societe` impose `mode: federe` et trois décisions de groupe avant les questions individuelles ; le fichier de profil les détaille. « Autre » ne crée pas de quatrième profil : demander ce qui ne rentre pas, puis rattacher à l'un des trois.

**Lire `_cortex/poste.json` s'il existe**, écrit par le maillon 0. Il pré-remplit sans question : le bloc `poste` de `config.yaml` (`os`, `outils` présents, `mail_fournisseur`, `mail_boites`, `mail_voie`), la voie mail que le maillon 2 prendra (`04-contrat.md` §7), et un candidat d'espace documentaire à proposer au §1 (`gmail` suggère un dossier de type Drive, `m365` un dossier de type OneDrive ou SharePoint). Proposer, jamais supposer : le candidat se confirme comme n'importe quelle racine. Sans `poste.json`, le bloc `poste` reste vide et la question mail du §3 se pose telle quelle.

## 1. Collecte, à trois niveaux, en une seule passe

Poser sous forme de liste compacte. Question par question, un cadrage prend une heure et le client décroche.

### Niveau 1 — bloquant

- Le nom de l'organisation, son orthographe exacte, et un slug court.
- **Qui porte ce vault.** Une personne, nommée. Pas une équipe, pas une fonction.
- Sa langue de travail.
- Où vivent les dossiers de projet sur sa machine.

### Niveau 2 — fortement recommandé, confirmation active

L'absence se signale et demande un « oui, je confirme, on avance sans ». Un silence relance la question.

- Les **substrats existants** : où vit l'état des dossiers, où vivent les fichiers, où vit le code. Nom de l'outil et adresse de la racine.
- Le secteur, pour orienter le vocabulaire — voir `references/secteurs.md`.
- L'effectif, qui donne l'ordre de grandeur des plafonds.
- **L'autorisation d'inventorier la messagerie**, si elle est envisagée. Voir §3.

### Niveau 3 — optionnel

Axes commerciaux (`vehicules`, `payeurs`), identité légale, échéance souhaitée.

### Les questions du profil, par lots de quatre

`references/profils/<profil>.md` porte huit sujets : métier, N+1, collègues, parties prenantes, projets portés, projets subis, outils, rituels. Chacun s'y trouve déjà formulé en langage ordinaire, avec ce que la réponse alimente. Les poser par AskUserQuestion, quatre par appel, options fermées plus « autre », dans l'ordre du fichier. Une réponse qui ouvre un point nouveau relance un lot ; un silence ne se comble pas.

**Les racines se proposent, elles ne se demandent pas.** Le fichier de profil liste `collecte.racines` en forme `~` ; y ajouter le candidat tiré de `poste.json`. Montrer la liste, faire confirmer, retirer ou ajouter chaque entrée. Chaque racine confirmée doit répondre (le dossier s'ouvre) avant d'être écrite. Une racine absente du disque ne s'écrit pas, elle se note dans `00-cadrage.md` comme à retrouver.

**Le régime de donnée se fixe ici, sans le nommer** (`04-contrat.md` §2). Dès que la réponse à « où suivez-vous l'état de vos dossiers ? » désigne un outil en ligne ou un logiciel, `substrats.base_projets` reçoit son adresse et `donnees.regime` vaut `pointeur`. Sinon, `copie` : le maillon 5 copiera, un par un et sur accord, les documents structurants listés dans `donnees.structurants`. Dire la conséquence dans les mots de la personne : « votre outil restera la référence, celui-ci y renverra » ou « vos documents de fond seront recopiés ici, un par un, avec votre accord ». Le régime peut encore basculer au maillon 3 si l'inventaire révèle une base non déclarée.

**Les domaines de départ du profil ne s'écrivent pas dans `config.yaml`.** Ils vont dans `00-cadrage.md`, section « Domaines de départ (hypothèses du profil) », pour que le maillon 3 les teste en premier contre l'inventaire. Un domaine écrit dans la config avant l'inventaire serait adopté par politesse (§Interdits).

### En mode solo — les mêmes questions, dans les mots du quotidien

Le fond ne change pas : mêmes trois niveaux, mêmes informations, même passe unique, mêmes confirmations actives au niveau 2. Seul le vocabulaire change — la personne n'a pas à apprendre le jargon de la chaîne pour répondre.

- « Déclarez vos substrats » devient **« où sont vos dossiers de travail ? »**, puis, si elle en a : où suit-elle l'état de ses projets, où vit son code.
- « Qui porte ce vault » devient **« c'est bien vous, et personne d'autre, qui écrirez dedans ? »** — la règle du rédacteur unique ne se relâche pas, elle se dit autrement.
- Le secteur et l'effectif se demandent comme on demande « que faites-vous, et à combien ? » — ils orientent le vocabulaire et les plafonds sans qu'il soit besoin de le dire.
- La messagerie ne se mentionne que si la personne souhaite l'inventorier. La question d'autorisation du §3 se pose alors dans les mêmes termes qu'en consultant : c'est la seule question réglementaire de la chaîne, elle ne se simplifie pas.

## 2. Le white-label

`marque.mentions_interdites` reçoit : ta marque, tes outils internes, tes noms propres, et **les clients que tu as déjà servis**.

Cette dernière catégorie est celle qu'on oublie, et c'est la plus dangereuse. Un vault livré chez un client qui contient le nom d'un autre client n'est pas un défaut de propreté, c'est une fuite — et elle se produit par des chemins qu'on n'imagine pas : un exemple laissé dans un template, un identifiant de page dans une note de méthode, un registre oublié dans un fichier d'agent.

Le contrôle est bloquant au maillon 7.

**En mode solo, ce bloc sort de la conversation.** Il n'y a aucune marque à effacer : la personne installe pour elle-même. `mentions_interdites` ne se demande pas — et ne reste pas vide pour autant : elle se pré-remplit avec les traces d'origine du gabarit (noms propres, exemples et identifiants laissés par son fabricant, à relever dans le gabarit lui-même), que le contrôle bloquant du maillon 7 attrapera si elles fuient dans l'outil. Le pré-remplissage est un geste du maillon ; la personne n'a rien à fournir ni à comprendre ici.

## 3. La messagerie — la seule question réglementaire

Si l'inventaire de la messagerie est envisagé, **poser la question explicitement et tracer la réponse**.

Ce qui est extrait : `domaine expéditeur → volume sur 12 mois`. **Rien d'autre.** Jamais un objet, jamais un corps, jamais une adresse individuelle.

Ce que ça apporte : la liste des organisations avec lesquelles le client travaille réellement, par ordre d'intensité. L'organigramme déclare qui compte ; la messagerie constate qui compte.

**Sans accord écrit, `collecte.mail_optin` reste à `false` et le maillon 2 n'ouvre pas la messagerie.** Ce n'est pas une formalité qu'on rattrape après : une donnée personnelle lue sans base légale ne se dé-lit pas.

## 4. Les plafonds — les poser maintenant

- **6 domaines au maximum.** Au-delà, plus rien n'est central : chaque note hésite entre deux rattachements et le classement cesse de porter de l'information.
- **60 projets, 80 acteurs au jour 1.** Au-delà, on livre un annuaire que personne n'ouvre.
- Profondeur d'arbre 3, 200 dossiers, 12 mois de messagerie.
- **Le profil abaisse ces valeurs, jamais ne les relève.** Le bloc config de `references/profils/<profil>.md` porte les siennes (un employé tient en 5 domaines, 30 projets, 40 acteurs). Les écrire telles quelles dans `collecte`.

Un client qui en demande quinze reçoit un **constat de sous-segmentation à discuter**, pas une case supplémentaire. C'est presque toujours un besoin de six domaines et de tags transverses.

Les poser au cadrage, quand ils sont abstraits, coûte une phrase. Les poser au maillon 3, quand le client a déjà sa liste en tête, coûte un arbitrage.

## 5. Écrire l'atelier

`<ton espace>/Cortex/<slug>/_cortex/` — **chez toi, jamais dans la livraison**. Le client reçoit son vault, pas tes notes de travail, tes hypothèses écartées ni les constats te concernant sa propre organisation.

Créer : `README.md` (index de chaîne, sections futures marquées `_À compléter dans le maillon N._`), `00-cadrage.md`. Initialiser git s'il ne l'est pas.

**`config.yaml` existe déjà** : le maillon 0 l'a créé dans `~/Cortex/<slug>/_cortex/` avec `version: 1` et le bloc `poste`. Ne jamais le recréer ni l'écraser : le relire avec `cortex_config.charger`, y fusionner les clés du cadrage, réécrire le fichier complet. Sans maillon 0 (parcours consultant hérité), partir de `${CLAUDE_SKILL_DIR}/../cortex-4-installation/template/config.example.yaml`. Dans les deux cas, le fichier reçoit, dans l'ordre : `conduite`, `profil`, le bloc config du profil (`mode`, `commun`, `donnees.regime`, `collecte` avec les racines confirmées), `organisation`, `substrats`, `poste` depuis `poste.json`, `marque` (§2). `domaines: []` et `cycles: []` restent vides : ils sont au maillon 3. `python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/cortex_config.py" _cortex/config.yaml` doit le relire sans erreur ; `valider_installable` le refusera encore, c'est attendu tant que les domaines manquent.

Le frontmatter de `00-cadrage.md` porte les contrôles :

```yaml
maillon: 1
produit_par: cortex-1-cadrage
statut: valide            # brouillon | valide | arbitre
controles:
  redacteur_unique_nomme: passe
  profil_pose: passe
  regime_fixe: passe
  racines_confirmees: passe
  substrats_declares: passe
  plafonds_acceptes: passe
  mail_optin_trace: passe   # ou `arbitre` avec motif si non traité
```

Le corps porte, en plus des réponses : « Domaines de départ (hypothèses du profil) », « Projets portés » et « Projets subis » séparés, « Parties prenantes déclarées » (N+1, collègues, externes), « Rituels déclarés ». Le maillon 3 confronte ces quatre listes à l'inventaire : c'est la matière de l'entretien de compréhension.

**Un fichier dont un contrôle n'est ni `passé` ni explicitement `arbitré` ne peut pas être consommé** par le maillon suivant. C'est la seule garde formelle de la chaîne, et elle vaut mieux qu'une consigne : le maillon 2 s'arrête en étape 0, sans repli.

## 6. Validation — par bloc

Identité, puis white-label, puis substrats, puis bornes. Attendre à chaque bloc.

C'est la granularité la plus fine de toute la chaîne, et elle se justifie par le coût de régénération : refaire ce maillon veut dire reprendre du temps au client. Tous les autres se rejouent seuls.

**En mode solo, la validation par bloc demeure, et la porte des bornes devient une récapitulation à confirmer.** Avant d'écrire l'atelier, relire d'une traite : voilà ce que l'outil regardera — les dossiers et outils déclarés —, voilà ce qu'il n'ouvrira pas — tout le reste, et la messagerie sans accord —, voilà les plafonds — 6 domaines, 60 projets, 80 acteurs. Une confirmation explicite, et on avance ; un refus rouvre le bloc concerné. La confirmation se trace dans `00-cadrage.md` : une ligne datée « Bornes récapitulées et confirmées le <date> » dans le corps du fichier, et le contrôle `plafonds_acceptes` ne passe à `passe` que par elle. Une porte supprimée serait un défaut, pas une simplification.

## Message de clôture

```
Cadrage terminé pour <organisation>.

- config.yaml initialisé : <N> substrats déclarés, plafonds acceptés
- white-label : <N> mentions interdites
- messagerie : <opt-in tracé | hors périmètre>

Pour toi :
1. Obtiens les accès aux substrats listés en §Substrats.
2. Quand ils répondent, lance `cortex-2-inventaire`.

Le maillon 2 vérifie que chaque substrat déclaré répond avant de commencer.
S'il en manque un, il s'arrête : mieux vaut attendre un accès que produire
un inventaire partiel dont personne ne saura ce qu'il a manqué.
```

**En mode solo**, la clôture récapitule, énonce la condition d'entrée du maillon suivant, et **propose** — jamais n'impose :

```
Cadrage terminé.

- vos endroits de travail : <N> déclarés
- bornes confirmées : ce qu'on regarde, ce qu'on n'ouvre pas, les plafonds
- messagerie : <autorisée et tracée | laissée de côté>

La suite est l'inventaire : parcourir ce que vous avez déclaré sans rien
en copier — noter où les choses sont, pas ce qu'elles contiennent.
Sa condition d'entrée : chaque endroit déclaré doit répondre — dossier
accessible, outil qui s'ouvre, compte actif.

On enchaîne ?
```

Si un accès manque (un mot de passe à retrouver, un compte à réactiver), s'arrêter et dire ce qui manque, et que l'inventaire démarrera quand ce sera réglé. Ne jamais enchaîner par-dessus une condition d'entrée non remplie.

## Interdits

- **Ne jamais décider des domaines ici.** Ils se déduisent de l'inventaire, avec preuve. Un domaine proposé au cadrage sera adopté par politesse et jamais réexaminé.
- **Ne jamais promettre la reprise du contenu.** Le vault pointe.
- **Ne jamais inventer** une valeur manquante : `_Non renseigné — à compléter_` est toujours préférable. Halluciner une décision de cadrage est pire que laisser un trou visible.
- **Ne jamais ouvrir la messagerie sans accord tracé.**
- **Ne jamais accepter un rédacteur collectif.** Un vault, une personne. « L'équipe » comme réponse est le début d'un produit différent.
- **En solo, ne jamais demander « quel mode »** ni prononcer « solo » ou « consultant » devant la personne. La question d'ouverture en langage ordinaire suffit, la réponse s'écrit, et elle ne se repose jamais.
- **Ne jamais prononcer « profil », « employé », « dirigeant », « société », « régime », « pointeur », « copie »** devant la personne. Ce sont des clés de `config.yaml`, pas des mots de conversation.
- **Ne jamais écrire une racine qui ne répond pas**, ni une racine en chemin absolu. Forme `~` seule.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
