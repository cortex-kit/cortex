---
name: cortex-2-inventaire
description: Deuxième maillon de la chaîne Cortex. Mesure le disque par scan.py (dossiers, extensions, dates, dépôts git, signaux de base déportée, bornes en entiers), remplit le bloc mail par le connecteur retenu au maillon 0 (en-têtes seuls, agrégats), relève les bases déportées et dérive les écarts candidats pour l'entretien du maillon 3. Produit 01-inventaire.json et son rapport lisible, sans jamais copier de contenu. Déclencher quand la personne dit "maillon 2", "inventaire", "on scanne l'existant", "regarde ce que j'ai", ou dispose d'un cadrage validé. Ne PAS confondre avec cortex-5-ingest, qui transforme ce catalogue en notes dans le vault.
---

# cortex-2-inventaire : cataloguer sans copier

Deuxième des neuf maillons. Il regarde ce que la personne a déjà, sans rien en rapatrier.

## Positionnement

Ce maillon **ne juge pas**. Il ne propose aucun domaine, ne qualifie rien d'important. Il compte, il localise, il relève des schémas. L'interprétation est le maillon 3, et les séparer est ce qui permet de rejouer une source sans rejouer l'arbitrage.

Il **ne rapatrie rien**. Voir §Le piège.

Trois acteurs se partagent le travail :

| Qui | Remplit | Source |
|---|---|---|
| `scripts/scan.py` | `disque`, `depots`, `bornes`, `racines`, écarts observables sur disque | les dossiers de `collecte.racines` |
| l'agent | `mail` | le connecteur de `_cortex/poste.json` (`mail.voie`), §Le bloc mail |
| l'agent | `bases`, `agenda`, le reste de `ecarts_candidats`, `resume` et `preuve_de` de chaque entrée | les substrats déclarés au cadrage |

## Étape 0 : bloquante, sans repli

1. `_cortex/00-cadrage.md` en `statut: valide`, `config.yaml` avec `collecte.racines` en forme `~`.
2. `_cortex/poste.json` présent (maillon 0) : il donne la voie mail.
3. **Chaque substrat déclaré répond.** Tester l'accès avant de commencer : chaque racine existe, chaque connecteur répond à une requête vide.

Si un substrat ne répond pas : **s'arrêter et le dire.** Ne pas inventorier les autres « en attendant ». Un inventaire partiel est pire qu'absent : le maillon 3 déduirait une ontologie d'un corpus troué en le croyant complet, et le trou deviendrait un domaine oublié.

Lire la clé `conduite` du `config.yaml` : absente, elle vaut `consultant`. En `solo`, le fond ne change pas. Changent l'adresse (« vos dossiers », pas « les substrats du client ») et le message de clôture, qui propose la suite au lieu de rendre la main.

## Le piège, et sa parade structurelle

Le piège est unique et il est fatal : **recopier au lieu de pointer**. La parade n'est pas une règle en prose, c'est le schéma. **`01-inventaire.json` n'a pas de champ `contenu`**, et `scan.py` refuse d'écrire un fichier qui en porterait un. S'il n'y a pas d'endroit où mettre la copie, la copie ne se fait pas.

## Étape 1 : le disque par `scan.py`

```
python3 "${CLAUDE_SKILL_DIR}/scripts/scan.py" --config <vault>/config.yaml --out <vault>/_cortex/01-inventaire.json
```

`--racine <dossier>` (répétable) remplace `collecte.racines` pour un rejeu ciblé. Le script :

- parcourt chaque racine jusqu'à `collecte.profondeur_arbre`, au plus `collecte.max_dossiers` dossiers, en ignorant les dossiers cachés ;
- écrit une entrée `disque` par dossier : chemin en forme `~`, profondeur, fichiers directs et dans le sous-arbre, sous-dossiers, extensions comptées, première et dernière modification, `depot_git`, `signal_ontologique` (mots des noms de dossiers et de fichiers, candidats structurants), `signaux_base_deportee` ;
- écrit une entrée `depots` par dossier `.git` : langages par extensions, dernier commit, vingt premières lignes du README, `graphify_propose: true` ;
- extrait le texte des candidats structurants (nom qui porte organigramme, process, contrat, fiche de poste, cahier des charges, cadrage) par `uvx markitdown` s'il est présent, au plus 64 Kio par fichier et 2 Mio au total, jusqu'à `sante.max_structurants` fichiers. Seuls des mots comptés en sortent ; le texte n'est jamais écrit ;
- mesure `bornes` en entiers : `profondeur_max_vue`, `dossiers_vus`, `fichiers_vus`, `octets_extraits`, `dossiers_au_dela`, `extractions`, rappel de `profondeur_arbre` et `max_dossiers`, et `depassement` dès qu'un dossier n'a pas été parcouru ;
- pré-remplit `ecarts_candidats` avec `base_deportee_non_declaree` (si `substrats.base_projets` est vide) et `depot_non_declare` ;
- laisse `mail` en squelette (`voie: aucune`, compteurs à zéro), `bases` et `agenda` vides, `resume` vide.

Sans `uvx`, le scan tourne quand même : `extraction.outil` vaut `""`, les mots viennent des seuls noms. Le dire dans le rapport, ne pas installer.

Lire ensuite la ligne imprimée : dossiers, fichiers, dépôts, extractions, écarts, dépassement. Un `depassement=true` se traite au §Les bornes avant d'aller plus loin.

## Étape 2 : le bloc `mail`

**Condition dure : `collecte.mail_optin: true` tracé au cadrage.** Sinon, `mail.voie` reste `aucune` et aucune requête ne part. Une donnée personnelle lue sans base légale ne se dé-lit pas.

Lire `mail.voie` dans `_cortex/poste.json`, puis suivre la ligne correspondante. Toujours : en-têtes seuls, sur `collecte.mail_mois` mois, plafond 2 000 en-têtes (par boîte pour `mcp-email`). Jamais un corps, jamais une pièce jointe, jamais un outil qui ouvre un message.

| Voie | Outil | Requête exacte | Champs lus | On ne touche jamais |
|---|---|---|---|---|
| `connecteur`, fournisseur `gmail` | `search_threads` du connecteur Gmail | `newer_than:<mail_mois>m`, page après page jusqu'à la fin ou 2 000 en-têtes | expéditeur, destinataires, objet, date de chaque message du fil ; un fil de n messages compte n en-têtes | `get_message`, `get_thread`, les extraits de corps renvoyés avec le fil |
| `connecteur`, fournisseur `m365` | `outlook_email_search` du connecteur Microsoft 365 | période des `mail_mois` derniers mois, paginée | `from`, `subject`, `receivedDateTime` | `read_resource` sur un message, les aperçus |
| `softeria` | serveur `ms-365-mcp-server`, preset `outlook` | `messages?$select=from,subject,receivedDateTime&$top=100`, filtrée sur `receivedDateTime` depuis `mail_mois` mois, suivie par `@odata.nextLink` | `from`, `subject`, `receivedDateTime` | `body`, `bodyPreview`, attachments |
| `mcp-email` | `list_accounts`, puis `list_emails` par compte et par dossier (`INBOX`, puis `Sent`) | période des `mail_mois` derniers mois, en-têtes seuls | expéditeur, destinataires, objet, date | `read_email`, `download_attachment` |

Compter au fil des pages, sans rien noter ailleurs que dans les agrégats. Quand le compteur atteint 2 000 :

1. arrêter la pagination ;
2. écrire `mail.en_tetes_lus: 2000`, `mail.plafond: 2000`, et passer `bornes.depassement` à `true` ;
3. noter dans `01-inventaire.md`, section « Au-delà des bornes », la date du plus ancien en-tête lu : c'est la période réellement couverte, pas `mail_mois` ;
4. porter `controles.volumes_sous_plafond: arbitre` avec ce motif.

Ce que l'agent dérive, et rien d'autre :

- `agregats` : domaine de l'expéditeur → volume, trié décroissant. Le domaine de la personne compte aussi : il mesure le volume interne.
- `acteurs` : chaque domaine, ou chaque expéditeur d'un même domaine, à 10 messages ou plus : `adresse_domaine`, `nom_affiche` (le nom, jamais l'adresse), `volume`, `declare` confronté aux parties prenantes de `00-cadrage.md`.
- `sujets_recurrents` : objet normalisé (minuscules, sans `re:`, `tr:`, `fwd:`, sans numéro), 5 occurrences ou plus, avec `premier` et `dernier`.
- `fils_structurants` : `[]` ici, toujours. Le maillon 5 le remplit en régime `copie`, fil par fil, validé un par un.

Écrire `mail.voie`, `mail.periode_mois`, `mail.en_tetes_lus` réels. Une adresse individuelle n'apparaît nulle part hors `acteurs`, et seulement sous forme de domaine et de nom affiché.

## Étape 3 : `bases`, `agenda`, `resume`

**Bases.** Deux sources : `substrats.base_projets` du `config.yaml` (déclarée), et les `signaux_base_deportee` du scan (exports csv d'outils, fichiers `.base`, liens vers un outil). Pour chaque base qui répond, relever le **schéma seul** : titre, noms de propriétés, options des listes déroulantes, volume, dernière mise à jour. Jamais le corps des pages. Les schémas sont le meilleur signal de toute la chaîne : un vocabulaire déjà curé par la personne.

**Agenda.** Titres des réunions **récurrentes** seulement, avec récurrence et nombre d'occurrences. Ce qui se pilote toutes les semaines est un domaine, quoi qu'en dise l'organigramme.

**Résumé.** Pour chaque entrée `disque`, `bases`, `depots` qui compte (plus de 5 fichiers, ou un candidat structurant, ou un signal), écrire `resume` en 10 lignes au plus à partir des seuls champs mesurés : ce qu'il y a, depuis quand, à quel rythme. Pas de jugement.

| Source | On extrait | On ne lit **jamais** |
|---|---|---|
| dossiers | noms, profondeur, nombre de fichiers, dates, extensions, mots des noms | le contenu des fichiers, hors mots-signaux des structurants |
| bases | schémas : propriétés et options de listes, titres, adresses | le corps des pages |
| dépôts de code | liste, langages, dernier commit, 20 premières lignes du README | le code |
| messagerie | agrégats, acteurs à 10 messages ou plus, objets récurrents | les corps, les pièces jointes, les adresses hors `acteurs` |
| agenda | titres des réunions récurrentes | le contenu des événements |

## Étape 4 : `ecarts_candidats`

Le maillon 3 transforme chaque écart en question. Six types, tous confrontés à `00-cadrage.md` :

| Type | Indice observé | Confronté à |
|---|---|---|
| `base_deportee_non_declaree` | `signaux_base_deportee` (pré-rempli par le scan) | `substrats.base_projets` vide |
| `depot_non_declare` | entrée `depots` (pré-rempli par le scan) | dépôts cités au cadrage |
| `correspondant_non_declare` | acteur mail à `declare: false` | parties prenantes déclarées |
| `dossier_sans_domaine` | dossier de plus de 5 fichiers dont aucun mot ne rejoint un projet, une fonction ou un domaine de départ | cadrage et `references/profils/<profil>.md` |
| `reunion_recurrente_sans_projet` | dossier de comptes rendus datés, ou réunion récurrente d'agenda, sans projet déclaré du même nom | projets déclarés |
| `projet_non_declare` | dossier de projet (candidat structurant de type `projet`, ou plus de 8 fichiers sous un dossier « Projets ») absent des projets déclarés | projets déclarés |

Chaque écart : `{type, indice, source_id}`, l'indice chiffré (« 9 fichiers », « 12 messages »), jamais une conclusion. Relire les deux écarts du scan avant d'en ajouter : un dépôt cité au cadrage se retire de la liste.

## Graphify : proposé, jamais installé d'office

Quand `depots` n'est pas vide, ou qu'une entrée `disque` porte `graphify_propose: true` (plus de 500 documents dans son sous-arbre), le dire une fois, en une phrase, dans le message de clôture : un graphe de dépendances aiderait le maillon 5 sur ce dépôt ou ce dossier, et son installation est une option du maillon 0. Ne rien installer, ne rien lancer, ne jamais le proposer sur le vault lui-même.

## Les bornes

Depuis `config.collecte`, jamais dépassées sans arbitrage écrit : `profondeur_arbre`, `max_dossiers`, `mail_mois`, 2 000 en-têtes, README seul pour les dépôts, 64 Kio par structurant extrait. Au-delà, on produit un catalogue que le maillon 3 ne peut plus lire, donc qu'il survolera.

Si `bornes.depassement` vaut `true`, le dire au lieu de tronquer en silence : `bornes.dossiers_au_dela` compte ce qui n'a pas été parcouru. Deux issues, à faire trancher : relever une borne dans `config.yaml` et relancer le scan, ou accepter la coupe et l'écrire dans « Au-delà des bornes ». Une troncature tacite se lit comme une couverture complète.

## Validation : par substrat

Un substrat, une validation. Pas par entrée. Les échecs sont partiels et fréquents (limites de débit, permissions, expirations) ; on veut pouvoir rejouer **une** source sans rejouer les autres, et sans jamais rejouer le cadrage. Rejouer le disque seul : `scan.py` avec le même `--out`, puis reporter le bloc `mail` et les blocs de l'agent. Rejouer la messagerie seule : refaire l'étape 2 sur le fichier existant.

## Écrire

`_cortex/01-inventaire.json` (machine, consommé par les maillons 3 et 5) et `01-inventaire.md` (lisible), avec ce frontmatter :

```yaml
maillon: 2
produit_par: cortex-2-inventaire
statut: valide
controles:
  tous_substrats_repondent: passe
  aucun_contenu_rapatrie: passe
  bornes_respectees: passe
  mail_conforme_optin: passe
  volumes_sous_plafond: passe    # ou `arbitre` avec motif
```

Le rapport lisible reprend, par substrat : ce qui a été parcouru, les chiffres de `bornes`, les agrégats mail, les schémas de bases, les écarts candidats, et la section « Au-delà des bornes », même vide.

## Message de clôture

```
Inventaire terminé pour <organisation>.

- <N> substrats parcourus, <M> entrées cataloguées
- disque : <dossiers_vus> dossiers, <fichiers_vus> fichiers, <extractions> structurants lus en mots
- schémas relevés : <K> bases, <P> propriétés distinctes
- messagerie : <en_tetes_lus> en-têtes sur <periode_mois> mois, <N domaines agrégés | hors périmètre>
- <E> écarts candidats pour l'entretien
- au-delà des bornes : <ce qui a été laissé de côté, ou rien>
- <graphe de dépendances proposé sur <dépôt ou dossier>, option du maillon 0 | rien>

Pour toi :
1. Relis 01-inventaire.md, surtout la section « Au-delà des bornes ».
2. Lance `cortex-3-ontologie`.
```

**En mode solo :**

```
Inventaire terminé.

- <N> endroits parcourus, <M> éléments repérés
- rien n'a été copié : tout est resté à sa place, l'outil a seulement
  noté où chaque chose vit
- <E> points à éclaircir ensemble à l'étape suivante
- laissé de côté : <ce qui dépasse les bornes, ou rien>

La suite décide les grandes familles de votre outil, sur ce que
l'inventaire vient de constater, pas sur des impressions.
```

Puis la section Notice ci-dessous. Si un endroit déclaré n'a pas pu être parcouru, ou si une borne a été dépassée sans arbitrage : s'arrêter et dire ce qui manque.

## Interdits

- **Jamais de contenu rapatrié.** Le schéma l'interdit ; ne pas le contourner par un champ ajouté.
- **Jamais la messagerie sans opt-in tracé.** Jamais un corps, jamais une adresse en clair hors `acteurs`.
- **Jamais d'inventaire partiel présenté comme complet.**
- **Jamais de troncature silencieuse.** Ce qui est laissé de côté se déclare.
- **Jamais de jugement ici.** « Ce dossier a l'air important » n'est pas un relevé.
- **Jamais d'installation** depuis ce maillon : Graphify se propose, le maillon 0 installe.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
