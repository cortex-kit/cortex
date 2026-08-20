# CLAUDE.md — {{NOM_PROJET}}

Chargé automatiquement pour toute session d'agent lancée depuis ce dépôt. Porte le cadre technique : pile, commandes, conventions, pointeurs.

## Identité projet

| Champ | Valeur |
|---|---|
| Nom | {{NOM_PROJET}} |
| Domaine | {{DOMAINE}} |
| Type | {{TYPE}} (application web / script / bibliothèque / service / autre) |
| Stade | {{STADE}} (amorçage / développement / production / maintenance) |
| Responsable | {{RESPONSABLE}} |

## Pointeurs canoniques

| Substrat | Rôle | Adresse |
|---|---|---|
| Dépôt | source de vérité du code | {{REPO_URL}} |
| Fiche vault | direction, journal, actions macro | `20 - Projets/{{PREFIX}} - {{NOM_PROJET}}.md` |
| Production | application déployée | {{PROD_URL}} |
| Base de données | substrat de données | {{DB_NOM}} |
| Documentation | docs internes ou externes | {{DOC_URL}} |

Le dépôt dit **ce qui** a changé, la fiche vault dit **pourquoi**. Aucun des deux ne recopie l'autre : un journal de projet qui liste les commits est du bruit, l'historique git le fait mieux.

## Pile technique

- Frontend : {{FRAMEWORK_FRONT}}
- Backend : {{FRAMEWORK_BACK}}
- Données : {{DATABASE}}
- Authentification : {{AUTH}}
- Hébergement : {{HOSTING}}
- Autres : {{AUTRES_LIBS}}

## Commandes

- Installation : `{{INSTALL_CMD}}`
- Développement : `{{DEV_CMD}}`
- Compilation : `{{BUILD_CMD}}`
- Tests : `{{TEST_CMD}}`
- Analyse statique : `{{LINT_CMD}}`
- Déploiement : `{{DEPLOY_CMD}}`

## Conventions projet

- {{CONVENTION_1}}
- {{CONVENTION_2}}

## Interdictions et garde-fous

- **Aucun secret dans le code ni dans l'historique.** Les fichiers d'environnement sont exclus du suivi de version et dupliqués dans la plateforme d'hébergement. Un secret commité reste dans l'historique même après suppression : il faut le révoquer, pas l'effacer.
- Aucune réécriture forcée de l'historique sur la branche principale.
- Aucune modification des données fournies par un tiers : elles sont la référence, pas un brouillon.
- **Aucun sous-CLAUDE.md dans les sous-dossiers.** Un seul par racine de projet. Plusieurs fichiers de contexte dans une même arborescence produisent des consignes qui divergent en silence, et l'agent applique celle qu'il a lue en dernier.
- {{AUTRES_INTERDICTIONS}}

## Statut

Instancié le {{DATE_PROJET}}. À mettre à jour à chaque changement de pile, ajout de dépendance structurante, ou évolution de convention — un CLAUDE.md périmé est plus nuisible qu'absent, parce qu'il est cru.
