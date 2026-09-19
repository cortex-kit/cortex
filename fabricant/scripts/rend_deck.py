#!/usr/bin/env python3
"""rend_deck.py — rend le pivot d'état en deck bento. stdlib + skill presentation.

Second rendu du MÊME pivot que le tableau de bord : mêmes étapes, mêmes
libellés d'état (importés de etat.py), aucune source secondaire. Le deck sert
à montrer, pas à suivre — une réunion, une démonstration, un lien.

Hors ligne par construction : le runtime bento (~670 Ko) est embarqué dans
modeles/bento-runtime.html et copié vers la sortie AVANT l'injection, si bien
que bento.build() n'a jamais rien à télécharger.

Usage (`py` sous Windows vaut `python3`) :
    python3 rend_deck.py --pivot <etat.json> --sortie <deck.bento.html>
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

_ICI = Path(__file__).resolve().parent
_DEPOT = _ICI.parent.parent
sys.path.insert(0, str(_DEPOT / "skills" / "cortex-4-installation" / "scripts"))
from etat import LIBELLES  # noqa: E402

# La skill presentation vit dans skills/ du dépôt. Sondée, jamais codée en dur.
# Absente du kit depuis le 2026-09-19 : l'import ne bloque plus, seul le rendu
# échoue, pour que la recette puisse importer ce module et mesurer le reste.
_PRESENTATION = _DEPOT / "skills" / "presentation" / "scripts"
_MANQUE = "[erreur] skill presentation introuvable dans skills/ ; le deck se rend avec elle."
if (_PRESENTATION / "bento.py").is_file():
    sys.path.insert(0, str(_PRESENTATION))
    from chartes import charte  # noqa: E402
    from bento import txt, rect, titre, runhead, slide, document, build  # noqa: E402
else:
    charte = None

_RUNTIME = _ICI.parent / "modeles" / "bento-runtime.html"

_ENCRE_ETAT = {  # encre du libellé d'état sur fond clair
    "a_faire": "#6B7280", "en_cours": "#8A6D1A", "faite": "#1F6E43",
    "faite_deduite": "#1F6E43", "arbitre": "#9A5B1F", "illisible": "#9B1C1C",
}


def _doc(pivot):
    C = charte("neutre")
    org = pivot.get("organisation") or "Second cerveau"
    faites = sum(1 for e in pivot["etapes"] if e["etat"].startswith("faite"))

    couverture = slide("cover", [
        rect("decor-fond", 0, 0, 1280, 720, C["fond_sombre"]),
        rect("rail", 96, 300, 40, 5, C["accent_doux"]),
        txt("runhead", 96, 238, 700, 48, "SECOND CERVEAU", size=18, weight=600,
            color=C["accent_doux"], font=C["police_corps"], ls=2.4),
        txt("cover-t", 96, 328, 1088, 130, org, size=64, weight=700,
            color="#FFFFFF", font=C["police_titre"], lh=1.0, role="title"),
        txt("cover-s", 96, 470, 900, 60,
            f"Installation : {faites}/7 étape(s) faite(s) · "
            f"généré le {pivot.get('genere_le', '')} · paquet {pivot.get('paquet', '')}",
            size=22, color=C["accent_doux"], font=C["police_corps"],
            role="subtitle"),
    ], notes="Couverture. L'état vient du pivot _cortex/etat.json, jamais "
             "d'une saisie : ce deck ne peut pas raconter une autre "
             "installation que celle qui a eu lieu.",
       background=C["fond_sombre"], transition="none")

    els = runhead(C, "OÙ EN EST L'INSTALLATION") + [
        titre(C, "t-etat", "Les sept étapes"),
    ]
    y = 268
    for e in pivot["etapes"]:
        i = e["numero"]
        libelle = LIBELLES.get(e["etat"], e["etat"])
        els += [
            txt(f"num-{i}", 96, y, 40, 34, str(i), size=20, weight=700,
                color=C["accent_doux"], font=C["police_chiffres"]),
            txt(f"nom-{i}", 150, y, 430, 34, e["nom"], size=21, weight=600,
                color=C["encre"], font=C["police_corps"]),
            txt(f"etat-{i}", 600, y, 220, 34, libelle, size=18, weight=600,
                color=_ENCRE_ETAT.get(e["etat"], C["attenue"]),
                font=C["police_corps"]),
            txt(f"art-{i}", 840, y, 344, 34,
                e["artefact"] or "sans artefact (voir note)", size=16,
                color=C["attenue"], font=C["police_corps"]),
        ]
        y += 52
    els.append(txt("raison-03", 96, y + 6, 1088, 60,
                   next(e["raison"] for e in pivot["etapes"] if e["artefact"] is None),
                   size=16, color=C["attenue"], font=C["police_corps"]))
    etat_s = slide("etat", els,
                   notes="Les sept étapes, projetées depuis le pivot. La "
                         "ligne 4 n'attend aucun artefact : sa sortie est le "
                         "vault lui-même, sa preuve le lint à 0.")

    return document(
        f"{org} — installation du second cerveau", C, [couverture, etat_s],
        meta={"cortex_etapes": [{"numero": e["numero"], "nom": e["nom"],
                                 "etat": e["etat"],
                                 "libelle": LIBELLES.get(e["etat"], e["etat"])}
                                for e in pivot["etapes"]],
              "genere_le": pivot.get("genere_le", ""),
              "paquet": pivot.get("paquet", "")},
        readonly=True, notes_publiques=True)


def rendre(pivot, sortie):
    """Copie le runtime embarqué puis injecte le document. Zéro réseau."""
    if charte is None:
        raise RuntimeError(_MANQUE)
    if not _RUNTIME.is_file():
        sys.exit(f"[erreur] runtime bento absent : {_RUNTIME}")
    sortie = Path(sortie)
    shutil.copyfile(_RUNTIME, sortie)
    return build(_doc(pivot), sortie)


def main():
    p = argparse.ArgumentParser(description="Pivot d'état → deck bento.")
    p.add_argument("--pivot", required=True, help="chemin de etat.json")
    p.add_argument("--sortie", required=True, help="fichier .bento.html à écrire")
    a = p.parse_args()
    pivot = json.loads(Path(a.pivot).read_text(encoding="utf-8"))
    rendre(pivot, a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
