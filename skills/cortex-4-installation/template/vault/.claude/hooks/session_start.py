#!/usr/bin/env python3
"""Hook SessionStart du vault. stdlib pure, lecture seule.

Trois lignes au plus, dans le contexte de la session :
  1. le lint en bref (contrôles durs, dette, dernière clôture trop ancienne) ;
  2. la proposition de `bilan` à J+7 et J+30 de la remise, lue dans
     `_cortex/06-passation.md` (clé `remis_le`) quand l'atelier est dans le vault.

Usage : python3 .claude/hooks/session_start.py [--autotest]
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


def racine_vault():
    """Le vault est celui que Claude Code annonce, pas le dossier courant.

    Sans `CLAUDE_PROJECT_DIR`, un hook lance depuis un sous-dossier ne trouvait
    ni le lint ni `_cortex/06-passation.md`, et se taisait sans le dire.
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def fenetre_bilan(remis_le, aujourdhui=None):
    """'J+7', 'J+30' ou '' selon l'âge de la remise. Une semaine de fenêtre
    chacune : la proposition revient à chaque session, sans état à tenir."""
    try:
        d = date.fromisoformat(str(remis_le).strip()[:10])
    except ValueError:
        return ""
    age = ((aujourdhui or date.today()) - d).days
    if 7 <= age < 14:
        return "J+7"
    if 30 <= age < 37:
        return "J+30"
    return ""


def remis_le(vault):
    p = vault / "_cortex" / "06-passation.md"
    if not p.is_file():
        return ""
    m = re.search(r"^remis_le:\s*(\S+)", p.read_text(encoding="utf-8", errors="replace"), re.M)
    return m.group(1).strip("\"'") if m else ""


def main():
    p = argparse.ArgumentParser(description="Hook SessionStart du vault Cortex.")
    p.add_argument("--autotest", action="store_true")
    if p.parse_args().autotest:
        return _autotest()
    vault = racine_vault()
    lint = vault / ".claude" / "skills" / "lint" / "lint_sante.py"
    if lint.is_file():
        r = subprocess.run([sys.executable, str(lint), "--vault", ".", "--bref"],
                           capture_output=True, text=True, cwd=vault)
        print((r.stdout or r.stderr).strip())
    f = fenetre_bilan(remis_le(vault))
    if f:
        print(f"Bilan {f} de la remise : dites « bilan » pour voir ce qui a vécu depuis.")
    return 0


def _autotest():
    j = date(2026, 9, 19)
    assert fenetre_bilan("2026-09-12", j) == "J+7"
    assert fenetre_bilan("2026-09-05", j) == ""
    assert fenetre_bilan("2026-08-20", j) == "J+30"
    assert fenetre_bilan("2026-09-18", j) == ""
    assert fenetre_bilan("pas une date", j) == ""
    # Le vault vient de CLAUDE_PROJECT_DIR, le dossier courant n'est qu'un repli.
    avant = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = "/tmp/vault-annonce"
    assert racine_vault() == Path("/tmp/vault-annonce")
    del os.environ["CLAUDE_PROJECT_DIR"]
    assert racine_vault() == Path.cwd()
    if avant is not None:
        os.environ["CLAUDE_PROJECT_DIR"] = avant
    print("OK session_start.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
