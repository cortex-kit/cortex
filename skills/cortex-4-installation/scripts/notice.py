#!/usr/bin/env python3
"""notice.py — régénère etat.json et notice.html d'un atelier _cortex/, puis ouvre la notice.

Appelé en fin de chaque maillon (section « Notice » de son SKILL.md). Il ne lance
rien d'autre : la notice propose la phrase suivante, la personne la prononce ou
non (invariant I10, aucun maillon n'invoque le suivant). Sort toujours en 0,
un tableau de bord qui manque ne doit jamais arrêter la chaîne. stdlib pure.

Usage : python3 notice.py --atelier <chemin de _cortex/> [--no-open]
        python3 notice.py --autotest
"""

import argparse
import sys
import tempfile
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI))
import etat  # noqa: E402
import rend_notice  # noqa: E402


def regenerer(atelier):
    """Écrit etat.json et notice.html dans l'atelier. Rend (chemin html, pivot)."""
    atelier = Path(atelier)
    _, pivot = etat.ecrire(atelier)
    html = atelier / "notice.html"
    html.write_text(rend_notice.rendre(pivot), encoding="utf-8")
    return html, pivot


def _autotest():
    with tempfile.TemporaryDirectory() as tmp:
        html, pivot = regenerer(tmp)
        assert html.is_file() and (Path(tmp) / "etat.json").is_file()
        assert len(pivot["etapes"]) == 9
        assert pivot["phrase_suivante"] in html.read_text(encoding="utf-8")
    print("notice.py : auto-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description="Régénère et ouvre la notice d'un atelier Cortex.")
    p.add_argument("--atelier", help="chemin du dossier _cortex/")
    p.add_argument("--no-open", action="store_true", help="régénérer sans ouvrir")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.atelier:
        print("[notice] --atelier manquant — rien à régénérer")
        return 0
    atelier = Path(a.atelier).expanduser()
    if not atelier.is_dir():
        print(f"[notice] atelier introuvable : {a.atelier} — rien à régénérer")
        return 0
    try:
        html, pivot = regenerer(atelier)
    except Exception as exc:  # noqa: BLE001 — la notice ne bloque jamais la chaîne
        print(f"[notice] régénération impossible : {exc}")
        return 0
    n = len(pivot["etapes"])
    print(f"OK — {html} : {etat.faites(pivot)}/{n} étape(s) faite(s)")
    print(f"Prochaine phrase à dire : « {pivot['phrase_suivante']} »")
    if not a.no_open and not rend_notice.ouvrir(html):
        print("[notice] aucun ouvreur disponible : ouvrez le fichier ci-dessus à la main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
