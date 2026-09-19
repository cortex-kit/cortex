---
name: bilan
description: Rend en une page ce que le vault a vécu sur une période : notes touchées, clôtures faites, notes orphelines, structurants périmés, prochaine étape de la chaîne. Lit 60 - Journal, git log, le lint et _cortex/etat.json ; n'écrit rien. Déclencher quand la personne dit "bilan", "qu'est-ce qui a bougé", "où en est mon second cerveau", "bilan de la semaine", ou quand le hook SessionStart le propose à J+7 et J+30 de la remise. Ne PAS utiliser pour corriger (cloture), auditer finement (lint) ni répondre à une question de fond (parle).
---

# bilan : ce que le vault a vécu

Un second cerveau meurt en silence : rien ne casse, on cesse seulement d'y écrire. Le bilan rend ce silence visible, en chiffres, sur une période.

## 0. La période

Par défaut, **depuis la dernière remise** (`_cortex/06-passation.md`, clé `remis_le`), ou sept jours si l'atelier n'est pas dans le vault. La personne peut donner une autre période : « bilan du mois », « depuis lundi ».

Le hook SessionStart propose ce bilan à **J+7** et à **J+30** de la remise. Ce sont les deux moments où l'usage se décide : à J+7 on sait si la clôture est devenue un réflexe, à J+30 on sait si le vault est encore consulté.

## 1. Lire

Quatre sources, toutes en lecture seule :

```bash
git log --since="<date>" --format="%ad %s" --date=short        # clôtures faites
git log --since="<date>" --name-only --format=""                # notes touchées
python3 .claude/skills/lint/lint_sante.py --vault . --json      # orphelins, structurants périmés
```

Puis `60 - Journal/` (les décisions structurantes de la période, par le nom des notes `AAAA-MM-JJ - Titre`) et `_cortex/etat.json` s'il existe (la clé `phrase_suivante` donne la prochaine étape de la chaîne, en langage ordinaire).

Un vault sans git rend un bilan partiel : le dire, et compter les notes par `dernier_journal` dans le frontmatter des fiches projet.

## 2. Rendre

Une page, toujours cette forme, en langage ordinaire :

```
Bilan du <date> au <date>

Clôtures : <N> (dernière le <date>)          <!-- 0 = le signal le plus important -->
Notes touchées : <N>, dont <M> fiches projet, <K> décisions dans 60 - Journal
Projets actifs sans nouvelle depuis <sante.journal_perime_jours> jours : <N> (<noms>)
Orphelins : <N>          Structurants périmés : <N>          Contrôles durs en échec : <N>
Décisions de la période : <une ligne par note de 60 - Journal, ou « aucune »>
Prochaine étape : <phrase_suivante de etat.json, ou « la chaîne est finie : clôturer, c'est tout »>
```

Puis **une phrase de lecture**, jamais plus : ce que les chiffres disent. Exemples :

- « Zéro clôture en sept jours : le vault n'a pas été alimenté. Le geste à retrouver est « clôture » en fin de bloc de travail. »
- « Trois structurants périmés : les sources ont changé depuis la copie. « ingest » les rafraîchit, un par un, sur accord. »
- « Douze clôtures, aucun orphelin : le vault vit. »

## 3. Ne rien écrire

Le bilan constate. Il ne corrige pas un orphelin, ne rafraîchit pas un structurant, ne coche pas une case. Chaque écart qu'il montre a sa skill : `cloture` pour écrire, `ingest` pour rafraîchir, `lint` pour le détail.

Si la personne veut agir sur un point du bilan, nommer la skill et attendre qu'elle la déclenche.

## Interdits

- **Jamais d'écriture**, ni dans le vault, ni dans git.
- **Jamais un chiffre recompté à la main** quand le lint ou git le donnent : deux comptes qui divergent, et plus personne ne sait lequel croire.
- **Jamais inventer une lecture rassurante.** Zéro clôture se dit tel quel.
- **Jamais plus d'une page.** Un bilan long ne sera pas lu, et un bilan non lu ne change rien.
