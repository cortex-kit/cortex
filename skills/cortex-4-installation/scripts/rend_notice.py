#!/usr/bin/env python3
"""rend_notice.py — rend le pivot d'état en tableau de bord HTML. stdlib pure.

Un seul fichier en sortie : le tableau de bord en haut (les sept étapes,
projetées depuis le pivot), la notice complète en dessous (le texte de
modeles/notice.md). Autoportant : styles embarqués, polices système, zéro URL
distante. Il s'ouvre par double-clic sur une machine sans réseau.

Usage (`py` sous Windows vaut `python3`) :
    python3 rend_notice.py --pivot <etat.json> --sortie <notice.html>
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI))
from etat import LIBELLES  # noqa: E402  — libellés partagés avec le deck

# Le texte de la notice : dans modeles/ à côté du dossier scripts/ (dépôt), ou
# dans le même dossier que ce script (zip, déposé par fabrique.py). On sonde.
def _notice_md():
    for cand in (_ICI.parent / "modeles" / "notice.md", _ICI / "notice.md"):
        if cand.is_file():
            return cand.read_text(encoding="utf-8")
    raise FileNotFoundError("notice.md introuvable : ni dans modeles/, ni à côté du script.")


# ── Markdown minimal → HTML ─────────────────────────────────────────────────
# Le sous-ensemble que notice.md s'engage à utiliser : titres #/##/###, listes
# - et 1., gras **, code `, paragraphes. Rien d'autre, à dessein.

def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def _md_vers_html(md):
    out, bloc, mode = [], [], None   # mode: None | 'p' | 'ul' | 'ol'

    def clore():
        nonlocal bloc, mode
        if not bloc:
            return
        if mode == "p":
            out.append("<p>" + _inline(" ".join(bloc)) + "</p>")
        else:
            items = "".join(f"<li>{_inline(i)}</li>" for i in bloc)
            out.append(f"<{mode}>{items}</{mode}>")
        bloc, mode = [], None

    for ligne in md.splitlines():
        nue = ligne.strip()
        m = re.match(r"^(#{1,3})\s+(.*)$", nue)
        if m:
            clore()
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
        elif not nue:
            clore()
        elif nue.startswith("- "):
            if mode != "ul":
                clore()
                mode = "ul"
            bloc.append(nue[2:])
        elif re.match(r"^\d+\.\s", nue):
            if mode != "ol":
                clore()
                mode = "ol"
            bloc.append(re.sub(r"^\d+\.\s+", "", nue))
        elif mode in ("ul", "ol") and ligne.startswith("  "):
            bloc[-1] += " " + nue          # continuation d'un item de liste
        else:
            if mode != "p":
                clore()
                mode = "p"
            bloc.append(nue)
    clore()
    return "\n".join(out)


# ── Tableau de bord ─────────────────────────────────────────────────────────

_COULEURS = {  # pastille par état : fond, encre
    "a_faire": ("#EDEDEA", "#6B7280"),
    "en_cours": ("#FDF2D0", "#8A6D1A"),
    "faite": ("#DCEFE3", "#1F6E43"),
    "faite_deduite": ("#DCEFE3", "#1F6E43"),
    "arbitre": ("#FDE8D8", "#9A5B1F"),
    "illisible": ("#F8DADA", "#9B1C1C"),
}


def _pastille(etat):
    fond, encre = _COULEURS.get(etat, _COULEURS["illisible"])
    return (f'<span class="pastille" style="background:{fond};color:{encre}">'
            f"{html.escape(LIBELLES.get(etat, etat))}</span>")


def _ligne(e):
    if e["artefact"] is None:
        detail = html.escape(e.get("raison", ""))
    elif not e["present"]:
        detail = f"attend <code>{html.escape(e['artefact'])}</code>"
    else:
        passes = sum(1 for c in e["controles"] if c["verdict"] == "passe")
        arbitres = sum(1 for c in e["controles"] if c["verdict"] == "arbitre")
        autres = len(e["controles"]) - passes - arbitres
        morceaux = [f"{passes} contrôle(s) passé(s)"]
        if arbitres:
            morceaux.append(f"{arbitres} arbitré(s)")
        if autres:
            morceaux.append(f"<strong>{autres} en défaut</strong>")
        detail = ", ".join(morceaux)
        if e["modifie_le"]:
            detail += f" · le {html.escape(e['modifie_le'])}"
    return (f"<tr><td class=\"num\">{e['numero']}</td>"
            f"<td class=\"nom\">{html.escape(e['nom'])}<br>"
            f"<small>{html.escape(e['maillon'])}</small></td>"
            f"<td>{_pastille(e['etat'])}</td>"
            f"<td class=\"detail\">{detail}</td></tr>")


_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Second cerveau — notice et tableau de bord</title>
<style>
  body {{ margin: 0; background: #FBFAF8; color: #1C1C1C;
         font: 17px/1.55 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 40px 24px 80px; }}
  h1 {{ font-size: 34px; line-height: 1.15; margin: 1.6em 0 .5em; }}
  h2 {{ font-size: 24px; margin: 1.8em 0 .4em; }}
  h3 {{ font-size: 19px; margin: 1.4em 0 .3em; }}
  code {{ background: #EFEEE9; border-radius: 4px; padding: 1px 6px;
          font-size: .9em; }}
  .bord {{ background: #FFFFFF; border: 1px solid #E5E5E3; border-radius: 12px;
           padding: 24px 28px; margin-top: 32px; }}
  .bord h2 {{ margin: 0 0 4px; }}
  .meta {{ color: #6B7280; font-size: 14px; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ border-top: 1px solid #EFEFEC; padding: 10px 10px 10px 0;
        vertical-align: top; }}
  tr:first-child td {{ border-top: none; }}
  .num {{ color: #94A7B3; font-weight: 700; width: 1.5em; }}
  .nom {{ font-weight: 600; width: 11em; }}
  .nom small {{ color: #6B7280; font-weight: 400; }}
  .detail {{ color: #4B5563; font-size: 15px; }}
  .pastille {{ display: inline-block; border-radius: 99px; padding: 2px 12px;
               font-size: 13px; font-weight: 600; white-space: nowrap; }}
</style>
</head>
<body>
<main>
<section class="bord">
<h2>Où en est l'installation</h2>
<p class="meta">{meta}</p>
<table>
{lignes}
</table>
</section>
{notice}
</main>
</body>
</html>
"""


def rendre(pivot, notice_md=None):
    """Rend la page HTML complète (str) depuis le pivot (dict)."""
    morceaux = []
    if pivot.get("organisation"):
        morceaux.append(html.escape(pivot["organisation"]))
    if pivot.get("conduite"):
        morceaux.append(f"conduite {html.escape(pivot['conduite'])}")
    morceaux.append(f"généré le {html.escape(pivot.get('genere_le', ''))}")
    morceaux.append(f"paquet {html.escape(str(pivot.get('paquet', '')))}")
    return _PAGE.format(
        meta=" · ".join(morceaux),
        lignes="\n".join(_ligne(e) for e in pivot["etapes"]),
        notice=_md_vers_html(notice_md if notice_md is not None else _notice_md()),
    )


def main():
    p = argparse.ArgumentParser(description="Pivot d'état → notice.html.")
    p.add_argument("--pivot", required=True, help="chemin de etat.json")
    p.add_argument("--sortie", required=True, help="fichier HTML à écrire")
    a = p.parse_args()
    pivot = json.loads(Path(a.pivot).read_text(encoding="utf-8"))
    Path(a.sortie).write_text(rendre(pivot), encoding="utf-8")
    print(f"OK — {a.sortie} : {len(pivot['etapes'])} étapes, notice incluse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
