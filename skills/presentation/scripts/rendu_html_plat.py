#!/usr/bin/env python3
"""Troisième rendu : un document bento → un HTML plat, une page par slide.

    python3 rendu_html_plat.py mon-deck.bento.html [sortie.html]

Ce rendu sert deux besoins d'un coup, et c'est ce qui justifie son existence :

**Voir.** Le rendu PPTX ne peut pas être contrôlé à l'œil — PowerPoint interdit
tout export scripté sur macOS. Ce HTML-ci se regarde dans un navigateur, slide
après slide, notes comprises. Il est produit depuis le même document, donc ce
qu'il montre est ce que les autres rendus posent.

**Entrer dans Canva sans glisser-déposer.** L'import Canva accepte le HTML et
sait le découper en pages, à condition qu'on le lui dise : chaque page porte
`data-document-role`, son titre va dans `data-label`, ses notes dans
`data-speaker-notes`. Ce n'est utile que lorsqu'une URL publique existe déjà —
et l'apport est le confort, pas la fidélité : le PPTX conserve lui aussi les
notes, les formes éditables et un graphique modifiable, ce qui a été vérifié.

Le premier usage est donc le principal : ce rendu existe surtout pour **voir**.

À la différence du `.bento.html`, il n'y a ici aucune application : des blocs
positionnés, rien d'interactif. C'est voulu — Canva importe un HTML interactif
comme un site, pas comme une présentation.

Les animations, le morph et les états repliés ne sont pas transposés : ce rendu
est un aplat. Les slides d'état sont dépliées à la suite de leur parent, comme
en PPTX, pour que le fil de lecture garde son sens.
"""

import html as _html
import json
import math
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rendu_pptx import (_BLOC, _ordonner, couleur, morceaux,  # noqa: E402
                        resoudre_jetons, texte_nu)


def _css_couleur(valeur, defaut=None):
    """Rend la valeur telle quelle : le navigateur sait lire rgba(), lui."""
    if not valeur or valeur in ("none", "transparent"):
        return defaut
    return valeur


def _gradient(el):
    g = el.get("fillGradient") or {}
    stops = g.get("stops") or []
    if not stops:
        return None
    arrets = ", ".join(f"{s.get('color', 'transparent')} {s.get('at', 0) * 100:.0f}%"
                       for s in stops)
    return f"linear-gradient({g.get('angle', 180)}deg, {arrets})"


def _texte_html(el, jetons):
    """Le html inline du document, jetons résolus, balises inconnues retirées."""
    brut = resoudre_jetons(el.get("html", ""), jetons)
    bouts = []
    for txt, gras, ital in morceaux(brut):
        morceau = _html.escape(txt).replace("\n", "<br>")
        if gras:
            morceau = f"<b>{morceau}</b>"
        if ital:
            morceau = f"<i>{morceau}</i>"
        bouts.append(morceau)
    return "".join(bouts)


# ─── Graphiques en SVG ───────────────────────────────────────────────────────
# Un graphique dessiné en SVG reste vectoriel : lisible ici, et éditable après
# import plutôt qu'aplati en image.

def _palier(valeur, divisions=4):
    """Arrondit un maximum d'axe à une graduation lisible.

    Un axe qui affiche 23,25 et 15,5 se lit deux fois plus lentement qu'un axe
    à 10, 20, 30 : l'œil doit calculer au lieu de comparer.
    """
    if valeur <= 0:
        return divisions
    brut = valeur / divisions
    ordre = 10 ** math.floor(math.log10(brut))
    for facteur in (1, 2, 2.5, 5, 10):
        if facteur * ordre >= brut:
            return facteur * ordre * divisions
    return brut * divisions


def _svg_barres(el, serie, cats, teinte, fond):
    w, h = el["w"], el["h"]
    marge_g, marge_b, marge_h = 48, 42, 16
    aire_w, aire_h = w - marge_g - 16, h - marge_b - marge_h
    valeurs = [v if isinstance(v, (int, float)) else 0 for v in serie]
    haut = _palier(max(valeurs + [1]))
    pas = aire_w / max(len(valeurs), 1)
    largeur = min(pas * 0.62, 76)
    out = []
    for i in range(5):                                   # grille horizontale
        y = marge_h + aire_h * i / 4
        out.append(f'<line x1="{marge_g}" y1="{y:.1f}" x2="{marge_g + aire_w}" '
                   f'y2="{y:.1f}" stroke="rgba(128,128,128,0.22)" stroke-width="1"/>')
        out.append(f'<text x="{marge_g - 10}" y="{y + 4:.1f}" font-size="13" '
                   f'text-anchor="end" fill="rgba(128,128,128,0.9)">'
                   f'{haut * (4 - i) / 4:.0f}</text>')
    for i, v in enumerate(valeurs):
        hb = aire_h * (v / haut)
        x = marge_g + pas * i + (pas - largeur) / 2
        y = marge_h + aire_h - hb
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{largeur:.1f}" '
                   f'height="{hb:.1f}" rx="6" fill="{teinte}"/>')
        if i < len(cats):
            out.append(f'<text x="{x + largeur / 2:.1f}" y="{h - marge_b + 20:.0f}" '
                       f'font-size="13" text-anchor="middle" '
                       f'fill="rgba(128,128,128,0.9)">{_html.escape(str(cats[i]))}</text>')
    return "".join(out)


def _svg_ligne(el, serie, cats, teinte, fond):
    w, h = el["w"], el["h"]
    marge_g, marge_b, marge_h = 48, 42, 16
    aire_w, aire_h = w - marge_g - 16, h - marge_b - marge_h
    valeurs = [v if isinstance(v, (int, float)) else 0 for v in serie]
    if not valeurs:
        return ""
    bas = min(valeurs + [0])
    haut = _palier(max(valeurs)) if bas >= 0 else max(valeurs)
    etendue = (haut - bas) or 1
    pas = aire_w / max(len(valeurs) - 1, 1)
    pts = [(marge_g + pas * i,
            marge_h + aire_h - aire_h * ((v - bas) / etendue))
           for i, v in enumerate(valeurs)]
    chemin = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                      for i, (x, y) in enumerate(pts))
    aire = (chemin + f" L{pts[-1][0]:.1f},{marge_h + aire_h:.1f}"
            f" L{pts[0][0]:.1f},{marge_h + aire_h:.1f} Z")
    out = [f'<path d="{aire}" fill="{teinte}" opacity="0.12"/>',
           f'<path d="{chemin}" fill="none" stroke="{teinte}" stroke-width="3"/>']
    for i, (x, y) in enumerate(pts):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{teinte}"/>')
        if i < len(cats):
            out.append(f'<text x="{x:.1f}" y="{h - marge_b + 20:.0f}" font-size="13" '
                       f'text-anchor="middle" fill="rgba(128,128,128,0.9)">'
                       f'{_html.escape(str(cats[i]))}</text>')
    return "".join(out)


def _svg_secteurs(el, points, teintes, fond):
    w, h = el["w"], el["h"]
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.38
    trou = r * 0.58
    total = sum(p.get("value", 0) for p in points) or 1
    angle = -math.pi / 2
    out = []
    for i, p in enumerate(points):
        part = p.get("value", 0) / total
        fin = angle + part * 2 * math.pi
        grand = 1 if part > 0.5 else 0
        x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        x2, y2 = cx + r * math.cos(fin), cy + r * math.sin(fin)
        xi, yi = cx + trou * math.cos(fin), cy + trou * math.sin(fin)
        xj, yj = cx + trou * math.cos(angle), cy + trou * math.sin(angle)
        d = (f"M{x1:.1f},{y1:.1f} A{r:.1f},{r:.1f} 0 {grand},1 {x2:.1f},{y2:.1f} "
             f"L{xi:.1f},{yi:.1f} A{trou:.1f},{trou:.1f} 0 {grand},0 {xj:.1f},{yj:.1f} Z")
        teinte = teintes[i % len(teintes)] if teintes else "#888"
        out.append(f'<path d="{d}" fill="{teinte}" stroke="{fond}" stroke-width="3"/>')
        mid = angle + part * math.pi
        lx, ly = cx + (r + 26) * math.cos(mid), cy + (r + 26) * math.sin(mid)
        ancre = "start" if math.cos(mid) > 0 else "end"
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="14" '
                   f'text-anchor="{ancre}" fill="rgba(128,128,128,0.95)">'
                   f'{_html.escape(str(p.get("name", "")))} : {p.get("value", 0)}</text>')
        angle = fin
    return "".join(out)


def _chart(el, fond):
    option = el.get("option") or {}
    series = option.get("series") or []
    if not series:
        return ""
    preset = el.get("preset", "bar")
    teintes = option.get("color") or []
    teinte = (teintes[0] if teintes
              else (series[0].get("itemStyle") or {}).get("color") or "#666")
    cats = ((option.get("xAxis") or {}).get("data")) or []
    if preset == "pie":
        corps = _svg_secteurs(el, series[0].get("data") or [], teintes or [teinte], fond)
    elif preset == "line":
        corps = _svg_ligne(el, series[0].get("data") or [], cats, teinte, fond)
    else:
        corps = _svg_barres(el, series[0].get("data") or [], cats, teinte, fond)
    return (f'<svg viewBox="0 0 {el["w"]} {el["h"]}" width="{el["w"]}" '
            f'height="{el["h"]}" xmlns="http://www.w3.org/2000/svg">{corps}</svg>')


def _table(el, fond, jetons):
    style = el.get("style") or {}
    colonnes = el.get("columns") or []
    total = sum(c.get("w", 1) for c in colonnes) or 1
    entete = el.get("header", True)
    bord = f"{style.get('borderWidth', 1)}px solid {style.get('borderColor', '#ddd')}"
    lignes = []
    for r, ligne in enumerate(el.get("rows") or []):
        cells = []
        for c, cellule in enumerate((ligne.get("cells") or [])):
            fondc = (style.get("headerBg") if r == 0 and entete
                     else (cellule.get("bg") or (style.get("zebra") if r % 2 == 0 else None)))
            teinte = (style.get("headerColor") if r == 0 and entete
                      else cellule.get("color") or style.get("color", "#000"))
            gras = "font-weight:700;" if (r == 0 and entete) or cellule.get("bold") else ""
            largeur = colonnes[c].get("w", 1) / total * 100 if c < len(colonnes) else None
            cells.append(
                f'<td style="{"width:%.2f%%;" % largeur if largeur else ""}'
                f'padding:{style.get("cellPadY", 11)}px {style.get("cellPadX", 16)}px;'
                f'border-bottom:{bord};'
                f'{"background:%s;" % fondc if fondc else ""}color:{teinte};{gras}'
                f'text-align:{cellule.get("align", "left")};">'
                f'{_texte_html(cellule, jetons)}</td>')
        lignes.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<table style="width:100%;border-collapse:collapse;'
            f'font-size:{style.get("fontSize", 18)}px;'
            f'border-radius:{style.get("radius", 0)}px;overflow:hidden;">'
            + "".join(lignes) + "</table>")


def _element(el, doc, fond, jetons):
    genre = el.get("type")
    base = (f'position:absolute;left:{el["x"]}px;top:{el["y"]}px;'
            f'width:{el["w"]}px;height:{el["h"]}px;'
            f'opacity:{el.get("opacity", 1)};')
    if el.get("rotation"):
        base += f'transform:rotate({el["rotation"]}deg);'

    if genre == "text":
        justif = {"top": "flex-start", "middle": "center",
                  "center": "center", "bottom": "flex-end"}.get(
                      el.get("valign", "top"), "flex-start")
        st = (base + f'font-size:{el.get("fontSize", 21)}px;'
              f'font-family:{el.get("fontFamily", "sans-serif")};'
              f'font-weight:{el.get("fontWeight", 400)};'
              f'color:{el.get("color", "#000")};'
              f'line-height:{el.get("lineHeight", 1.35)};'
              f'text-align:{el.get("align", "left")};'
              f'display:flex;flex-direction:column;justify-content:{justif};')
        if el.get("letterSpacing"):
            st += f'letter-spacing:{el["letterSpacing"]}px;'
        return f'<div style="{st}"><div>{_texte_html(el, jetons)}</div></div>'

    if genre == "shape":
        st = base
        grad = _gradient(el)
        if grad:
            st += f"background:{grad};"
        else:
            f = _css_couleur(el.get("fill"))
            if f:
                st += f"background:{f};"
        if el.get("radius"):
            st += f'border-radius:{el["radius"]}px;'
        if el.get("shape") == "ellipse":
            st += "border-radius:50%;"
        trait = _css_couleur(el.get("stroke"))
        if trait and el.get("strokeWidth"):
            st += f'border:{el["strokeWidth"]}px solid {trait};box-sizing:border-box;'
        return f'<div style="{st}"></div>'

    if genre == "chart":
        return f'<div style="{base}">{_chart(el, fond)}</div>'

    if genre == "table":
        return f'<div style="{base}">{_table(el, fond, jetons)}</div>'

    if genre == "image":
        src = el.get("src", "")
        if src.startswith("asset:"):
            src = (doc.get("assets") or {}).get(src[6:], "")
        return (f'<img src="{src}" style="{base}'
                f'object-fit:{el.get("fit", "cover")};'
                f'border-radius:{el.get("radius", 0)}px;" alt="">')

    if genre == "media":
        return (f'<div style="{base}background:rgba(128,128,128,0.10);'
                f'display:flex;align-items:center;justify-content:center;'
                f'color:rgba(128,128,128,0.9);font-size:15px;">média</div>')
    return ""


def _fontface(doc):
    """Réutilise les polices déjà embarquées dans le document.

    Elles sont là, en data URI : les redéclarer ici ne coûte rien et garantit
    que ce rendu montre la même typographie que le rendu web.
    """
    regles = []
    for f in doc.get("fonts") or []:
        uri = (doc.get("assets") or {}).get(f.get("asset", ""), "")
        if uri:
            regles.append(f"@font-face{{font-family:'{f['family']}';"
                          f"src:url({uri}) format('woff2');"
                          f"font-weight:{f.get('weight', 400)};font-style:normal;}}")
    return "".join(regles)


def rendre(doc, sortie, pour_canva=True):
    taille = doc.get("size") or {"width": 1280, "height": 720}
    W, H = taille["width"], taille["height"]
    theme = doc.get("theme") or {}
    fond_deck = theme.get("background", "#ffffff")
    meta = doc.get("meta") or {}

    ordre = _ordonner(doc.get("slides") or [])
    numerotees = [s for s in ordre if not s.get("stateOf") and not s.get("hidden")]
    rang = {s["id"]: i + 1 for i, s in enumerate(numerotees)}
    base_jetons = {"title": doc.get("title", ""), "pages": len(numerotees),
                   "author": meta.get("author", ""), "company": meta.get("company", ""),
                   "subject": meta.get("subject", ""), "event": meta.get("event", "")}

    pages = []
    for s in ordre:
        jetons = dict(base_jetons, page=rang.get(s["id"], ""))
        fond = s.get("background") or fond_deck
        corps = "".join(_element(el, doc, fond, jetons)
                        for el in (s.get("elements") or []))
        # Le titre de page : le premier texte portant le rôle « title », sinon l'id.
        libelle = next((texte_nu(e.get("html", "")) for e in (s.get("elements") or [])
                        if e.get("type") == "text" and e.get("role") == "title"),
                       s.get("name") or s["id"])
        annot = ""
        if pour_canva:
            annot = (f' data-document-role="page"'
                     f' data-label="{_html.escape(libelle[:120], quote=True)}"')
            if s.get("notes"):
                annot += (f' data-speaker-notes='
                          f'"{_html.escape(s["notes"][:4900], quote=True)}"')
        pages.append(
            f'<section class="page"{annot} style="width:{W}px;height:{H}px;'
            f'background:{fond};">{corps}</section>')

    style = f"""
    :root {{ color-scheme: light dark; }}
    {_fontface(doc)}
    body {{ margin:0; background:#2a2a2e; font-family:{theme.get('fontFamily', 'sans-serif')}; }}
    .pile {{ display:flex; flex-direction:column; align-items:center; gap:28px; padding:28px; }}
    .page {{ position:relative; overflow:hidden; flex:none;
             box-shadow:0 8px 40px rgba(0,0,0,.45); }}
    .notes {{ width:{W}px; max-width:100%; color:#c9c9cf; font-size:14px;
              line-height:1.55; background:#1e1e22; border-left:3px solid #6b6b78;
              padding:12px 16px; margin-top:-16px; }}
    .notes b {{ display:block; font-size:11px; letter-spacing:.10em;
                text-transform:uppercase; color:#8a8a96; margin-bottom:5px; }}
    @media (max-width:1360px) {{ .pile {{ zoom:.72 }} }}
    """

    bloc = []
    for s, page in zip(ordre, pages):
        bloc.append(page)
        if s.get("notes") and not pour_canva:
            bloc.append(f'<div class="notes"><b>Notes</b>'
                        f'{_html.escape(s["notes"])}</div>')

    doc_html = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
                f'<title>{_html.escape(doc.get("title", "deck"))}</title>'
                f'<style>{style}</style></head><body>'
                f'<div class="pile">{"".join(bloc)}</div></body></html>')
    chemin = pathlib.Path(sortie)
    chemin.write_text(doc_html, encoding="utf-8")
    return chemin, len(pages)


def depuis_fichier(chemin_html, sortie=None, pour_canva=True):
    brut = pathlib.Path(chemin_html).read_text(encoding="utf-8")
    m = _BLOC.search(brut)
    if not m:
        raise RuntimeError(f"Bloc #bento-doc introuvable dans {chemin_html}")
    doc = json.loads(m.group(1).replace("\\u003c", "<"))
    if not sortie:
        sortie = re.sub(r"(\.bento)?\.html$", "", str(chemin_html)) + "-plat.html"
    return rendre(doc, sortie, pour_canva)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    # --controle : ajoute les notes sous chaque slide et retire l'annotation Canva
    controle = "--controle" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dest, n = depuis_fichier(args[0], args[1] if len(args) > 1 else None,
                             pour_canva=not controle)
    print(f"OK — {n} pages → {dest}"
          + ("  (mode contrôle : notes visibles, pas d'annotation Canva)"
             if controle else "  (annoté pour l'import Canva)"))
