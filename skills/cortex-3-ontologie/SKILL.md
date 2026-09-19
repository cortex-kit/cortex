---
name: cortex-3-ontologie
description: Troisième maillon de la chaîne Cortex, et le seul qui juge. Décide les domaines du second cerveau à partir de l'inventaire réel, chacun avec sa preuve chiffrée, puis remplit la matrice d'ownership des substrats du client. Produit 02-ontologie.md, à faire signer avant toute matérialisation. Déclencher quand le consultant dit "maillon 3", "on décide les domaines", "ontologie du vault", ou dispose d'un 01-inventaire.json validé. Ne PAS confondre avec cortex-1-cadrage, qui collecte sans décider, ni avec cortex-4-installation, qui matérialise sans juger.
---

# cortex-3-ontologie — le seul maillon qui juge

Troisième des sept. Tous les autres exécutent ; celui-ci arbitre. C'est aussi le seul dont la sortie se fait **signer** avant de passer à la suite.

Doctrine du découpage et pièges par famille : `cortex-1-cadrage/references/secteurs.md`.

## Positionnement

Ce maillon décide **la carte**, pas le territoire. Il ne crée rien dans le vault — la matérialisation est le maillon 4, et cette séparation est délibérée : l'analyse est chère et subjective, la matérialisation est gratuite et mécanique. Les mélanger interdirait de rejouer la seconde sans re-payer la première.

Il ne collecte rien non plus. Si une information manque, elle manque : **c'est un constat à remonter, pas un trou à combler**.

## Étape 0 — bloquante

1. `_cortex/00-cadrage.md` en `statut: valide`.
2. `_cortex/01-inventaire.json` existe et son `01-inventaire.md` est en `statut: valide`.

**Si un contrôle échoue, s'arrêter. Pas de repli.** Décider une ontologie sans inventaire, c'est la déduire de ce que le client a dit vouloir plutôt que de ce qu'il fait — et ces deux choses diffèrent toujours.

**Lire aussi la clé `conduite` du `config.yaml`** — absente ⇒ `consultant`, comportement actuel à l'identique. En `solo`, ce maillon est le plus exposé de la chaîne : c'est le seul qui juge, et personne n'est là pour contredire le jugement. Deux conséquences, détaillées plus bas : les trois seuils qui invalident deviennent explicatifs (§3), et la signature devient une confirmation explicite dont le coût est énoncé avant (§6).

## 1. Lire l'inventaire comme un corpus, pas comme une liste

Trois signaux, par ordre de valeur décroissante.

**Les schémas des bases existantes.** Noms de propriétés, options de listes déroulantes. C'est le meilleur signal disponible : ce vocabulaire a été choisi par le client et accepté par son équipe. Une ontologie qui reprend ces mots gagne l'adhésion ; une ontologie qui les traduit se fait rejeter, même quand la traduction est meilleure.

**La forme de l'arborescence.** Les noms de dossiers de premier et deuxième niveau sont une taxonomie subie, celle que l'usage a imposée faute de décision. Elle est souvent mauvaise, et toujours instructive : elle montre où le classement a cédé.

**Les volumes et la fraîcheur.** Un dossier avec 400 fichiers et une modification d'hier est un centre de gravité. Un dossier avec 3 fichiers de 2019 est un vestige. Les deux ont l'air d'un domaine dans une liste ; un seul en est un.

## 2. Proposer les domaines — chacun avec sa preuve

**Format imposé.** Aucune proposition sans évidence chiffrée :

```
Domaine « Actifs »
  ← 312 fichiers sous /Portefeuille (2 niveaux, maj il y a 3 jours)
  ← base « Biens » : 47 entrées, propriétés Statut / Ville / Surface / Bail
  ← 41 % du volume de messagerie entrante sur 12 mois
```

Une proposition sans preuve n'est pas proposée. Cette règle a un effet secondaire recherché : elle rend visible ce que l'inventaire ne couvre pas, et donc ce qui reste à sonder.

Ce qui n'est pas observé s'écrit **`Non observé dans l'inventaire`**. Jamais une supposition plausible : une fois écrite, elle sera lue comme un constat.

Marqueurs conservés dans `02-ontologie.md` : `[déduction]` pour une inférence assumée, `[?]` pour un point incertain, `[!]` pour une contradiction non tranchée. Et une section finale **« Points incertains à challenger »**, qui est ce que le client doit lire en premier.

## 3. Les trois seuils qui invalident

Mesurés, pas appréciés. Une ontologie se discute mal en opinion et bien en chiffres.

| Seuil | Signification | Action |
|---|---|---|
| un domaine capte **> 70 %** des notes attendues | sous-segmentation : le classement ne porte plus d'information | **`statut` ne passe pas à `valide`**. Re-découper |
| un domaine capte **0** note attendue | créé par anticipation | le retirer, quitte à l'ajouter le jour où il sert |
| **plus de 6** domaines | plafond dur | constat de sous-segmentation à remonter, pas une case à ajouter |

**Le dénominateur, c'est les notes — pas les projets.** Projets, acteurs et ressources comptent tous. La distinction n'est pas une subtilité : mesurés sur les seuls projets, ces deux seuils se combinent pour **découper ce qui est homogène et supprimer ce qui est distinct**.

Le cas se produit sur toute organisation mono-activité, c'est-à-dire sur la plupart des PME. Chez une menuiserie d'agencement, les chantiers captaient 100 % des projets — le premier seuil invalidait donc le seul découpage évident — tandis que le bureau d'études, les achats et l'atelier n'en captaient aucun et tombaient sous le second, alors qu'ils portaient le dossier le plus récemment modifié du corpus et deux réunions hebdomadaires. Une fonction support porte des acteurs, des ressources et des décisions ; elle ne porte jamais de projet daté, et ce n'est pas une anticipation.

Le premier seuil reste le plus important et le plus contre-intuitif : un client qui range 90 % de son travail dans « Opérations » n'a pas un gros domaine, il a un découpage qui ne sert à rien.

**En mode solo, ces seuils s'expliquent au moment où ils frappent.** Personne ne défend les plafonds à la place du consultant, donc c'est le maillon qui le fait : quand un domaine proposé ne tient pas son seuil, ne jamais le retirer ni le re-découper en silence — dire **lequel** des trois seuils il casse, montrer le chiffre, et dire ce que ça signifie. « “Administratif” capterait 78 % des fiches : à ce niveau, le classement ne classe plus rien — tout serait administratif, donc rien ne le serait. Voici un re-découpage possible : … » vaut mieux que la même correction faite sans un mot. Le jugement s'expose, il ne s'impose pas : la personne doit pouvoir contester chaque retrait, et un domaine écarté reste visible dans `02-ontologie.md` avec son chiffre et son seuil.

## 4. Remplir la matrice d'ownership

C'est le second livrable, et il est aussi structurant que les domaines. La table à trous d'`Architecture Mémoire` §2 se remplit ici, à partir de l'inventaire réel.

Pour chaque type de fait : quelle est la source de vérité, et que fait le vault. Un type de fait sans source déclarée **finira écrit deux fois** — mieux vaut une ligne `_à renseigner_` visible qu'une case remplie au hasard.

**Déclarer au moins un lien INTERDIT.** Il en existe toujours un : le sens d'écriture qui créerait une double écriture sur un champ déjà miroir. Un sens interdit non écrit est un sens qui sera pris, parce qu'il paraît pratique le jour où on en a besoin.

## 5. Fixer le reste du contrat

- **Les cycles et leurs phases**, dérivés du vocabulaire du client. Ce sont ses mots, pas les tiens : `Cadrage / Production / Livraison` est un défaut raisonnable, pas une norme.
- **Les codes de domaine** : 2 à 4 lettres minuscules. Ils pilotent le tag et le préfixe de fiche, et ne changeront plus sans réaffecter tout le vault.
- **Les axes commerciaux**, seulement s'ils servent. Liste vide est le bon défaut : ils n'ont de sens que pour qui vend sous plusieurs marques ou encaisse via plusieurs entités.
- **Les personnes physiques restent hors du vault.** Décision explicite, pas un oubli.

## 6. Validation — par décision, une par une

La granularité la plus fine de la chaîne avec le maillon 1, et pour une autre raison : chaque ligne est un arbitrage qu'il faudrait re-litiger avec le client si on le passait en bloc.

Puis **faire signer `02-ontologie.md`**. Pas une formalité : c'est le document qui empêchera, dans trois mois, de refaire le débat des domaines sur un vault déjà peuplé — moment où le changer coûte cent fois ce qu'il coûte aujourd'hui.

**En mode solo, la signature devient une confirmation explicite — et le coût se dit avant.** Récapituler la carte entière : les familles retenues avec leur preuve, ce qui a été écarté et pourquoi, les cycles, les points incertains. Puis énoncer le coût, en clair : « revenir sur cette carte une fois l'outil rempli demandera de tout reprendre — chaque fiche re-rattachée une à une. C'est maintenant que changer d'avis est bon marché. » Attendre la confirmation ; un refus rouvre la décision concernée, pas la carte entière. La confirmation se trace dans `02-ontologie.md` — une ligne datée « Carte récapitulée, coût de retour énoncé, confirmée le <date> » — et c'est par elle que le contrôle `ontologie_signee_client` passe : en solo, le signataire et le bénéficiaire sont la même personne, la trace remplace le papier. Une porte supprimée serait un défaut, pas une simplification.

## 7. Écrire

`_cortex/02-ontologie.md`, et reporter les blocs `domaines`, `cycles` et `substrats` dans `config.yaml`.

```yaml
maillon: 3
produit_par: cortex-3-ontologie
statut: valide
controles:
  domaines_sous_plafond: passe
  chaque_domaine_a_une_preuve: passe
  distribution_equilibree: passe      # aucun domaine > 70 %
  aucun_domaine_vide: passe
  matrice_ownership_remplie: passe
  lien_interdit_declare: passe
  ontologie_signee_client: passe
```

## Message de clôture

```
Ontologie arrêtée pour <organisation>.

- <N> domaines, chacun avec sa preuve
- matrice d'ownership : <M> types de faits, <K> lien(s) INTERDIT déclaré(s)
- cycles : <liste>
- points incertains à challenger : <N>

Pour toi :
1. Fais signer 02-ontologie.md. Ne saute pas cette étape.
2. Puis lance `cortex-4-installation`.

Le maillon 4 refuse de démarrer si 02-ontologie.md n'est pas en statut
valide. Installer sur une ontologie non arbitrée produit un vault qu'il
faudra refaire — et refaire un vault déjà rempli coûte cent fois
l'installation.
```

**En mode solo :**

```
La carte de votre outil est arrêtée.

- <N> familles, chacune appuyée sur ce que l'inventaire a constaté
- écarté : <ce qui n'a pas tenu son seuil, avec le chiffre — ou rien>
- points encore incertains : <N — les relire, c'est par eux qu'on se
  trompe>

Vous venez de la confirmer, c'est tracé.

La suite installe l'outil lui-même : une seconde, entièrement
automatique, rien à décider. Sa condition d'entrée : cette carte
confirmée — c'est fait.

On enchaîne ?
```

Sur accord, lancer `cortex-4-installation`. Si la carte n'est pas confirmée : s'arrêter et dire ce qui reste en suspens — rien ne s'installe avant la confirmation.

## Interdits

- **Jamais un domaine sans preuve chiffrée.**
- **Jamais un domaine parce que le client l'a nommé** au cadrage. Il l'a nommé avant qu'on regarde ; l'inventaire prime.
- **Jamais le découpage par organigramme.** Il décrit qui rapporte à qui, pas où le travail se fait — et il change tous les dix-huit mois.
- **Jamais dépasser 6 domaines** pour faire plaisir.
- **Jamais combler un trou de l'inventaire par une supposition.** `Non observé` est une réponse.
- **Jamais matérialiser ici.** Aucun fichier créé dans le vault : c'est le maillon 4, et le garder mécanique est ce qui le rend rejouable à coût nul.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
