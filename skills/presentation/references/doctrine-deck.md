# Fabrication d'un deck, de la source au projeté

Norme de fabrication, toutes marques et tous véhicules. Elle ne dépend d'aucune mission :
les mesures qui l'établissent viennent de la production, les règles valent partout.

Publiée sur Notion, sous « Process d'audit IA — 5 phases » :
https://app.notion.com/p/3cc0ef92eb038194b9a3d15a6ea593f1
Les deux disent la même chose ; **celle-ci fait foi**, la page Notion est la surface
de partage. Une correction se fait ici, puis se republie là-bas.

---

## Le principe

**Une saisie, plusieurs rendus, aucune reprise en aval.**

Le contenu existe à un endroit et un seul. Le deck, la page web, le document projeté n'en sont
que des rendus. Un rendu ne se corrige jamais sur lui-même : on corrige la saisie et on relance.

La règle est ancienne et elle est juste. Ce qui lui manquait, c'est de quoi la constater.

### Pourquoi elle ne tenait pas

Trois mesures, prises sur une production réelle le 30/08/2026.

**Le fichier projeté avait divergé de sa source sans que personne le voie.** Sur 48 pages
appariables entre un design retouché dans l'outil de présentation et le PPTX qui l'avait produit,
7 étaient identiques au caractère près. 41 portaient 192 segments modifiés : 126 conversions de
nombres écrits en lettres vers des chiffres, 35 suppressions, 28 réécritures, 3 ajouts. Certaines
réécritures touchaient le propos. Une relance suivie d'un réimport les aurait toutes effacées.

**Le livrable avait divergé de ses propres scripts.** Le fichier remis ne se reproduisait depuis
aucun état du code, ni le dépôt ni le répertoire de travail. Neuf slides différaient.

**Les moteurs, eux, étaient sains.** Deux exécutions donnaient zéro écart, les assertions de
non-régression passaient. Le défaut n'est jamais venu du code.

**Conclusion opératoire.** Une règle de source unique qui repose sur la discipline se rompt sans
bruit. Elle tient quand un outil la constate.

---

## Les quatre étages

| Étage | Ce qu'il porte | Où |
|---|---|---|
| **Charte** | Marques, couleurs, polices, échelle, colonnes | `presentation/scripts/chartes.py` |
| **Moteur** | La mesure, les primitives, les rendus, les contrôles, le retour | `presentation/scripts/` |
| **Composants** | Les objets métier d'un profil de livrable | Un skill par profil |
| **Contenu** | Les slides d'une mission | Le pack de la mission |

**On lit chez le voisin, on l'appelle, on ne le réécrit jamais.**

### Le mode de panne, nommé une fois pour toutes

**« Dans l'esprit de » est le mode de panne.** Un moteur qui réécrit le contrôle du voisin au
lieu de l'appeler reproduit le défaut que le voisin avait déjà payé.

Démonstration, sur un troisième moteur écrit le 30/08/2026. Il portait son contrôle géométrique
« dans l'esprit de » celui du moteur principal. Le sien mesurait les boîtes, l'autre mesurait
aussi le texte dans les boîtes. Résultat : contrôle au vert, et **trois diapos sur quatre
partaient avec un défaut visible** — deux titres barrés par un filet, deux blocs chevauchant une
ligne de pied. Le contrôle qui les attrape existait à côté depuis dix jours.

La correction n'a pas consisté à améliorer le contrôle maison : le moteur importe le socle et
mesure avec lui. Onze lignes.

Le même refactoring, appliqué au moteur principal, a été **prouvé neutre** : 400 mesures croisées
sans écart, puis un deck de 50 slides régénéré avant et après avec la même empreinte de géométrie
et de texte. Un déplacement de code qui change un rendu n'est pas un déplacement, c'est une
régression.

---

## Le critère de choix du rendu

**La géométrie tranche, elle est mesurée, elle ne se discute pas.**

| Rendu | Sortie | Quand |
|---|---|---|
| **Natif** | Formes PPTX éditables | Par défaut |
| **Flux** | HTML rendu en image, emballé en PPTX | Quand le natif refuse |
| **Web** | Page autoportante | Quand le livrable se transmet par lien |

Le natif refuse dans deux cas, et l'outil le dit lui-même :

1. `ajuster()` descend sous le plancher de lisibilité et rend `tient = False`.
2. Le contrôle de débordement échoue à hauteur contrainte.

Le critère a tranché seul sur les deux cas réels : une grille de 38 étapes réclamait 1148 points
pour 900 disponibles, refus et bascule en flux ; des diapos d'annonce ne faisaient refuser rien,
natif.

**Corollaire : ce qui déborde, c'est le contenu qu'on coupe, jamais la police qu'on écrase.** Une
coupe se déclare sur la page.

### Deux critères écartés, et pourquoi

**Le nombre de formes n'est pas un critère.** Proposé à dix formes par diapo, il se contredit sur
le cas qui l'a fait naître : les diapos concernées en portaient dix-huit et le natif y était le
bon choix. Il pousse en outre à appauvrir une mise en page pour rester sous une barre.

**Et le choix du moteur ne prévient aucun défaut graphique.** Les trois défauts trouvés le
30/08 sont nés en natif, qui était le bon moteur. Ce qui les a laissés passer, c'est un contrôle
qui mesurait les boîtes. **Le levier est le contrôle, jamais le moteur.**

### Ce que la sortie image coûte

**Quand la sortie est une image, la netteté finale n'appartient plus au producteur.** Un PPTX ne
porte pas de pixels, seulement des pouces : rien n'y dit au lecteur quelle finesse préserver, et
l'outil qui importe rééchantillonne à la sienne. Monter la définition de 2× à 3× déplace le seuil
sans supprimer le rééchantillonnage. Cela ne se voit qu'à l'import ; la sortie locale, elle, est
nette.

En contrepartie, une image ne se retouche pas, donc elle ne peut pas diverger. **Le choix du
rendu est aussi un choix de garde-fou** : là où la mise en page est le livrable et le texte une
donnée, le flux protège mieux ; là où le présentateur doit pouvoir reprendre la main, le natif
est nécessaire et le contrôle de retour devient obligatoire.

---

## Le format d'émission

**13,333 × 7,5 pouces**, le 16:9 de PowerPoint et des outils de présentation. Un canevas
surdimensionné est un cas particulier assumé, jamais une référence : il a le même rapport, donc
rien ne signale l'erreur, mais une page de 20 pouces ne s'insère pas dans une présentation
ordinaire. **Le rapport ne suffit pas, la taille absolue compte.**

---

## Les règles de rendu, et ce qu'elles ont coûté

Chacune a été payée par un défaut réel.

**Mesurer avant de poser.** `ajuster()` rend la plus grande taille qui tient. Si même la taille
minimale déborde, elle le dit. Origine : six défauts d'un même moteur, tous de la même famille,
un composant qui se dimensionne sur la place offerte au lieu du contenu réel.

**Chaque composant retourne le bas qu'il occupe réellement**, et l'appelant enchaîne dessus.
Enchaîner sur la hauteur allouée produit des trous béants.

**Un composant se dimensionne sur son contenu**, pas sur la place qu'on lui offre.

**Ancrage haut.** Un bloc centré dans une grande bande flotte au milieu de la slide.

**Formes natives, jamais d'image.** C'est ce qui garde la main après import et ce qui permet au
contrôle de mesurer.

**Aucun pictogramme en Unicode.** Ni émoji, ni flèche, ni triangle. Certains moteurs substituent
une police à couleur fixe et ignorent la couleur demandée, ce qui produit un pictogramme orange
là où la charte demandait autre chose. Les marqueurs se dessinent. **Deux chaînes indépendantes
ont payé ce défaut**, sur des marqueurs de registre et sur des flèches de séquence.

**Le logo se pose en dernier.** Tout élément décoratif posé après lui le recouvre.

**Pas de tiret cadratin.**

**Majorer la mesure de 12 % avant de poser un budget vertical.** La mesure compte
taille × interligne × lignes ; le moteur qui trace ajoute de quoi loger les jambages et arrondit
ses lignes de base. Mesuré au rendu réel : à coefficient 1,00 avec 0,05 pouce de jeu, un filet
soulignait encore le bas d'un titre. `mesure.MARGE_RENDU` porte la valeur. **Elle ne s'applique
pas d'office** : un moteur déjà calibré verrait toutes ses mises en page bouger.

**Un recouvrement se mesure sur les deux axes.** Deux blocs ne se gênent que s'ils se recouvrent
en hauteur **et** en largeur. Un contrôle qui ne teste que la verticale fait sonner toute mise en
page à deux colonnes : première version, 16 alertes dont 16 fausses. Un contrôle qui crie sans
cesse cesse d'être lu.

**Écrire le test avant le correctif.** Un garde-fou qu'on n'a pas vu échouer ne garde rien. Un
moteur a eu pour septième défaut son garde-fou lui-même : la détection de texte sur forme était
posée à 25 % de recouvrement, le défaut d'origine en recouvrait 13 %.

---

## La vérification visuelle

Le contrôle géométrique voit les boîtes, pas le rendu. Six défauts d'affilée y ont échappé et ont
tous été vus à l'œil. **Regarder chaque slide n'est pas une étape qu'on saute.**

**L'export scripté de PowerPoint échoue sur macOS** — erreur `-9074`, bac à sable. Il ne faut pas
y retourner. **Mais ce n'est pas un mur** : LibreOffice rend n'importe quel PPTX sans AppleScript
ni bac à sable. Mesuré : 50 slides en 12 secondes.

```bash
soffice --headless --convert-to pdf --outdir . deck.pptx
pdftoppm -png -r 110 deck.pdf slide          # puis on regarde
```

**La substitution de police est réelle et elle se corrige.** LibreOffice ne résout pas les
polices utilisateur de `~/Library/Fonts` sur macOS, même correctement nommées et visibles de
`fontconfig`. Sans correction, il rend un deck qui n'est pas le vôtre.

```bash
cp ~/Library/Fonts/<Famille>-*.otf /Applications/LibreOffice.app/Contents/Resources/fonts/truetype/
```

À refaire après chaque mise à jour de LibreOffice. **Le contrôle se fait sur le PDF produit**, pas
sur la confiance : les polices réellement embarquées s'y lisent en une seconde.

```bash
python3 -c "import re,collections,sys;d=open(sys.argv[1],'rb').read();\
print(collections.Counter(m.decode().split('+')[-1].split('-')[0] \
for m in re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-,_]+)',d)))" deck.pdf
```

---

## Le retour du projeté

Le maillon qui n'existait pas. Le PPTX partait à l'import, et rien ne comparait ce qui revenait.

`presentation/scripts/retour.py` compare le fichier projeté à la source, page à page, et affiche
l'écart chiffré par famille.

**La frontière est nette : l'agent exporte, le script mesure.** L'export du design passe par un
jeton de session qu'un script isolé n'a pas. Le script prend deux fichiers et ne parle à personne.

**Les pages s'apparient par ressemblance, jamais par rang.** Un deck retouché gagne et perd des
pages ; comparer rang à rang donne 48 divergences là où il y en a 41 et noie le signal.

**Les quatre familles ne se valent pas.** Une conversion de nombre est une décision de style, une
réécriture change ce que le lecteur lit. Le total seul ne dit rien.

**Il informe et ne bloque pas.** Un garde-fou qui immobilise une production un jour de rush finit
contourné, et c'est un rush qui produit les retouches. Ce qu'on lui demande, c'est que personne ne
puisse dire qu'il ne savait pas.

**À lancer à deux moments** : avant toute relance qui va réimporter, et avant toute séance.

**Ce qu'il ne voit pas** : la géométrie. Passé sur une version défectueuse et sa correction, il
rend « identiques au caractère près ». Il répond à « quelqu'un a-t-il changé ce qui est écrit »,
le rendu réel répond à « est-ce que ça se voit correctement ». **Il faut les deux.**

---

## Rejouer à froid, six mois plus tard

**Les prérequis se vérifient avant de produire.**

```bash
python3 -c "import pptx, PIL; print('ok')"
fc-list : family | tr ',' '\n' | grep -ix <police>
ls /Applications/LibreOffice.app/Contents/Resources/fonts/truetype/<police>-Regular.otf
```

La troisième ligne est celle qu'on oublie. Une police installée pour le système ne suffit pas.

**Le contrôle tourne avant le contenu.** Un contrôle qu'on n'a pas vu réussir ne prouve rien.

**Le pack porte son état sous git**, et l'état de livraison est commité. C'est ce qui permet de
répondre à « le livrable correspond-il au code ». Sans lui, la question n'a pas de réponse.

**Un prompt de reprise périmé est plus dangereux qu'aucun prompt** : il se lit comme valide.
Il s'archive dès qu'il devient faux.

**Ce qui reste en place se lit comme valide.** C'est la raison de purger.
