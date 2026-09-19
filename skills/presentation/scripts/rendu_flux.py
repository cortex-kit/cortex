#!/usr/bin/env python3
"""rendu_flux.py — le troisième rendu : une page HTML devient une diapo.

Le natif est le rendu par défaut, et il le reste. Celui-ci sert quand le natif
refuse : quand la grille est si dense que le moteur ne peut plus la poser sans
descendre sous le plancher de lisibilité. Le navigateur sait faire ce que
PowerPoint ne sait pas — flexbox, grid, hauteur qui s'adapte au contenu.

Le prix est connu et il s'assume : **la sortie est une image**. Le texte n'y est
pas modifiable après import. Deux conséquences opposées :

- **La netteté finale ne vous appartient plus.** Un PPTX ne porte pas de pixels,
  seulement des pouces : rien n'y dit au lecteur quelle finesse préserver, et
  l'outil qui importe rééchantillonne à la sienne. Monter la définition déplace
  le seuil, il ne supprime pas le rééchantillonnage. Constaté sur une production
  réelle : passer de 2× à 3× n'a pas réglé un flou d'import.
- **Mais elle ne peut pas diverger.** Ce qui ne se retouche pas ne s'éloigne pas
  de sa source. Là où la mise en page est le livrable et le texte une donnée,
  c'est le rendu qui protège le mieux.

## Ce que ce module fait, et ne fait pas

Il **capture** et il **emballe**. Il ne compose pas : le HTML vient de l'appelant,
qui connaît sa matière. C'est la frontière qui rend ce module réutilisable — un
moteur de cartographie et un moteur d'annonce n'ont rien en commun sauf ces deux
gestes-là.

## Le contrôle de débordement, et pourquoi il ne va pas de soi

Une diapo est à **hauteur contrainte**. Ce qui dépasse n'est pas signalé par le
navigateur : il est simplement coupé, sans un mot. On mesure donc d'abord la
hauteur NATURELLE du contenu, hauteur libérée, et on refuse la sortie si elle
dépasse. Sans cette passe, le contrôle regarde une image déjà tronquée et la
trouve parfaite.

Et la règle qui s'applique alors est celle du socle : **ce qui déborde, c'est le
contenu qu'on coupe, jamais la police qu'on écrase.**

    from rendu_flux import Flux
    F = Flux()
    F.capturer("page.html", "page.png", 1600, 900)      # diapo contrainte
    F.capturer("haute.html", "haute.png", 1600, hauteur=None)   # page libre
    F.emballer(["p1.png", "p2.png"], "sortie.pptx")
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ImportError:
    sys.exit("Pillow manquant : pip install pillow")

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 16:9 standard de PowerPoint et des outils de présentation. Un canevas
# surdimensionné a le même rapport, donc rien ne signale l'erreur, mais il ne
# s'insère pas dans une présentation ordinaire : le rapport ne suffit pas, la
# taille absolue compte.
CANEVAS = (13.3333, 7.5)
EMU = 914400


class Flux:
    """Capture par navigateur, puis emballage en PPTX.

    `echelle` est le facteur de densité de la capture. 2 suffit : au-delà on
    fabrique des fichiers lourds pour une netteté que l'import ne conservera pas
    de toute façon.
    """

    def __init__(self, chrome=CHROME, echelle=2, seuil_blanc=6):
        self.chrome = chrome
        self.echelle = echelle
        self.seuil_blanc = seuil_blanc
        if not Path(chrome).exists():
            raise SystemExit(f"navigateur introuvable : {chrome}")

    # ─────────────────────────────────────── capture

    def _tirer(self, html, png, largeur, hauteur):
        subprocess.run(
            [self.chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={self.echelle}",
             f"--window-size={largeur},{hauteur}",
             f"--screenshot={Path(png).resolve()}",
             "--default-background-color=FFFFFFFF",
             f"file://{Path(html).resolve()}"],
            check=True, capture_output=True)

    def _bas_du_contenu(self, png):
        """Où s'arrête l'encre, en points de la page d'origine.

        On compare au pixel du coin, pas au blanc pur : une page sur fond crème
        ou sur fond sombre se mesure aussi bien.
        """
        with Image.open(png) as im:
            im = im.convert("RGB")
            fond = Image.new("RGB", im.size, im.getpixel((2, 2)))
            boite = (ImageChops.difference(im, fond).convert("L")
                     .point(lambda v: 255 if v > self.seuil_blanc else 0).getbbox())
            return ((boite[3] + boite[1]) // self.echelle) if boite else 0

    def hauteur_naturelle(self, html, largeur, hauteur_mesure=2400):
        """Ce que le contenu réclame vraiment, contrainte de hauteur levée.

        Les deux substitutions sont volontairement séparées : `height` et
        `overflow` ne se touchent pas dans la même règle CSS, et les remplacer
        d'un seul coup rate l'une des deux selon la feuille de style.
        """
        source = Path(html).read_text(encoding="utf-8")
        libre = re.sub(r"height\s*:\s*\d+px", "height:auto", source)
        libre = re.sub(r"overflow\s*:\s*hidden", "overflow:visible", libre)
        with tempfile.TemporaryDirectory() as d:
            tmp_html = Path(d) / "mesure.html"
            tmp_png = Path(d) / "mesure.png"
            tmp_html.write_text(libre, encoding="utf-8")
            # La feuille de style peut être relative : on mesure sur place.
            voisin = Path(html).parent / ".mesure-flux.html"
            voisin.write_text(libre, encoding="utf-8")
            try:
                self._tirer(voisin, tmp_png, largeur, hauteur_mesure)
                return self._bas_du_contenu(tmp_png)
            finally:
                voisin.unlink(missing_ok=True)

    def capturer(self, html, png, largeur, hauteur=None, rogner=True):
        """Capture une page.

        `hauteur=None` pour une page haute, à hauteur libre : on tire large puis
        on rogne le blanc de queue. Une hauteur donnée signifie diapo contrainte :
        on mesure d'abord ce que le contenu réclame et on le dit.

        Rend `(largeur_px, hauteur_px, hauteur_reclamee)`. `hauteur_reclamee` est
        `None` pour une page libre, un nombre de points sinon — à comparer par
        l'appelant à la hauteur disponible.
        """
        if hauteur is None:
            self._tirer(html, png, largeur, 4000)
            if rogner:
                bas = self._bas_du_contenu(png)
                with Image.open(png) as im:
                    im = im.crop((0, 0, im.width,
                                  min(im.height, bas * self.echelle)))
                    im.save(png)
            with Image.open(png) as im:
                return im.width, im.height, None

        reclamee = self.hauteur_naturelle(html, largeur)
        self._tirer(html, png, largeur, hauteur)
        with Image.open(png) as im:
            return im.width, im.height, reclamee

    # ─────────────────────────────────────── emballage

    def emballer(self, pngs, sortie, canevas=CANEVAS, modele=None,
                 tolerance=0.002):
        """Pose chaque image en pleine page dans un PPTX.

        `modele` : un PPTX dont on reprend le canevas au lieu de le recopier de
        mémoire. C'est ce qui garantit qu'une page produite ici s'insère au
        caractère près dans un deck existant.

        **Refuse une image hors format.** Une image au mauvais rapport se poserait
        avec une bande blanche ou un recadrage, et personne ne le verrait avant
        l'import.
        """
        from pptx import Presentation
        from pptx.util import Emu

        if modele:
            source = Presentation(str(modele))
            largeur, hauteur = source.slide_width, source.slide_height
        else:
            largeur, hauteur = (Emu(round(canevas[0] * EMU)),
                                Emu(round(canevas[1] * EMU)))

        prs = Presentation()
        prs.slide_width, prs.slide_height = largeur, hauteur
        vierge = prs.slide_layouts[6]          # disposition vide, aucun cadre

        rapport_cible = largeur / hauteur
        for png in pngs:
            chemin = Path(png)
            if not chemin.exists():
                raise SystemExit(f"{chemin.name} absent — capturer d'abord")
            with Image.open(chemin) as im:
                if abs(im.width / im.height - rapport_cible) > tolerance:
                    raise SystemExit(
                        f"{chemin.name} est en {im.width}×{im.height}, hors du "
                        f"format demandé ({rapport_cible:.4f}). Une image au "
                        f"mauvais rapport se pose avec une bande ou un recadrage.")
            s = prs.slides.add_slide(vierge)
            s.shapes.add_picture(str(chemin), Emu(0), Emu(0),
                                 width=largeur, height=hauteur)

        prs.save(str(sortie))
        return len(pngs), largeur / EMU, hauteur / EMU


def rapport(flux, pages, largeur, hauteur):
    """Capture une série de diapos contraintes et dit ce qui déborde.

    Rend le nombre de pages en débordement, pour un code de sortie. Zéro est la
    seule valeur acceptable : une diapo qui déborde est coupée en silence.
    """
    deborde = 0
    for html, png in pages:
        w, h, reclamee = flux.capturer(html, png, largeur, hauteur)
        if reclamee and reclamee > hauteur:
            print(f"  ⚠ {Path(html).stem}  contenu {reclamee} pt pour {hauteur} "
                  f"disponibles — COUPER DU CONTENU, pas la police")
            deborde += 1
        else:
            print(f"  ✅ {Path(html).stem}  contenu {reclamee} pt sur {hauteur} "
                  f"· {w}×{h}")
    return deborde
