#!/usr/bin/env python3
"""controle_geo.py — les défauts de forme qu'aucun œil ne rattrape seul.

Ce fichier existe parce que le même contrôle avait été écrit trois fois, et que
les trois versions ne savaient pas les mêmes choses. Le 30/08/2026, la plus
récente a été écrite « dans l'esprit de » la plus ancienne : elle mesurait les
BOÎTES quand l'autre mesurait aussi le TEXTE dedans. Elle est sortie au vert
pendant que trois diapos sur quatre partaient avec un titre barré par un filet.

**« Dans l'esprit de » est le mode de panne.** On appelle, on ne réécrit pas.

Le code vient de la version mûre, celle d'un pack de production calibré sur un
deck de cinquante slides. Il n'a pas été simplifié au passage : ses exclusions et
ses seuils ont chacun été payés par un faux positif ou par un défaut passé.

## Les cinq mesures

**Texte plus haut que sa boîte.** Le défaut le plus fréquent et le plus
invisible : la boîte reste en place, seul son contenu déborde. Demande un
mesureur, parce qu'une hauteur de texte ne se déduit pas du fichier.

**Sous la ligne de pied**, **hors marges**, **hors canevas.** Les trois qui se
déduisent du fichier seul.

**Chevauchement de deux textes.** Chaque élément tient dans sa boîte, aucune
boîte ne sort du cadre, et pourtant deux textes se marchent dessus.

**Texte illisible sur une forme pleine.** L'angle mort qui a laissé passer un
libellé sous sa pastille : il ne chevauchait aucun autre texte, il disparaissait
sous un cercle. Le seuil de recouvrement est volontairement bas, c'est le
contraste qui filtre, pas la surface.

## Les exclusions, et pourquoi chacune

Un contrôle qui crie sans cesse cesse d'être lu. Sont donc exemptés :

- **Ce qui est pleine largeur ou pleine hauteur par construction** : fond de
  slide, filet supérieur, filet d'accent vertical. Ils sortent des marges
  volontairement.
- **Ce qui commence dans la bande de pied** : c'est du chrome. L'exemption ne
  porte que sur ce qui y COMMENCE ; un bloc de contenu qui y descend depuis
  au-dessus reste signalé.
- **Un écart plus fin que ce que l'outil sait corriger.** Le quantum vaut un
  demi-point de corps. En deçà, signaler un débordement reviendrait à demander
  une correction plus fine que la résolution de celui qui doit la faire.

## Ce qu'il ne voit pas

Le contraste global, l'équilibre, un mot de trop. Il attrape ce qui se mesure ;
**il ne dit jamais qu'une diapo est bonne.** Le rendu réel reste obligatoire.

    from controle_geo import Cadre
    C = Cadre(mesureur=pack, bas=0.930, marge=0.055, pied=0.935)
    defauts, n = C.verifier("deck.pptx")
"""

EMU = 914400


def _luminance(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _texte(sh):
    return sh.has_text_frame and sh.text_frame.text.strip()


def _fond(sh):
    """Couleur de remplissage unie d'une forme, ou None."""
    try:
        if sh.fill.type == 1:
            return str(sh.fill.fore_color.rgb)
    except Exception:
        pass
    return None


def _couleur_texte(sh):
    try:
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.color and r.font.color.rgb:
                    return str(r.font.color.rgb)
    except Exception:
        pass
    return None


def _nom(sh):
    return (sh.text_frame.text.strip().split("\n")[0][:40]
            if _texte(sh) else "forme")


class Cadre:
    """Le gabarit d'une diapo, et ce qu'on y vérifie.

    Les bornes sont en **fraction du canevas**, jamais en pouces : c'est ce qui
    permet au même contrôle de servir un canevas de 13,333 pouces et un de 20
    sans recalibrage. La version qui codait ses marges en dur ne servait qu'un
    moteur, et c'est une des raisons pour lesquelles les autres l'ont réécrite.

    `mesureur` expose `hauteur(texte, taille_pt, largeur_in, interligne, gras,
    italique, serif)` et, si possible, `largeur(...)` pour la sonde de police.
    `police_serif` nomme la famille à traiter comme serif, s'il y en a une.
    """

    def __init__(self, mesureur=None, bas=1.0, marge=0.0, pied=1.0,
                 police_serif=None, quantum_pt=0.5, interligne_defaut=1.28,
                 recouvrement_texte=0.006, recouvrement_forme=0.004,
                 part_min_forme=0.03, contraste_min=0.45,
                 marge_rendu=None):
        self.mesureur = mesureur
        self.bas = bas
        self.marge = marge
        self.pied = pied
        self.police_serif = police_serif
        self.quantum_pt = quantum_pt
        self.interligne_defaut = interligne_defaut
        self.recouvrement_texte = recouvrement_texte
        self.recouvrement_forme = recouvrement_forme
        self.part_min_forme = part_min_forme
        self.contraste_min = contraste_min
        if marge_rendu is None:
            from mesure import MARGE_RENDU
            marge_rendu = MARGE_RENDU
        self.marge_rendu = marge_rendu

    # ─────────────────────────────────────── mesure de l'encre

    def _hauteur_texte(self, sh, H):
        """Hauteur d'ENCRE d'une zone de texte, en fraction de la hauteur.

        C'est la mesure qui manque à tout contrôle naïf : il compare des boîtes
        et jamais l'encre. Une boîte dont la hauteur a été posée à la main peut
        être plus petite que son texte ; le texte en sort par le bas et la
        géométrie reste verte, parce que la boîte, elle, est à sa place.

        On mesure paragraphe par paragraphe, avec la fonction qui sert à poser :
        contrôler avec un autre instrument que celui qui pose reviendrait à
        comparer deux mesures qui ne mesurent pas la même chose.
        """
        largeur_in = (sh.width or 0) / EMU
        if largeur_in <= 0:
            return None
        paras = [p for p in sh.text_frame.paragraphs if list(p.runs)]
        total = 0.0
        for rang, p in enumerate(paras):
            runs = list(p.runs)
            r = runs[0]
            serif = bool(self.police_serif) and (r.font.name or "") == self.police_serif
            total += self.mesureur.hauteur(
                "".join(x.text for x in runs),
                r.font.size.pt if r.font.size else 12,
                largeur_in,
                p.line_spacing or self.interligne_defaut,
                gras=bool(r.font.bold), italique=bool(r.font.italic),
                serif=serif)
            # L'espacement après le DERNIER paragraphe ne pose pas d'encre :
            # le compter fabriquerait des débordements qui ne se voient nulle part.
            if p.space_after and rang < len(paras) - 1:
                total += p.space_after.pt / 72.0
        return total / (H / EMU)

    def _sonde(self, defauts):
        """La police se charge-t-elle vraiment ?

        Importer un mesureur ne prouve rien : les fichiers de police ne se
        chargent qu'à la première mesure. Sans police, c'est ici que ça tombe,
        et pas au milieu de cinquante slides.
        """
        if self.mesureur is None:
            return False
        try:
            self.mesureur.largeur("sonde", 12)
            return True
        except Exception as e:
            defauts.append((0, "mesure du texte indisponible",
                            f"{type(e).__name__}: {e}. Le contrôle des boîtes "
                            "tourne, celui de l'encre non : ne pas lire ce "
                            "passage comme un feu vert"))
            return False

    # ─────────────────────────────────────── le contrôle

    def verifier(self, source):
        """`source` : un chemin de PPTX ou une Presentation déjà ouverte.

        Rend `(defauts, nombre_de_diapos)`. Chaque défaut est
        `(numero_de_diapo, genre, detail)`.
        """
        from pptx import Presentation
        prs = source if hasattr(source, "slides") else Presentation(str(source))
        W, H = prs.slide_width, prs.slide_height
        defauts = []
        mesurable = self._sonde(defauts)
        quantum = (self.quantum_pt * self.interligne_defaut / 72) / (H / EMU)

        for i, s in enumerate(prs.slides, 1):
            boites = [(sh, sh.left / W, sh.top / H,
                       (sh.left + (sh.width or 0)) / W,
                       (sh.top + (sh.height or 0)) / H)
                      for sh in s.shapes
                      if sh.left is not None and sh.top is not None]

            for sh, x1, y1, x2, y2 in boites:
                nom = _nom(sh)
                large = (sh.width or 0) / W >= 0.98
                haute = (sh.height or 0) / H >= 0.98
                # Pleine page par construction : fond, filet supérieur, filet
                # d'accent vertical. Ils sortent des marges volontairement.
                if (large and (haute or y2 <= 0.03)) or (haute and not _texte(sh)):
                    continue
                if y1 >= self.pied:
                    continue                       # bande de pied, chrome assumé

                if mesurable and _texte(sh):
                    encre = self._hauteur_texte(sh, H)
                    boite = y2 - y1
                    if encre is not None and boite > 0 and encre > boite + quantum:
                        defauts.append((i, "texte plus haut que sa boîte",
                                        f"{nom} — {encre / boite:.2f}× "
                                        f"({(encre - boite) * H / EMU:.2f} in de trop)"))
                if y2 > self.bas + 0.002:
                    defauts.append((i, "sous la ligne de pied",
                                    f"{nom} — bas à {y2:.1%}"))
                if x1 < self.marge - 0.002 and not large:
                    defauts.append((i, "hors marge gauche", f"{nom} — {x1:.1%}"))
                if x2 > 1 - self.marge + 0.002 and not large:
                    defauts.append((i, "hors marge droite", f"{nom} — {x2:.1%}"))
                if y1 < -0.001 or y2 > 1.001:
                    defauts.append((i, "hors canevas", nom))

            txts = [b for b in boites if _texte(b[0])]
            for a in range(len(txts)):
                for b in range(a + 1, len(txts)):
                    _, ax1, ay1, ax2, ay2 = txts[a]
                    _, bx1, by1, bx2, by2 = txts[b]
                    ox = min(ax2, bx2) - max(ax1, bx1)
                    oy = min(ay2, by2) - max(ay1, by1)
                    if ox > self.recouvrement_texte and oy > self.recouvrement_texte:
                        na = txts[a][0].text_frame.text.strip().split("\n")[0][:26]
                        nb = txts[b][0].text_frame.text.strip().split("\n")[0][:26]
                        defauts.append((i, "chevauchement", f"« {na} » ∩ « {nb} »"))

            # Texte qui traverse un filet. Cas particulier du suivant, et il lui
            # échappe : un filet gris sous un titre marine a un contraste fort,
            # donc le test de lisibilité le laisse passer. Or un trait qui coupe
            # une ligne de texte est toujours un défaut, quel que soit le
            # contraste — c'est ce qui a barré deux titres sur quatre diapos le
            # 30/08/2026, et ce que le quantum de débordement ne rattrape pas
            # parce que l'excès y valait un centième de la boîte.
            filets = [b for b in boites
                      if not _texte(b[0]) and _fond(b[0])
                      and (b[4] - b[2]) < 0.01 and 0.20 < (b[3] - b[1]) < 0.98]
            if mesurable:
                for tb, tx1, ty1, tx2, ty2 in txts:
                    encre = self._hauteur_texte(tb, H)
                    if encre is None:
                        continue
                    # Majorée : la mesure compte taille × interligne × lignes,
                    # le traceur ajoute de quoi loger les jambages. Sans cette
                    # majoration le test rate d'un millième et le titre part
                    # barré — mesuré, c'est exactement ce qui s'est produit.
                    bas_reel = ty1 + encre * self.marge_rendu
                    # Un texte posé sur une forme pleine qui le porte n'est pas
                    # barré : la forme masque le filet. C'est le cas d'un numéro
                    # dans une pastille de timeline, dont le trait de liaison
                    # passe DERRIÈRE. Sans cette exclusion, une timeline sonne
                    # cinq fois par diapo pour un dessin parfaitement lisible.
                    porte = any(
                        fx1 <= tx1 + 0.002 and fx2 >= tx2 - 0.002
                        and fy1 <= ty1 + 0.002 and fy2 >= ty2 - 0.002
                        for _, fx1, fy1, fx2, fy2 in
                        [b for b in boites if _fond(b[0]) and not _texte(b[0])
                         and (b[3] - b[1]) < 0.98])
                    if porte:
                        continue
                    for fo, fx1, fy1, fx2, fy2 in filets:
                        if min(tx2, fx2) - max(tx1, fx1) <= 0.01:
                            continue
                        # Le texte est barré quand il DESCEND franchement sous le
                        # haut du filet. Affleurer ne barre pas : le vrai défaut
                        # mesuré dépassait de 1,3 point de pourcentage, le faux
                        # positif de 0,2. Le seuil sépare les deux populations.
                        if ty1 < fy1 and bas_reel > fy1 + 0.005:
                            n = tb.text_frame.text.strip().split("\n")[0][:30]
                            defauts.append((i, "texte traversé par un filet",
                                            f"« {n} » descend à {bas_reel:.1%}, "
                                            f"le filet est à {fy1:.1%}"))
                            break

            # Texte posé sur une forme pleine dont il ne peut pas se détacher.
            formes = [b for b in boites if _fond(b[0]) and not _texte(b[0])]
            for tb, tx1, ty1, tx2, ty2 in txts:
                ct = _couleur_texte(tb)
                if not ct:
                    continue
                aire = max(1e-9, (tx2 - tx1) * (ty2 - ty1))
                for fo, fx1, fy1, fx2, fy2 in formes:
                    if (fx2 - fx1) >= 0.98 or (fy2 - fy1) >= 0.98:
                        continue                   # fond de slide, légitime
                    ox = min(tx2, fx2) - max(tx1, fx1)
                    oy = min(ty2, fy2) - max(ty1, fy1)
                    if ox <= self.recouvrement_forme or oy <= self.recouvrement_forme:
                        continue                   # simple contact de bord
                    # Seuil bas assumé : un recouvrement PARTIEL suffit à rendre
                    # une ligne illisible. C'est le contraste qui filtre, pas la
                    # surface — l'inverse laissait passer un libellé mordu par sa
                    # pastille.
                    if (ox * oy) / aire < self.part_min_forme:
                        continue
                    if abs(_luminance(_fond(fo)) - _luminance(ct)) < self.contraste_min:
                        n = tb.text_frame.text.strip().split("\n")[0][:30]
                        defauts.append((i, "texte illisible sur forme",
                                        f"« {n} » sur #{_fond(fo)} — "
                                        f"{(ox * oy) / aire:.0%} recouvert"))
                        break
        return defauts, len(prs.slides)


def rapport(defauts, titre="CONTRÔLE GÉOMÉTRIQUE"):
    """Affiche le verdict et rend le nombre de défauts, pour un code de sortie."""
    print(f"\n  {titre}")
    if defauts:
        for i, genre, detail in defauts:
            print(f"    ⚠ diapo {i:>2} · {genre} · {detail}")
    else:
        print("    ✅ rien hors marges, rien sous la ligne de pied, aucun texte "
              "plus haut que sa boîte, aucun chevauchement")
    return len(defauts)
