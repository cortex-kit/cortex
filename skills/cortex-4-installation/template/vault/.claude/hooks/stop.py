#!/usr/bin/env python3
"""Hook Stop du vault : rappelle la clôture si des fichiers ont changé.

Ne bloque jamais l'arrêt : un rappel, pas une contrainte. La sortie JSON porte
`systemMessage`, la seule forme qu'un hook Stop montre à la personne.

Usage : python3 .claude/hooks/stop.py [--autotest]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def racine_vault():
    """Le vault est celui que Claude Code annonce, pas le dossier courant."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def message(porcelain):
    fichiers = [l for l in porcelain.splitlines() if l.strip()]
    if not fichiers:
        return ""
    return (f"{len(fichiers)} fichier(s) modifié(s) sans clôture. "
            "Dites « clôture » pour garder la raison de ce qui vient de changer.")


def main():
    p = argparse.ArgumentParser(description="Hook Stop du vault Cortex.")
    p.add_argument("--autotest", action="store_true")
    if p.parse_args().autotest:
        return _autotest()
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                           text=True, cwd=racine_vault())
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
    avant = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = "/tmp/vault-annonce"
    assert racine_vault() == Path("/tmp/vault-annonce")
    del os.environ["CLAUDE_PROJECT_DIR"]
    assert racine_vault() == Path.cwd()
    if avant is not None:
        os.environ["CLAUDE_PROJECT_DIR"] = avant
    print("OK stop.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
