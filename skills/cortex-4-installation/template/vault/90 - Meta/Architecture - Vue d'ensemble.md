---
type: meta
tags:
  - doctrine
cree: {{DATE}}
maj: {{DATE}}
---
# Architecture - Vue d'ensemble

Remonte vers [[Centre]]. **C'est la note d'entrée** : si tu n'en lis qu'une, lis celle-ci. Carte pédagogique des 4 couches, de la topologie réelle des substrats, et de qui écrit quoi dans quel sens.

C'est un **index**. Les explications canoniques restent dans [[Architecture Mémoire]] et [[Conventions]]. Pointeur jamais copie — y compris pour cette note, qui ne doit jamais devenir un résumé qui les contredit.

## Lecture rapide en 30 secondes

- Ce vault = **mémoire et pilotage léger**. Les substrats métier = le canon. La vue = générée.
- 4 couches empilées sur le socle ÉTAT : **ÉTAT / JOURNAL / PLAYBOOK / VUE**.
- 4 opérations canoniques : **Ingest / Query / Lint / Cloture**.
- Sens unique sur tous les flux automatiques. Une seule source de vérité par type de fait.
- Aucun chemin absolu. Aucun plugin requis.

## (a) Les 4 couches

| Couche | Rôle | Dossiers représentatifs | Source canonique |
|---|---|---|---|
| ÉTAT | socle : où en sont les choses **maintenant** | `10 - Domaines/`, `20 - Projets/`, `40 - Acteurs/` | [[Architecture Mémoire]] §3.1 |
| JOURNAL | carnet du **pourquoi** | `60 - Journal/`, sections `## Décisions` et `## Journal` des fiches | [[Architecture Mémoire]] §3.2 |
| PLAYBOOK | process à plat + carte des outils | `90 - Meta/` | [[Architecture Mémoire]] §3.3 |
| VUE | tableau de bord qui **lit** les trois autres et ne stocke rien | hors vault | [[Architecture Mémoire]] §3.4 |

Une cinquième opération est **transversale** : la clôture. Ce n'est pas une couche — elle audite les quatre et complète les marqueurs manquants. Sans effet si tout est déjà là.

## (b) Topologie réelle — substrats et flux

À compléter à l'installation avec les substrats réels de l'organisation. Les cadres `_à renseigner_` sont des trous **volontairement visibles** : un substrat non déclaré est un substrat où la donnée partira en double.

```
┌─────────────────────────────────────────────────────────────────────┐
│  CANON MÉTIER (hors vault)                                          │
│                                                                     │
│  ┌──────────────────────────┐      ┌──────────────────────────┐     │
│  │ BASE DE PROJETS          │      │ ESPACE DOCUMENTAIRE      │     │
│  │ _à renseigner_           │      │ _à renseigner_           │     │
│  │ - état détaillé          │      │ - livrables              │     │
│  │ - travaux structurés     │      │ - fichiers bruts         │     │
│  └────────────┬─────────────┘      └────────────┬─────────────┘     │
│               │                                 │                   │
└───────────────┼─────────────────────────────────┼───────────────────┘
                │ pointeur                        │ pointeur
                │ url_canonique                   │ dossier_local
                │ (lecture seule)                 │ (chemin RELATIF)
                ▼                                 ▼
   ┌──────────────────────────────────────────────────────────┐
   │  LE VAULT — mémoire et pilotage léger                    │
   │                                                          │
   │  00 - Centre/     point d'entrée unique                  │
   │  10 - Domaines/   les centres de gravité                 │
   │  20 - Projets/    fiches de pilotage léger, 4 sections   │
   │                   canoniques : Actions / Décisions /      │
   │                   Journal / Pointeurs                    │
   │  40 - Acteurs/    entités, jamais de personnes physiques │
   │  50 - Ressources/ sources externes ingérées              │
   │  60 - Journal/    décisions structurantes                │
   │  80 - Identité/   immatriculations, sans donnée sensible │
   │  90 - Meta/       le PLAYBOOK (cette note, Conventions,  │
   │                   Architecture Mémoire, Runbooks)        │
   │  99 - Inbox/      captures à trier                       │
   │                                                          │
   │  config.yaml      LE seul fichier qui varie par client   │
   │  .claude/         6 skills + 2 sous-agents               │
   └──────────────────────────┬───────────────────────────────┘
                              │
                              │ skill `cloture`, 3 à 10 fois par jour
                              │ (manuelle : aucun automate n'écrit
                              │  dans le vault sans validation)
                              ▼
                     ┌────────────────────┐
                     │  VUE               │
                     │  à construire en   │
                     │  dernier, sur      │
                     │  données propres   │
                     └────────────────────┘
```

## (c) Matrice de liaisons — qui écrit quoi, dans quel sens

**La colonne « sens » est la plus importante de tout le vault.** Un sens non déclaré finit par être pris dans les deux directions.

| Lien | Sens | Mécanisme | Fréquence |
|---|---|---|---|
| Base de projets → vault (champs miroir) | unidirectionnel | _à renseigner_ | _à renseigner_ |
| Espace documentaire → vault | pointeur seul | frontmatter `dossier_local` | statique |
| Dépôts de code → vault | pointeur seul | frontmatter `repo`, `claude_md` | statique |
| Vault → vue | unidirectionnel | à construire en dernier | — |
| Vault → vault commun (mode fédéré) | unidirectionnel, **généré** | passe d'agrégation | sur demande |
| **Vault → tout substrat, sur un champ miroir** | **INTERDIT** | — | — |

La dernière ligne n'est pas une précaution rhétorique. Une écriture inverse sur un champ miroir crée un conflit qu'aucune règle automatique ne peut trancher : la valeur se met à alterner entre deux états selon qui a écrit en dernier, et personne ne s'en aperçoit avant d'avoir pris une décision sur la mauvaise.

## (d) Les 5 règles cardinales

1. **Une seule source de vérité par type de fait.** Tout doublon physique est une divergence différée, donc une source d'erreur pour quiconque — humain ou agent — lira le vault.
2. **Le vault n'est pas le canon métier.** Les substrats portent les travaux et les fichiers ; le vault porte les décisions, les pointeurs, les macro-actions et les trous qualifiés.
3. **Sens unique sur les flux automatiques.** Aucune écriture inverse.
4. **La clôture est idempotente.** Elle audite, rapporte les trous, marque seulement les manquants validés. Aucune écriture si tout est déjà là.
5. **Pointeur jamais copie.** Une note consigne le pourquoi et le lien, jamais plus de {{SEUIL_JOURNAL}} lignes reprises d'une source canonique.

## (e) Pour situer rapidement

| Question | Source canonique |
|---|---|
| Où vit cette information ? | [[Architecture Mémoire]] §2, matrice d'ownership |
| Quel vocabulaire pour `phase` ? | [[Configuration]], section Cycles |
| Quelle section de fiche projet utiliser ? | [[Conventions]] |
| Comment démarrer un projet ? | [[Runbook - Nouveau Projet]] |
| Comment finir une session ? | [[Runbook - Sessions de travail]] |
| Comment mener un chantier interne ? | [[Runbook - Chantiers (phase packs)]] |
| Comment intégrer une source externe ? | [[Ingest - Sources externes]] |
| Comment déléguer à un sous-agent ? | [[Méthode - Délégation et sous-agents]] |
| Les requêtes Dataview, si je l'installe | [[Vue Obsidian (Dataview, optionnel)]] |

## Ce que ce vault n'est pas

Utile à dire une fois, parce que la dérive va toujours dans ce sens :

- **Ce n'est pas un wiki d'équipe.** Un vault, un rédacteur. Plusieurs personnes se traitent par plusieurs vaults et un commun généré, jamais par plusieurs mains dans le même.
- **Ce n'est pas un gestionnaire de tâches.** Les actions ici sont des macro-actions de pilotage. Le backlog détaillé vit dans le substrat qui en est le canon.
- **Ce n'est pas un espace de stockage.** Aucun document n'y vit ; seulement des pointeurs vers là où ils vivent.
- **Ce n'est pas un double du substrat métier.** C'est l'erreur que tout le monde commet au deuxième mois, parce qu'elle est confortable : tout mettre au même endroit. Le plafond de {{SEUIL_JOURNAL}} lignes existe pour la rendre impossible.
