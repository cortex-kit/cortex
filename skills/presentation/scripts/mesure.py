#!/usr/bin/env python3
"""mesure.py — savoir ce qu'un texte occupe avant de le poser.

C'est la brique que trois moteurs de deck ont réécrite chacun de son côté, et
dont deux se sont passés. Le résultat s'est vu le 30/08/2026 : un pack qui posait
0,72 pouce pour un titre qui en réclamait 0,73, et trois diapos sur quatre parties
avec un texte barré par un filet. Le contrôle qui l'aurait vu existait à côté.

Elle vient de `_pack-deck/pack.py`, où elle a été calibrée en production sur un
deck de cinquante slides, et elle en garde les valeurs au chiffre près. Rien n'a
été « amélioré » au passage : un moteur de mesure qui change de résultat déplace
toutes les mises en page qu'il a servies.

## Le principe

**On mesure avant de poser, jamais après.** `ajuster()` rend la plus grande taille
qui tient dans la boîte. Si même la taille minimale déborde, elle le dit : c'est
alors le CONTENU qu'on coupe, jamais la police qu'on écrase en silence.

## Ce qui n'est pas ici

La conversion en fraction de canevas. Elle dépend du canevas, donc du moteur qui
appelle, et elle reste chez lui.

    from mesure import Police
    P = Police("Inter")
    P.hauteur("un titre un peu long", 23, largeur_in=6.6, interligne=1.14)
    P.ajuster("un titre un peu long", 6.6, 0.72, 23, taille_min=17)
"""

from pathlib import Path

from PIL import ImageFont

# Taille de rastérisation de référence. PIL ne charge que des tailles entières :
# mesurer un texte de 16,5 pt en chargeant la police à 16 sous-estime sa largeur
# d'environ 3 %, assez pour qu'une ligne de plus apparaisse au rendu et déborde en
# silence. Comme `ajuster()` rend des demi-points, le défaut touchait la majorité
# des textes adaptatifs. On mesure haut, puis on met à l'échelle.
REF = 256

# Marge de sécurité de la découpe. Relevée le 21/08/2026 en production.
#
# Le moteur mesure avec sa police à sa résolution, et déclare que le texte tient.
# Il tient, chez nous. Une ligne à 7,479 pouce dans une boîte de 7,482 tient par
# deux dixièmes de point ; la même chaîne mesurée à une autre résolution de
# rastérisation donne 7,491, soit deux lignes et un débordement entier.
#
# Le seuil ne couvre pas le bruit de l'instrument, qui ne vaut que 0,25 % sur
# quatre résolutions testées. Il couvre le vrai risque : une SUBSTITUTION de
# police au rendu, dont les chasses s'écartent de un à trois pour cent sur du
# texte mélangé. C'est ce qui arrive quand le poste qui projette n'a pas la police.
#
# Balayage sur un deck réel, et le résultat est contre-intuitif : élargir la marge
# ne coûte rien, parce qu'un composant bien écrit dimensionne sa boîte sur son
# contenu. Plus de lignes prévues donne des blocs plus hauts, donc des slides plus
# pleines, pas plus vides.
#
#   marge   plancher toléré   blocs sous 2 %   slides courtes
#   1,0 %        1,20 %              6              10
#   2,0 %        2,27 %              0              10
#   3,0 %        3,16 %              0               9
#   4,0 %        4,65 %              0               9
#
# Retenu : 3 %. Au-delà on réserve de la place pour un écart qui ne viendra pas.
# Le sens du compromis est assumé : mieux vaut une ligne prévue qui ne vient pas
# qu'une ligne qui vient sans être prévue. La première laisse un blanc, la seconde
# déborde.
MARGE_DECOUPE = 0.030

# Écart entre ce que la mesure compte et ce que le moteur trace. La mesure compte
# taille × interligne × lignes ; le traceur ajoute de quoi loger les jambages et
# arrondit ses lignes de base. Mesuré le 30/08/2026 au rendu réel : à coefficient
# 1,00 avec un jeu de 0,05 pouce, un filet soulignait encore le bas d'un titre.
# La charte `upted-pptx-style` pose la même majoration pour la même raison, sur
# une chaîne indépendante.
#
# Il ne s'applique PAS automatiquement : un moteur déjà calibré verrait toutes ses
# mises en page bouger. À utiliser explicitement quand on pose un budget vertical.
MARGE_RENDU = 1.12

# Les familles connues, et où trouver leurs fichiers. Une famille absente d'ici se
# déclare par `fichiers=` plutôt que par une copie de ce module.
FAMILLES = {
    "Inter": (Path.home() / "Library" / "Fonts", {
        (False, False): "Inter-Regular.otf",
        (True, False): "Inter-Bold.otf",
        (False, True): "Inter-Italic.otf",
        (True, True): "Inter-Bold.otf",
    }),
    "Georgia": (Path("/System/Library/Fonts/Supplemental"), {
        (False, False): "Georgia.ttf",
        (True, False): "Georgia Bold.ttf",
        (False, True): "Georgia Italic.ttf",
        (True, True): "Georgia Bold Italic.ttf",
    }),
}


class Police:
    """Un mesureur pour une famille. Le cache est par instance, pas global.

    Deux familles se comportent différemment à taille égale : une mise en page qui
    tient dans l'une peut déborder dans l'autre. C'est la raison pour laquelle le
    mesureur porte sa famille au lieu de la recevoir à chaque appel.
    """

    def __init__(self, famille="Inter", dossier=None, fichiers=None,
                 marge_decoupe=MARGE_DECOUPE):
        if fichiers is None:
            if famille not in FAMILLES:
                raise SystemExit(
                    f"famille inconnue : {famille!r}. Attendu l'une de "
                    f"{tuple(FAMILLES)}, ou passer `dossier=` et `fichiers=`. "
                    f"Une famille nouvelle se déclare dans FAMILLES, jamais en dur "
                    f"chez l'appelant.")
            dossier, fichiers = FAMILLES[famille]
        self.famille = famille
        self.dossier = Path(dossier)
        self.fichiers = fichiers
        self.marge_decoupe = marge_decoupe
        self._cache = {}

    def fichier(self, gras=False, italique=False):
        return self.dossier / self.fichiers[(bool(gras), bool(italique))]

    def _charge(self, taille_pt, gras=False, italique=False):
        """La police à `taille_pt` : les longueurs PIL sont alors en points."""
        chemin = self.fichier(gras, italique)
        cle = (str(chemin), round(taille_pt))
        if cle not in self._cache:
            self._cache[cle] = ImageFont.truetype(str(chemin),
                                                  max(1, round(taille_pt)))
        return self._cache[cle]

    def largeur(self, texte, taille_pt, gras=False, italique=False):
        """Largeur en pouces, exacte à la demi-taille près."""
        f = self._charge(REF, gras, italique)
        return f.getlength(texte) / 72.0 * taille_pt / REF

    def decouper(self, texte, taille_pt, largeur_in, gras=False, italique=False):
        """Découpe en lignes comme le fera le moteur, marge de sécurité comprise."""
        utile = largeur_in * (1 - self.marge_decoupe)
        lignes = []
        for paragraphe in texte.split("\n"):
            courante = ""
            for mot in paragraphe.split():
                essai = (courante + " " + mot).strip()
                if self.largeur(essai, taille_pt, gras, italique) <= utile \
                        or not courante:
                    courante = essai
                else:
                    lignes.append(courante)
                    courante = mot
            lignes.append(courante)
        return lignes

    def hauteur(self, texte, taille_pt, largeur_in, interligne=1.28,
                gras=False, italique=False):
        """Hauteur occupée, en pouces."""
        n = len(self.decouper(texte, taille_pt, largeur_in, gras, italique))
        return n * taille_pt * interligne / 72.0

    def ajuster(self, texte, largeur_in, hauteur_in, taille_base, taille_min=None,
                interligne=1.28, gras=False, italique=False):
        """La plus grande taille ≤ `taille_base` qui tient dans la boîte.

        Rend `(taille, tient)`. `tient` à False signifie que même la taille
        minimale déborde : c'est alors le contenu qu'il faut couper, jamais la
        police qu'il faut écraser. L'appelant qui ignore ce booléen annule
        l'intérêt de la fonction.
        """
        taille_min = taille_min or max(9, taille_base * 0.62)
        t = taille_base
        while t >= taille_min:
            if self.hauteur(texte, t, largeur_in, interligne,
                            gras, italique) <= hauteur_in:
                return t, True
            t -= 0.5
        return taille_min, False
