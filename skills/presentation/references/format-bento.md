# Le format bento/slides — l'essentiel, et ce qui a coûté

Référence autoportante : de quoi composer un deck complet sans réseau. Pour le
schéma exhaustif (tous les champs, tous les presets), **récupérer
`https://bento.page/agents.md`** — c'est la source à jour, ce fichier en est
l'extrait utile plus ce qu'elle ne dit pas : les défauts rencontrés ici.

## Table

1. [Ce qu'est un deck](#ce-quest-un-deck)
2. [Faire correspondre matière et forme](#faire-correspondre-matière-et-forme)
3. [Le morph](#le-morph)
4. [Grille et lisibilité](#grille-et-lisibilité)
5. [Les défauts payés en production](#les-défauts-payés-en-production)
6. [Vérifier](#vérifier)

## Ce qu'est un deck

Un fichier `.bento.html` autoportant : l'application entière (~670 Ko) plus le
document, en un seul fichier. Celui qui le reçoit l'ouvre dans son navigateur —
aucune installation, aucun compte, et il édite s'il veut.

Le document est du JSON dans un unique bloc près du haut :

```html
<script type="application/bento+json" id="bento-doc"> { "format":"bento/slides", … } </script>
```

On édite **ce bloc et rien d'autre** ; le reste est le runtime compressé.
`scripts/bento.py` s'en charge — il échappe aussi `<` en `<`, sans quoi un
`</script>` dans du contenu fermerait le bloc et casserait le fichier.

`size` et `theme` (dont `fontFamily`) sont obligatoires : sans eux l'app ne
démarre pas du tout, écran blanc.

## Faire correspondre matière et forme

C'est l'étape qui sépare un deck bento d'un empilement de paragraphes. Le
format vaut par le mouvement, le morph, les graphiques et l'interactivité : un
résultat correct mais statique gaspille tout, et c'est le mode d'échec numéro un.
Regarder la matière, et pour chaque morceau choisir ce qui a été construit pour :

| Quand la matière est… | Prendre | Pourquoi |
|---|---|---|
| des nombres à comparer (tendance, ordre de grandeur, part) | un **chart** | une barre se lit d'un coup d'œil, une liste de chiffres non |
| une grille de comparaison, tarifs, specs | une **table** | des cellules structurées battent vingt zones de texte posées à la main |
| deux slides sur **la même chose qui change** | un **morph** (mêmes ids + `transition:"morph"`) | les éléments glissent au lieu de sauter — le geste signature, presque toujours oublié |
| un point à **approfondir** | une **slide d'état** (`stateOf` + `link`) | le fil linéaire reste court, le détail est à un clic |
| une **image pleine page** | image plein cadre + voile + texte, avec **ken-burns** | une photo fixe paraît morte, une dérive lente paraît voulue |
| une **séquence, un flux** | un trait `dash-march`, ou un surlignage qu'on morphe d'étape en étape | le mouvement porte l'œil le long de la séquence |
| un **chiffre-titre** | grand texte + `fx:{countUp:true}` | le décompte capte l'attention |
| une **couverture, un intercalaire** | au moins un mouvement d'ambiance | une couverture figée gâche la première impression |

## Le morph

Deux slides consécutives, `"transition": "morph"` sur la seconde : tout élément
dont l'`id` existe sur les deux est interpolé — position, taille, couleur.

- Ids **déterministes et stables**. Des ids différents = pas de morph, les
  éléments se contentent de sauter.
- `morphId` découple l'appariement de l'`id` quand deux éléments créés
  séparément doivent se répondre. La clé réelle est `morphId || id`.
- Sur une arrivée en morph, un élément **qui a un partenaire** ne joue ni son
  entrée ni son `countUp` : il est déjà en mouvement, et un décompte
  repartirait de zéro. Un élément **nouveau** sur la slide joue tout
  normalement. Donc un chiffre en `countUp` doit être neuf sur sa slide.
- `runhead()` dans `bento.py` applique ça au bandeau de rappel : ids fixes,
  il glisse de slide en slide.

## Grille et lisibilité

Canevas 1280×720, marges latérales 96 px, bande utile 1088 px (bord droit à
1184). Colonnes déjà calculées dans `COLS` (`chartes.py`) : 2 col = 528 px,
3 col = 340 px, 4 col = 254 px. Bandeau de titre `y:72 h:84`, contenu à partir
de `y:208`.

Un accent, deux familles de caractères au maximum. **Plancher de corps : 16 px**
— sous ce seuil c'est illisible au fond d'une salle, et rétrécir pour faire
tenir du texte revient à traiter le symptôme : c'est le contenu qu'on coupe.

`{{page}}`, `{{pages}}`, `{{title}}`, `{{date}}`, `{{author}}`, `{{company}}`
se résolvent au rendu : insérer une slide ne renumérote rien à la main.

## Les défauts payés en production

Chacun a coûté un aller-retour. Ils ne sont pas dans `agents.md`.

**Les séries bar/line veulent des nombres nus.** Un `{value: 12}` se lit `0`.
Seul `pie` prend `{name, value}`. Et `label` sur une série bar/line ne fait
rien : les valeurs au-dessus des barres n'existent pas — mettre un tableau à
côté, ou des zones de texte.

**Le moteur de graphique est « charts-lite ».** Il lit la forme de l'option
ECharts et ignore en silence tout ce qu'il n'implémente pas. Garder les options
minimales et juger sur le rendu, jamais sur le JSON.

**`name` (libellé d'une slide d'état) est du texte brut.** Une entité HTML y
reste littérale : `R&eacute;gulier` s'affiche tel quel dans la barre latérale.
Écrire `Régulier` directement. Idem pour `notes`, `title`, `meta`.

**Un disque semi-transparent laisse un bord net** sur fond sombre, même à 5 %
d'opacité : ça se voit comme un défaut, pas comme un halo. Utiliser un
`fillGradient` sur un rectangle plein cadre.

**Le débordement de texte est invisible dans le JSON.** La hauteur d'une chaîne
à une largeur et une police données n'est pas déductible — un titre qui passe
sur deux lignes mange la rangée en dessous et rien ne le signale. C'est ce que
`validate()` mesure, et c'est la raison pour laquelle il n'est pas optionnel.

**Mais `validate()` ne mesure pas la hauteur d'un tableau.** Un tableau dont les
rangées dépassent sa boîte se fait couper net — la dernière ligne disparaît à
moitié — et le rapport reste à zéro avertissement. Le piège se déclenche quand
une cellule passe sur deux lignes : quatre rangées prévues en une ligne tiennent
dans 300 px, les mêmes en deux lignes non. Compter large (≈ 60 px par rangée à
18 px de corps et 14 px de marge verticale) et **regarder la slide** : c'est le
seul contrôle qui voie ce cas.

**Une police de titre à chiffres de style ancien fait danser les nombres.**
Cormorant, EB Garamond et la plupart des serifs d'inspiration humaniste
composent le 2, le 8 et le 9 sous la ligne de base. C'est superbe dans un
paragraphe et bancal pour un chiffre-clé de 76 px. D'où `police_chiffres` dans
les chartes : elle suit la police de titre, sauf là où il faut repasser au
sans-serif pour les nombres mis en avant.

**Une police non embarquée retombe en silence** — et paraît correcte chez soi.
Voir `scripts/fonts.py`.

**Le fond du `theme` n'est pas appliqué en mode présentation.** Il retombe sur
du noir, et un deck en charte claire devient illisible — texte foncé sur fond
noir. Le piège tient à l'endroit où il se déclenche : l'éditeur, lui, applique
le fond du thème correctement, donc le défaut est **invisible pendant toute la
composition** et n'apparaît que dans le fichier de remise, celui qui démarre en
présentation et qui part chez le client. `document()` pose désormais le fond sur
chaque slide ; une slide qui déclare le sien le garde. Corollaire de méthode :
une revue faite uniquement dans l'éditeur ne voit pas tout — le rendu plat
(`rendu_html_plat.py`) tranche, lui, sans dépendre du mode ni du focus.

**Le mode présentation gèle ses animations quand l'onglet n'a pas le focus.**
Les entrées ne se déclenchent jamais et la slide paraît vide : ce n'est pas un
défaut du deck. Faire la revue visuelle **dans l'éditeur**, où le rendu est
statique et fidèle.

## Vérifier

Ouvrir le fichier, puis dans la console :

```js
const { ok, counts, findings } = window.bento.validate()
findings.filter(f => f.severity !== 'info')
```

Il rapporte en une passe ce que le runtime avale sans rien dire : débordements
mesurés au vrai moteur de rendu, propriétés inconnues (une faute de frappe est
ignorée, donc le style ne s'applique jamais), `link` et `asset:` cassés, ids en
double, collisions de morph, options de graphique non implémentées, police non
embarquée. `severity: "info"` est volontairement discret — une photo qui
déborde du cadre est un parti pris, pas un défaut.

`window.bento.measure({html, w, fontSize, lineHeight})` rend la hauteur réelle
avant même que l'élément existe — pour arrêter de deviner en empilant des
cartes.

Et regarder chaque slide. `validate()` attrape ce qui est vérifiable ; il ne
dit pas si une slide est bonne.
