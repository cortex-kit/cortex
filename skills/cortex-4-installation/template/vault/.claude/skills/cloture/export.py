#!/usr/bin/env python3
"""export.py : ce qui part au commun, écrit par la clôture. stdlib pure.

Contrat 04 §6. Le `<slug>` est `organisation.code` du `config.yaml`, la seule
clé qui le porte : `~/Cortex/<slug>/`, `_export/<slug>/`, le dépôt `cortex-<slug>`
et l'entrée du membre dans `federation.yaml` en dérivent tous.

En mode `federe`, vide puis réécrit `<vault>/<commun.export>/<slug>/` :
  index.json      {"format": "cortex/export", "version": 1, "slug", "exporte_le", "notes": [{chemin, hash}]}
  10 - Domaines/, 20 - Projets/, 40 - Acteurs/, 60 - Journal/
                  copie des notes dont `visibilite` vaut `commun`, frontmatter enrichi
                  de `source_vault` et `exporte_le`

Une note sans clé `visibilite` prend `commun.visibilite_defaut`. Une note `prive`
n'est jamais exportée. Régénéré en entier à chaque appel : idempotent. Le `hash`
est le sha256 de la note d'origine, pour que l'agrégateur voie ce qui a changé.

En mode `solo`, ne fait rien et le dit : il n'y a personne à qui exporter.

Usage : python3 .claude/skills/cloture/export.py --vault . [--autotest]
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

# Dans un vault installé, les modules vivent dans .claude/skills/lint/ ; dans le
# gabarit du dépôt, dans scripts/ de la skill d'installation (auto-test).
_ICI = Path(__file__).resolve()
sys.path.insert(0, str(_ICI.parent.parent / "lint"))
# Le second chemin ne vaut que dans le gabarit, et il se reconnait a ce qu'il
# contient, jamais a une profondeur : dans un vault installe sous
# `~/Cortex/<slug>/`, `parents[5]` designe un dossier hors du vault.
_scripts = _ICI.parents[5] / "scripts" if len(_ICI.parents) > 5 else None
if _scripts is not None and (_scripts / "cortex_config.py").is_file():
    sys.path.append(str(_scripts))
import cortex_config  # noqa: E402
import lint_sante  # noqa: E402

DOSSIERS = ("10 - Domaines", "20 - Projets", "40 - Acteurs", "60 - Journal")


def exporter(vault, conf, aujourdhui=None):
    vault = Path(vault)
    if conf.get("mode") != "federe":
        return None, []
    commun = conf.get("commun") or {}
    slug = (conf.get("organisation") or {}).get("code", "vault")
    defaut = commun.get("visibilite_defaut", "prive")
    cible = vault / (commun.get("export") or "_export") / slug
    jour = (aujourdhui or date.today()).isoformat()

    shutil.rmtree(cible, ignore_errors=True)
    cible.mkdir(parents=True)
    notes = []
    for dossier in DOSSIERS:
        for md in sorted((vault / dossier).rglob("*.md")):
            if md.name == "_README.md":
                continue
            brut = md.read_bytes()
            texte = brut.decode("utf-8", errors="replace")
            fm = lint_sante.parse_frontmatter(texte)
            if (fm.get("visibilite") or defaut) != "commun":
                continue
            rel = md.relative_to(vault)
            enrichi = (f"---\nsource_vault: {slug}\nexporte_le: {jour}\n" + texte[4:]
                       if texte.startswith("---\n")
                       else f"---\nsource_vault: {slug}\nexporte_le: {jour}\n---\n{texte}")
            (cible / rel).parent.mkdir(parents=True, exist_ok=True)
            (cible / rel).write_text(enrichi, encoding="utf-8")
            notes.append({"chemin": str(rel), "hash": hashlib.sha256(brut).hexdigest()})
    index = {"format": "cortex/export", "version": 1, "slug": slug,
             "exporte_le": jour, "notes": notes}
    (cible / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
    return cible, notes


def main():
    p = argparse.ArgumentParser(description="Export vers le commun (contrat §6).")
    p.add_argument("--vault", default=".")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    vault = Path(a.vault).expanduser().resolve()
    conf = cortex_config.charger(vault / "config.yaml")
    cible, notes = exporter(vault, conf)
    if cible is None:
        print("mode solo : aucun export, rien à faire.")
    else:
        print(f"✓ Export : {len(notes)} note(s) dans {cible.relative_to(vault)}/")
    return 0


def _autotest():
    import tempfile
    conf = {"mode": "federe", "organisation": {"code": "camille"},
            "commun": {"export": "_export", "visibilite_defaut": "prive"}}
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        for d in DOSSIERS:
            (v / d).mkdir()
        (v / "20 - Projets" / "A.md").write_text("---\ntype: projet\nvisibilite: commun\n---\n# A\n", encoding="utf-8")
        (v / "20 - Projets" / "B.md").write_text("---\ntype: projet\nvisibilite: prive\n---\n# B\n", encoding="utf-8")
        (v / "40 - Acteurs" / "C.md").write_text("---\ntype: acteur\n---\n# C\n", encoding="utf-8")
        (v / "40 - Acteurs" / "_README.md").write_text("# readme\n", encoding="utf-8")
        cible, notes = exporter(v, conf, date(2026, 9, 19))
        assert [n["chemin"] for n in notes] == ["20 - Projets/A.md"], notes
        exporte = (cible / "20 - Projets" / "A.md").read_text(encoding="utf-8")
        assert exporte.startswith("---\nsource_vault: camille\nexporte_le: 2026-09-19\ntype: projet"), exporte
        assert not (cible / "20 - Projets" / "B.md").exists()
        idx = json.loads((cible / "index.json").read_text(encoding="utf-8"))
        assert idx["format"] == "cortex/export" and idx["slug"] == "camille"
        assert len(idx["notes"][0]["hash"]) == 64
        # Défaut `commun` : la note sans clé part ; deux passes donnent le même arbre.
        conf["commun"]["visibilite_defaut"] = "commun"
        _, notes2 = exporter(v, conf, date(2026, 9, 19))
        assert [n["chemin"] for n in notes2] == ["20 - Projets/A.md", "40 - Acteurs/C.md"], notes2
        avant = sorted((str(p.relative_to(cible)), p.read_bytes()) for p in cible.rglob("*") if p.is_file())
        exporter(v, conf, date(2026, 9, 19))
        apres = sorted((str(p.relative_to(cible)), p.read_bytes()) for p in cible.rglob("*") if p.is_file())
        assert avant == apres
        assert exporter(v, {"mode": "solo"})[0] is None
    print("OK export.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
