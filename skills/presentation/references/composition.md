# Composer une slide — règles relevées, pas inventées

Ce fichier vient d'un audit du template de restitution Mister IA que `claudia-6`
clone : 137 slides, 1920 × 1080, analysées run par run. Ce ne sont donc pas des
principes de design généraux mais **les décisions réellement prises** dans un
deck qui est passé devant des clients — avec, quand c'est mesurable, la mesure.

Un deck qui suit ces règles ressemble aux decks de la maison. Un deck qui les
ignore fait « fait ailleurs », même quand ses couleurs sont bonnes.

## Table

1. [Le titre porte le message](#le-titre-porte-le-message)
2. [Une couleur, un emploi](#une-couleur-un-emploi)
3. [Les petites tailles sont des étiquettes](#les-petites-tailles-sont-des-étiquettes)
4. [Le gras est la règle, pas l'exception](#le-gras-est-la-règle-pas-lexception)
5. [Le chiffre qui est la slide](#le-chiffre-qui-est-la-slide)
6. [Une série descend la gradation](#une-série-descend-la-gradation)
7. [Ce qu'on ne fait jamais](#ce-quon-ne-fait-jamais)

## Le titre porte le message

Règle reprise mot pour mot de `claudia-6`, parce qu'elle est la plus rentable du
lot : **on doit comprendre la slide en lisant son seul titre**, sans regarder le
contenu.

- Oui : « Trois irritants concentrent l'essentiel du temps perdu », « La
  production des reportings coûte 3 à 4 h par semaine », « Claude couvre 100 %
  des cas d'usage identifiés ».
- Non : « Votre réalité aujourd'hui », « Plongée au cœur de vos données », « Cap
  sur demain ». Ces titres-là décorent, ils ne disent rien.

Phrase courte, affirmative, qui porte le message ou le chiffre clé. Pas de
superlatif, pas de jeu de mots, pas de ponctuation gadget. Un titre repris tel
quel d'un plan ou d'un intitulé générique est presque toujours à reformuler.

C'est aussi ce qui rend un deck lisible sans son orateur — et un deck web
transmissible par lien sera souvent lu sans orateur.

## Une couleur, un emploi

Le relevé est sans ambiguïté : **le titre de slide est de la couleur de titre
dans 100 % des cas** (217 runs à 38 pt, tous en `titre_couleur`). Aucun titre
n'est en accent, aucun n'est en gris. La discipline est là, pas dans la variété.

Les rôles observés, désormais dans la charte :

| Rôle | Emploi relevé |
|---|---|
| `titre_couleur` | tout titre de slide, sans exception |
| `titre_variante` | intercalaires de partie, très grands titres de section |
| `accent` | mise en avant ponctuelle — n'apparaît qu'à partir de 20 px |
| `chapitre` | un chapitre entier qui doit se distinguer du reste du deck |
| `encre` | texte courant |
| `annotation` | commentaire, précision — plus discret que le corps, plus lisible qu'une légende |
| `attenue` | légende, mention de bas de slide |

L'accent ne sert jamais de couleur de texte courant. Il marque, il ne compose
pas — c'est ce qui lui garde sa force.

## Les petites tailles sont des étiquettes

Entre 12 et 16 px, **34 à 39 % des textes du template sont en capitales**. Ce
n'est pas du corps rétréci : c'est une fonction distincte — surtitre, rubrique,
étiquette de carte, catégorie.

Un texte courant à cette taille serait sous le plancher de lisibilité de 16 px.
Si du corps se retrouve à 13 px, ce n'est pas un choix typographique, c'est un
symptôme : il y a trop de contenu sur la slide.

Le bandeau de rappel de `bento.py` applique déjà ce motif — 16 px, capitales,
interlettrage ouvert, couleur atténuée.

## Le gras est la règle, pas l'exception

Sur l'ensemble du template, **Inter Bold est employé 7240 fois contre 4892 pour
Inter regular** : environ 60 % du texte est en gras. Un deck entièrement en
graisse normale paraîtra pâle à côté des decks de la maison.

En pratique : titres, chiffres, étiquettes, en-têtes et libellés de carte en
600-700 ; seuls les paragraphes suivis et les légendes restent en 400.

## Le chiffre qui est la slide

Le template pose des chiffres à 195 pt — 176 px sur un canevas de 1280, soit
`echelle["geant"]`. Ce n'est pas un titre agrandi, c'est un objet à part : le
chiffre occupe la slide, le reste le commente.

À réserver au moment où un seul nombre porte tout le propos. Deux chiffres
géants sur la même slide, et ni l'un ni l'autre ne l'est.

## Une série descend la gradation

Pour plusieurs barres, plusieurs jauges, plusieurs niveaux comparés, prendre les
teintes dans l'ordre de `charte["gradation"]` — du plus soutenu au plus pâle.
Elles viennent du template et s'accordent entre elles.

Inventer une couleur par série produit un arc-en-ciel qui n'appartient à aucune
charte. La règle « un accent » ne dit pas « une seule teinte » : elle dit
qu'elles descendent toutes de la même famille.

## Ce qu'on ne fait jamais

Relevé dans les garde-fous de `claudia-6`, et transposable tel quel :

- **Pas de liste en vrac là où des cartes s'imposent.** Une liste de personnes,
  de services, d'items comparables se pose en cartes encadrées. Le texte à puces
  est le réflexe par défaut, et c'est ce qui fait qu'un deck ressemble à un
  document.
- **Pas de logo tiers qui traîne.** Les noms d'outils restent du texte éditable ;
  un logo est un objet de marque qui n'est pas la vôtre.
- **Pas de contenu d'un autre client.** Un composant repris d'un deck précédent
  doit être vidé de ses données avant d'être rempli, jamais laissé « pour
  l'exemple ».
- **Pas de police réduite pour faire tenir le texte.** Le plancher est à 16 px ;
  en dessous, c'est le contenu qu'on coupe. Réduire le corps déplace le problème
  d'un cran et le rend invisible jusqu'à la projection.
