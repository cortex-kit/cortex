#!/usr/bin/env python3
"""notice.py — régénère etat.json et notice.html d'un atelier _cortex/, puis ouvre la notice.

Appelé en fin de chaque maillon (section « Notice » de son SKILL.md). Il ne lance
rien d'autre : la notice propose la phrase suivante, la personne la prononce ou
non (invariant I10, aucun maillon n'invoque le suivant). stdlib pure.

Usage : python3 notice.py --atelier <chemin de _cortex/> [--no-open]
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI))
import etat  # noqa: E402
import rend_notice  # noqa: E402


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


def main():
    p = argparse.ArgumentParser(description="Régénère et ouvre la notice d'un atelier Cortex.")
    p.add_argument("--atelier", required=True, help="chemin du dossier _cortex/")
    p.add_argument("--no-open", action="store_true", help="régénérer sans ouvrir")
    a = p.parse_args()
    atelier = Path(a.atelier).expanduser()
    if not atelier.is_dir():
        print(f"[notice] atelier introuvable : {a.atelier} — rien à régénérer")
        return 0
    _, pivot = etat.ecrire(atelier)
    html = atelier / "notice.html"
    html.write_text(rend_notice.rendre(pivot), encoding="utf-8")
    n = len(pivot["etapes"])
    print(f"OK — {html} : {etat.faites(pivot)}/{n} étape(s) faite(s)")
    if not a.no_open and not ouvrir(html):
        print("[notice] aucun ouvreur disponible : ouvrez le fichier ci-dessus à la main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
