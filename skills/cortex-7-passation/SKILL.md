---
name: cortex-7-passation
description: Septième maillon de la chaîne Cortex. Produit le pack de remise du vault au client — guide d'usage, runbook des quatre opérations, fiche de reprise à froid — passe la recette d'acceptation mécanique, dont le contrôle de white-label bloquant, date la remise (remis_le) pour que la skill bilan du vault fasse le point à J+7 et J+30, et termine en ouvrant la notice. Déclencher quand le consultant dit "maillon 7", "passation", "on remet le vault", "recette", ou quand le vault est peuplé et vérifié. Ne PAS utiliser pour produire un support de formation : hors périmètre par décision.
---

# cortex-7-passation — remettre, et prouver que c'est remettable

Septième maillon ; la fédération (`cortex-8`) ne suit qu'en mode `federe`. Régénérable à coût nul, et **à tout moment plus tard** : quand le vault du client aura évolué, on relance ce maillon et la documentation redevient juste.

## Positionnement

Ce maillon **ne forme pas**. Il produit un guide écrit et une recette. La formation humaine est une prestation à part.

La raison n'est pas commerciale : un support de formation périme plus vite que la doctrine qu'il présente, et un support périmé enseigne des gestes qui ne marchent plus — ce qui est pire que pas de support du tout.

## Étape 0 — bloquante

Tous les fichiers `_cortex/` en `statut: valide` ou explicitement `arbitre` avec motif. Le lint du vault sort en 0.

**Lire aussi la clé `conduite` du `config.yaml`** — absente ⇒ `consultant`, comportement actuel à l'identique. En `solo`, ce maillon devient une remise à soi-même, ce qui n'a rien d'absurde : le guide d'usage et la fiche de reprise à froid servent exactement à la personne qu'on sera dans six mois, quand plus rien de l'installation ne sera frais. La recette ne perd pas un contrôle — voir §3.

## 1. Le guide d'usage — dans le vault du client

`90 - Meta/Guide d'usage.md`. C'est le seul document que le client lira vraiment, donc le seul endroit où l'effort de rédaction compte.

Il répond à quatre questions, dans cet ordre :

**« Qu'est-ce que c'est ? »** — La mémoire longue et le pilotage léger de l'organisation. Il pointe, il ne stocke pas. Ce qu'il n'est pas : un wiki d'équipe, un gestionnaire de tâches, un espace de stockage, un double du substrat métier.

**« Qu'est-ce que je fais tous les jours ? »** — Une chose : lancer `cloture` à la fin de chaque bloc de travail. Trois à dix fois par jour, moins de trente secondes.

C'est le seul geste qui compte, et c'est celui sur lequel tout repose. Un vault sans clôture se remplit une fois, à l'installation, puis meurt — personne ne retourne écrire ce qui s'est décidé. Le dire ainsi, sans l'enrober.

**« Qu'est-ce que je fais de temps en temps ? »** — `nouveau-projet` quand un projet démarre, `ingest` quand une source vaut d'être gardée, `lint` une fois par mois et avant toute reprise après absence, `parle` pour poser une question et obtenir une réponse qui cite, `bilan` quand le hook le propose (J+7, J+30) ou à la demande.

**« Qu'est-ce que je ne dois jamais faire ? »** — Recopier un document dans le vault. Y écrire un secret. Y créer une fiche pour une personne physique. Écrire à plusieurs dans le même vault.

## 2. La fiche de reprise à froid

`90 - Meta/Reprise.md`. Pour le jour où le client rouvre son vault après trois semaines et ne sait plus par où entrer.

L'ordre est le livrable — il va du général au particulier sans jamais faire lire plus que nécessaire :

1. `Architecture - Vue d'ensemble` si le système n'est plus familier ;
2. **le lint** — ce qui a dérivé pendant l'absence. Le geste le plus rentable : une commande donne la liste des projets dont plus personne ne sait rien ;
3. `60 - Journal/`, les dernières notes — les décisions prises depuis ;
4. `Centre`, section « quoi regarder » — l'état courant.

Ne jamais commencer par la liste des projets. Un état lu sans les décisions qui l'ont produit se comprend de travers, et on refait des arbitrages déjà tranchés.

## 3. La recette d'acceptation — mécanique

Des commandes, pas des appréciations.

```bash
V="<racine du vault>"

# 1. WHITE-LABEL — BLOQUANT
#    -w est indispensable : sans limites de mot, « matis » matche
#    « auto-MATIS-ation » et « for-MATIS-me ». Un contrôle qui produit huit
#    faux positifs à chaque exécution finit par être ignoré, et c'est ainsi
#    qu'une vraie fuite passe.
grep -rwiE "<config.marque.mentions_interdites, en alternance>" "$V"   # attendu : vide

# 2. Transmissibilité
grep -rE "/Users/|/home/|[A-Z]:\\\\" "$V" --include='*.md'            # attendu : vide

# 3. Santé
python3 "$V/.claude/skills/lint/lint_sante.py" --vault "$V"           # attendu : exit 0

# 4. Autonomie : le lint tourne DEPUIS le vault, sans rien de la machine du consultant
ls "$V/.claude/skills/lint/lint_sante.py"

# 5. Zéro plugin requis
test ! -f "$V/.obsidian/community-plugins.json"

# 6. Pointeurs vivants : trois au hasard, vérifiés à la main
```

**Le contrôle 1 est bloquant et sans exception.** Un vault livré chez un client qui contient le nom d'un autre client n'est pas un défaut de finition : c'est une fuite, et elle ne se rattrape pas après remise.

**Le contrôle 6 est le seul manuel, et il est irremplaçable.** Le lint vérifie qu'un pointeur est présent, jamais qu'il mène quelque part. Un pointeur faux est invisible pour la machine et ne se découvre qu'à l'usage, des semaines plus tard, au pire moment.

**En mode solo, la recette tourne à l'identique, et la porte demeure.** Il n'y a personne à convaincre, mais il y a soi-même dans six mois, et chaque contrôle garde son objet : le white-label attrape les traces d'origine du gabarit — la liste pré-remplie au maillon 1 —, les chemins absolus rendraient l'outil intransportable, le contrôle 6 reste manuel — trois liens vérifiés de sa propre main, personne d'autre ne le fera. Une fois les six verdicts rendus, la porte : les récapituler à l'écran en langage ordinaire, demander une confirmation explicite, et la tracer dans `06-passation.md` — une ligne datée « Recette récapitulée et confirmée le <date> ». Une recette passée sans être lue n'est une porte pour personne ; une porte supprimée serait un défaut, pas une simplification.

## 4. L'invariant de remise

**Un contrôle qui n'est ni `passé` ni explicitement `arbitré` avec motif bloque la remise.** Pas de « on verra après » : après la remise, plus personne ne revient sur la recette.

## 5. Écrire l'état

`_cortex/06-passation.md` — le dernier fichier de l'atelier.

```yaml
maillon: 7
produit_par: cortex-7-passation
statut: valide
remis_le: AAAA-MM-JJ           # la date que le hook SessionStart et la skill bilan lisent
controles:
  white_label_zero_occurrence: passe
  zero_chemin_absolu: passe
  lint_vert: passe
  lint_execute_depuis_le_vault: passe
  zero_plugin_requis: passe
  trois_pointeurs_verifies_main: passe
```

`remis_le` est la date du jour de la remise confirmée. Sans elle, le suivi n'a pas de point de départ.

## 6. Le suivi après remise : J+7 et J+30, par `bilan`

Le suivi n'est pas un protocole ni une prestation : c'est une skill du vault, `bilan`, et un hook qui la propose. À **J+7** et à **J+30** de `remis_le`, le hook `SessionStart` du vault affiche une ligne : « Bilan J+7 de la remise : dites « bilan ». » La skill lit `60 - Journal`, `git log`, le lint et `_cortex/etat.json`, et rend une page : clôtures faites, notes touchées, orphelins, structurants périmés, prochaine étape.

Ces deux dates sont les deux moments où l'usage se décide. À J+7, on sait si la clôture est devenue un réflexe ; zéro clôture en sept jours est le signal à ne pas manquer. À J+30, on sait si le vault est encore consulté. En mode `consultant`, prévoir de demander ces deux bilans au client ; en mode `solo`, le hook suffit.

Le hook lit `remis_le` dans `_cortex/06-passation.md` **quand l'atelier vit dans le vault** (mode `solo`). En mode `consultant`, l'atelier ne part pas chez le client : copier la seule ligne `remis_le` dans un `_cortex/06-passation.md` réduit à son frontmatter, sans inventaire ni constats.

**La remise ouvre la notice.** Le dernier geste du maillon est la commande de la section Notice ci-dessous : le tableau de bord montre les étapes faites et la phrase suivante, qui est désormais « clôture ». La personne voit l'installation finie et le seul geste qui reste.

## Message de clôture

```
Vault remis à <organisation>.

Recette : <N>/6 contrôles passés<, arbitrages : …>
Livré : guide d'usage, fiche de reprise, runbook des 4 opérations
        <N> notes, <M> domaines, kit de 6 skills, <K> sous-agents, 2 hooks
Remise datée du <remis_le> : bilan proposé à J+7 et J+30.

Pour toi :
1. Fais la remise en montrant UN geste : `cloture` sur une vraie session.
   Pas une visite guidée du vault.
2. Archive _cortex/ de ton côté. Il ne part pas chez le client, sauf la
   ligne remis_le (§6).
3. À J+7 et J+30, demande le `bilan`.

Ce maillon se relance quand tu veux : si le vault évolue, la documentation
se régénère. C'est pour ça qu'elle n'est pas écrite à la main.
```

**En mode solo :**

```
Votre second cerveau est installé, rempli et vérifié.

Recette : <N>/6 contrôles passés — vous venez de la lire et de la
confirmer, c'est tracé.
Dans l'outil : le guide d'usage, et la fiche de reprise — c'est elle
qu'on ouvre après trois semaines sans y avoir touché.
Le dossier d'atelier _cortex/ reste chez vous : c'est le carnet de
bord de cette installation.

Il ne reste qu'un geste, et tout repose sur lui : à la fin de chaque
bloc de travail, dites « clôture ». Moins de trente secondes, trois à
dix fois par jour. Un second cerveau sans clôture se remplit une fois,
puis meurt.

Dans une semaine, puis dans un mois, l'outil vous proposera un bilan à
l'ouverture : dites « bilan », il vous dira ce qui a vécu.

La chaîne s'arrête ici pour un cerveau seul. Celui-ci se relance quand
vous voulez : si l'outil évolue, sa documentation se régénère.

Faites une première clôture maintenant, sur cette installation même :
dites « clôture ».
```

Puis la notice (section ci-dessous) : c'est elle qui montre l'installation finie.

## Interdits

- **Jamais remettre avec le contrôle de white-label en échec.**
- **Jamais livrer `_cortex/`.** L'atelier contient l'inventaire brut, les hypothèses écartées et les constats sur l'organisation du client. Il reste chez le consultant.
- **Jamais produire un support de formation** : hors périmètre par décision. Le suivi, lui, existe et tient en une skill, `bilan`, à J+7 et J+30 ; pas un protocole de plus.
- **Jamais remettre sans `remis_le`** : sans date, aucun bilan ne sera proposé.
- **Jamais déclarer un contrôle passé sans l'avoir lancé.** C'est le seul mensonge de toute la chaîne qui arrive jusqu'au client.
- **Jamais faire la remise en visite guidée.** Montrer un geste réel vaut mieux qu'un tour du propriétaire : ce qu'on veut, c'est que le client lance `cloture` le lendemain, pas qu'il ait vu tous les dossiers.

## Notice

En fin de maillon, régénérer le tableau de bord et l'ouvrir, sans rien lancer d'autre :

    python3 "${CLAUDE_SKILL_DIR}/../cortex-4-installation/scripts/notice.py" --atelier <chemin de _cortex/>

La notice montre l'état des étapes et propose la phrase à prononcer pour la suivante. Elle ne l'exécute jamais : la personne décide d'enchaîner.
