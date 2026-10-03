#!/usr/bin/env python3
"""cloture.py : le commit de la clôture, passé par un script. stdlib pure.

Un `git commit` tapé par l'assistant reçoit les lignes d'attribution de la
session (`Co-Authored-By: Claude …`, `Claude-Session: https://claude.ai/…`) :
la session du consultant voyageait ainsi dans l'historique du vault livré
(Phase H2, lane C). Ce script commite sous l'identité locale du vault et retire
ces lignes du message, quel que soit ce que l'assistant y a mis.

    python3 .claude/skills/cloture/cloture.py --vault . --message "<message>" <chemin> [<chemin> ...]

Ajoute les chemins nommés (jamais `add -A`), plus l'export du commun s'il
existe, commite, puis pousse si un dépôt distant existe. Sort en 0 quand il n'y
a rien à commiter. Un push en échec se signale, le commit local reste.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

_ICI = Path(__file__).resolve()
sys.path.insert(0, str(_ICI.parent.parent / "lint"))
_scripts = _ICI.parents[5] / "scripts" if len(_ICI.parents) > 5 else None
if _scripts is not None and (_scripts / "cortex_config.py").is_file():
    sys.path.append(str(_scripts))

TRAILER = re.compile(r"^\s*(?:co-authored-by:|claude-session:|🤖|generated with claude).*$|^.*claude\.ai/code.*$",
                     re.I | re.M)


def nettoyer(message):
    """Le message sans aucune ligne d'attribution de session."""
    propre = TRAILER.sub("", message)
    return re.sub(r"\n{3,}", "\n\n", propre).strip()


def git(vault, *args, **kw):
    return subprocess.run(["git", "-C", str(vault), *args], capture_output=True, text=True, **kw)


def config(vault):
    try:
        import cortex_config
        return cortex_config.charger(Path(vault) / "config.yaml") or {}
    except Exception as e:  # config illisible : on le dit, on garde les replis neutres
        print(f"[i] config.yaml illisible ({e}) : identité « Cortex », export « _export ».", file=sys.stderr)
        return {}


def identite(vault, conf):
    """L'identité locale du vault ; à défaut, le rédacteur de config.yaml, jamais celle du poste."""
    nom = git(vault, "config", "--local", "user.name").stdout.strip()
    courriel = git(vault, "config", "--local", "user.email").stdout.strip()
    if nom and courriel:
        return nom, courriel
    org = conf.get("organisation") or {}
    return (nom or str(org.get("redacteur") or "").strip() or "Cortex",
            courriel or str(org.get("courriel") or "").strip() or "cortex@localhost")


def cloturer(vault, message, chemins):
    vault = Path(vault).expanduser().resolve()
    if not (vault / ".git").exists():
        print("vault sans historique git : rien à enregistrer.")
        return 0
    message = nettoyer(message)
    if not message:
        print("[X] message vide une fois les lignes d'attribution retirées.", file=sys.stderr)
        return 1
    conf = config(vault)
    export = (conf.get("commun") or {}).get("export") or "_export"
    cibles = [c for c in chemins if (vault / c).exists() or git(vault, "ls-files", "--", c).stdout]
    if (vault / export).is_dir():
        cibles.append(export)
    if cibles:
        r = git(vault, "add", "--", *cibles)
        if r.returncode:
            print(f"[X] git add : {r.stderr.strip()}", file=sys.stderr)
            return 1
    if git(vault, "diff", "--cached", "--quiet").returncode == 0:
        print("rien à enregistrer.")
        return 0
    nom, courriel = identite(vault, conf)
    r = git(vault, "-c", f"user.name={nom}", "-c", f"user.email={courriel}",
            "commit", "-q", "-m", message)
    if r.returncode:
        print(f"[X] commit : {(r.stderr or r.stdout).strip()}", file=sys.stderr)
        return 1
    print(f"✓ Enregistré : {message.splitlines()[0]}")
    if git(vault, "remote").stdout.strip():
        r = git(vault, "push", "-q")
        if r.returncode:
            print(f"⚠ Sauvegarde en ligne en échec, l'enregistrement local reste : {r.stderr.strip()}")
        else:
            print("✓ Sauvegarde en ligne faite.")
    else:
        print("↻ Sauvegarde en ligne absente.")
    return 0


def _autotest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        git(v, "init", "-q")
        git(v, "config", "user.name", "Hélène Vasseur")
        git(v, "config", "user.email", "helene@exemple.test")
        (v / "note.md").write_text("# note\n", encoding="utf-8")
        sale = ("Clôture : fiche Caluire\n\nCo-Authored-By: Claude Opus <noreply@anthropic.com>\n"
                "Claude-Session: https://claude.ai/code/session_x\n🤖 Generated with Claude Code\n")
        assert cloturer(v, sale, ["note.md", "absent.md"]) == 0
        corps = git(v, "log", "-1", "--format=%an <%ae>%n%B").stdout
        assert corps.startswith("Hélène Vasseur <helene@exemple.test>"), corps
        assert "Clôture : fiche Caluire" in corps, corps
        assert not re.search(r"co-authored-by|claude-session|claude\.ai|generated with", corps, re.I), corps
        assert cloturer(v, "rien", ["note.md"]) == 0          # rien à commiter : 0, aucun commit
        assert git(v, "rev-list", "--count", "HEAD").stdout.strip() == "1"
        assert cloturer(v, "Co-Authored-By: Claude <x>", ["note.md"]) == 1
    print("OK cloture.py")
    return 0


def main():
    p = argparse.ArgumentParser(description="Commit de la clôture, sans trace de session.")
    p.add_argument("--vault", default=".")
    p.add_argument("--message", "-m")
    p.add_argument("chemins", nargs="*")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.message:
        p.error("--message requis")
    return cloturer(a.vault, a.message, a.chemins)


if __name__ == "__main__":
    sys.exit(main())
