#!/usr/bin/env python3
"""fabrique.py — assemble le paquet distribuable Cortex. stdlib pure, zéro réseau.

Lit kit.txt, copie les dossiers depuis skills/ du dépôt (les maillons présents,
trouvés par glob `cortex-*`, et les skills annexes du manifeste), y ajoute la
notice et PROVENANCE.md, et produit le zip de repli. Aucun nombre n'est codé en
dur : le zip compte ce qui est là. La voie principale est le plugin Claude
Code ; le zip sert aux postes sans marketplace.

Trois contrôles BLOQUANTS, dans cet ordre :
  1. Provenance — chaque entrée du manifeste couverte par PROVENANCE.md avec
     un verdict de redistribution positif. Un zip distribué ne se rappelle pas.
  2. Complétude — chaque entrée présente avec un SKILL.md au frontmatter
     valide (`name` et `description`).
  3. Profondeur — aucun SKILL.md au-delà de <dossier>/SKILL.md dans le zip.
     C'est LE critère qui décide si le kit est vu ou muet : Claude Code ne lit
     que skills/<nom>/SKILL.md. Seule exception, documentée : le gabarit
     cortex-4-installation/template/, dont les SKILL.md sont un CHARGEMENT de
     scaffold — invisibles ici par le mécanisme même de _archive, et déposés
     au bon niveau dans le vault du client par scaffold.py.

Les outils du tableau de bord (etat.py, rend_notice.py, notice.md) vivent
dans cortex-4-installation/scripts/ et partent avec le maillon ; fabricant/
reste chez le fabricant, hors plugin et hors zip. Seul VERSION est ajouté.

Usage (`py` sous Windows vaut `python3`) :
    python3 fabrique.py --sortie <cortex.zip> [--version 2026-08-23]
    python3 fabrique.py --autotest
"""

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

_ICI = Path(__file__).resolve().parent
PAQUET = _ICI.parent                 # <dépôt>/fabricant
SKILLS = PAQUET.parent / "skills"    # <dépôt>/skills : maillons et annexes


def _rang(nom):
    """Le numéro du maillon, ou l'infini : un dossier `cortex-<mot>` se range en
    fin de liste au lieu de faire lever le tri (`cortex-paquet`, un essai local…)."""
    morceau = nom.split("-")[1] if "-" in nom else ""
    return (int(morceau), nom) if morceau.isdigit() else (float("inf"), nom)


def maillons():
    """Les maillons présents dans skills/, par glob, dans l'ordre de leur numéro."""
    return sorted((p.name for p in SKILLS.glob("cortex-*") if p.is_dir()), key=_rang)


# `recette` : harnais de vérification, il reste au dépôt (amendement §3).
EXCLUS = shutil.ignore_patterns("__pycache__", ".DS_Store", ".git", "recette")
# Chargement de scaffold : SKILL.md volontairement profonds, hors contrôle.
EXEMPTION_PROFONDEUR = "cortex-4-installation/template/"


def _pluriel(n, mot):
    return f"{n} {mot}" + ("s" if n > 1 else "")


def _erreur(msg):
    print(f"[bloquant] {msg}", file=sys.stderr)
    return 2


def _kit():
    manifeste = PAQUET / "kit.txt"
    lignes = [l.strip() for l in manifeste.read_text(encoding="utf-8").splitlines()]
    return [l for l in lignes if l and not l.startswith("#")]


def controle_provenance(kit):
    """Chaque emprunt couvert, verdict positif. Rend la liste des défauts."""
    provenance = (PAQUET.parent / "PROVENANCE.md").read_text(encoding="utf-8")
    defauts = []
    for skill in kit:
        m = re.search(rf"^\|\s*{re.escape(skill)}\s*\|(.+)\|\s*$",
                      provenance, re.M)
        if not m:
            defauts.append(f"provenance : {skill} sans ligne dans PROVENANCE.md")
        elif "Oui" not in m.group(1).rsplit("|", 1)[-1]:
            defauts.append(f"provenance : {skill} sans verdict de "
                           "redistribution positif")
    return defauts


def controle_completude(dossiers):
    """Chaque dossier existe et porte un SKILL.md avec name et description."""
    defauts = []
    for nom in dossiers:
        skill_md = SKILLS / nom / "SKILL.md"
        if not skill_md.is_file():
            defauts.append(f"completude : {nom}/SKILL.md absent")
            continue
        lignes = skill_md.read_text(encoding="utf-8").splitlines()
        if not lignes or lignes[0].strip() != "---":
            defauts.append(f"completude : {nom}/SKILL.md sans frontmatter")
            continue
        try:
            fin = next(i for i, l in enumerate(lignes[1:], 1) if l.strip() == "---")
        except StopIteration:
            defauts.append(f"completude : {nom}/SKILL.md frontmatter non clos")
            continue
        cles = {l.split(":", 1)[0].strip() for l in lignes[1:fin] if ":" in l}
        for cle in ("name", "description"):
            if cle not in cles:
                defauts.append(f"completude : {nom}/SKILL.md sans `{cle}`")
    return defauts


def controle_profondeur(racine):
    """Aucun SKILL.md sous <dossier>/SKILL.md, exemption du gabarit comprise."""
    defauts = []
    for p in Path(racine).rglob("SKILL.md"):
        rel = p.relative_to(racine).as_posix()
        if len(rel.split("/")) == 2:
            continue                       # <dossier>/SKILL.md : la bonne place
        if rel.startswith(EXEMPTION_PROFONDEUR):
            continue                       # chargement de scaffold, voir en-tête
        defauts.append(f"profondeur : {rel} serait invisible pour Claude Code")
    return defauts


def fabriquer(sortie, version=None):
    version = version or date.today().isoformat()
    kit = _kit()
    MAILLONS = maillons()
    if not MAILLONS:
        return _erreur("aucun maillon cortex-* dans skills/")

    for nom, defauts in (("provenance", controle_provenance(kit)),
                         ("completude", controle_completude(MAILLONS + kit))):
        if defauts:
            for d in defauts:
                print(f"[bloquant] {d}", file=sys.stderr)
            return 2

    with tempfile.TemporaryDirectory(prefix="cortex-fabrique-") as tmp:
        scene = Path(tmp) / "cortex"
        scene.mkdir()
        for nom in MAILLONS + kit:
            shutil.copytree(SKILLS / nom, scene / nom, ignore=EXCLUS)
        shutil.copyfile(PAQUET.parent / "PROVENANCE.md", scene / "PROVENANCE.md")

        # Outillage du tableau de bord (etat.py, rend_notice.py, notice.md) :
        # il vit dans cortex-4-installation/scripts/ et part avec le maillon.
        outils = scene / "cortex-4-installation" / "scripts"
        (outils / "VERSION").write_text(version + "\n", encoding="utf-8")

        # La notice de déballage : l'état VIERGE (toutes les étapes à faire,
        # phrase d'entrée en tête). Générée par la même chaîne que le suivi
        # vivant, pour que l'état zéro soit lui aussi une projection.
        sys.path.insert(0, str(SKILLS / "cortex-4-installation" / "scripts"))
        import etat as m_etat
        import rend_notice as m_rend
        atelier_vierge = Path(tmp) / "_cortex"
        atelier_vierge.mkdir()
        pivot = m_etat.generer(atelier_vierge, paquet=version)
        (scene / "LISEZ-MOI.html").write_text(m_rend.rendre(pivot),
                                              encoding="utf-8")

        defauts = controle_profondeur(scene)
        if defauts:
            for d in defauts:
                print(f"[bloquant] {d}", file=sys.stderr)
            return 2

        sortie = Path(sortie)
        with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(scene.rglob("*")):
                z.write(p, p.relative_to(scene))

    dossiers = len(MAILLONS) + len(kit)
    print(f"OK — {sortie} : {_pluriel(dossiers, 'dossier')} "
          f"({_pluriel(len(MAILLONS), 'maillon')} + {_pluriel(len(kit), 'annexe')}), "
          f"LISEZ-MOI.html, PROVENANCE.md, version {version}")
    return 0


def _autotest():
    with tempfile.TemporaryDirectory() as tmp:
        z = Path(tmp) / "t.zip"
        assert fabriquer(z, version="autotest") == 0
        with zipfile.ZipFile(z) as zf:
            noms = zf.namelist()
        dossiers = {n.split("/")[0] for n in noms if "/" in n}
        assert dossiers == set(maillons()) | set(_kit()), dossiers
        assert {n for n in noms if "/" not in n} == {"LISEZ-MOI.html", "PROVENANCE.md"}
        assert "cortex-4-installation/scripts/VERSION" in noms
        # Défaut 11 : la recette reste au dépôt, elle ne part pas dans le zip.
        assert not [n for n in noms if "/recette/" in n], "recette embarquée"
    # Défaut 10 : un dossier `cortex-<mot>` se range, il ne fait pas lever le tri.
    assert _rang("cortex-4-installation") < _rang("cortex-paquet")
    assert _rang("cortex-paquet")[0] == float("inf")
    # Défaut 8 : singulier quand il n'y en a qu'un.
    assert _pluriel(1, "annexe") == "1 annexe" and _pluriel(2, "annexe") == "2 annexes"
    print("fabrique.py : auto-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description="Fabrique le zip Cortex.")
    p.add_argument("--sortie", default="cortex.zip", help="zip à produire")
    p.add_argument("--version", help="version du paquet (défaut : date du jour)")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    return fabriquer(a.sortie, a.version)


if __name__ == "__main__":
    sys.exit(main())
