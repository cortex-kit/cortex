---
name: cortex-6-agents-metier
description: Sixième maillon de la chaîne Cortex. Conçoit et génère les sous-agents sur mesure au métier du client, une fois le vault peuplé — un lecteur de baux pour une foncière, un dépouilleur d'appels d'offres pour un bureau d'études. Chaque agent naît d'une spec versionnée et porte une date de revue que le lint surveille. Déclencher quand le consultant dit "maillon 6", "agents métier", "agent sur mesure", ou après l'ingest si le cadrage a identifié une tâche répétitive. Ne PAS utiliser pour les 2 sous-agents génériques, livrés par cortex-4-installation.
---

# cortex-6-agents-metier — sur mesure, avec une date de péremption

Sixième maillon, et le dernier de construction. Il vient **après** l'ingest, délibérément.

## Pourquoi après, et pas à l'installation

Un agent métier conçu sur un vault vide encode ce que le consultant **suppose** du métier. Conçu sur un vault peuplé, il part des documents réels et des répétitions observées.

L'écart entre les deux est exactement l'écart entre un agent qu'on utilise et un agent qu'on a fait pour la démonstration.

## Le problème que ce maillon doit gérer

Les agents métier encodent des règles de gestion, et les règles de gestion changent tous les trimestres.

Un agent qui a cessé d'être juste **continue de répondre**. Il ne signale rien, ne se plaint pas, et sa réponse a exactement la même allure qu'avant — sûre, structurée, plausible. C'est ce qui les rend plus dangereux qu'utiles à moyen terme, et c'est la raison pour laquelle beaucoup de bibliothèques d'agents métier sont mortes au deuxième trimestre sans que personne le remarque.

On ne traite pas ça par de la prose dans une documentation. On le traite par un mécanisme.

## Le test d'éligibilité — trois conditions cumulatives

Un agent métier ne se crée que si les **trois** sont réunies :

1. **La tâche est répétitive** — au moins une fois par semaine, ou vingt fois par an.
2. **Elle est lourde en lecture** — beaucoup de matière en entrée, peu de sortie. C'est ce qui justifie un contexte séparé plutôt qu'une skill.
3. **Elle porte sur un type de document nommé** — un bail, un appel d'offres, un rapport d'expertise. Pas « les documents du client ».

**Si une condition manque, ne pas créer l'agent. Le dire, et expliquer laquelle.**

C'est la partie la plus utile de ce maillon. Tout client demande des agents, et la moitié de ces demandes décrivent une tâche qui se fait mieux dans le fil principal, sans agent du tout.

## Étape 0 — bloquante

1. Le vault est peuplé, `_cortex/04-ingest.md` en `statut: valide`.
2. Le lint sort en 0.
3. Au moins un besoin identifié au cadrage ou constaté à l'ingest.

Si aucun besoin ne passe le test à trois conditions : **livrer zéro agent métier et le dire.** Le kit générique — quatre skills et deux sous-agents — couvre l'usage courant. Zéro est un résultat valide, et souvent le bon.

**Lire aussi la clé `conduite` du `config.yaml`** — absente ⇒ `consultant`, comportement actuel à l'identique. En `solo`, la réponse honnête au test des trois conditions est le plus souvent « pas encore » : un agent sur mesure se conçoit sur des répétitions observées, et quelqu'un qui vient d'installer son outil n'en a encore aucune. Le dire comme un rendez-vous, jamais comme un refus : « Aucun geste ne s'est encore répété dans votre outil — c'est normal, il vient d'être rempli. Travaillez avec pendant trois semaines ; si une même corvée revient chaque semaine sur un même type de document, revenez me le dire : c'est exactement ce qu'un assistant sur mesure sait absorber. » Ce maillon se relance à tout moment ; passer au maillon 7 n'y ferme aucune porte.

## 1. La spec, avant le code

Chaque agent naît d'une entrée dans `_cortex/05-agents-metier.md` :

```yaml
- nom: lecteur-de-baux
  type_document: "bail commercial (PDF, 15-40 pages)"
  irritant: "relever 6 champs dans chaque bail, ~3 h par lot de 10"
  frequence: "hebdomadaire, 8 à 12 baux"
  source_de_verite: "l'espace documentaire, dossier Baux"
  perimetre_lecture: "le PDF seul, jamais la base"
  sortie: "table de 6 colonnes + les incertitudes marquées"
  revoir_le: 2027-02-17
  motif_revue: "la trame de bail change à chaque renouvellement de modèle"
```

La spec se fait valider **avant** l'écriture de l'agent. C'est aussi elle qui rend l'agent maintenable par quelqu'un d'autre : sans elle, personne ne sait plus ce qu'il était censé faire ni pourquoi.

## 2. Le mécanisme de péremption

Chaque agent porte dans son frontmatter :

```yaml
metier: true
revoir_le: 2027-02-17
```

**Le lint signale tout agent dont la date est dépassée**, au même titre qu'un projet actif sans journal depuis deux semaines. Défaut : `config.sante.agent_metier_revue_mois`, six mois.

C'est tout le dispositif, et il tient en deux lignes de frontmatter. Un agent périmé ne disparaît pas et ne se bloque pas — il devient **visible**, ce qui suffit : le problème des agents métier n'a jamais été qu'ils vieillissent, mais que personne ne s'en aperçoive.

## 3. Écrire l'agent

Dans `<vault>/.claude/agents/<nom>.md`. Frontmatter `name`, `description` avec ses déclencheurs et ses non-déclencheurs, `tools` **limités à la lecture**.

Contraintes non négociables, les mêmes que pour les deux agents génériques :

- **Il ne décide pas.** Il lit, il extrait, il rend. L'interprétation reste au fil principal.
- **Il n'écrit rien.** Aucune note créée ni modifiée.
- **Il marque ce dont il n'est pas sûr** : `[?]` sur un champ incertain, `[!]` sur une contradiction dans la source.
- **Il cite ses sources** : page, section, chemin. Une extraction sans source est invérifiable, donc inexploitable.
- **Un champ absent se déclare absent.** Jamais une valeur plausible : dans une extraction, une valeur inventée est indistinguable d'une valeur lue, et c'est le seul défaut qui contamine toutes les autres.

## 4. Tester sur du réel

Faire tourner l'agent sur **trois documents réels**, et vérifier chaque champ à la main.

Un agent métier accepté sans cette vérification est un agent dont personne ne connaît le taux d'erreur — et un taux d'erreur inconnu sur une extraction rend toute la sortie inutilisable, puisqu'il faudra tout revérifier de toute façon.

## 5. Écrire l'état

```yaml
maillon: 6
produit_par: cortex-6-agents-metier
statut: valide
controles:
  test_trois_conditions_applique: passe
  chaque_agent_a_une_spec: passe
  chaque_agent_a_une_date_de_revue: passe
  aucun_agent_ecrit: passe
  teste_sur_documents_reels: passe
```

## Message de clôture

```
Agents métier livrés pour <organisation> : <N>.

- <liste, avec la date de revue de chacun>
- écartés faute de remplir les 3 conditions : <N, avec la condition manquante>
- testés sur <M> documents réels

Pour toi :
1. Explique la date de revue au client. Un agent périmé répond quand même.
2. Lance `cortex-7-passation`.
```

**En mode solo :**

```
Assistants sur mesure : <N | aucun pour l'instant — et c'est normal>.

<Si N > 0 : la liste, avec la date de revue de chacun et ce qu'elle
signifie — un assistant périmé répond quand même, d'où la date.>
<Si N = 0 : aucun geste ne s'est encore assez répété pour en justifier
un. Revenez après trois semaines de travail réel — ce maillon se
relance quand vous voulez.>

Le dernier maillon prépare la remise : le guide d'usage, la fiche de
reprise pour dans six mois, et la recette qui prouve que tout tient.
Sa condition d'entrée : tous les jalons précédents au vert —
<c'est fait | il manque : …>.

On enchaîne ?
```

Sur accord, lancer `cortex-7-passation`. S'il manque un jalon — un fichier d'atelier ni valide ni arbitré — s'arrêter et dire lequel : le maillon 7 le refuserait de toute façon en étape 0.

## Interdits

- **Jamais un agent par métier ou par service.** C'est la demande la plus fréquente et le plus sûr moyen de produire une bibliothèque morte au deuxième trimestre.
- **Jamais un agent sans date de revue.**
- **Jamais un agent qui écrit.**
- **Jamais un agent livré sans test sur du réel.**
- **Jamais forcer une création** parce que le client en attend une. Zéro agent métier avec le kit générique vaut mieux qu'un agent qui répondra faux dans six mois.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
