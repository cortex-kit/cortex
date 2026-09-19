---
name: presentation
description: >-
  Skill socle de création de decks de présentation. Un document JSON pivot, deux
  rendus depuis la même saisie : un .bento.html autoportant qui embarque
  l'application et porte morph, graphiques vivants, tableaux, slides d'état
  cliquables et notes orateur ; et un .pptx en formes natives, donc éditable
  dans PowerPoint comme dans Canva. Charte automatique par marque (mia /
  devprom / vde / neutre), polices embarquées, contrôle de mise en page et de
  géométrie, publication optionnelle sur le cockpit via passage de relais à
  /publier. Déclencher dès qu'il est question de produire une présentation, un
  deck, des slides, un support de formation, un support de comité, un plan de
  restitution intermédiaire, une soutenance, un pitch, un point d'étape à
  présenter, ou d'exporter un deck en PowerPoint — y compris quand
  l'utilisateur dit seulement « il me faut de quoi présenter X », « prépare le
  support pour la réunion », « fais des slides sur Y », « mets ça en
  présentation », « un deck pour le client », « il me faut ça en PPT », sans
  nommer d'outil ni de format. Déclencher aussi pour reprendre, recharter,
  compléter ou convertir un .bento.html existant. Ne PAS utiliser quand le
  livrable doit reproduire à l'identique le template PowerPoint de référence
  (claudia-6) ou porter les composants métier du profil bis — verbatims,
  timeline, irritants (claudia-bis-4-deck).
---

# /presentation — decks de présentation

Ce skill produit des decks **web** : un fichier `.bento.html` unique qui
contient l'application et le document. Celui qui le reçoit l'ouvre dans son
navigateur, sans installation ni compte. C'est ce qui le rend transmissible par
lien et vivant — graphiques, transitions morph, drill-down cliquable — là où un
fichier de présentation classique est une pièce jointe figée.

Il ne remplace aucune chaîne existante : il en occupe le créneau manquant.

## Un document, deux rendus

Le document JSON est le **pivot**. Il se rend en web et en PowerPoint, depuis la
même source :

```
                document (pivot)
               /                \
        rendu bento          rendu pptx  →  Canva
        .bento.html            .pptx
```

C'est la distinction qui compte : **une seule saisie, deux rendus**. Le contenu
n'existe qu'à un endroit ; si un chiffre change, il change dans le fichier de
deck et les deux formats suivent. Deux fichiers composés séparément, ça, ce
serait deux vérités qui divergent.

```bash
python3 scripts/rendu_pptx.py mon-deck.bento.html      # → mon-deck.pptx
```

Le PPTX sort en **formes natives, jamais en image** — règle établie par
`claudia-bis-4-deck` et reprise telle quelle : un deck aplati n'est plus
retouchable, et l'intérêt du passage par Canva disparaît. Le rendu vérifie sa
propre géométrie après écriture et signale tout écart de plus d'un demi-pixel.

**Tout ne survit pas au PPTX** — morph, slides d'état, animations. La
dégradation est nommée, jamais silencieuse : le rendu retourne la liste de ce
qu'il a perdu, et cette liste s'affiche. Le contrat complet est en tête de
`scripts/rendu_pptx.py` ; si un rendu perd autre chose que ce qui y figure,
c'est un défaut, pas une dégradation.

## La doctrine — à lire avant de produire un deck de livraison

`references/doctrine-deck.md` porte la norme de fabrication, toutes marques et
tous véhicules : le critère de choix du rendu, les règles de rendu et ce que
chacune a coûté, la vérification visuelle, le retour du projeté, et de quoi
rejouer une chaîne à froid six mois plus tard.

**La lire quand le deck part chez quelqu'un** — client, comité, formation, ou
tout ce qui sera projeté ou transmis. Un brouillon interne s'en passe.

Trois choses en sortent, à retenir même sans l'ouvrir :

1. **Une saisie, plusieurs rendus, aucune reprise en aval.** Un rendu ne se
   corrige jamais sur lui-même : on corrige la source et on relance. Mesuré sur
   une production réelle, la règle ne tient pas toute seule : 41 pages sur 48
   avaient divergé de leur source dans l'outil de présentation, 192 segments,
   sans que personne le voie.
2. **Le levier est le contrôle, jamais le moteur.** Un défaut graphique ne vient
   pas d'avoir choisi le mauvais rendu, il vient d'un contrôle qui mesure les
   boîtes au lieu du texte dedans.
3. **On appelle, on ne réécrit pas.** « Dans l'esprit de » est le mode de panne.

## Routage — quand ce n'est pas ici

Deux chaînes gardent leur périmètre, et pour une raison précise :

- **`claudia-6`** clone un template PowerPoint de référence, slide par slide.
  Quand le livrable doit reproduire ce template à l'identique, c'est là.
  ⚠ Archivée : elle n'est plus la chaîne d'aucun profil en service.
- **`claudia-bis-4-deck`** porte des composants métier du profil de restitution
  d'audit — verbatims, timeline, étapes, irritants, pastilles de registre. Un
  deck qui a besoin de ces objets-là passe par elle. Elle **appelle ce socle**
  pour la mesure et le contrôle, elle ne les réécrit pas.

**Tout le reste passe ici**, y compris ce qui doit finir en PPTX ou dans Canva :
support de formation, point d'étape, comité, pitch, note de cadrage, soutenance,
livrable de décision à faire signer, deck interne.

En cas de doute, demander. Un deck produit dans le mauvais moule est du travail
entier à refaire, pas une retouche.

## Quel rendu — le critère se mesure, il ne se discute pas

**Natif par défaut.** On bascule en image seulement quand le moteur natif refuse
de poser sans écraser la police : `ajuster()` rend `tient = False`, ou le
contrôle de débordement échoue à hauteur contrainte. C'est une mesure de
faisabilité, pas une appréciation, et surtout **pas un comptage de formes** — un
seuil au nombre de formes se trompe, et il pousse à appauvrir une mise en page
pour rester sous la barre.

Ce qui déborde, c'est le **contenu** qu'on coupe, jamais la police qu'on écrase.
Une coupe se déclare sur la page.

**Émettre en 13,333 × 7,5 pouces.** Un canevas surdimensionné a le même rapport,
donc rien ne signale l'erreur, mais il ne s'insère pas dans une présentation
ordinaire. Le rapport ne suffit pas, la taille absolue compte.

**Une sortie image perd la netteté à l'import** : un PPTX ne porte que des
pouces, l'outil qui importe rééchantillonne à sa définition, et monter la
résolution ne fait que déplacer le seuil. En échange elle ne peut pas diverger,
puisqu'elle ne se retouche pas.

## Cycle

### 0. Sur une machine neuve, vérifier les prérequis

```bash
python3 ~/.claude/skills/presentation/scripts/prerequis.py
python3 ~/.claude/skills/presentation/scripts/prerequis.py --corriger
```

Le dépôt des skills synchronise le CODE entre les machines. Pas les polices, pas
les applications, pas les paquets Python : chaque machine les installe pour
elle-même. Le script dit ce qui manque et la commande pour le poser.

**Il va plus loin qu'un inventaire de fichiers** : il rend un PPTX d'une slide,
le convertit, et lit les polices réellement embarquées dans le PDF. C'est la
seule vérification qui prouve quelque chose, parce qu'une police absente ne fait
pas échouer LibreOffice — elle lui fait rendre un deck qui n'est pas le vôtre,
en silence, avec d'autres largeurs donc d'autres retours à la ligne.

À relancer après chaque mise à jour de LibreOffice, qui efface les polices
posées dans son bundle.

### 1. Cadrer, en quatre points

Ne pas commencer à composer avant d'avoir ces quatre-là. Les déduire du
contexte quand ils sont déductibles, demander seulement ce qui manque
vraiment — une question par information absente, pas un questionnaire.

- **La marque** : `mia`, `devprom`, `vde`, `neutre`. En session projet, elle se
  lit dans le frontmatter de la fiche vault (`vehicule` : `mister-ia` → mia,
  `devprom` → devprom, `voies-egypte` → vde). Hors projet, demander. Ne jamais
  deviner : un deck en charte VDE envoyé sous en-tête Mister IA se voit.
- **La destination** : fichier local seulement, ou lien transmissible via le
  cockpit ? Ça change le nommage du fichier et impose la copie read-only
  (voir `references/publication.md`).
- **La matière** : d'où vient le contenu. Une fiche vault, une passation, un
  compte rendu, des notes. **Aller la lire.** Un deck composé sur des souvenirs
  de conversation contient des chiffres faux, et un chiffre faux dans un deck
  client coûte plus cher que le deck.
- **L'intention** : ce que l'auditoire doit décider ou comprendre en sortant.
  C'est ce qui détermine la dernière slide, et souvent tout le reste.

### 2. Composer — faire correspondre matière et forme

L'étape qui fait la différence entre un deck bento et un empilement de
paragraphes. Reprendre la table de correspondance de
`references/format-bento.md` : des chiffres à comparer deviennent un graphique,
deux slides sur la même chose qui change deviennent un morph, un point à
approfondir devient une slide d'état cliquable.

**Lire `references/composition.md` avant la première slide.** Il porte les
règles relevées sur le template de restitution Mister IA — 137 slides analysées
run par run : le titre autoporteur, un emploi par couleur, les petites tailles
en capitales, le gras majoritaire, le chiffre qui occupe la slide, la gradation
pour les séries. Ce sont elles qui font qu'un deck ressemble aux decks de la
maison plutôt qu'à un deck correct fait ailleurs.

Le réflexe par défaut — un titre et des puces — gaspille tout ce qui fait la
valeur du format. Si un deck fini n'a ni graphique, ni morph, ni mouvement,
c'est le signe que la matière n'a pas été regardée, pas que la matière ne s'y
prêtait pas.

Écrire un fichier `deck_<sujet>.py` qui importe le moteur. **Le moteur ne
connaît aucun contenu, le fichier de deck ne porte aucune géométrie** — pas de
couleur en dur, pas de gouttière recalculée : la couleur est dans la charte, la
gouttière dans `COLS`. Un fichier de deck qui contient un hexadécimal est un
fichier à corriger.

```python
import os, sys                      # $HOME : le skill tourne sur les deux Macs
sys.path.insert(0, os.path.expanduser("~/.claude/skills/presentation/scripts"))
from chartes import charte, COLS
from bento import txt, rect, chart, table, runhead, titre, slide, document, build
from fonts import embarquer

C = charte("mia")
assets, fonts = embarquer(C["embarquer"])
slides = [ … ]
build(document("Titre du deck", C, slides, assets=assets, fonts=fonts),
      "Nom_Du_Deck.bento.html")
```

`build()` télécharge le runtime si le fichier n'existe pas, injecte le document
et lance le contrôle statique — il lève plutôt que de produire un deck cassé en
silence. Les notes orateur ne sont pas optionnelles : elles voyagent dans le
fichier et servent de trame le jour J.

### 3. Contrôler — dans le navigateur, et avec les yeux

Le contrôle statique de `build()` attrape les ids en double, les liens cassés,
les débordements de cadre et la fuite de session. Il ne voit pas le
débordement de **texte** : la hauteur d'une chaîne à une largeur et une police
données n'est pas déductible du JSON. Un titre qui passe sur deux lignes mange
la rangée en dessous, et rien ne le signale.

Ouvrir le fichier, puis dans la console :

```js
const v = window.bento.validate()
v.findings.filter(f => f.severity !== 'info')
```

Corriger, régénérer, relancer jusqu'à zéro `warning`. Sur un deck de onze
slides, ce contrôle a remonté dix-huit débordements strictement invisibles dans
le JSON — sans lui, le deck partait cassé chez le client.

Deux choses échappent à `validate()` et se voient seulement à l'écran : **la
hauteur d'un tableau** (les rangées en trop sont coupées net, sans le moindre
avertissement, dès qu'une cellule passe sur deux lignes) et **le contraste**.

`rendu_pptx.py` ajoute deux contrôles que le rendu web n'a pas, parce qu'il
mesure le texte avec sa vraie police : le **débordement** d'une boîte, et le
**chevauchement** de deux textes. Ce dernier est le défaut qui échappe à tout le
reste — chaque élément tient dans sa boîte, aucune boîte ne sort du cadre, et
pourtant deux textes se marchent dessus. Passer le rendu PPTX même sur un deck
qui ne partira jamais en PowerPoint est donc un bon réflexe de contrôle.

Puis **regarder chaque slide**. Deux points pratiques :

- Faire la revue **dans l'éditeur**, pas en mode présentation : celui-ci gèle
  ses animations quand l'onglet n'a pas le focus, et les slides paraissent
  vides alors qu'elles ne le sont pas.
- `validate()` dit ce qui est vérifiable. Il ne dit pas si une slide est bonne.
  Un deck que personne n'a regardé n'est pas fini.

#### Le rendu réel — obligatoire dès que le deck sort du poste

L'export scripté de PowerPoint échoue sur macOS (`-9074`, bac à sable) et il ne
faut pas y retourner. **Ce n'est pas un mur** : LibreOffice rend n'importe quel
PPTX, quel que soit ce qui l'a produit. 50 slides en 12 secondes.

```bash
soffice --headless --convert-to pdf --outdir . deck.pptx
pdftoppm -png -r 110 deck.pdf slide          # puis on REGARDE les images
```

⚠ **Vérifier les polices sur le PDF, pas sur la confiance.** LibreOffice ne
résout pas les polices de `~/Library/Fonts` sur macOS, même correctement nommées
et visibles de `fontconfig` : sans correction il rend un deck qui n'est pas le
vôtre, en substituant en silence. Le correctif est une copie, à refaire après
chaque mise à jour de LibreOffice :

```bash
cp ~/Library/Fonts/Inter-*.otf /Applications/LibreOffice.app/Contents/Resources/fonts/truetype/
```

Le détail, y compris la commande qui lit les polices réellement embarquées dans
le PDF, est dans `references/doctrine-deck.md`.

#### Le retour du projeté — avant toute relance qui réimporte

Quand un deck a été importé dans un outil de présentation et qu'on s'apprête à
régénérer, `scripts/retour.py` dit ce que le projeté porte que la source n'a pas.
Sans lui, la relance efface des retouches que personne n'a vues.

```bash
python3 scripts/retour.py projete.pptx source.pptx
```

L'agent exporte le design (MCP : `get-export-formats` puis `export-design` en
`pptx`), le script mesure. Il informe et ne bloque jamais. **Il ne voit que le
texte** : un défaut de mise en page lui est invisible, d'où le rendu réel
ci-dessus. Il faut les deux.

### 4. Publier — seulement si c'était demandé

Lire `references/publication.md` avant. Deux règles y priment.

**Publier une copie read-only**, jamais le fichier de travail. Le document
généré ici est propre, mais l'application forge des identifiants de
collaboration dormants dès la première ouverture-enregistrement — publier le
fichier de travail, c'est distribuer avec le lien la clé qui permet d'écrire
dedans. `document(readonly=True)` produit cette copie : elle démarre en
présentation, sans éditeur.

**Relire les notes orateur** avant de produire cette copie. Elles voyagent dans
le fichier et la vue orateur les affiche : une note de travail du type « point de
débat probable avec X » ou « bloqué côté client » part avec le lien, chez la
personne dont il est question. Les réécrire pour celui qui va lire, puis passer
`notes_publiques=True` — le contrôle refuse un fichier de remise sans cette
déclaration, parce que l'oubli est silencieux et irréversible une fois le lien
transmis.

Ensuite passer la main à `/publier`, qui porte les treize étapes, la signature
du jeton et l'attente du déploiement. Ne rien réimplémenter. Et ne jamais
pousser sans validation explicite : c'est une règle de `/publier`, elle ne se
contourne pas depuis ici.

## Les chartes

Quatre marques, valeurs relevées sur les templates réels et déjà en production
ailleurs — `scripts/chartes.py` en est la source unique.

| Marque | Esprit |
|---|---|
| `mia` | Institutionnel, marine et bleu franc sur fond clair. Sobriété de cabinet. |
| `devprom` | Bleu Prusse et Or Bronze. Montserrat en titre, Inter en corps. |
| `vde` | Bleu nuit, or et sable. Titres en Cormorant, le serif porte le haut de gamme. |
| `neutre` | Aucune marque, aucun logo, pile système. Pour ce qui ne doit engager personne. |

Une charte qui évolue évolue **dans `chartes.py`**, et tous les decks suivants
en héritent. Une marque nouvelle s'y ajoute. Recopier une couleur dans un
fichier de deck, c'est créer une seconde vérité qui divergera.

L'échelle typographique dérive de celle relevée sur le template Mister IA,
convertie en pixels. Son plancher de 16 px n'est pas cosmétique : sous ce
seuil, c'est illisible au fond d'une salle — et rétrécir le corps pour faire
tenir du texte traite le symptôme. C'est le contenu qu'il faut couper.

Les polices sont **embarquées** dans le document (`scripts/fonts.py`), jamais
seulement nommées. Une police absente retombe en silence sur la suivante, et le
piège est qu'elle paraîtra correcte sur la machine de celui qui compose,
puisqu'il l'a installée. Le destinataire, lui, voit du Helvetica.

## Non-négociables

- **Ne jamais publier un fichier de travail.** Copie read-only, sans exception.
  Les identifiants de session voyagent dans le fichier et rien ne les distingue
  du reste du document.
- **Ne jamais pousser sur `main` sans validation explicite** — règle de
  `/publier`, valable ici aussi.
- **Ne jamais produire de deck sur une matière non lue.** Les chiffres d'un
  deck sont vérifiables par l'auditoire.
- **Ne jamais livrer un deck sans l'avoir ouvert et parcouru.**
- **Ne pas produire ici ce qui doit finir en PPTX** — voir Routage.

## Fichiers du skill

- `scripts/chartes.py` — les quatre chartes, l'échelle, la grille. Source unique.
- `scripts/temoin.py` — deck-témoin de quatre slides sur contenu factice, qui
  exerce chaque rôle de couleur et chaque famille de la charte :
  `python3 temoin.py <marque>`. À passer sur toute charte nouvelle ou modifiée —
  une police absente, un contraste trop faible ou des chiffres de style ancien
  ne se voient qu'à l'écran.
- `scripts/bento.py` — helpers d'éléments, composition, injection, contrôle
  statique. Ne connaît aucun contenu.
- `scripts/rendu_pptx.py` — second rendu : document → .pptx en formes natives,
  avec ses règles de dégradation et son contrôle de géométrie. En tête du
  fichier, le tableau de ce qui se perd et pourquoi.
- `scripts/rendu_html_plat.py` — troisième rendu : document → HTML plat, une
  page par slide, graphiques en SVG. Sert à **voir** ce que le PPTX pose
  (PowerPoint interdit tout export scripté sur macOS) avec `--controle`, et de
  véhicule d'import Canva sans lui — pages annotées, notes orateur comprises.
- `scripts/fonts.py` — polices : woff2 embarqué pour le rendu web, ttf mis en
  cache pour mesurer le rendu PPTX. Même source, deux formats, donc les deux
  rendus découpent le texte à l'identique.

**Le socle partagé — appelé par les autres chaînes, jamais recopié :**

- `scripts/prerequis.py` — ce qui doit être là avant de produire, avec preuve de
  rendu et correction des polices : `--corriger`. À passer sur toute machine neuve.
- `scripts/mesure.py` — ce qu'un texte occupe, mesuré sur le vrai fichier de
  police avant de le poser. `largeur`, `decouper`, `hauteur`, `ajuster`. Porte
  `MARGE_DECOUPE` (3 %, contre la substitution de police au rendu) et
  `MARGE_RENDU` (12 %, l'écart entre ce que la mesure compte et ce que le
  traceur trace). **Ne jamais réimplémenter** : un moteur de mesure qui change
  de résultat déplace toutes les mises en page qu'il a servies.
- `scripts/controle_geo.py` — les quatre défauts de forme : texte plus haut que
  sa boîte, recouvrement sur les deux axes, hors marges, sous le plancher. Les
  bornes sont en fraction de canevas, donc il sert un canevas de 13,333 pouces
  comme un de 20 sans recalibrage.
- `scripts/rendu_flux.py` — le rendu par navigateur, quand le natif refuse :
  capture avec contrôle de débordement à hauteur contrainte, puis emballage en
  PPTX au canevas voulu (ou lu d'un deck existant). Refuse une image hors format.
- `scripts/retour.py` — l'écart entre le fichier projeté et la source.

- `references/doctrine-deck.md` — **la norme de fabrication**, toutes marques et
  tous véhicules. Critère de rendu, règles payées en production, vérification
  visuelle, retour du projeté, rejeu à froid.
- `references/format-bento.md` — le format, la table matière→forme, et les
  défauts payés en production. À lire avant de composer le premier deck.
- `references/composition.md` — les règles esthétiques relevées sur le template
  de restitution Mister IA, mesures à l'appui. À lire avec la précédente.
- `references/publication.md` — copie read-only et passage de relais à
  `/publier`. À lire avant toute publication.

Pour le schéma exhaustif du format, récupérer `https://bento.page/agents.md` —
c'est la source à jour ; `references/format-bento.md` en porte l'essentiel plus
ce qu'elle ne dit pas.
