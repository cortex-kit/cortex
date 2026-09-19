# Email Auditor — Exemples d'utilisation

## Exemple 1: Mail client générique → 3 variantes

### INPUT (brouillon collé)
```
Bonjour,

J'espère que vous allez bien. Je vous écris pour vous proposer nos services de formation 
en intelligence artificielle. Nous proposons des formations adaptées à vos besoins.

N'hésitez pas à me contacter si vous avez des questions.

Cordialement
```

### AUDIT INITIAL
```
Contexte: CLIENT

Objet: [pas d'objet]
├─ Clarté d'attente: ✗ (vague, pas d'action explicite)
├─ Absence généricité: ✗ (template classique, "formations adaptées")
├─ CTA mou: ✗ ("N'hésitez pas à me contacter")
├─ Signature: ✗ (juste "Cordialement", pas de nom)
Score: 1/5

Verdict: GÉNÉRIQUE — Structure template, zéro urgence, CTA mou
```

### RESTRUCTURATION APPLIQUÉE
```
Objet proposé: "Formation IA — proposition personnalisée"

Mail restructuré:
Suite à la demande d'optimiser ta stratégie formation, je te propose un parcours IA adapté 
à ta structure (équipe/effectifs/secteur à préciser).

Action: Transmets-moi ton dossier d'entreprise d'ici vendredi pour affiner la devis.

Evrard Mister IA
```

### VARIANTE 1 — DIRECT
```
Formation IA — ta structure

Besoin du dossier d'entreprise avant vendredi pour affiner devis.
Tu confirmes réception ?

Evrard
```

### VARIANTE 2 — PROFESSIONNEL
```
Formation IA — proposition personnalisée

Suite à échange initial, je te propose un parcours formatif adapté à ta structure.

Pour construire la devis précise, transmets-moi:
- Effectif / secteur
- Objectifs prioritaires
- Budget/calendrier

À retour d'ici vendredi.

Evrard Mister IA
```

### VARIANTE 3 — RELATIONNEL
```
Formation IA — optimisons ensemble

L'IA transforme les organisations. Pour construire ton parcours optimal, j'ai besoin 
de comprendre ta structure et tes objectifs spécifiques.

Peux-tu me transmettre ton dossier d'entreprise d'ici vendredi ? 
Avec ça, je construis une proposition vraiment calibrée.

Evrard Mister IA
```

### NOTES
- Points forts: Pas vraiment
- Améliorations clés: 
  - Objet vague → actionnable + contexte
  - CTA mou → demande précise + deadline
  - Template → personnalisé
  - Signature faible → contextualisée
- Variante recommandée: Variante 3 (client prospect, besoin relationnel + impact)

---

## Exemple 2: Mail partenaire avec ordre logique faible → Variante DIRECT

### INPUT
```
Salut,

En fait, j'aurais besoin du plan parcelle qu'on avait discuté mercredi. 
Ensuite, il faut aussi vérifier les contraintes PLU sur la zone. 
Et d'ailleurs, tu aurais du lien vers la base cadastrale ?

Pas de rush évidemment, mais ça m'aiderait pour le devis.

Merci beaucoup.
```

### AUDIT INITIAL
```
Contexte: PARTENAIRE

Objet: [pas d'objet]
├─ Clarté d'attente: ✗ (3 demandes implicites, ambigu)
├─ Absence généricité: ✓ (personnalisé)
├─ CTA mou: ✗ ("pas de rush", "ça m'aiderait")
├─ Signature: ✗ (absente)
Score: 2/5

Verdict: À AMÉLIORER — Ordre logique faible, CTA mou, multi-demande non hiérarchisée
```

### RESTRUCTURATION APPLIQUÉE
```
Objet proposé: "Plan parcelle + PLU - dossier devis"

Mail restructuré:
Pour affiner le devis Bordeaux, j'ai besoin de trois éléments:

1. Plan parcelle (de l'échange mercredi)
2. Contraintes PLU sur la zone
3. Lien base cadastrale (si tu l'as)

Deadline: mercredi 13h.

Evrard DEVPROM
```

### VARIANTE 1 — DIRECT
```
Plan parcelle + PLU dossier

Envoie-moi mercredi 13h:
- Plan parcelle (discussion mercredi)
- Contraintes PLU zone
- Lien cadastre (si dispo)

Pour affiner devis.

Evrard
```

### VARIANTE 2 — PROFESSIONNEL
```
Dossier Bordeaux — 3 éléments requis

Pour finaliser le devis, j'ai besoin de:

1. Plan parcelle (ref discussion 27 mars)
2. Contraintes PLU applicables (zone)
3. Accès base cadastrale (si tu l'as)

Delai: mercredi 13h.

Evrard DEVPROM
```

### VARIANTE 3 — RELATIONNEL
```
Dossier Bordeaux — on finalise la devis

On parlait d'optimiser le développement sur cette parcelle. Pour affiner ma proposition,
j'ai besoin de valider trois points clés:

- Plan parcelle à jour
- Règles PLU spécifiques (zone)
- Accès cadastre pour cartographie

Peux-tu me transmettre ça mercredi matin ?

Evrard DEVPROM
```

### NOTES
- Points forts: Personnalisé, contexte clair
- Améliorations clés:
  - Hiérarchiser les 3 demandes
  - Deadline explicite (mercredi 13h)
  - Éliminer "pas de rush" (CTA mou)
- Variante recommandée: Variante 1 DIRECT (partenaire, besoin d'action immédiate)

---

## Exemple 3: Mail équipe avec CTA mou → Variante DIRECT

### INPUT
```
Salut l'équipe,

Vous pourriez vérifier si tout est bon pour le devis Bordeaux ? 
Pas trop urgé, mais idéalement avant mercredi si possible.

Merci d'avance.
```

### AUDIT INITIAL
```
Contexte: ÉQUIPE

Objet: [pas d'objet, "Devis Bordeaux" implicite]
├─ Clarté d'attente: ✗ (vague "vérifier si tout est bon")
├─ Absence généricité: ✗ ("l'équipe" au lieu de noms)
├─ CTA mou: ✗ ("pas trop urgé", "idéalement si possible")
├─ Signature: ✗ (absente)
Score: 1/5

Verdict: GÉNÉRIQUE — CTA flou, pas d'urgence explicite, sans signature
```

### RESTRUCTURATION APPLIQUÉE
```
Objet proposé: "Devis Bordeaux — validation mercredi"

Mail restructuré:
Équipe, validez le devis Bordeaux (v2.3 shared folder) avant mercredi 14h.

Checklist:
- Coûts terrains OK
- Charges promotion validées
- Timeline réaliste

Confirmez une fois fait.

Evrard
```

### VARIANTE 1 — DIRECT
```
Devis Bordeaux — validation mercredi 14h

Validez devis v2.3 (shared folder):
- Coûts terrains
- Charges promo
- Timeline

Confirmez une fois fait.

Evrard
```

### VARIANTE 2 — PROFESSIONNEL
```
Devis Bordeaux — validation requise

Avant mercredi 14h, validez le devis v2.3 (shared folder):

Checklist:
- Coûts terrains (à jour)
- Charges promotion (réalistes)
- Timeline de déploiement

Confirmez validation par message.

Evrard
```

### VARIANTE 3 — RELATIONNEL
```
Devis Bordeaux — on finalise

Le devis v2.3 est prêt pour validation. Avant d'aller client mercredi, 
on a besoin de vos retours sur:

- Structuration coûts
- Realisme charges/timeline

Vous confirmez OK d'ici mercredi 14h ?

Evrard
```

### NOTES
- Points forts: Contexte clair, activité identifiée
- Améliorations clés:
  - CTA mou → urgent explicite (mercredi 14h)
  - "vérifier si tout est bon" → checklist précise
  - "l'équipe" → noms spécifiques (bonus)
  - Ajouter signature
- Variante recommandée: Variante 1 DIRECT (équipe interne, action claire + deadline)

---

## Utilisation en workflow

**Via Notion:**
1. Rédige brouillon mail dans bloc texte Notion
2. Copy-paste dans chat Claude → email-auditor s'active
3. Choisis variante → Envoie

**Via Make:**
1. Workflow formation génère draft mail
2. Lance fonction Claude "email-auditor"
3. Retour: 3 variantes → Sélectionne meilleure
4. Send via Gmail automation

**Directe (adhoc):**
1. Colle mail brut quand tu doutes
2. Audit immédiat + 3 variantes
3. Choisis selon contexte/urgent
4. Envoie
