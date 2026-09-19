# 10 - Domaines — les centres de gravité

Une note par domaine, créée depuis `_Template Domaine`. Entre 1 et 6 : le plafond est dans `config.collecte.plafond_domaines` et le lint le vérifie.

Le plafond n'est pas de la prudence. Au-delà de six centres de gravité, plus rien n'est central : chaque note hésite entre deux rattachements, le choix se fait au hasard, et le classement cesse de porter de l'information. Un besoin de quinze domaines est presque toujours un besoin de six domaines et de tags transverses.

Le `code` d'un domaine pilote deux choses : son tag `#d/<code>` et le préfixe des fiches de projet `<CODE>`. Il vit dans `config.yaml` et se change là, jamais ici.

Un domaine ne se supprime pas : il passe en `statut: archive`. Supprimer casse les liens entrants et efface la trace des projets qu'il a portés.
