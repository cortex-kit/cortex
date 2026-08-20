---
name: nouveau-projet
description: Instancie un nouveau projet — la fiche dans le vault, le dossier de travail, et le CLAUDE.md du projet avec son back-pointer. À utiliser dès qu'un projet, un dossier client, une mission ou un chantier démarre. Déclencher quand l'utilisateur dit "nouveau projet", "nouveau client", "je démarre X", "setup projet X", "on lance X", ou décrit un travail qui va durer et produire des livrables. Ne PAS utiliser pour une tâche ponctuelle (une case dans une fiche existante suffit) ni pour créer un domaine.
---

# nouveau-projet

Trois objets, dans cet ordre, et rien de plus.

## Étape 0 — Prérequis

`config.yaml` à la racine du vault. Sans lui, ni les domaines, ni les cycles, ni la racine des dossiers de travail ne sont connus.

## 1. Collecte — à trois niveaux

Poser les questions **en une seule passe**, sous forme de liste compacte. Question par question, la création d'un projet prend dix minutes et devient un geste qu'on évite.

**Niveau 1, bloquant.** Sans ces réponses, on ne crée rien :

- le nom du projet ;
- son domaine — une valeur de `config.domaines` ;
- son cycle — une clé de `config.cycles`, ou `aucun` ;
- la date de démarrage.

**Niveau 2, fortement recommandé.** L'absence se signale explicitement et demande une **confirmation active** — « oui, je confirme, on avance sans » :

- le client, en tant qu'entité ;
- le substrat canonique et son adresse ;
- l'échéance.

Un silence ou une réponse non conclusive relance la question. C'est ce qui évite qu'un projet naisse sans pointeur canonique, cas que le lint refusera ensuite à chaque exécution.

**Niveau 3, optionnel** : budget, payeur, véhicule, effectif, responsable.

### La détection ne dispense jamais de la question

Si le type de projet se devine, il **pré-coche la réponse par défaut** ; il ne saute pas la validation. Un type mal deviné produit une arborescence et un CLAUDE.md qu'il faudrait défaire — et personne ne les défait, on vit avec.

### Ingestion préalable

Si un document de cadrage est fourni, **le lire avant de poser la moindre question** et pré-remplir tout ce qui s'y trouve. Ne demander que le reste. Faire ressaisir ce qui est déjà écrit est la meilleure façon de faire abandonner la skill.

## 2. Présenter le plan avant d'écrire

Afficher les trois chemins qui vont être créés et les valeurs retenues. **Attendre la validation.** Aucune création avant.

Défaire trois objets à moitié créés coûte plus que les relire une fois.

## 3. Créer

**La fiche** — `20 - Projets/<CODE> - <Nom>.md`, depuis `_Template Projet`. `<CODE>` est le code du domaine en majuscules.

Renseigner : `type`, `domaine` en lien, `statut`, `cycle`, `phase` **appartenant à l'enum de ce cycle**, `priorite`, `debut`, `client` en lien, le tag `#d/<code>`, et **au moins un pointeur canonique**.

Si le client n'existe pas dans `40 - Acteurs`, le créer depuis `_Template Acteur` — une **entité**, jamais une personne physique.

**Le dossier de travail** — `<config.chemins.dossiers_projets>/<CODE>/<Nom>/`. Une seule convention, sans variante par type. Trois conventions concurrentes rendent tout chemin imprévisible, et c'est ce qui arrive quand on en autorise une deuxième.

**Le CLAUDE.md** — depuis le template adapté (`_Template Projet CLAUDE.md` ou `_Template Code CLAUDE.md`), par substitution. Il porte le **back-pointer** vers le vault : sans lui, les sessions lancées dans le dossier ignoreront le vault, donc les décisions ne seront jamais consignées.

**Un seul CLAUDE.md par racine de projet.** Vérifier après création :

```bash
find "<dossier>" -name "CLAUDE.md" -type f | wc -l   # attendu : 1
```

## 4. Boucler le pointeur

Si le substrat canonique a été créé pendant cette session, **demander son adresse et la reporter** dans `url_canonique` de la fiche.

C'est le seul retour d'information de la chaîne, et celui qu'on saute. Une fiche sans `url_canonique` oblige à rechercher l'espace à la main à chaque session, et le lint la signalera indéfiniment.

## 5. Récap

```
✓ Créé : fiche, dossier, CLAUDE.md
✎ Chemins : <les trois>
⚠ Trous : <niveau 2 non renseigné, ou rien>
→ Suite : <la prochaine action>
```

## Interdits

- **Ne jamais inventer** une valeur manquante. Un trou déclaré vaut mieux qu'une valeur plausible : une fois écrite, elle est indistinguable d'une valeur réelle.
- **Ne jamais écraser** une fiche existante sans arbitrage explicite.
- **Ne jamais créer de sous-CLAUDE.md** dans les sous-dossiers.
- **Ne jamais créer de fiche pour une personne physique.**
- Ne pas créer de domaine au passage : c'est une décision structurante, elle se pose et se journalise.
