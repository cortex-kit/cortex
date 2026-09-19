#!/usr/bin/env python3
"""Second rendu : un document bento → un fichier .pptx.

Le document JSON est le pivot ; ce module en est le rendu PowerPoint, comme
`bento.py` en est le rendu web. **Une seule source, deux rendus** — jamais deux
saisies. Si le contenu change, il change dans le fichier de deck, et les deux
formats suivent.

    python3 rendu_pptx.py mon-deck.bento.html [sortie.pptx]

Le PPTX sert deux usages : la remise d'un fichier éditable, et l'entrée dans
Canva — qui importe le PowerPoint. D'où la règle que `claudia-bis-4-deck` a
établie avant nous et qu'on reprend telle quelle : **formes natives, jamais
d'image**. Un deck aplati en images n'est plus retouchable, et l'intérêt du
passage par PPTX disparaît.

## Ce qui se dégrade, et comment

PowerPoint n'a pas d'équivalent pour ce qui fait la valeur du format bento. La
dégradation est donc assumée et nommée, jamais silencieuse — `rendre()` retourne
la liste de ce qu'il a perdu, et l'appelant l'affiche.

| En bento | En PPTX | Pourquoi |
|---|---|---|
| slide d'état (`stateOf`) | slide ordinaire insérée après son parent | le détail reste lisible, il perd son repli |
| lien vers une slide | lien PowerPoint vers cette slide | préservé : PowerPoint sait le faire |
| `transition: morph` | rien | les deux slides subsistent, sans le fondu |
| `fx.countUp` | le nombre, posé | il était déjà écrit dans le document |
| ken-burns, motion-path, dash-march | l'état de repos | aucune boucle en PPTX |
| `fx.enter` | rien | l'entrée n'existe pas hors présentation web |
| dégradé | aplat de la couleur dominante | le dégradé PPTX ne se transpose pas fidèlement |
| couleur semi-transparente | composée sur le fond de la slide | PowerPoint n'a pas d'alpha simple sur un fond |
| média (vidéo, audio) | cadre vide légendé | un fichier lié ne survit pas au transport |
| coins arrondis d'une barre de graphique | barres à angle vif | le moteur de graphique PowerPoint ne les expose pas |

Ce tableau est le contrat : rien d'autre ne se perd. Si un rendu perd autre
chose, c'est un défaut, pas une dégradation.

## Ce que le logiciel de destination ajoute de lui-même

Un piège d'une autre nature, relevé à l'import Canva : le fichier peut être
juste et le rendu faux, parce que PowerPoint et Canva appliquent **leur** style
de tableau quand le document en laisse la possibilité. Le banding alterné est
actif par défaut dans python-pptx ; les deux logiciels l'interprètent avec leur
propre habillage et écrasent marges et alignement une ligne sur deux — ce qui
saute aux yeux et ne se voit dans aucun contrôle, puisque le fichier, lui, porte
les bonnes valeurs.

D'où `horz_banding = False` et un zebra peint cellule par cellule. La règle
générale : **ne rien laisser à l'interprétation du logiciel de destination.**
Ce qui n'est pas posé explicitement sera posé par quelqu'un d'autre.
"""

import base64
import html as _html
import io
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation                                    # noqa: E402
from pptx.chart.data import CategoryChartData                    # noqa: E402
from pptx.dml.color import RGBColor                              # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE                        # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                           # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN                  # noqa: E402
from pptx.util import Emu, Pt                                    # noqa: E402
from PIL import ImageFont                                        # noqa: E402

from fonts import fichier_mesurable                              # noqa: E402

# 1280×720 px à 96 dpi = 13,333 × 7,5 pouces : le 16:9 natif de PowerPoint.
# Le mapping est exact, il n'y a aucune approximation à assumer ici.
PX_PAR_POUCE = 96.0
PX_EN_PT = 72.0 / PX_PAR_POUCE          # 0,75
EMU_PAR_POUCE = 914400

_ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
          "right": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
_ANCRE = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
          "center": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}
_TYPE_CHART = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
               "line": XL_CHART_TYPE.LINE_MARKERS,
               "pie": XL_CHART_TYPE.DOUGHNUT,
               "scatter": XL_CHART_TYPE.XY_SCATTER}


# ─── Unités et couleurs ──────────────────────────────────────────────────────

def emu(px):
    return Emu(int(round(px / PX_PAR_POUCE * EMU_PAR_POUCE)))


def pt(px):
    return Pt(px * PX_EN_PT)


def _melange(av, ar, a):
    return tuple(int(round(av[i] * a + ar[i] * (1 - a))) for i in range(3))


def couleur(valeur, fond=(255, 255, 255)):
    """Rend (r, g, b) ou None si la valeur signifie « pas de remplissage ».

    Une couleur semi-transparente est composée sur le fond fourni : PowerPoint
    n'offre pas d'alpha simple sur un remplissage, et un aplat opaque au ton
    juste vaut mieux qu'une transparence perdue.
    """
    if not valeur or valeur in ("none", "transparent"):
        return None
    v = valeur.strip()
    if v.startswith("#"):
        v = v[1:]
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        p = [x.strip() for x in m.group(1).split(",")]
        rgb = tuple(int(float(x)) for x in p[:3])
        a = float(p[3]) if len(p) > 3 else 1.0
        if a <= 0.02:
            return None
        return rgb if a >= 0.98 else _melange(rgb, fond, a)
    return None


def _rgb(t):
    return RGBColor(*t)


def _remplir(forme, rgb):
    if rgb is None:
        forme.fill.background()
    else:
        forme.fill.solid()
        forme.fill.fore_color.rgb = _rgb(rgb)


def _dominante(el, fond):
    """Couleur représentative d'un élément dégradé : le dernier arrêt visible."""
    stops = (el.get("fillGradient") or {}).get("stops") or []
    for s in reversed(stops):
        c = couleur(s.get("color"), fond)
        if c:
            return c
    return couleur(el.get("fill"), fond)


# ─── Texte ───────────────────────────────────────────────────────────────────

_BALISE = re.compile(r"<(/?)(b|strong|i|em|br)\s*/?>", re.I)


def morceaux(html_source):
    """Découpe un html inline en [(texte, gras, italique)], `<br>` → \\n.

    Le document n'accepte qu'un sous-ensemble volontairement pauvre — gras,
    italique, saut de ligne — donc un analyseur complet serait du gâchis. Tout
    autre balisage est retiré plutôt qu'interprété.
    """
    out, gras, ital, pos = [], 0, 0, 0
    for m in _BALISE.finditer(html_source):
        brut = html_source[pos:m.start()]
        if brut:
            out.append((_html.unescape(brut), gras > 0, ital > 0))
        fermante, nom = m.group(1), m.group(2).lower()
        if nom == "br":
            out.append(("\n", gras > 0, ital > 0))
        elif nom in ("b", "strong"):
            gras += -1 if fermante else 1
        else:
            ital += -1 if fermante else 1
        pos = m.end()
    reste = html_source[pos:]
    if reste:
        out.append((_html.unescape(reste), gras > 0, ital > 0))
    return [(re.sub(r"<[^>]+>", "", t), g, i) for t, g, i in out if t]


def texte_nu(html_source):
    return "".join(t for t, _, _ in morceaux(html_source))


_JETON = re.compile(r"\{\{(\w+)(?::(\d+))?\}\}")


def resoudre_jetons(html_source, contexte):
    """Remplace {{page}}, {{pages}}, {{title}}… par leur valeur.

    En bento ces jetons se résolvent au rendu, ce qui permet d'insérer une slide
    sans renuméroter. PowerPoint n'a pas d'équivalent pour la plupart d'entre
    eux : on les fige donc ici. C'est une différence assumée — le PPTX est un
    instantané, le document reste la source.
    """
    def _un(m):
        cle, pad = m.group(1), m.group(2)
        if cle not in contexte:
            return m.group(0)
        val = str(contexte[cle])
        return val.zfill(int(pad)) if pad and val.isdigit() else val
    return _JETON.sub(_un, html_source)


class Mesureur:
    """Mesure une chaîne avec la vraie police, comme le fera PowerPoint.

    La police est chargée à sa taille en points : les longueurs rendues par PIL
    sont alors directement en points, sans conversion. Technique reprise de
    `claudia-bis-4-deck`, qui l'a éprouvée en production.
    """

    def __init__(self):
        self._cache = {}
        self._absentes = set()

    def _police(self, famille, graisse, taille_pt):
        cle = (famille, graisse, round(taille_pt))
        if cle in self._cache:
            return self._cache[cle]
        try:
            chemin = fichier_mesurable(famille, graisse)
            f = ImageFont.truetype(str(chemin), max(1, round(taille_pt)))
        except Exception:
            self._absentes.add(famille)
            f = None
        self._cache[cle] = f
        return f

    def lignes(self, texte, famille, graisse, taille_px, largeur_px):
        """Nombre de lignes après retour automatique, à cette largeur."""
        f = self._police(famille, graisse, taille_px * PX_EN_PT)
        if f is None:                       # sans police, estimation prudente
            largeur_moy = taille_px * 0.5
            n = 0
            for para in texte.split("\n"):
                n += max(1, int(len(para) * largeur_moy // largeur_px) + 1)
            return n
        limite = largeur_px * PX_EN_PT
        n = 0
        for para in texte.split("\n"):
            mots, courante, lignes = para.split(), "", 1
            for mot in mots:
                essai = (courante + " " + mot).strip()
                if f.getlength(essai) <= limite or not courante:
                    courante = essai
                else:
                    lignes += 1
                    courante = mot
            n += lignes
        return n

    def hauteur_px(self, texte, famille, graisse, taille_px, largeur_px, lh):
        return self.lignes(texte, famille, graisse, taille_px, largeur_px) \
            * taille_px * lh


def famille_de(css_stack):
    """Première famille nommée d'une pile CSS, sans les guillemets.

    Une pile purement système ne nomme aucune famille embarquable ; on rend None
    et la mesure retombe sur une estimation, faute de fichier à charger.
    """
    for part in (css_stack or "").split(","):
        p = part.strip().strip("'\"")
        if p and not p.startswith("-") and p not in (
                "system-ui", "sans-serif", "serif", "monospace", "ui-sans-serif"):
            return p
    return None


# ─── Rendu des éléments ──────────────────────────────────────────────────────

def _poser_texte(slide, el, fond, mesureur, pertes, jetons=None):
    boite = slide.shapes.add_textbox(emu(el["x"]), emu(el["y"]),
                                     emu(el["w"]), emu(el["h"]))
    cadre = boite.text_frame
    cadre.word_wrap = True
    cadre.margin_left = cadre.margin_right = 0
    cadre.margin_top = cadre.margin_bottom = 0
    cadre.vertical_anchor = _ANCRE.get(el.get("valign", "top"), MSO_ANCHOR.TOP)

    famille = famille_de(el.get("fontFamily"))
    graisse = int(el.get("fontWeight", 400))
    taille = el.get("fontSize", 21)
    lh = el.get("lineHeight", 1.35)
    coul = couleur(el.get("color"), fond) or (0, 0, 0)

    para = cadre.paragraphs[0]
    para.alignment = _ALIGN.get(el.get("align", "left"), PP_ALIGN.LEFT)
    para.line_spacing = lh
    brut = resoudre_jetons(el.get("html", ""), jetons or {})
    for txt, gras, ital in morceaux(brut) or [("", False, False)]:
        for i, bout in enumerate(txt.split("\n")):
            if i:
                para = cadre.add_paragraph()
                para.alignment = _ALIGN.get(el.get("align", "left"), PP_ALIGN.LEFT)
                para.line_spacing = lh
            if not bout:
                continue
            r = para.add_run()
            r.text = bout
            r.font.size = pt(taille)
            r.font.bold = gras or graisse >= 600
            r.font.italic = ital
            r.font.color.rgb = _rgb(coul)
            if famille:
                r.font.name = famille
            if el.get("letterSpacing"):
                r.font._rPr.set("spc", str(int(el["letterSpacing"] * PX_EN_PT * 100)))

    if famille:
        besoin = mesureur.hauteur_px(texte_nu(brut), famille,
                                     graisse, taille, el["w"], lh)
        if besoin > el["h"] + 1:
            pertes.append(f"{el['id']} : le texte demande {besoin:.0f} px "
                          f"pour une boîte de {el['h']} px")
    return boite


def _poser_forme(slide, el, fond, pertes):
    genre = el.get("shape", "rect")
    if genre == "ellipse":
        auto = MSO_SHAPE.OVAL
    elif genre == "triangle":
        auto = MSO_SHAPE.ISOSCELES_TRIANGLE
    elif genre == "rect" and el.get("radius"):
        auto = MSO_SHAPE.ROUNDED_RECTANGLE
    elif genre in ("line", "path"):
        auto = MSO_SHAPE.RECTANGLE          # un filet est un rectangle plat
    else:
        auto = MSO_SHAPE.RECTANGLE

    f = slide.shapes.add_shape(auto, emu(el["x"]), emu(el["y"]),
                               emu(max(el["w"], 1)), emu(max(el["h"], 1)))
    f.shadow.inherit = False
    if el.get("fillGradient"):
        _remplir(f, _dominante(el, fond))
        pertes.append(f"{el['id']} : dégradé rendu en aplat")
    else:
        _remplir(f, couleur(el.get("fill"), fond))
    trait = couleur(el.get("stroke"), fond)
    if trait and el.get("strokeWidth"):
        f.line.color.rgb = _rgb(trait)
        f.line.width = pt(el["strokeWidth"])
    else:
        f.line.fill.background()
    if el.get("rotation"):
        f.rotation = el["rotation"]
    f.text_frame.word_wrap = True
    return f


def _poser_table(slide, el, fond, pertes, jetons=None):
    lignes = el.get("rows") or []
    colonnes = el.get("columns") or []
    if not lignes or not colonnes:
        return None
    style = el.get("style") or {}
    forme = slide.shapes.add_table(len(lignes), len(colonnes),
                                   emu(el["x"]), emu(el["y"]),
                                   emu(el["w"]), emu(el["h"]))
    t = forme.table
    total = sum(c.get("w", 1) for c in colonnes) or 1
    for i, c in enumerate(colonnes):
        t.columns[i].width = emu(el["w"] * c.get("w", 1) / total)

    entete = el.get("header", True)
    t.first_row = bool(entete)
    # Le banding alterné est actif par défaut, et PowerPoint comme Canva y
    # appliquent LEUR style de bande : marges et alignement écrasés une ligne
    # sur deux, ce qui se voit immédiatement (relevé à l'import Canva). On le
    # coupe et on peint le zebra soi-même, comme le fait le rendu web.
    t.horz_banding = False
    t.vert_banding = False
    zebra = couleur(style.get("zebra"), fond)
    encre = couleur(style.get("color"), fond) or (0, 0, 0)
    taille = style.get("fontSize", 18)
    fam = famille_de(el.get("fontFamily")) or None

    for r, ligne in enumerate(lignes):
        for c, cellule in enumerate((ligne.get("cells") or [])[:len(colonnes)]):
            cel = t.cell(r, c)
            cel.margin_left = cel.margin_right = emu(style.get("cellPadX", 16))
            cel.margin_top = cel.margin_bottom = emu(style.get("cellPadY", 11))
            cel.vertical_anchor = MSO_ANCHOR.MIDDLE
            if r == 0 and entete:
                bg = couleur(style.get("headerBg"), fond)
            else:
                bg = couleur(cellule.get("bg"), fond) or (
                    zebra if (r - (1 if entete else 0)) % 2 == 1 else None)
            _remplir(cel, bg)
            p = cel.text_frame.paragraphs[0]
            p.alignment = _ALIGN.get(cellule.get("align", "left"), PP_ALIGN.LEFT)
            teinte = (couleur(style.get("headerColor"), fond)
                      if r == 0 and entete else
                      couleur(cellule.get("color"), fond) or encre)
            for txt, gras, ital in morceaux(
                    resoudre_jetons(cellule.get("html", ""), jetons or {})):
                run = p.add_run()
                run.text = txt.replace("\n", " ")
                run.font.size = pt(taille)
                run.font.bold = gras or cellule.get("bold") or (r == 0 and entete)
                run.font.italic = ital
                run.font.color.rgb = _rgb(teinte or (0, 0, 0))
                if fam:
                    run.font.name = fam
    return forme


def _poser_chart(slide, el, fond, pertes):
    option = el.get("option") or {}
    series = option.get("series") or []
    if not series:
        return None
    preset = el.get("preset", "bar")
    donnees = CategoryChartData()

    if preset == "pie":
        points = series[0].get("data") or []
        donnees.categories = [p.get("name", "") for p in points]
        donnees.add_series("", [p.get("value", 0) for p in points])
    else:
        axe = option.get("xAxis") or {}
        cats = axe.get("data") or list(range(len(series[0].get("data") or [])))
        donnees.categories = [str(c) for c in cats]
        for s in series:
            valeurs = [v if isinstance(v, (int, float)) else 0
                       for v in (s.get("data") or [])]
            donnees.add_series(s.get("name", "série"), valeurs)

    cadre = slide.shapes.add_chart(
        _TYPE_CHART.get(preset, XL_CHART_TYPE.COLUMN_CLUSTERED),
        emu(el["x"]), emu(el["y"]), emu(el["w"]), emu(el["h"]), donnees)
    graphe = cadre.chart
    graphe.has_title = False
    graphe.has_legend = len(series) > 1 or preset == "pie"

    teintes = option.get("color") or []
    for i, s in enumerate(graphe.plots[0].series):
        brut = (teintes[i] if i < len(teintes)
                else ((series[i].get("itemStyle") or {}).get("color")
                      if i < len(series) else None))
        c = couleur(brut, fond)
        if c:
            s.format.fill.solid()
            s.format.fill.fore_color.rgb = _rgb(c)
    if preset == "scatter":
        pertes.append(f"{el['id']} : nuage rendu en graphique de dispersion simple")
    return cadre


def _poser_image(slide, el, doc, fond, pertes):
    src = el.get("src") or ""
    if src.startswith("asset:"):
        src = (doc.get("assets") or {}).get(src[6:], "")
    m = re.match(r"data:[^;]+;base64,(.+)", src, re.S)
    if not m:
        pertes.append(f"{el['id']} : image non embarquée, cadre laissé vide")
        return None
    flux = io.BytesIO(base64.b64decode(m.group(1)))
    return slide.shapes.add_picture(flux, emu(el["x"]), emu(el["y"]),
                                    emu(el["w"]), emu(el["h"]))


# ─── Assemblage ──────────────────────────────────────────────────────────────

def _ordonner(slides):
    """Aplatit les slides d'état juste après leur parent, dans l'ordre.

    Une slide d'état n'existe pas en PPTX : elle devient une slide ordinaire
    posée derrière celle dont elle dépendait, pour que le fil de lecture garde
    son sens même si le repli est perdu.
    """
    principales = [s for s in slides if not s.get("stateOf")]
    etats = {}
    for s in slides:
        if s.get("stateOf"):
            etats.setdefault(s["stateOf"], []).append(s)
    ordre = []
    for s in principales:
        ordre.append(s)
        ordre.extend(etats.get(s["id"], []))
    orphelins = [s for s in slides
                 if s.get("stateOf") and s["stateOf"] not in
                 {p["id"] for p in principales}]
    return ordre + orphelins


def rendre(doc, sortie):
    """Écrit le .pptx. Rend (chemin, pertes) — `pertes` est le rapport de
    dégradation, à afficher : une dégradation tue est une mauvaise surprise."""
    pertes = []
    prs = Presentation()
    taille = doc.get("size") or {"width": 1280, "height": 720}
    prs.slide_width = emu(taille["width"])
    prs.slide_height = emu(taille["height"])
    vierge = prs.slide_layouts[6]
    mesureur = Mesureur()

    theme = doc.get("theme") or {}
    fond_deck = couleur(theme.get("background"), (255, 255, 255)) or (255, 255, 255)
    ordre = _ordonner(doc.get("slides") or [])
    index = {s["id"]: i for i, s in enumerate(ordre)}
    liens = []

    meta = doc.get("meta") or {}
    numerotees = [s for s in ordre if not s.get("stateOf") and not s.get("hidden")]
    rang = {s["id"]: i + 1 for i, s in enumerate(numerotees)}
    base_jetons = {"title": doc.get("title", ""), "pages": len(numerotees),
                   "author": meta.get("author", ""),
                   "company": meta.get("company", ""),
                   "subject": meta.get("subject", ""),
                   "event": meta.get("event", "")}

    for s in ordre:
        jetons = dict(base_jetons, page=rang.get(s["id"], ""))
        slide = prs.slides.add_slide(vierge)
        fond = couleur(s.get("background"), fond_deck) or fond_deck
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = _rgb(fond)

        if s.get("stateOf"):
            pertes.append(f"{s['id']} : état déplié en slide ordinaire")
        if s.get("transition") == "morph":
            pertes.append(f"{s['id']} : transition morph perdue")
        if s.get("hidden"):
            slide.element.set("show", "0")

        for el in s.get("elements") or []:
            genre = el.get("type")
            forme = None
            if genre == "text":
                forme = _poser_texte(slide, el, fond, mesureur, pertes, jetons)
            elif genre == "shape":
                forme = _poser_forme(slide, el, fond, pertes)
            elif genre == "table":
                forme = _poser_table(slide, el, fond, pertes, jetons)
            elif genre == "chart":
                forme = _poser_chart(slide, el, fond, pertes)
            elif genre == "image":
                forme = _poser_image(slide, el, doc, fond, pertes)
            elif genre == "media":
                forme = _poser_forme(slide, {**el, "shape": "rect",
                                             "fill": "rgba(0,0,0,0.06)"},
                                     fond, pertes)
                pertes.append(f"{el['id']} : média remplacé par un cadre vide")
            elif genre == "svg":
                pertes.append(f"{el['id']} : svg non transposé")

            fx = el.get("fx") or {}
            if fx.get("ambient") or fx.get("loop"):
                pertes.append(f"{el['id']} : animation d'ambiance perdue")
            if el.get("link") and forme is not None:
                liens.append((forme, el["link"]))

        if s.get("notes"):
            slide.notes_slide.notes_text_frame.text = s["notes"]

    # Les liens se posent en dernier : la slide cible doit exister.
    for forme, cible in liens:
        if cible not in index:
            pertes.append(f"lien vers {cible} : slide absente")
            continue
        try:
            forme.click_action.target_slide = prs.slides[index[cible]]
        except Exception:
            pertes.append(f"lien vers {cible} : non transposable")

    chemin = pathlib.Path(sortie)
    prs.save(str(chemin))
    if mesureur._absentes:
        pertes.append("polices non mesurées (estimation) : "
                      + ", ".join(sorted(mesureur._absentes)))
    pertes.extend(verifier(ordre, prs))
    pertes.extend(chevauchements(ordre, mesureur))
    return chemin, pertes


def chevauchements(slides, mesureur, marge=4):
    """Textes qui se recouvrent réellement, hauteur mesurée à l'appui.

    Comparer les boîtes déclarées ne servirait à rien : une boîte de titre est
    volontairement plus haute que sa ligne, et un chevauchement de boîtes n'est
    pas un chevauchement de texte. C'est la hauteur RÉELLE qu'il faut, et elle
    n'existe qu'une fois le texte mesuré avec sa police.

    C'est le défaut qui échappe à tous les autres contrôles : chaque élément
    tient dans sa boîte, aucune boîte ne sort du cadre, et pourtant deux textes
    se marchent dessus à l'écran.
    """
    collisions = []
    for s in slides:
        boites = []
        for el in s.get("elements") or []:
            if el.get("type") != "text" or not texte_nu(el.get("html", "")).strip():
                continue
            fam = famille_de(el.get("fontFamily"))
            reelle = el["h"]
            if fam:
                reelle = min(el["h"], mesureur.hauteur_px(
                    texte_nu(el["html"]), fam, int(el.get("fontWeight", 400)),
                    el.get("fontSize", 21), el["w"], el.get("lineHeight", 1.35)))
            haut = el["y"]
            if el.get("valign") in ("middle", "center"):
                haut = el["y"] + (el["h"] - reelle) / 2
            elif el.get("valign") == "bottom":
                haut = el["y"] + el["h"] - reelle
            boites.append((el["id"], el["x"], haut, el["w"], reelle))
        for i in range(len(boites)):
            for j in range(i + 1, len(boites)):
                a, b = boites[i], boites[j]
                dx = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
                dy = min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2])
                if dx > marge and dy > marge:
                    collisions.append(f"{s['id']} : {a[0]} et {b[0]} se "
                                      f"chevauchent sur {dy:.0f} px")
    return collisions


def verifier(slides, prs, tolerance_px=0.5):
    """Compare la géométrie posée à celle du document. Rend les écarts.

    Le rendu web se contrôle à l'œil dans le navigateur ; le PPTX ne le peut pas
    — PowerPoint interdit tout export scripté sur macOS. Cette comparaison prend
    le relais : si chaque forme est là où le document la place, la mise en page
    est fidèle par construction, et il ne reste à juger que la typographie.
    """
    ecarts = []
    for s_doc, s_ppt in zip(slides, prs.slides):
        rendus = [f for f in s_ppt.shapes]
        for el, forme in zip(s_doc.get("elements") or [], rendus):
            for cle, obtenu in (("x", forme.left), ("y", forme.top),
                                ("w", forme.width), ("h", forme.height)):
                if obtenu is None or cle not in el:
                    continue
                px = obtenu / (EMU_PAR_POUCE / PX_PAR_POUCE)
                if abs(el[cle] - px) > tolerance_px:
                    ecarts.append(f"{s_doc['id']}/{el['id']}.{cle} : "
                                  f"{el[cle]} px posé à {px:.1f} px")
    return ecarts


_BLOC = re.compile(
    r'<script type="application/bento\+json" id="bento-doc"[^>]*>(.*?)</script>',
    re.S)


def depuis_fichier(chemin_html, sortie=None):
    """Relit le document d'un .bento.html déjà produit et le rend en PPTX."""
    brut = pathlib.Path(chemin_html).read_text(encoding="utf-8")
    m = _BLOC.search(brut)
    if not m:
        raise RuntimeError(f"Bloc #bento-doc introuvable dans {chemin_html}")
    doc = json.loads(m.group(1).replace("\\u003c", "<"))
    if not sortie:
        sortie = re.sub(r"(\.bento)?\.html$", "", str(chemin_html)) + ".pptx"
    return rendre(doc, sortie)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dest, pertes = depuis_fichier(sys.argv[1],
                                  sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"OK — {dest}")
    if pertes:
        print(f"\nDégradations ({len(pertes)}) :")
        for p in pertes:
            print(f"  - {p}")
