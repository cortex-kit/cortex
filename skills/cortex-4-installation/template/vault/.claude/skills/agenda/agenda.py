#!/usr/bin/env python3
"""agenda.py — les cases datées du vault, en une page. stdlib pure, lecture seule.

Une case est une ligne `- [ ] …` d'une note. Elle est datée par `📅 AAAA-MM-JJ`
et prioritaire par 🔺 (urgent) ou ⏫ (haut). Rien d'autre n'est lu : l'agenda
réel (rendez-vous) vit dans le calendrier, le backlog détaillé dans son outil.

Usage :
  python3 .claude/skills/agenda/agenda.py --vault .            # la page du matin
  python3 .claude/skills/agenda/agenda.py --vault . --jours 14 # horizon élargi
  python3 .claude/skills/agenda/agenda.py --vault . --bref     # une ligne, pour le hook
  python3 .claude/skills/agenda/agenda.py --autotest
"""
import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

CASE = re.compile(r"^\s*- \[ \] (.+)$")
DATE = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")
# Dossiers dont les cases ne sont pas des engagements : gabarits, doctrine, outillage.
IGNORES = {"Templates", ".claude", ".git", "_cortex", "_export", ".obsidian"}


def cases(vault):
    """[(note, texte, date|None, priorite)] pour toutes les cases ouvertes."""
    out = []
    for md in sorted(vault.rglob("*.md")):
        if IGNORES & set(md.relative_to(vault).parts):
            continue
        for ligne in md.read_text(encoding="utf-8", errors="replace").splitlines():
            m = CASE.match(ligne)
            if not m:
                continue
            texte = m.group(1)
            d = DATE.search(texte)
            try:
                quand = date.fromisoformat(d.group(1)) if d else None
            except ValueError:
                quand = None
            prio = 2 if "🔺" in texte else 1 if "⏫" in texte else 0
            propre = re.sub(r"\s*(📅\s*\S+|🔺|⏫|#d/\S+)", "", texte).strip()
            out.append((md.stem, propre, quand, prio))
    return out


def classer(liste, jour, jours):
    fin = jour + timedelta(days=jours)
    retard = sorted((c for c in liste if c[2] and c[2] < jour), key=lambda c: (c[2], -c[3]))
    auj = [c for c in liste if c[2] == jour]
    proches = sorted((c for c in liste if c[2] and jour < c[2] <= fin), key=lambda c: (c[2], -c[3]))
    sans_date = [c for c in liste if not c[2] and c[3]]
    return retard, auj, proches, sans_date


def page(liste, jour, jours):
    retard, auj, proches, sans_date = classer(liste, jour, jours)
    marque = {2: "🔺 ", 1: "⏫ ", 0: ""}
    L = [f"Agenda du {jour.isoformat()}", ""]
    for titre, groupe, avec_date in (("En retard", retard, True), ("Aujourd'hui", auj, False),
                                     (f"Les {jours} prochains jours", proches, True),
                                     ("Prioritaires sans date", sans_date, False)):
        L.append(f"{titre} : {len(groupe)}")
        for note, texte, quand, prio in groupe:
            d = f"{quand.isoformat()} " if avec_date and quand else ""
            L.append(f"- {d}{marque[prio]}[[{note}]] : {texte}")
        L.append("")
    hautes = sum(1 for c in liste if c[3])
    if hautes > 7:
        L.append(f"{hautes} cases prioritaires ouvertes : si tout est prioritaire, rien ne l'est.")
    return "\n".join(L).rstrip() + "\n"


def bref(liste, jour, jours):
    retard, auj, proches, _ = classer(liste, jour, jours)
    if not (retard or auj or proches):
        return ""
    return (f"Agenda : {len(retard)} en retard, {len(auj)} aujourd'hui, "
            f"{len(proches)} sur {jours} jours. Dites « agenda » pour le détail.")


def main():
    p = argparse.ArgumentParser(description="Cases datées du vault Cortex.")
    p.add_argument("--vault", default=".")
    p.add_argument("--jours", type=int, default=7)
    p.add_argument("--bref", action="store_true")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    liste = cases(Path(a.vault).expanduser())
    texte = bref(liste, date.today(), a.jours) if a.bref else page(liste, date.today(), a.jours)
    if texte:
        print(texte.rstrip("\n"))
    return 0


def _autotest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        (v / "20 - Projets").mkdir()
        (v / "90 - Meta" / "Templates").mkdir(parents=True)
        (v / "20 - Projets" / "IA - Alpha.md").write_text(
            "## Actions\n- [ ] Relancer le client #d/ia ⏫ 📅 2026-10-01\n"
            "- [x] Fait 📅 2026-09-01\n- [ ] Restitution 📅 2026-10-08\n"
            "- [ ] Envoyer le devis 📅 2026-10-03\n- [ ] Idée sans date\n- [ ] Urgent sans date 🔺\n",
            encoding="utf-8")
        (v / "90 - Meta" / "Templates" / "_T.md").write_text("- [ ] Gabarit 📅 2020-01-01\n", encoding="utf-8")
        liste = cases(v)
        assert len(liste) == 5, liste                      # la case faite et le gabarit sont exclus
        j = date(2026, 10, 3)
        r, a, p, s = classer(liste, j, 7)
        assert [c[1] for c in r] == ["Relancer le client"] and r[0][3] == 1, r
        assert [c[1] for c in a] == ["Envoyer le devis"], a
        assert [c[1] for c in p] == ["Restitution"], p
        assert [c[1] for c in s] == ["Urgent sans date"], s
        assert bref(liste, j, 7) == "Agenda : 1 en retard, 1 aujourd'hui, 1 sur 7 jours. Dites « agenda » pour le détail."
        assert "[[IA - Alpha]]" in page(liste, j, 7) and "#d/" not in page(liste, j, 7)
        assert bref([], j, 7) == ""
    print("OK agenda.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
