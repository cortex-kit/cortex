#!/usr/bin/env python3
"""notice.py — régénère etat.json et notice.html d'un atelier _cortex/, puis ouvre la notice.

Appelé en fin de chaque maillon (section « Notice » de son SKILL.md). Il pose
`notice_ouverte_le` dans poste.json à la première régénération, même avec
--no-open : la notice est présentée, l'étape 0 est faite. Il ne lance rien
d'autre : la notice propose la phrase suivante, la personne la prononce ou non
(invariant I10, aucun maillon n'invoque le suivant). Sort toujours en 0, un
tableau de bord qui manque ne doit jamais arrêter la chaîne. stdlib pure.

Usage : python3 notice.py --atelier <chemin de _cortex/> [--no-open]
        python3 notice.py --autotest
"""

import argparse
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI))
import etat  # noqa: E402
import rend_notice  # noqa: E402


def marquer_notice_ouverte(atelier):
    """Pose `notice_ouverte_le` dans poste.json à la première régénération, même
    avec --no-open : la notice est présentée, l'étape 0 est faite (amendement §5).
    Sans poste.json (atelier vierge du zip), il n'y a rien à marquer."""
    chemin = Path(atelier) / "poste.json"
    if not chemin.is_file():
        return False
    try:
        poste = json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError:
        return False                      # poste.json illisible : etat.py le dira
    if poste.get("notice_ouverte_le"):
        return False
    poste["notice_ouverte_le"] = datetime.now().isoformat(timespec="seconds")
    chemin.write_text(json.dumps(poste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def regenerer(atelier):
    """Écrit etat.json et notice.html dans l'atelier. Rend (chemin html, pivot)."""
    atelier = Path(atelier)
    marquer_notice_ouverte(atelier)
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
        # Défaut 7 : un poste.json sans notice_ouverte_le est marqué ici, une seule fois.
        poste = Path(tmp) / "poste.json"
        poste.write_text('{"format": "cortex/poste", "notice_ouverte_le": ""}', encoding="utf-8")
        assert marquer_notice_ouverte(tmp) is True
        pose = json.loads(poste.read_text(encoding="utf-8"))["notice_ouverte_le"]
        assert pose and marquer_notice_ouverte(tmp) is False
        _, pivot = regenerer(tmp)
        assert pivot["etapes"][0]["etat"] == "faite"
        assert json.loads(poste.read_text(encoding="utf-8"))["notice_ouverte_le"] == pose
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
    print(f"OK — {html} : {etat.compte(pivot)} étape(s)")
    print(f"Prochaine phrase à dire : « {pivot['phrase_suivante']} »")
    if not a.no_open and not rend_notice.ouvrir(html):
        print("[notice] aucun ouvreur disponible : ouvrez le fichier ci-dessus à la main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
