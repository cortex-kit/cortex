"""Moteur bento — helpers de composition, injection dans le fichier, contrôle.

Séparation stricte, reprise de claudia-bis-4-deck : **le moteur ne connaît
aucun contenu, un fichier de deck ne porte aucune géométrie de bas niveau.**
Un `deck_xxx.py` qui recalcule une gouttière ou redéfinit une couleur est un
fichier à corriger — la gouttière est dans COLS, la couleur dans chartes.py.

Usage typique depuis un fichier de deck :

    import sys; sys.path.insert(0, "<skill>/scripts")
    from chartes import charte, theme, COLS
    from bento import txt, rect, chart, table, runhead, titre, build

    C = charte("mia")
    slides = [ {...}, {...} ]
    doc = {"format": "bento/slides", "version": 1, "title": "…",
           "size": {"width": 1280, "height": 720}, "theme": theme(C),
           "slides": slides}
    build(doc, "Sortie.bento.html")

`build()` télécharge le runtime si le fichier n'existe pas, injecte le document
et lance le contrôle statique. Il lève une exception plutôt que de produire un
deck cassé en silence.
"""

import json
import pathlib
import re
import subprocess
import urllib.request

RUNTIME_URL = "https://bento.page/releases/slides/Bento_Slides.bento.html"
# bento.page comme Google Fonts refusent l'agent par défaut d'urllib (403).
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CANVAS = {"width": 1280, "height": 720}
_BLOC = re.compile(
    r'(<script type="application/bento\+json" id="bento-doc"[^>]*>)(.*?)(</script>)',
    re.S,
)
# Un <script> qui charge son code depuis un hôte distant. Le runtime de
# bento.page est autoportant — scripts inline, polices embarquées — donc un
# `src` absolu n'est jamais du bento : c'est un tiers greffé par l'hébergeur.
# `[^>]*` ne franchit pas le `>` : la balise ne peut pas déborder sur la
# suivante. Un `src` relatif n'est pas visé, il resterait dans le document.
_SCRIPT_TIERS = re.compile(
    r'[ \t]*<script[^>]*\ssrc="https?://[^"]*"[^>]*>\s*</script>\n?',
    re.I,
)

# Éléments dont le débordement hors canevas est un parti pris (décor plein bord)
# et non un défaut. Préfixer un id par « decor » suspend le contrôle de cadre
# pour cet élément — c'est une dérogation explicite, pas un oubli.
PREFIXE_DECOR = "decor"


# ─── Éléments ────────────────────────────────────────────────────────────────
# Tous partagent id/x/y/w/h/rotation/opacity. Les champs sont écrits en entier :
# bento ignore silencieusement une propriété inconnue, donc un champ manquant ne
# lève rien — il rend simplement mal, et on ne le voit qu'à l'écran.

def txt(id_, x, y, w, h, html, size=21, weight=400, color="#000", font=None,
        align="left", valign="top", lh=1.35, role=None, fx=None, ls=None):
    e = {"id": id_, "type": "text", "x": x, "y": y, "w": w, "h": h,
         "rotation": 0, "opacity": 1, "html": html,
         "fontSize": size, "fontFamily": font or "system-ui, sans-serif",
         "fontWeight": weight, "color": color,
         "align": align, "valign": valign, "lineHeight": lh}
    if role:
        e["role"] = role          # title|subtitle|body|kicker — laisse un
    if fx:                        # tiers restyler le deck sans le retaper
        e["fx"] = fx
    if ls is not None:
        e["letterSpacing"] = ls
    return e


def rect(id_, x, y, w, h, fill, radius=0, stroke="none", sw=0, opacity=1,
         fx=None, link=None, gradient=None):
    e = {"id": id_, "type": "shape", "shape": "rect", "x": x, "y": y,
         "w": w, "h": h, "fill": fill, "stroke": stroke, "strokeWidth": sw,
         "radius": radius, "rotation": 0, "opacity": opacity}
    if gradient:
        e["fillGradient"] = gradient
    if fx:
        e["fx"] = fx
    if link:
        e["link"] = link
    return e


def ellipse(id_, x, y, w, h, fill, opacity=1, fx=None, link=None):
    e = {"id": id_, "type": "shape", "shape": "ellipse", "x": x, "y": y,
         "w": w, "h": h, "fill": fill, "stroke": "none", "strokeWidth": 0,
         "radius": 0, "rotation": 0, "opacity": opacity}
    if fx:
        e["fx"] = fx
    if link:
        e["link"] = link
    return e


def image(id_, x, y, w, h, src, fit="cover", radius=0, fx=None):
    return {"id": id_, "type": "image", "x": x, "y": y, "w": w, "h": h,
            "src": src, "fit": fit, "radius": radius,
            "rotation": 0, "opacity": 1, **({"fx": fx} if fx else {})}


def chart(id_, x, y, w, h, preset, option, fx=None):
    """preset ∈ bar | line | pie | scatter.

    Le moteur est « charts-lite », pas ECharts : il lit la FORME de l'option et
    ignore en silence tout ce qu'il n'implémente pas. Deux pièges coûteux :
    les séries bar/line veulent des nombres nus (un `{value: …}` se lit 0, seul
    pie prend `{name, value}`), et `label` sur une série bar/line ne fait rien —
    les valeurs au-dessus des barres n'existent pas, il faut un tableau à côté.
    """
    e = {"id": id_, "type": "chart", "x": x, "y": y, "w": w, "h": h,
         "rotation": 0, "opacity": 1, "preset": preset, "option": option}
    if fx:
        e["fx"] = fx
    return e


def table(id_, x, y, w, h, columns, rows, style, header=True, fx=None):
    """columns : [{"w": poids}] · rows : [{"cells": [{"html": …}]}]

    Pour une grille de comparaison / tarifs / specs. Pas pour une tendance
    chiffrée — là c'est un chart, l'œil lit une barre plus vite qu'un nombre.
    """
    e = {"id": id_, "type": "table", "x": x, "y": y, "w": w, "h": h,
         "rotation": 0, "opacity": 1, "header": header,
         "columns": columns, "rows": rows, "style": style}
    if fx:
        e["fx"] = fx
    return e


def media(id_, x, y, w, h, src, kind="video", poster=None, controls=True,
          autoplay=False, loop=False, muted=True, fit="cover", radius=0):
    e = {"id": id_, "type": "media", "kind": kind, "src": src,
         "x": x, "y": y, "w": w, "h": h, "rotation": 0, "opacity": 1,
         "controls": controls, "autoplay": autoplay, "loop": loop,
         "muted": muted, "fit": fit, "radius": radius}
    if poster:
        e["poster"] = poster
    return e


# ─── Composition ─────────────────────────────────────────────────────────────

def runhead(c, label, folio=True):
    """Le bandeau de rappel : filet d'accent + rubrique + folio.

    Ses ids sont stables (`rail`, `runhead`, `folio`) et c'est délibéré : sur une
    slide en `transition:"morph"`, bento apparie les éléments par id et le
    bandeau glisse d'une slide à l'autre au lieu de réapparaître. C'est le geste
    signature du format, et il ne coûte que la stabilité des ids.

    Le folio utilise les jetons `{{page}}`/`{{pages}}` : ils se résolvent au
    rendu, donc insérer une slide ne renumérote rien à la main.
    """
    els = [
        rect("rail", 96, 84, 40, 5, c["accent"]),
        txt("runhead", 148, 68, 700, 48, label, size=16, weight=600,
            color=c["attenue"], font=c["police_corps"], ls=1.6),
    ]
    if folio:
        els.append(txt("folio", 1064, 68, 120, 48, "{{page:2}} / {{pages}}",
                       size=16, weight=500, color=c["attenue"],
                       font=c["police_corps"], align="right"))
    return els


def etiquette(c, id_, x, y, w, html, color=None):
    """Surtitre, rubrique, catégorie — en capitales, interlettré.

    Relevé sur le template : entre 12 et 16 px, un tiers des textes sont en
    capitales. Ce n'est pas du corps rétréci, c'est une fonction distincte. Si
    du texte courant se retrouve à cette taille, ce n'est pas un choix
    typographique — c'est qu'il y a trop de contenu sur la slide.

    Écrire le libellé déjà en capitales : une mise en majuscules automatique
    abîmerait les entités HTML (`&eacute;` deviendrait `&EACUTE;`).
    """
    return txt(id_, x, y, w, 30, html, size=16, weight=600,
               color=color or c["attenue"], font=c["police_corps"], ls=1.6)


def chiffre(c, id_, x, y, w, valeur, legende=None, geant=False, decompte=True):
    """Un nombre mis en avant, avec sa légende sous lui.

    `geant=True` passe à l'échelle où le chiffre EST la slide (176 px, relevé à
    195 pt sur le template). À n'employer que si un seul nombre porte tout le
    propos : deux chiffres géants sur une slide, et aucun ne l'est.

    Le décompte ne joue que si l'élément est neuf sur sa slide — sur une arrivée
    en morph, un élément apparié repartirait de zéro, donc bento le saute.
    """
    taille = c["echelle"]["geant"] if geant else 76
    els = [txt(id_, x, y, w, int(taille * 1.16), str(valeur),
               size=taille, weight=700, color=c["accent"],
               font=c["police_chiffres"], align="center", lh=1,
               **({"fx": {"countUp": True}} if decompte else {}))]
    if legende:
        els.append(txt(id_ + "-l", x, y + int(taille * 1.22), w, 56, legende,
                       size=c["echelle"]["secondaire"], weight=500,
                       color=c["titre_couleur"], font=c["police_corps"],
                       align="center", lh=1.3))
    return els


def carte(c, id_, x, y, w, h, titre_carte=None, corps=None, sur=None,
          accentuee=False, link=None):
    """Une carte : panneau, filet d'accent optionnel, surtitre, titre, corps.

    À préférer systématiquement à une liste à puces dès que les items sont
    comparables — personnes, services, options, niveaux. Le texte à puces est le
    réflexe par défaut, et c'est ce qui fait qu'un deck ressemble à un document.
    """
    els = [rect(id_, x, y, w, h, c["panneau"], radius=12, link=link)]
    if accentuee:
        els.append(rect(id_ + "-f", x, y, w, 5, c["accent"]))
    curseur = y + 32
    if sur:
        els.append(etiquette(c, id_ + "-s", x + 28, curseur, w - 56, sur,
                             color=c["accent"]))
        curseur += 38
    if titre_carte:
        els.append(txt(id_ + "-t", x + 28, curseur, w - 56, 44, titre_carte,
                       size=26, weight=700, color=c["titre_couleur"],
                       font=c["police_titre"], lh=1.2))
        curseur += 52
    if corps:
        els.append(txt(id_ + "-c", x + 28, curseur, w - 56, y + h - curseur - 24,
                       corps, size=c["echelle"]["secondaire"] + 1, weight=400,
                       color=c["encre"], font=c["police_corps"], lh=1.45))
    return els


def barres(c, id_, x, y, w, h, valeurs, libelles=None, teintes=None,
           valeurs_visibles=True):
    """Un histogramme dessiné en rectangles, une teinte par barre.

    Pourquoi ne pas prendre un `chart` : le moteur de graphique colore **par
    série**, pas par barre. Une série unique de cinq valeurs sort donc en cinq
    barres identiques — et la gradation, qui est justement la règle, devient
    impossible à montrer. Cinq séries d'un point chacune seraient un détour
    fragile.

    Dessiner en rectangles règle ça et rend un bonus : chaque barre reste une
    forme éditable après import dans Canva, là où un graphique importé est un
    objet qu'on ne retouche pas au doigt.

    À réserver aux séries courtes et comparées. Pour une tendance, une
    distribution, un axe temporel, le `chart` reste le bon outil : il porte ses
    axes, sa grille et ses infobulles.
    """
    teintes = teintes or teintes_serie(c, len(valeurs))
    haut = max(valeurs) or 1
    pas = w / max(len(valeurs), 1)
    largeur = min(pas * 0.66, 96)
    socle = y + h - (34 if libelles else 0)
    els = [rect(id_ + "-base", x, socle, w, 2, c["filet"])]
    for i, v in enumerate(valeurs):
        hb = max((socle - y - (30 if valeurs_visibles else 0)) * (v / haut), 3)
        bx = x + pas * i + (pas - largeur) / 2
        els.append(rect(f"{id_}-b{i}", round(bx), round(socle - hb),
                        round(largeur), round(hb), teintes[i % len(teintes)],
                        radius=6))
        if valeurs_visibles:
            els.append(txt(f"{id_}-v{i}", round(bx), round(socle - hb - 34),
                           round(largeur), 30, str(v), size=20, weight=700,
                           color=c["titre_couleur"], font=c["police_chiffres"],
                           align="center"))
        if libelles and i < len(libelles):
            els.append(txt(f"{id_}-l{i}", round(bx - 12), socle + 10,
                           round(largeur + 24), 26, libelles[i], size=16,
                           color=c["attenue"], font=c["police_corps"],
                           align="center"))
    return els


def teintes_serie(c, n):
    """`n` teintes prises dans la gradation de la charte, du soutenu au pâle.

    Inventer une couleur par série produit un arc-en-ciel qui n'appartient à
    aucune charte. La règle « un accent » ne dit pas « une seule teinte » : elle
    dit qu'elles descendent toutes de la même famille.
    """
    g = c["gradation"]
    if n <= len(g):
        return g[:n]
    return [g[i % len(g)] for i in range(n)]


def titre(c, id_, html, y=136, h=126, size=None, w=1088, color=None):
    """Titre de slide, ancré en haut, sur deux lignes par défaut.

    La hauteur tient deux lignes parce qu'un titre autoporteur — celui qui dit
    le message plutôt que de nommer le sujet — est rarement assez court pour
    une seule. Réserver un espace qui suffit évite de découvrir le débordement
    au rendu ; le texte étant ancré en haut, une boîte trop haute ne se voit pas.

    Le contenu de la slide commence alors à y = 268.
    """
    return txt(id_, 96, y, w, h, html,
               size=size or c["echelle"]["titre"], weight=700,
               color=color or c["titre_couleur"], font=c["police_titre"],
               lh=1.15, role="title")


def slide(id_, elements, notes, background=None, transition="morph",
          state_of=None, name=None, hidden=False):
    """Une slide. `notes` n'est pas optionnel par choix : les notes voyagent
    dans le fichier et servent de trame orale — un deck sans notes oblige son
    auteur à se souvenir de ce qu'il voulait dire.

    `state_of` fait de la slide une variante d'une autre, atteinte seulement par
    un `link` (les flèches la sautent, ← revient au parent). C'est le bon outil
    pour un « cliquer pour dérouler » : le fil linéaire reste court, le détail
    est à un clic.
    """
    s = {"id": id_, "transition": transition, "notes": notes,
         "elements": elements}
    if background:
        s["background"] = background
    if state_of:
        s["stateOf"] = state_of
    if name:
        s["name"] = name          # texte brut : les entités HTML s'y affichent
    if hidden:                    # littéralement (&eacute; reste &eacute;)
        s["hidden"] = True
    return s


def document(titre_deck, c, slides, meta=None, layouts=None, assets=None,
             fonts=None, readonly=False, notes_publiques=False):
    """Assemble le document. Ni `docId` ni `collab` : l'app forge l'identité à
    la première ouverture. En écrire un ici casserait l'identité du document.

    `readonly=True` produit un fichier de remise : il démarre directement en
    présentation, sans éditeur. C'est la forme à publier — et comme le document
    est forgé ici et n'a jamais été ouvert-enregistré, il ne porte aucun
    identifiant de session. Voir references/publication.md.

    `notes_publiques=True` déclare que les notes orateur ont été relues pour le
    destinataire. Elles voyagent dans le fichier et la vue orateur les affiche :
    des notes de travail (« point de débat probable avec X », « bloqué côté
    client ») partent avec le lien. Le contrôle refuse de produire un fichier
    `readonly` sans cette déclaration, parce que l'oubli est silencieux et
    irréversible une fois le lien transmis.
    """
    # Le fond du thème ne suffit pas : le mode PRÉSENTATION ne l'applique pas et
    # retombe sur du noir. C'est le mode dans lequel s'ouvre le fichier de
    # remise — donc le défaut n'existe que dans le fichier livré au client, et
    # reste invisible pendant toute la composition, l'éditeur affichant
    # correctement le fond du thème. D'où le fond posé sur CHAQUE slide.
    # Une slide qui déclare le sien (couverture sombre, intercalaire) le garde.
    for s in slides:
        s.setdefault("background", c["fond"])

    doc = {
        "format": "bento/slides", "version": 1, "title": titre_deck,
        "size": dict(CANVAS),
        "theme": {"background": c["fond"], "color": c["encre"],
                  "accent": c["accent"], "fontFamily": c["police_corps"]},
        "slides": slides,
    }
    if meta:
        doc["meta"] = meta
    if layouts:
        doc["layouts"] = layouts
    if assets:
        doc["assets"] = assets
    if fonts:
        doc["fonts"] = fonts
    if readonly:
        doc["readonly"] = True
        doc["_notes_relues"] = bool(notes_publiques)   # lu puis retiré par controle()
    return doc


# ─── Fabrication ─────────────────────────────────────────────────────────────

def runtime(dest):
    """Assure la présence du fichier hôte. Le runtime est l'app entière (~670
    Ko) : le deck n'a besoin d'aucune installation chez celui qui l'ouvre.

    ⚠️ Le fichier de sortie est AUSSI le cache de runtime : s'il existe déjà et
    porte le bloc `#bento-doc`, il est réutilisé tel quel plutôt que
    re-téléchargé. C'est cette réutilisation qui rendait une contamination
    permanente par fichier — d'où le désinfectant posé sur les DEUX chemins,
    celui du téléchargement ET celui de la réutilisation. Le poser sur le seul
    téléchargement aurait laissé infecté tout deck déjà sorti une fois.
    """
    p = pathlib.Path(dest)
    if p.exists() and 'id="bento-doc"' in p.read_text(encoding="utf-8"):
        return _sans_script_tiers(p)
    req = urllib.request.Request(RUNTIME_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        p.write_bytes(r.read())
    if 'id="bento-doc"' not in p.read_text(encoding="utf-8"):
        raise RuntimeError(f"Runtime téléchargé sans bloc #bento-doc : {p}")
    return _sans_script_tiers(p)


def _sans_script_tiers(p):
    """Retire du fichier hôte tout `<script>` chargé depuis un hôte distant.

    Le runtime servi par `bento.page` arrive avec le beacon Cloudflare de SON
    hébergeur — `static.cloudflareinsights.com`, token `08c37cb0…`, qui n'est
    l'analytics de personne ici. Mesuré le 2026-09-07 sur un téléchargement
    neuf : le runtime en porte exactement un, et c'est sa SEULE sortie réseau.
    Le retirer ne coupe aucune mesure d'audience ; le garder fait appeler un
    tiers à chaque ouverture d'un livrable, chez le client.

    N'écrit que s'il a retiré quelque chose : un `write_text` inutile touche la
    date de modification, et ces fichiers vivent dans OneDrive.
    """
    html = p.read_text(encoding="utf-8")
    propre, n = _SCRIPT_TIERS.subn("", html)
    if n:
        p.write_text(propre, encoding="utf-8")
    return p


def controle_esthetique(doc, c):
    """Contrôle les règles de composition relevées sur le template.

    Ce sont des avis, pas des refus : une règle de style a toujours une
    exception défendable, et `build()` ne bloque que sur ce qui casse. Ce qui
    est vérifiable mécaniquement l'est ; le reste — un titre est-il vraiment
    autoporteur — demande un lecteur.
    """
    avis = []
    titre_ok = {c["titre_couleur"].lower(), c["titre_variante"].lower(),
                "#ffffff"}
    for s in doc["slides"]:
        for e in s.get("elements", []):
            if e.get("role") != "title" or e.get("type") != "text":
                continue
            if (e.get("color") or "").lower() not in titre_ok:
                avis.append(
                    f"{s['id']}/{e['id']} : titre en {e.get('color')} — sur le "
                    "template, 100 % des titres sont en couleur de titre")
            if e.get("fontWeight", 400) < 600:
                avis.append(f"{s['id']}/{e['id']} : titre en graisse "
                            f"{e.get('fontWeight')} — le gras est la règle")
        # Respiration sous le titre. Un titre sur deux lignes descend plus bas
        # que sa position déclarée, et le texte qui suit vient se coller
        # dessous : ça ne chevauche pas, donc aucun contrôle ne le voit, mais
        # à l'écran les deux blocs se touchent et la hiérarchie se perd.
        for t in [e for e in s.get("elements", [])
                  if e.get("role") == "title" and e.get("type") == "text"]:
            lignes = 1 + t.get("html", "").lower().count("<br")
            bas_reel = t["y"] + lignes * t.get("fontSize", 50) * t.get("lineHeight", 1.15)
            for e in s.get("elements", []):
                if e.get("type") != "text" or e is t or e["y"] < t["y"]:
                    continue
                if 0 <= e["y"] - bas_reel < 24:
                    avis.append(
                        f"{s['id']}/{e['id']} : {e['y'] - bas_reel:.0f} px sous "
                        f"le titre — compter 24 px au moins, sinon les deux "
                        "blocs se touchent")
        # L'accent marque, il ne compose pas : il n'apparaît qu'à partir de 20 px.
        for e in s.get("elements", []):
            if (e.get("type") == "text" and e.get("fontSize", 99) < 20
                    and (e.get("color") or "").lower() == c["accent"].lower()
                    and not e.get("letterSpacing")):
                avis.append(f"{s['id']}/{e['id']} : accent sur du texte de "
                            f"{e['fontSize']} px — l'accent met en avant, "
                            "il ne compose pas du corps")
    return avis


def controle(doc):
    """Contrôle statique. Rend la liste des anomalies (vide = rien à signaler).

    Ce contrôle ne remplace pas `window.bento.validate()` dans le navigateur :
    lui seul mesure le texte avec le vrai moteur de rendu et voit les
    débordements. Celui-ci attrape ce qui est vérifiable sans rendu — et
    surtout la fuite de session, qui ne se voit nulle part ailleurs.
    """
    pbs = []
    if doc.get("readonly") and not doc.pop("_notes_relues", False):
        pbs.append(
            "Fichier de remise (`readonly`) sans relecture des notes déclarée. "
            "Les notes orateur voyagent dans le fichier et la vue orateur les "
            "affiche : des notes de travail partiraient avec le lien. Les relire, "
            "puis passer `notes_publiques=True`."
        )
    doc.pop("_notes_relues", None)
    if "collab" in doc or "docId" in doc:
        pbs.append(
            "FUITE : le document porte `collab` ou `docId`. Les clés de session "
            "voyagent avec le fichier — quiconque le reçoit peut écrire dedans. "
            "Repartir d'une copie read-only."
        )
    if "size" not in doc or "theme" not in doc:
        pbs.append("`size` et `theme` sont obligatoires — sans eux l'app ne démarre pas.")
    if not doc.get("theme", {}).get("fontFamily"):
        pbs.append("`theme.fontFamily` manquant — l'app ne démarre pas.")

    ids = [s["id"] for s in doc["slides"]]
    for d in {i for i in ids if ids.count(i) > 1}:
        pbs.append(f"id de slide en double : {d}")

    for s in doc["slides"]:
        eids = [e["id"] for e in s["elements"]]
        for d in {i for i in eids if eids.count(i) > 1}:
            pbs.append(f"{s['id']} : id d'élément en double : {d} "
                       "(le morph apparie par id, un doublon casse l'appariement)")
        if not s.get("notes") and not s.get("stateOf"):
            pbs.append(f"{s['id']} : pas de notes orateur")
        for e in s["elements"]:
            if e["id"].startswith(PREFIXE_DECOR):
                continue
            if e["x"] + e["w"] > CANVAS["width"]:
                pbs.append(f"{s['id']}/{e['id']} : déborde à droite "
                           f"({e['x'] + e['w']} > {CANVAS['width']})")
            if e["y"] + e["h"] > CANVAS["height"]:
                pbs.append(f"{s['id']}/{e['id']} : déborde en bas "
                           f"({e['y'] + e['h']} > {CANVAS['height']})")
            if e.get("type") == "text" and e.get("fontSize", 99) < 16:
                pbs.append(f"{s['id']}/{e['id']} : {e['fontSize']} px sous le "
                           "plancher de 16 px — c'est le contenu qu'il faut couper")

    cibles = set(ids)
    for s in doc["slides"]:
        for e in s["elements"]:
            if e.get("link") and e["link"] not in cibles:
                pbs.append(f"{s['id']}/{e['id']} : link vers une slide "
                           f"inexistante ({e['link']})")
    return pbs


def build(doc, dest, ouvrir=False, charte_=None):
    """Injecte `doc` dans le fichier `dest` et contrôle. Rend le chemin.

    Le `<` est échappé en `\\u003c` : sans ça, un `</script>` dans du contenu
    fermerait le bloc et casserait le fichier entier.
    """
    p = runtime(dest)
    pbs = controle(doc)
    if pbs:
        raise AssertionError("Contrôle échoué :\n  - " + "\n  - ".join(pbs))

    html = p.read_text(encoding="utf-8")
    if not _BLOC.search(html):
        raise RuntimeError(f"Bloc #bento-doc introuvable dans {p}")
    charge = json.dumps(doc, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    html = _BLOC.sub(lambda m: m.group(1) + "\n" + charge + "\n" + m.group(3),
                     html, count=1)
    p.write_text(html, encoding="utf-8")

    relu = json.loads(_BLOC.search(p.read_text(encoding="utf-8"))
                      .group(2).replace("\\u003c", "<"))
    if relu["title"] != doc["title"]:
        raise RuntimeError("Le document réinjecté ne se relit pas à l'identique")

    n_etats = sum(1 for s in doc["slides"] if s.get("stateOf"))
    n_el = sum(len(s["elements"]) for s in doc["slides"])
    print(f"OK — {len(doc['slides'])} slides ({n_etats} états), {n_el} éléments "
          f"→ {p}")
    if charte_:
        for a in controle_esthetique(doc, charte_):
            print(f"   · {a}")
    if ouvrir:
        subprocess.run(["open", str(p)], check=False)
    return p
