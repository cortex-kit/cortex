---
name: lint
description: Audite la santé du vault contre son contrat de données. À lancer avant toute reprise à froid, après une absence, quand quelque chose semble incohérent, et une fois par mois en routine. Rend les écarts classés en contrôles bloquants et en dette, avec un code de retour exploitable. Déclencher quand l'utilisateur dit "lint", "audit du vault", "est-ce que tout est propre", "qu'est-ce qui a dérivé", ou avant de reprendre un chantier laissé de côté. Ne PAS utiliser pour corriger — cette skill constate.
---

# lint — audit de santé du vault

## La commande

```bash
python3 .claude/skills/lint/lint_sante.py --vault .
```

Sortie JSON pour un traitement automatisé : ajouter `--json`. Sortie d'une ligne pour le hook de démarrage de session : ajouter `--bref`, qui rend le compte des contrôles durs, celui de la dette et le rappel de clôture quand elle est trop ancienne.

Code retour : **0** = sain, **1** = au moins un contrôle dur en échec, **2** = erreur d'appel.

## Comment lire le rapport

Deux registres, et ne jamais les confondre dans un compte rendu.

**`[!]` — contrôles durs.** Ce sont des violations du contrat de données. Ils mettent le code de retour à 1 et se corrigent avant de passer à autre chose.

| Contrôle | Ce qu'il attrape |
|---|---|
| `orphelins` | note sans `domaine` ni lien sortant : injoignable autrement qu'en s'en souvenant |
| `pointeur_canonique_absent` | projet actif sans `url_canonique`, `repo` ni `dossier_local` : on ne peut pas rejoindre le travail réel |
| `phase_hors_enum` | `phase` qui n'appartient pas au vocabulaire de son `cycle` |
| `tags_hors_domaines` | tag `#d/` dont le code n'est pas déclaré, ou dont la casse a dérivé |
| `tags_anti_pattern` | tag encodant une logique déjà portée par une propriété |
| `journal_entree_obese` | entrée de journal au-delà du seuil : c'est une copie déguisée |
| `moustaches_residuelles` | placeholder d'installation non substitué |
| `chemins_absolus` | chemin lié à une machine : le vault cesse d'être transmissible |
| `commun_edite_main` | note du vault commun modifiée à la main, en mode fédéré |
| `progression_absente` | projet actif sans progression |
| `visibilite_hors_enum` | `visibilite` autre que `prive` ou `commun` : l'export ne saurait pas quoi en faire |

**`[i]`, la dette.** À surveiller, sans bloquer : journal long, `dernier_journal` périmé, agent métier à revoir, note sans frontmatter, structurant périmé, clôture ancienne.

## Les quatre contrôles du régime copie et de la fédération

Ils sont venus avec le régime `copie` et l'export vers un vault commun. Ce que le lint fait avec eux dépend de `config.yaml`.

**Le régime, d'abord.** Le lint lit `donnees.regime` et le rappelle dans ses statistiques. En `pointeur`, les deux premiers contrôles ci-dessous ne trouvent rien, faute de copies.

**`structurant_perime`, dette.** Pour chaque note de `50 - Ressources/Structurants/`, le lint recalcule le sha256 de `source_path` et le compare au `hash` du frontmatter. Trois raisons possibles : `source modifiee depuis la copie`, `source absente`, `frontmatter incomplet`. C'est une dette voulue : une source qui bouge n'est pas une faute, c'est un rafraîchissement à décider. Le geste est dans la skill `ingest`, section « Rafraîchir un structurant périmé ». Le code de retour reste 0.

**Le plafond de lignes, suspendu sur les structurants.** `journal_entree_obese` ne s'applique pas dans `50 - Ressources/Structurants/`. Une copie de process fait la longueur de son process ; lui imposer dix lignes reviendrait à interdire le régime copie au moment même où on l'a choisi.

**`visibilite`, contrôle dur.** Une note porte `visibilite: prive` ou `visibilite: commun`, ou rien du tout, auquel cas `commun.visibilite_defaut` tranche. Toute autre valeur bloque, parce que l'export du mode fédéré décide sur cette clé : une valeur hors enum enverrait dans le commun une note que personne n'a voulu y mettre, ou retiendrait une note attendue.

**La dernière clôture, dette.** Le lint lit la date du dernier commit (`git log -1`) et la compare à `sante.jours_sans_cloture_alerte`, sept jours par défaut. Au-delà, il le dit. Sans dépôt git, il se tait plutôt que d'inventer. C'est ce même constat que le hook `SessionStart` reprend à l'ouverture.

## Pourquoi certains contrôles bloquent

C'est la décision la plus importante de cette skill, et elle vient d'un constat.

Dans le système dont ce vault est issu, le journal obèse et le pointeur manquant étaient des avertissements. Ils étaient détectés, affichés à chaque exécution, et n'empêchaient rien. Résultat au bout d'un an : sept fiches dont le journal était devenu un compte rendu — la pire avec **une seule entrée de 51 lignes** — et sept fiches dont la `phase` était sortie de tout vocabulaire.

**La détection sans blocage ne protège pas.** Elle produit seulement la sensation d'être surveillé. D'où le passage en contrôle dur de tout ce qui, une fois dérivé, ne se rattrape plus à la main.

## Ce que cette skill ne fait pas

- **Elle ne corrige rien.** Un lint qui répare enlève à l'utilisateur la certitude que ce qui est écrit a été voulu.
- **Elle ne juge pas la valeur du contenu.** Qu'un projet soit pertinent n'est pas son affaire ; qu'il soit conforme et retrouvable l'est.
- **Elle ne voit pas le sens.** Un domaine qui capte 90 % des projets, deux notes qui décrivent la même chose, une entrée de journal qui raconte le *quoi* dans les formes — c'est le travail du sous-agent `auditeur-ontologie`.

## Quand le lint se trompe

Si un constat te paraît faux, **le défaut du lint est le constat à remonter**, pas la note à tordre pour lui plaire.

Un contrôle qui ne mesure pas ce qu'il prétend mesurer est plus dangereux qu'un contrôle absent : il produit une assurance fausse. Les seuils et les enums vivent dans `config.yaml` — les ajuster là est légitime, contourner un contrôle en modifiant une note ne l'est pas.
