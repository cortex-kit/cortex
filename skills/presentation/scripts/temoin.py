#!/usr/bin/env python3
"""Deck-témoin : éprouve une charte sans contenu réel.

    python3 temoin.py devprom [sortie.html]

Produit quatre slides qui exercent chaque rôle de couleur et chaque famille de
caractères de la charte : couverture sur fond sombre, cartes de chiffres sur
panneau, graphique, tableau. Le contenu est factice — c'est la charte qu'on
regarde, pas le propos.

À passer sur toute charte nouvelle ou modifiée, pour trois raisons qui ne se
voient pas autrement :

  - une police déclarée mais absente du document retombe en silence, et paraît
    correcte sur la machine qui compose ; `validate()` la signale
    (`font-not-embedded`) une fois le témoin ouvert ;
  - deux familles de caractères se comportent différemment à taille égale, donc
    une charte qui bascule titre/corps peut déborder là où une autre tient ;
  - un contraste insuffisant (texte atténué sur panneau, accent sur fond
    sombre) ne se voit qu'à l'écran.

Après génération : ouvrir le fichier, lancer
`window.bento.validate().findings.filter(f => f.severity !== 'info')`, puis
regarder les quatre slides.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chartes import charte, COLS, BANDE          # noqa: E402
from bento import (txt, rect, chart, table, runhead, titre, slide,  # noqa: E402
                   document, build)
from fonts import embarquer                      # noqa: E402


def temoin(marque, sortie=None):
    C = charte(marque)
    E = C["echelle"]
    FT, FC, FN = C["police_titre"], C["police_corps"], C["police_chiffres"]
    nom = C["nom"] or "sans marque"
    slides = []

    # 1. Couverture — fond sombre, police de titre à la taille héroïque
    slides.append(slide("cover", [
        rect("decor-fond", 0, 0, 1280, 720, C["fond_sombre"]),
        rect("rail", 96, 300, 40, 5, C["accent_doux"]),
        txt("runhead", 96, 238, 700, 48, "T&Eacute;MOIN DE CHARTE", size=18,
            weight=600, color=C["accent_doux"], font=FC, ls=2.4),
        txt("cover-t", 96, 328, 940, 190, nom, size=E["hero"], weight=700,
            color="#FFFFFF", font=FT, lh=0.98, role="title"),
        txt("cover-s", 96, 496, 900, 100,
            "Quatre slides pour voir la charte, pas pour dire quelque chose",
            size=E["sous_titre"], color=C["accent_doux"], font=FC,
            role="subtitle", fx={"enter": "fade-up", "order": 1}),
        txt("folio", 1064, 238, 120, 48, "", size=16, weight=500,
            color=C["accent_doux"], font=FC, align="right"),
    ], notes="Couverture. On vérifie ici la police de titre à sa taille "
             "maximale et le contraste du texte clair sur le fond sombre.",
       background=C["fond_sombre"], transition="none"))

    # 2. Chiffres — cartes sur panneau, décompte, texte atténué
    els = runhead(C, "LES CHIFFRES") + [
        titre(C, "t2", "Quatre cartes, quatre d&eacute;comptes"),
    ]
    for i, (n, lbl) in enumerate([("128", "unit&eacute;s trait&eacute;es"),
                                  ("42", "cas identifi&eacute;s"),
                                  ("7", "domaines couverts"),
                                  ("93", "pour cent d'accord")]):
        x = COLS[4]["x"][i]
        els += [
            rect(f"card{i}", x, 300, COLS[4]["w"], 210, C["panneau"], radius=12),
            txt(f"n{i}", x, 318, COLS[4]["w"], 106, n, size=76, weight=700,
                color=C["accent"], font=FN, align="center",
                fx={"countUp": True, "order": i}),
            txt(f"l{i}", x + 20, 430, COLS[4]["w"] - 40, 60, lbl,
                size=E["secondaire"], weight=500, color=C["titre_couleur"],
                font=FC, align="center", lh=1.3),
        ]
    els.append(txt("f2", BANDE["x"], 550, BANDE["w"], 60,
        "Ligne de bas de slide en texte att&eacute;nu&eacute; : c'est le "
        "contraste le plus fragile d'une charte, et celui qu'on ne voit qu'&agrave; "
        "l'&eacute;cran.", size=E["secondaire"], color=C["attenue"], font=FC))
    slides.append(slide("s2", els,
        notes="Cartes de chiffres. On vérifie le décompte, le contraste de "
              "l'accent sur le panneau, et la lisibilité du texte atténué."))

    # 3. Graphique — accent en série, filets d'axe
    slides.append(slide("s3", runhead(C, "LE GRAPHIQUE") + [
        titre(C, "t3", "Une s&eacute;rie &agrave; l'accent, des filets discrets"),
        chart("c3", 96, 240, 700, 340, "bar", {
            "grid": {"left": 44, "right": 12, "top": 20, "bottom": 56},
            "xAxis": {"type": "category",
                      "data": ["Alpha", "Bravo", "Charlie", "Delta", "Echo"],
                      "axisLabel": {"color": C["attenue"], "fontSize": 13},
                      "axisLine": {"lineStyle": {"color": C["filet"]}}},
            "yAxis": {"type": "value",
                      "axisLabel": {"color": C["attenue"], "fontSize": 13},
                      "splitLine": {"lineStyle": {"color": C["filet"]}}},
            "series": [{"type": "bar", "name": "Volume",
                        "data": [24, 18, 31, 12, 27],
                        "itemStyle": {"color": C["accent"], "borderRadius": 6},
                        "barWidth": 62}],
            "tooltip": {"trigger": "item", "formatter": "{b} : {c}"},
        }, fx={"enter": "fade-up"}),
        rect("p3", 848, 240, 336, 340, C["panneau"], radius=12),
        txt("p3t", 880, 272, 272, 40, "Encart lat&eacute;ral", size=20,
            weight=700, color=C["titre_couleur"], font=FT),
        txt("p3b", 880, 322, 272, 240,
            "Un encart sur panneau, avec du <b>gras</b> et une ligne assez "
            "longue pour passer sur plusieurs lignes et r&eacute;v&eacute;ler "
            "un d&eacute;bordement s'il y en a un.",
            size=E["corps"], color=C["titre_couleur"], font=FC, lh=1.45),
    ], notes="Graphique. On vérifie que l'accent tient en aplat, que les filets "
             "d'axe restent discrets, et que l'encart ne déborde pas."))

    # 4. Tableau — en-tête sur fond sombre, zébrures, bordures
    slides.append(slide("s4", runhead(C, "LE TABLEAU") + [
        titre(C, "t4", "En-t&ecirc;te, z&eacute;brures et bordures"),
        table("tbl", 96, 244, BANDE["w"], 380,
              [{"w": 1.2}, {"w": 1}, {"w": 2}, {"w": 0.7}],
              [{"cells": [{"html": "Colonne"}, {"html": "Type"},
                          {"html": "Description"},
                          {"html": "Valeur", "align": "right"}]}] +
              [{"cells": [{"html": f"<b>Ligne {i}</b>"}, {"html": "T&eacute;moin"},
                          {"html": "Une description assez longue pour occuper "
                                   "la cellule"},
                          {"html": str(i * 11), "align": "right"}]}
               for i in range(1, 5)],
              {"headerBg": C["fond_sombre"], "headerColor": "#FFFFFF",
               "zebra": "rgba(0,0,0,0.03)", "borderColor": C["filet"],
               "borderWidth": 1, "cellPadX": 20, "cellPadY": 14,
               "fontSize": 18, "color": C["encre"], "radius": 10},
              fx={"enter": "fade-up"}),
        txt("f4", BANDE["x"], 644, BANDE["w"], 56,
            "Si l'en-t&ecirc;te est illisible ou les z&eacute;brures invisibles, "
            "c'est la charte qu'on ajuste &mdash; jamais ce fichier.",
            size=E["secondaire"], color=C["attenue"], font=FC, lh=1.4),
    ], notes="Tableau. On vérifie le contraste de l'en-tête clair sur fond "
             "sombre, la visibilité des zébrures et la finesse des bordures."))

    assets, fonts = embarquer(C["embarquer"])
    return build(document(f"Témoin de charte — {nom or marque}", C, slides,
                          assets=assets, fonts=fonts),
                 sortie or f"temoin-{marque}.html")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    temoin(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
