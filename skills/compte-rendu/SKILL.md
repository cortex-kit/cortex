---
name: compte-rendu
description: Génère automatiquement des mails de compte rendu structurés à partir de notes manuscrites (photo), d'un fichier audio, ou de texte brut. Produit des versions distinctes selon les destinataires détectés parmi : moi (interne opérationnel), client, partenaire. Couvre les activités Mister IA et Devprom. Déclencher dès que l'utilisateur : (1) uploade une photo de notes manuscrites, (2) uploade un fichier audio d'une réunion ou d'une prise de notes vocale, (3) colle du texte brut ressemblant à des notes ("voici le CR", "voici mes notes", suite de bullet points non formatés, résumé de réunion), (4) mentionne "compte rendu", "CR", "réunion", "notes de séance", "résumé de réu". Déclencher aussi sur tout input multi-lignes non structuré qui ressemble à des notes prises à la volée, même sans mot-clé explicite. Ne PAS attendre confirmation — traiter immédiatement.
---

# Compte Rendu — Skill Evrard

## Objectif

Transformer tout input brut (photo, audio, texte) en mails de CR prêts à envoyer, segmentés par destinataire, avec ton et contenu adaptés à chaque audience.

---

## Étape 1 — Ingestion selon format input

### Photo de notes manuscrites
- Analyser visuellement le contenu via vision
- Extraire tout le texte lisible, même partiel
- Si illisible ou ambigu : indiquer le passage et continuer avec le reste

### Audio (fichier uploadé)
- Transcrire le contenu audio intégralement
- Nettoyer : supprimer les hésitations, répétitions, faux départs
- Conserver les noms, chiffres, dates, engagements verbaux explicites

### Texte brut / copié-collé
- Traiter directement sans transformation préalable

---

## Étape 2 — Extraction structurée

À partir du contenu ingéré, extraire systématiquement les 4 sections suivantes. Si une section est absente des notes, l'indiquer explicitement ("Non mentionné").

```
DÉCISIONS PRISES
- [Décision 1]
- [Décision 2]

ACTIONS + RESPONSABLE + DEADLINE
- [Action] → [Responsable] → [Deadline ou "À définir"]

POINTS EN SUSPENS
- [Point non tranché ou en attente]

PROCHAINE RÉUNION / RDV
- [Date, heure, format ou "Non planifié"]
```

---

## Étape 3 — Détection automatique

### Activité
Détecter parmi le contenu : **Mister IA** (formation, coaching, IA, apprenant, module, session) vs **Devprom** (foncier, promoteur, agent, parcelle, PLU, développement, programme). Si les deux sont présents : traiter comme Mister IA par défaut et signaler l'ambiguïté.

### Destinataires présents
Détecter quels destinataires sont pertinents selon le contenu :
- **Moi (interne)** : toujours généré
- **Client** : si un client, apprenant, acheteur, ou prospect est mentionné
- **Partenaire** : si un partenaire, prestataire, co-intervenant, broker est mentionné

Ne pas générer un mail pour un destinataire non pertinent.

---

## Étape 4 — Génération des mails

Générer un mail par destinataire détecté. Structure et ton différenciés.

---

### Mail 1 — MOI (interne opérationnel)

**Objet** : `CR [activité] — [date ou thème principal]`

**Ton** : brut, dense, exhaustif. Inclut tout, y compris les éléments sensibles ou non encore tranchés.

**Structure** :
```
DÉCISIONS : [liste]
ACTIONS : [liste avec responsable + deadline]
SUSPENS : [liste]
PROCHAIN RDV : [info]
NOTES BRUTES : [tout ce qui ne rentre pas dans les cases ci-dessus mais qui a de la valeur]
```

**Signature** : aucune (mail interne à moi-même)

---

### Mail 2 — CLIENT

**Objet** : `Suite à notre échange — [thème] [date]`

**Ton** : professionnel/relationnel. Valorise les engagements pris. Exclut les éléments internes sensibles (marges, tensions, doutes non résolus). Formule les actions côté client de façon claire et non aggressive.

**Structure** :
```
[Phrase d'ouverture contextuelle — 1 ligne max]

Suite à notre échange :

Décisions actées :
- [...]

Ce que nous faisons de notre côté :
- [Action Evrard → deadline]

Ce que nous attendons de votre côté :
- [Action client → deadline]

Points à confirmer :
- [Suspens pertinents pour le client]

Prochain contact : [date/format]

[Signature]
```

**Signature selon activité** :
- Mister IA → `Evrard Mister IA`
- Devprom → `Evrard DEVPROM`

---

### Mail 3 — PARTENAIRE

**Objet** : `CR [thème] — actions et suite`

**Ton** : neutre/efficace. Synthétique. Centré sur les next steps mutuels. Pas de détails inutiles.

**Structure** :
```
[Contexte de l'échange — 1 phrase]

Décisions :
- [...]

Actions de notre côté :
- [Action → deadline]

Actions de ton côté :
- [Action → deadline]

Points en suspens :
- [...]

Prochain RDV : [info]

[Signature]
```

**Signature** : `Evrard` (partenaire = contexte neutre)

---

## Étape 5 — Format de sortie

Présenter les mails dans cet ordre, séparés par des séparateurs visuels :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVITÉ DÉTECTÉE : [Mister IA / Devprom]
DESTINATAIRES : [Moi / Client / Partenaire]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━ MAIL 1 — MOI (INTERNE) ━━━
Objet : [...]
[corps]

━━━ MAIL 2 — CLIENT ━━━
Objet : [...]
[corps]
[signature]

━━━ MAIL 3 — PARTENAIRE ━━━
Objet : [...]
[corps]
[signature]
```

Si un destinataire est absent : ne pas inclure son bloc, sans mention.

---

## Règles strictes

- Langue : FR exclusivement
- Zéro généricité ("belle réunion", "merci pour les échanges") sauf si contexte relationnel fort le justifie
- Zéro CTA mou ("n'hésitez pas", "dites-moi si")
- Actions toujours formulées avec responsable + deadline (ou "À définir" explicite)
- Contenu interne (tensions, marges, doutes) → visible uniquement dans Mail 1 (moi)
- Si input audio ou photo manquant de clarté : signaler les passages incertains entre [crochets]

---

## Cas limites

| Situation | Comportement |
|-----------|-------------|
| Activité indétectable | Demander : "Mister IA ou Devprom ?" avant de générer |
| Aucun client ni partenaire mentionné | Générer Mail 1 uniquement, signaler |
| Notes trop fragmentaires (<5 infos extractibles) | Signaler, demander si on continue avec ce qui est disponible |
| Audio inaudible / photo illisible | Signaler les zones, traiter le reste |
| Les deux activités présentes | Traiter Mister IA par défaut, signaler ambiguïté |
