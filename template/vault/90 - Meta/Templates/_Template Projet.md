---
type: projet
domaine: "[[NOM_DOMAINE]]"
statut: actif                 # idee | actif | attente | termine | archive
cycle: mission                # cle de config.cycles, ou `aucun`
facturable: true              # axe commercial, independant du cycle
phase: ""                     # DOIT appartenir a l'enum de `cycle` (controle dur)
progression: 0                # 0-100 ; prime sur le mapping derive de phase
priorite: P2                  # P0 | P1 | P2 | P3
debut: {{date:YYYY-MM-DD}}
echeance:
client: ""                    # "[[Acteur]]"
partenaire: ""
responsable: ""
effectif:
budget:
payeur: ""                    # qui verse l'argent, valeur de config.payeurs
dossier_local: ""             # RELATIF a config.chemins.dossiers_projets
substrat_canonique: ""        # notion | sharepoint | confluence | drive | git | aucun
url_canonique: ""             # adresse du substrat, jamais son contenu
repo: ""
claude_md: ""
dernier_journal:              # ISO date, patche par la skill cloture
blocages_actifs: 0            # patche par la skill cloture
tags:
  - d/CODE
---
# {{title}}

Domaine : [[NOM_DOMAINE]]

Une ligne sur l'objet du projet. Pas un paragraphe : le détail vit dans le substrat canonique.

## Actions

<!-- Macro-actions de pilotage seulement : un pointeur à vérifier, une décision à
ancrer, un trou à qualifier, une dépendance transverse. Le backlog détaillé reste
dans le substrat canonique. Recopier les tâches du substrat ici crée deux listes
qui divergent, et on finit par ne plus savoir laquelle fait foi. -->

- [ ] Première macro-action #d/CODE 📅

## Décisions

<!-- Décisions mineures locales à ce projet, en puces datées. Les décisions
structurantes vont dans 60 - Journal comme note dediee, pour être requêtables et
visibles dans le graphe. -->

-

## Journal

<!-- Le POURQUOI, jamais le QUOI. Ce qui a changé est déjà dans l'historique du
substrat ou du dépôt ; ce qui n'est écrit nulle part ailleurs, c'est la raison.

Une entrée = `### YYYY-MM-DD` puis {{SEUIL_JOURNAL}} lignes maximum. C'est un
contrôle dur du lint, pas une recommandation : sans ce plafond, une fiche de
projet actif atteint cinquante lignes sur une seule entrée en quelques mois, et
le vault devient un double du substrat qu'il devait seulement pointer. -->

## Pointeurs

<!-- Adresses des sources canoniques. Jamais de contenu recopié. -->

- Substrat canonique :
- Dossier de travail :
