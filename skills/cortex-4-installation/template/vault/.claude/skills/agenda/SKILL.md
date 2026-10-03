---
name: agenda
description: Rend en une page les cases datées du vault : en retard, aujourd'hui, les sept prochains jours, les prioritaires sans date. Lit les lignes « - [ ] » des notes, avec leur date 📅 et leur priorité 🔺 ou ⏫ ; n'écrit rien. Sert de point du matin. Déclencher quand la personne dit "agenda", "mon agenda", "qu'est-ce qui m'attend", "point du matin", "mes échéances", "qu'est-ce qui est en retard". Ne PAS utiliser pour acter une case faite (cloture) ni pour l'agenda des rendez-vous, qui vit dans le calendrier.
---

# agenda : ce qui attend, daté

Le vault porte des macro-actions sous `## Actions`, une ligne chacune : `- [ ] Relancer le client #d/<code> ⏫ 📅 2026-10-12`. L'agenda les rassemble. Il ne remplace ni le calendrier (les rendez-vous) ni l'outil de suivi (le backlog détaillé).

**Devant la personne** : ses mots, jamais ceux de l'outil (ni le nom d'un script, ni une clé de `config.yaml`) ; et tout ce qu'on lui demande de valider s'affiche en entier avant la question.

## La commande

```bash
python3 .claude/skills/agenda/agenda.py --vault .
```

`--jours 14` élargit l'horizon. `--bref` rend une ligne, celle que le hook de démarrage affiche.

## Rendre

La page telle que le script la sort, puis, en une à trois phrases :

- les cases **en retard** d'abord : pour chacune, faite (à cocher par une clôture), à redater, ou à abandonner. Une case échue qu'on laisse ouverte brouille l'agenda de tous les jours suivants ;
- si le script signale trop de cases prioritaires, le dire : si tout est prioritaire, rien ne l'est.

Ne rien cocher, redater ni supprimer ici : proposer, et laisser la clôture écrire après accord.

## Écrire une case qui se lit

- Une macro-action, pas une tâche de backlog : une relance, une décision à obtenir, une échéance qui engage.
- Une date seulement si elle engage (`📅 AAAA-MM-JJ`). Une case sans date n'apparaît pas à l'agenda, sauf prioritaire.
- 🔺 pour l'urgent, ⏫ pour le haut ; sept au plus à la fois.
