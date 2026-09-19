#!/usr/bin/env python3
"""Hook Stop du vault : rappelle la clôture si des fichiers ont changé.

Ne bloque jamais l'arrêt : un rappel, pas une contrainte. La sortie JSON porte
`systemMessage`, la seule forme qu'un hook Stop montre à la personne.

Usage : python3 .claude/hooks/stop.py [--autotest]
"""
import json
import subprocess
import sys


def message(porcelain):
    fichiers = [l for l in porcelain.splitlines() if l.strip()]
    if not fichiers:
        return ""
    return (f"{len(fichiers)} fichier(s) modifié(s) sans clôture. "
            "Dites « clôture » pour garder la raison de ce qui vient de changer.")


def main():
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        porcelain = r.stdout if r.returncode == 0 else ""
    except FileNotFoundError:
        porcelain = ""
    m = message(porcelain)
    if m:
        print(json.dumps({"systemMessage": m}, ensure_ascii=False))
    return 0


def _autotest():
    assert message("") == ""
    assert message(" M 20 - Projets/X.md\n?? y.md\n").startswith("2 fichier(s)")
    print("OK stop.py")
    return 0


if __name__ == "__main__":
    sys.exit(_autotest() if "--autotest" in sys.argv else main())
