---
name: prompt-architect
description: Transforme toute intention brute ou mal formulée en prompt structuré, précis et directement opérationnel pour un LLM. Déclencher dès que l'utilisateur : (1) dit "transforme ça en prompt", "fais-en un prompt", "reformule en prompt", "écris-moi un prompt pour", "optimise ce prompt", (2) fournit une idée vague, une phrase incomplète, ou un bloc de notes brutes en demandant quelque chose à faire avec l'IA, (3) demande un "bon prompt", un "prompt efficace", un "prompt système", un "prompt de rôle", (4) veut automatiser une tâche répétitive et cherche comment l'instruire à une IA. Déclencher aussi quand l'intention est implicite : l'utilisateur décrit ce qu'il veut obtenir d'une IA sans formuler de prompt — c'est une intention brute à transformer. Généraliste : fonctionne pour tous domaines, toutes cibles (Claude, GPT, Gemini, LLM embarqués).
---

# Prompt Architect

Pipeline en 4 phases : extraction d'intention → sélection de type → assemblage structuré → livraison.

---

## Phase 1 — Extraction d'intention

Extraire depuis l'input brut :

| Dimension | Question implicite |
|---|---|
| **Objectif final** | Que doit produire l'IA exactement ? |
| **Rôle à assigner** | Qui est l'IA dans ce contexte ? |
| **Contexte opérationnel** | Quelles contraintes, données, environnement ? |
| **Format de sortie** | Texte libre / liste / JSON / tableau / code / document ? |
| **Ton et registre** | Expert / pédagogique / commercial / neutre / créatif ? |
| **Garde-fous** | Ce que l'IA ne doit jamais faire dans ce prompt |

Si une dimension est non-inférable et bloquante → poser UNE question unique, ciblée. Jamais plusieurs questions simultanées.

---

## Phase 2 — Sélection du type de prompt

Choisir le type adapté à l'objectif extrait :

| Type | Usage |
|---|---|
| **Prompt système (system prompt)** | Définir un comportement permanent, un rôle, des règles d'interaction |
| **Prompt de tâche** | Instruction one-shot pour produire un livrable précis |
| **Prompt chaîné** | Séquence d'étapes successives, chaque output alimente le suivant |
| **Prompt avec variables** | Template réutilisable avec slots `{{VARIABLE}}` à instancier |
| **Prompt d'analyse** | Extraire, synthétiser, classer, évaluer un contenu fourni |
| **Prompt de rôle** | Persona persistant avec contraintes comportementales définies |

Un prompt peut combiner plusieurs types (ex : système + variables).

---

## Phase 3 — Assemblage structuré

Structure canonique à respecter selon le type sélectionné.

### Blocs disponibles (ordonnés)

```
[RÔLE]         — Qui es-tu ? Expertise, posture, identité fonctionnelle
[CONTEXTE]     — Situation, données disponibles, environnement d'usage
[OBJECTIF]     — Ce que l'IA doit produire, atteindre, résoudre
[INSTRUCTIONS] — Étapes, règles, logique de traitement (liste ordonnée si multi-étapes)
[FORMAT]       — Structure de l'output attendu (longueur, forme, langue, balises)
[CONTRAINTES]  — Ce qui est interdit, à éviter, hors périmètre
[VARIABLES]    — Slots {{NOM_VARIABLE}} si prompt réutilisable
[EXEMPLE]      — Shot(s) d'illustration si nécessaire pour ancrer le comportement
```

**Règles d'assemblage :**
- Inclure uniquement les blocs nécessaires. Un prompt de tâche simple n'a pas besoin de [RÔLE].
- [INSTRUCTIONS] en liste numérotée si > 2 étapes.
- [CONTRAINTES] toujours présent si le risque de dérive est élevé (hallucination, hors-sujet, ton inadapté).
- Variables en `{{MAJUSCULES_UNDERSCORE}}` systématiquement.
- Pas de formulations polies ou de filler ("S'il vous plaît", "Merci de bien vouloir").

### Calibration de la densité

| Complexité de la tâche | Longueur cible du prompt |
|---|---|
| Simple (une action, output court) | 50–150 mots |
| Moyenne (workflow, format défini) | 150–400 mots |
| Complexe (système, multi-domaine) | 400–800 mots |
| Système complet | 800+ mots, découper en sections nommées |

---

## Phase 4 — Livraison

Output exclusif : **le prompt structuré, prêt à copier-coller**, encadré dans un bloc de code markdown.

```
[prompt assemblé ici]
```

Après le bloc : une ligne de méta-annotation optionnelle si pertinente (type sélectionné, slots à instancier, modèle cible si spécifique). Pas d'explication des choix, pas de justification, pas de commentaire sur la qualité.

---

## Règles transversales

- **Inférence maximale** : extraire le maximum depuis l'input avant de poser une question.
- **Zéro filler** : aucun mot dans le prompt produit ne sert à être poli — chaque mot instrumente.
- **Précision > exhaustivité** : un prompt court et précis surpasse toujours un prompt long et vague.
- **Testabilité** : le prompt produit doit être utilisable tel quel sans modification par l'utilisateur.
- **Neutralité modèle** : par défaut, optimiser pour Claude (Anthropic). Si l'utilisateur précise GPT/Gemini/autre, adapter les conventions (balises XML → Markdown, format system prompt, etc.).

---

## Exemples de transformation

### Input brut → Prompt de tâche

**Input :** "je veux un prompt pour résumer des articles de presse immobilière"

**Output :**
```
Tu es un analyste immobilier senior. On te fournit un article de presse sur le marché immobilier français.

Produis une synthèse structurée en 3 blocs :
1. Faits clés (chiffres, tendances, acteurs cités) — liste à puces, 5 items max
2. Signal marché (haussier / baissier / neutre) — 1 ligne + justification en 2 phrases
3. Implications opérationnelles pour un promoteur ou investisseur — 2–3 points actionnables

Longueur totale : 150–200 mots. Aucune reformulation éditoriale de l'article.

ARTICLE :
{{ARTICLE}}
```

---

### Input brut → Prompt système

**Input :** "un prompt système pour un assistant qui aide mes commerciaux à rédiger des mails de prospection"

**Output :**
```
Tu es un expert en développement commercial B2B, spécialisé dans la rédaction de communications à haute conversion.

Ton rôle : aider les commerciaux à rédiger des emails de prospection percutants, adaptés à leur cible et à leur offre.

Règles permanentes :
- Chaque email doit comporter : accroche personnalisée, valeur proposition en 1 phrase, preuve sociale ou chiffre, appel à l'action unique et précis
- Longueur : 80–120 mots maximum
- Ton : direct, professionnel, sans formules creuses
- Jamais de : "j'espère que vous allez bien", "je me permets de", "n'hésitez pas à"
- Si l'utilisateur ne précise pas la cible ou l'offre, poser ces deux questions avant de rédiger

Format de livraison : email prêt à envoyer, sujet inclus, aucune variante sauf demande explicite.
```
