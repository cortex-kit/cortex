---
id: email-auditor
name: Email Auditor
version: "1.0"
description: Audite et améliore mails bruts en générant 3 variantes contextualisées (DIRECT/PROFESSIONNEL/RELATIONNEL) avec signatures dynamiques. Élimine généricité, renforce clarté, valide strictement sans chattiness.
author: Evrard
tags:
  - email
  - communication
  - writing
  - business
trigger: "colle mail|audit ce mail|améliore brouillon"
---

# Email Auditor — Compétence Evrard

## Description courte
Audite et améliore mails bruts en générant 3 variantes contextualisées (DIRECT / PROFESSIONNEL / RELATIONNEL) avec signatures dynamiques. Élimine généricité, renforce clarté, valide strictement sans chattiness.

## Déclenchement
- User colle un mail brut ("Voici mon brouillon", "audit ce mail", etc.)
- Contexte détecté automatiquement (client/partenaire/équipe) ou demandé si ambigu
- Pas besoin d'attendre confirmation pour traiter

## Workflow complet

1. **Détection contexte** → Client / Partenaire / Équipe
2. **Audit initial** → Scoring 5 critères (objet, clarté, généricité, CTA mou, signature)
3. **Restructuration silencieuse** → Réordonne contexte → enjeu → action
4. **Génération 3 variantes** → Niveaux de formalité différents
5. **Signature dynamique** → Appliquée selon contexte

## Profil d'écriture de référence (capturé lors de l'audit initial)

**Ton adaptatif:**
- Clients = chaleureux/direct
- Partenaires = neutre/efficace  
- Équipe = direct/assertif

**Structure**: Contexte + enjeu + action attendue, jamais de fioriture inutile

**Clôture**: Signature unique dynamique
- Evrard (partenaires/équipe)
- Evrard DEVPROM (clients devprom)
- Evrard Mister IA (clients formations/coaching)
- Evrard Voies d'Égypte (clients voyage)
- Evrard Rotaract (équipe associative)

**Caractéristiques strictes:**
- Objet court, actionnable, 3-7 mots max
- CTA zéro formule molle ("n'hésitez pas", "dites-moi si", excuses)
- Format: Paragraphes percutants, zéro "et" / "mais" / "donc" superflus

## 5 Critères d'audit qualité

| Critère | Validation ✓ | Flag si ✗ |
|---------|-----------|---------|
| **Objet** | Court, actionnable, 3-7 mots | >10 mots ou vague ("Mail important") |
| **Clarté d'attente** | Qui fait quoi, quand = explicite | Ambigu ou "on verra" |
| **Absence généricité** | Personnalisé au destinataire | Formule template ("bonjour à tous") |
| **Zéro CTA mou** | Pas de "dites-moi", "n'hésitez pas" | Présence de phrases molles |
| **Signature unique** | Correspond au contexte prédéfini | Générique ou absente |

Score final: X/5 → Verdict (CONFORME / À AMÉLIORER / GÉNÉRIQUE)

## 3 Niveaux de formalité (variantes)

### Variante 1: DIRECT (équipe/partenaire)
- Zéro détour, action immédiate
- Ton assertif/confiant
- Signature: **Evrard**
- Format: Impératif court
- Exemple: "Valide la devis Bordeaux mercredi 13h. Evrard"

### Variante 2: PROFESSIONNEL (partenaire standard/client B2B)
- Contexte + enjeu + action
- Ton neutre/efficace
- Signature: **Evrard [CONTEXTE]** (ex: Evrard DEVPROM)
- Format: Propositionnel clair, 2-3 paragraphes max
- Exemple: "Suite à ta demande devis. J'ai besoin du plan parcelle avant mercredi. Confirmé ? Evrard DEVPROM"

### Variante 3: RELATIONNEL (client/prospect premium)
- Chaleureux mais efficace
- Enjeu avant action
- Signature: **Evrard Mister IA** ou contextualisée
- Format: Narratif court
- Exemple: "Nous parlons d'optimiser ta stratégie formation. Pour avancer, transmets-moi ton dossier d'entreprise d'ici vendredi. Evrard Mister IA"

## Process de restructuration (appliqué silencieusement)

1. Détecte flou: phrase longue, ordre logique faible, CTA enterré
2. Réordonne: contexte → enjeu → action → détails (si nécessaire)
3. Raccourcit: supprime redondance, nexus inutiles ("et", "donc", "d'ailleurs")
4. Garde style: syntaxe personnelle respectée, pas de réécriture agressive
5. Signal au user: "Restructuration appliquée" avec version reformulée visible

## Format de sortie standard

```
━━━ AUDIT INITIAL ━━━
Contexte: [CLIENT / PARTENAIRE / ÉQUIPE]

Objet: [évaluation du titre]
├─ Clarté d'attente: [✓ ou ✗]
├─ Absence généricité: [✓ ou ✗]
├─ CTA mou: [✓ ou ✗]
├─ Signature: [✓ ou ✗]
Score: X/5

Verdict: [CONFORME / À AMÉLIORER / GÉNÉRIQUE]

━━━ RESTRUCTURATION APPLIQUÉE ━━━
[mail refondu en ordre logique, avec annotations minimes]

━━━ VARIANTE 1 — DIRECT ━━━
[version courte assertive]
— Evrard

━━━ VARIANTE 2 — PROFESSIONNEL ━━━
[version équilibrée]
— Evrard [CONTEXTE]

━━━ VARIANTE 3 — RELATIONNEL ━━━
[version chaleureux/efficace]
— Evrard Mister IA / Evrard [CONTEXTE]

━━━ NOTES ━━━
- Points forts: [x, y]
- Améliorations clés: [z, w]
- Variante recommandée: Variante X (car...)
```

## Pièges courants (matrice de détection)

| Piège | Détection | Correction |
|-------|-----------|-----------|
| "Bonjour à tous" | Template générique | Personnaliser au destinataire |
| "N'hésitez pas à..." | CTA mou | "Envoyez-moi..." / "Confirmez..." |
| "Cordialement" seul | Signature faible | Ajouter "Evrard [CONTEXTE]" |
| Objet vague | "Mail", "Demande", "Question" | "Devis devprom - Bordeaux mars 2026" |
| 3+ paragraphes de contexte | Flou logique | Resserrer à 1-2 phrases max |
| Excuse inutile | "Désolé de...", "Pardon de..." | Supprimer ou "Pour accélérer..." |
| CTA à la fin (après signature) | Ordre logique faible | Placer avant signature |
| Double demande | "Et aussi, peux-tu..." | Hiérarchiser: action 1 / action 2 |

## Signature dynamique — Règles de sélection

| Contexte | Signature | Cas d'usage |
|----------|-----------|-----------|
| Client/Prospect | Evrard Mister IA | Formations, coaching, formation IA |
| Client Devprom | Evrard DEVPROM | Devis, formations agents, dev foncier |
| Client Voies d'Égypte | Evrard Voies d'Égypte | Propositions, itinéraires, voyage |
| Partenaire/Fournisseur | Evrard | Collaboration ponctuelle |
| Équipe/Collaborateur | Evrard | Interne, instruction |
| Rotaract Paris | Evrard Rotaract | Commission leadership |

## Notes de design

- **Multimodal**: Génère OU améliore OU valide selon besoin user
- **Hétérogène**: Clients/partenaires/équipe gérés dans même compétence
- **Scalable**: 3 variantes = matrice réutilisable pour tous contextes
- **Non-invasive**: Restructure silencieusement, visible dans output
- **Audit strict**: Scoring transparent, pas de validation fausse
- **Signature contextualisée**: Dynamique selon destinataire et activité

## Cas d'usage typiques

**Brouillon client generic → 3 variantes professionnel/relationnel**
```
Input: "Bonjour, j'ai besoin de vos services de formation. N'hésitez pas à me contacter."
Output: Audit score 2/5 (générique) + 3 variantes personalisées
```

**Mail partenaire, ordre logique faible → restructure + variante direct**
```
Input: "J'aimerais savoir si tu peux... en fait, d'abord j'aurais besoin de... et puis aussi..."
Output: Restructuration + Variante 1 DIRECT ultra-claire
```

**Mail équipe avec CTA mou → Variante 1 assertive**
```
Input: "Salut, si tu pouvais valider ce devis... pas de rush. Merci."
Output: Variante 1 "Valide la devis mercredi. Evrard"
```

## Intégrations potentielles

- **Notion**: Draft mail dans Notion → Lance email-auditor avant envoi
- **Make**: Workflow formation → email-auditor sur mails de convocation
- **Claude in Chrome**: Drafts dans Gmail → Audit avant send
