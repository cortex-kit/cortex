#!/usr/bin/env python3
"""rend_notice.py — rend le pivot d'état en notice pas à pas. stdlib pure.

Un seul fichier HTML, autoportant : styles embarqués, polices système, zéro
URL distante. Il s'ouvre par double-clic sur une machine sans réseau.

Ordre de la page, pensé pour un novice :
  1. l'étape courante en tête, avec la phrase à dire à Claude Code en évidence ;
  2. les étapes à venir, en une ligne chacune ;
  3. les étapes faites, repliées ;
  4. la notice complète (le texte de notice.md).

Usage (`py` sous Windows vaut `python3`) :
    python3 rend_notice.py --pivot <etat.json> --sortie <notice.html> [--no-open]
    python3 rend_notice.py --autotest
"""

import argparse
import html
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI))
from etat import LIBELLES, PHRASES, RAISON_SOLO  # noqa: E402


# Le texte de la notice : à côté de ce script (dépôt et zip).
def _notice_md():
    cand = _ICI / "notice.md"
    if cand.is_file():
        return cand.read_text(encoding="utf-8")
    raise FileNotFoundError("notice.md introuvable à côté de rend_notice.py.")


# Ce que chaque étape fait, en une phrase pour la personne. Affiché sous le
# nom de l'étape ; le nom et l'état viennent du pivot, jamais d'ici.
RESUMES = {
    0: "Votre ordinateur reçoit les quelques outils nécessaires, et votre messagerie est reconnue.",
    1: "Quelques questions : qui vous êtes, où sont vos dossiers, ce que l'outil peut regarder.",
    2: "L'outil compte vos dossiers et vos fichiers, sans les lire en profondeur.",
    3: "Vos grandes familles d'activité, décidées sur preuve et confirmées par vous.",
    4: "Votre second cerveau est créé, vide et sain.",
    5: "Vos projets réels y entrent, sous forme de fiches qui pointent vers vos vrais fichiers.",
    6: "Des assistants sur mesure, si l'usage le justifie. Souvent la réponse honnête est « pas encore ».",
    7: "Une fiche de reprise pour vous dans six mois, et deux rendez-vous de suivi.",
    8: "Plusieurs cerveaux reliés à un commun, pour une société. Sans objet pour une personne seule.",
}


def ouvrir(chemin):
    """Ouvre le fichier avec l'ouvreur de la plateforme, sans jamais bloquer."""
    systeme = platform.system()
    if systeme == "Darwin":
        cmd = ["open", str(chemin)]
    elif systeme == "Windows":
        cmd = ["cmd", "/c", "start", "", str(chemin)]
    else:
        cmd = ["xdg-open", str(chemin)]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False  # session distante ou conteneur : le fichier est là, on le dit


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


def _detail(e):
    if e["artefact"] is None and e["etat"] == "faite_deduite":
        return html.escape(e["raison"])
    if e["etat"] == "arbitre" and e.get("raison"):
        if e["raison"] == RAISON_SOLO:
            return "sans objet pour une personne seule"
        return "sans objet : " + html.escape(e["raison"])
    if not e["present"]:
        return html.escape(RESUMES.get(e["numero"], ""))
    passes = sum(1 for c in e["controles"] if c["verdict"] == "passe")
    arbitres = sum(1 for c in e["controles"] if c["verdict"] == "arbitre")
    autres = len(e["controles"]) - passes - arbitres
    morceaux = []
    if e["controles"]:
        morceaux.append(f"{passes} contrôle(s) passé(s)")
    if arbitres:
        morceaux.append(f"{arbitres} arbitré(s)")
    if autres:
        morceaux.append(f"<strong>{autres} en défaut</strong>")
    detail = ", ".join(morceaux) or html.escape(RESUMES.get(e["numero"], ""))
    if e["modifie_le"]:
        detail += f" · le {html.escape(e['modifie_le'])}"
    return detail


def _ligne(e):
    return (f"<tr><td class=\"num\">{e['numero']}</td>"
            f"<td class=\"nom\">{html.escape(e['nom'])}<br>"
            f"<small>{html.escape(e['maillon'])}</small></td>"
            f"<td>{_pastille(e['etat'])}</td>"
            f"<td class=\"detail\">{_detail(e)}</td></tr>")


def _table(etapes):
    return "<table>\n" + "\n".join(_ligne(e) for e in etapes) + "\n</table>"


def _courante(pivot):
    n = pivot.get("etape_suivante")
    phrase = html.escape(pivot.get("phrase_suivante", ""))
    if n is None:
        return (f'<section class="courante"><p class="sur">Tout est installé</p>'
                f"<h2>Votre second cerveau est en place</h2>"
                f"<p>Il reste un seul geste, à répéter à la fin de chaque séance de travail.</p>"
                f'<p class="phrase">Dites à Claude Code : <strong>« {phrase} »</strong></p>'
                f"</section>")
    e = next(x for x in pivot["etapes"] if x["numero"] == n)
    en_cours = e["etat"] == "en_cours"
    sur = "Étape en cours" if en_cours else "Prochaine étape"
    consigne = ("Cette étape a commencé. Pour la reprendre, dites à Claude Code :"
                if en_cours else "Pour la lancer, dites à Claude Code :")
    # Rang affiché, pas numéro d'étape : le novice lit « 1 sur 9 », jamais « 0 sur 8 ».
    return (f'<section class="courante"><p class="sur">{sur} · {n + 1} sur {len(pivot["etapes"])}</p>'
            f"<h2>{html.escape(e['nom'])}</h2>"
            f"<p>{html.escape(RESUMES.get(n, ''))}</p>"
            f'<p class="phrase">{consigne} <strong>« {phrase} »</strong></p>'
            f"<p class=\"meta\">La notice propose, elle ne lance rien : vous décidez d'enchaîner.</p>"
            f"</section>")


_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Second cerveau : notice pas à pas</title>
<style>
  body {{ margin: 0; background: #FBFAF8; color: #1C1C1C;
         font: 17px/1.55 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 40px 24px 80px; }}
  h1 {{ font-size: 34px; line-height: 1.15; margin: 1.6em 0 .5em; }}
  h2 {{ font-size: 24px; margin: 1.8em 0 .4em; }}
  h3 {{ font-size: 19px; margin: 1.4em 0 .3em; }}
  code {{ background: #EFEEE9; border-radius: 4px; padding: 1px 6px; font-size: .9em; }}
  .bord {{ background: #FFFFFF; border: 1px solid #E5E5E3; border-radius: 12px;
           padding: 24px 28px; margin-top: 24px; }}
  .bord h2, .courante h2 {{ margin: 0 0 4px; }}
  .courante {{ background: #1C2A3A; color: #FFFFFF; border-radius: 12px;
               padding: 28px 32px; margin-top: 8px; }}
  .courante .sur {{ margin: 0; font-size: 13px; letter-spacing: .08em;
                    text-transform: uppercase; color: #A9B8C9; }}
  .courante .phrase {{ font-size: 21px; margin: 18px 0 6px; }}
  .courante .phrase strong {{ background: #F4D35E; color: #1C1C1C;
                              border-radius: 8px; padding: 4px 12px; }}
  .courante .meta {{ color: #A9B8C9; }}
  .meta {{ color: #6B7280; font-size: 14px; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ border-top: 1px solid #EFEFEC; padding: 10px 10px 10px 0; vertical-align: top; }}
  tr:first-child td {{ border-top: none; }}
  .num {{ color: #94A7B3; font-weight: 700; width: 1.5em; }}
  .nom {{ font-weight: 600; width: 11em; }}
  .nom small {{ color: #6B7280; font-weight: 400; }}
  .detail {{ color: #4B5563; font-size: 15px; }}
  .pastille {{ display: inline-block; border-radius: 99px; padding: 2px 12px;
               font-size: 13px; font-weight: 600; white-space: nowrap; }}
  details summary {{ cursor: pointer; font-weight: 600; margin: 0 0 8px; }}
</style>
</head>
<body>
<main>
<p class="meta">{meta}</p>
{courante}
<section class="bord">
<h2>Ce qui vient ensuite</h2>
{a_venir}
</section>
<section class="bord">
<details {ouvert}><summary>{titre_faites}</summary>
{faites}
</details>
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
    if pivot.get("profil"):
        morceaux.append(f"profil {html.escape(pivot['profil'])}")
    morceaux.append(f"généré le {html.escape(pivot.get('genere_le', ''))}")
    morceaux.append(f"paquet {html.escape(str(pivot.get('paquet', '')))}")
    n = pivot.get("etape_suivante")
    faites = [e for e in pivot["etapes"]
              if e["etat"].startswith("faite") or e["etat"] == "arbitre"]
    a_venir = [e for e in pivot["etapes"] if e not in faites and e["numero"] != n]
    if n is not None:
        a_venir = [e for e in a_venir if e["numero"] > n]
    return _PAGE.format(
        meta=" · ".join(morceaux),
        courante=_courante(pivot),
        a_venir=_table(a_venir) if a_venir else "<p>Rien : c'est la dernière.</p>",
        titre_faites=(f"{len(faites)} étape(s) faite(s) ou sans objet"
                      if faites else "Aucune étape faite pour l'instant"),
        faites=_table(faites) if faites else "",
        ouvert="open" if n is None else "",
        notice=_md_vers_html(notice_md if notice_md is not None else _notice_md()),
    )


def _autotest():
    import etat
    with tempfile.TemporaryDirectory() as tmp:
        page = rendre(etat.generer(tmp), notice_md="# Titre\n\nUn `code` **gras**.\n- a\n- b\n")
        assert PHRASES[0] in page and "Prochaine étape" in page
        assert "1 sur 9" in page and "0 sur 8" not in page   # défaut 5
        assert page.count("À faire") == 8, page.count("À faire")   # neuf moins la courante
        assert not re.search(r"https?://", page)
        assert "<strong>gras</strong>" in page and "<ul><li>a</li><li>b</li></ul>" in page
        (Path(tmp) / "poste.json").write_text('{"notice_ouverte_le": "x"}', encoding="utf-8")
        page = rendre(etat.generer(tmp), notice_md="")
        assert PHRASES[1] in page and "1 étape(s) faite(s)" in page
        assert "2 sur 9" in page
    print("rend_notice.py : auto-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description="Pivot d'état → notice.html pas à pas.")
    p.add_argument("--pivot", help="chemin de etat.json")
    p.add_argument("--sortie", help="fichier HTML à écrire")
    p.add_argument("--no-open", action="store_true", help="écrire sans ouvrir (recette)")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.pivot or not a.sortie:
        p.error("--pivot et --sortie sont requis")
    pivot = json.loads(Path(a.pivot).expanduser().read_text(encoding="utf-8"))
    sortie = Path(a.sortie).expanduser()
    sortie.write_text(rendre(pivot), encoding="utf-8")
    print(f"OK — {sortie} : {len(pivot['etapes'])} étapes, "
          f"suivante « {pivot.get('phrase_suivante', '')} »")
    if not a.no_open and not ouvrir(sortie):
        print("[notice] aucun ouvreur disponible : ouvrez le fichier ci-dessus à la main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
