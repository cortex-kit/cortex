#!/usr/bin/env python3
"""copie_structurant.py : copie un document structurant dans le vault, régime copie. stdlib pure.

Contrat 04 §2. Écrit `50 - Ressources/Structurants/<type>/<nom>.md` avec le
frontmatter `type: structurant`, `structurant: <type>`, `domaine`, `source_path`
(forme `~`), `hash` (sha256 de la source), `copie_le`, et le texte de la source.

Le texte vient du fichier lui-même (.md, .txt, .csv) ou de `uvx markitdown`
pour les autres formats ; à défaut, `--texte <fichier>` fournit une conversion
déjà faite. Pour un `fil_structurant`, `--texte` porte le résumé anonymisé et
`--source` est facultatif : un fil de messagerie n'a pas de fichier qui change.

Refuse : un régime autre que `copie`, un type hors `donnees.structurants`, le
plafond `sante.max_structurants` atteint, une note existante écrite à la main.
Rejoue sans dupliquer : même hash, rien ; hash différent, la copie se rafraîchit.

Usage :
  python3 copie_structurant.py --vault <vault> --source <fichier> --type process --domaine "Ops"
  python3 copie_structurant.py --vault <vault> --type fil_structurant --domaine "Ops" --titre "Revue fournisseurs" --texte resume.md
  python3 copie_structurant.py --autotest
"""
import argparse
import hashlib
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

_ICI = Path(__file__).resolve()
sys.path.insert(0, str(_ICI.parents[2] / "cortex-4-installation" / "scripts"))
import cortex_config  # noqa: E402
from scaffold import forme_tilde  # noqa: E402

STRUCTURANTS = Path("50 - Ressources/Structurants")
MARQUEUR = "<!-- cortex-5-ingest: structurant:{nom} {jour} -->"
TEXTE_DIRECT = {".md", ".txt", ".csv", ".markdown"}


def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 16), b""):
            h.update(bloc)
    return h.hexdigest()


def texte_de(source, max_octets):
    """Texte d'un fichier : direct pour le texte brut, `uvx markitdown` sinon."""
    if source.suffix.lower() in TEXTE_DIRECT:
        brut = source.read_bytes()[:max_octets]
        return brut.decode("utf-8", errors="replace")
    try:
        r = subprocess.run(["uvx", "markitdown", str(source)], capture_output=True,
                           text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout[:max_octets]


def nom_note(titre):
    nom = re.sub(r"[\\/:*?\"<>|#\[\]]+", " ", titre).strip()
    return re.sub(r"\s+", " ", nom) or "sans-titre"


def copier(vault, conf, typ, domaine, source=None, titre=None, texte=None,
           max_octets=200_000, jour=None):
    """Renvoie (code, message). 0 = écrit ou à jour, 2 = refus."""
    vault = Path(vault)
    regime = (conf.get("donnees") or {}).get("regime", "pointeur")
    if regime != "copie":
        return 2, f"regime {regime!r} : aucune copie. Le vault pointe, il ne stocke pas."
    types = (conf.get("donnees") or {}).get("structurants") or []
    if typ not in types:
        return 2, f"type {typ!r} hors de donnees.structurants {types}."
    plafond = (conf.get("sante") or {}).get("max_structurants", 40)
    dossier = vault / STRUCTURANTS
    existants = [p for p in dossier.rglob("*.md") if p.name != "_README.md"] if dossier.is_dir() else []

    if source is not None:
        source = Path(source).expanduser()
        if not source.is_file():
            return 2, f"source introuvable : {source}"
        h = sha256_fichier(source)
        src = forme_tilde(str(source.resolve()))
        if texte is None:
            texte = texte_de(source, max_octets)
            if texte is None:
                return 2, ("conversion impossible (uvx markitdown absent ou en echec) : "
                           "fournir --texte avec le contenu converti.")
    else:
        if typ != "fil_structurant":
            return 2, "--source est requis sauf pour un fil_structurant."
        if texte is None:
            return 2, "un fil_structurant se copie en resume anonymise : --texte requis."
        h, src = hashlib.sha256(texte.encode("utf-8")).hexdigest(), ""

    titre = titre or (source.stem if source is not None else "")
    if not titre:
        return 2, "--titre requis."
    cible = dossier / typ / f"{nom_note(titre)}.md"
    jour = (jour or date.today()).isoformat()

    if cible.is_file():
        ancien = cible.read_text(encoding="utf-8", errors="replace")
        if "<!-- cortex-5-ingest: structurant:" not in ancien:
            return 2, f"{cible.relative_to(vault)} existe et a ete ecrite a la main : arbitrer, jamais ecraser."
        m = re.search(r"^hash:\s*(\S+)", ancien, re.M)
        if m and m.group(1) == h:
            return 0, f"a jour : {cible.relative_to(vault)} (meme hash)."
        verbe = "rafraichie"
    else:
        if len(existants) >= plafond:
            return 2, (f"plafond sante.max_structurants atteint ({plafond}) : au-dela, le vault "
                       "devient un second disque. Ecarter ou arbitrer.")
        verbe = "ecrite"

    cible.parent.mkdir(parents=True, exist_ok=True)
    corps = texte.rstrip() + "\n"
    if len(corps.encode("utf-8")) >= max_octets:
        corps += f"\n<!-- tronque a {max_octets} octets : le reste vit a la source -->\n"
    cible.write_text(
        f"---\ntype: structurant\nstructurant: {typ}\ndomaine: \"[[{domaine}]]\"\n"
        f"source_path: \"{src}\"\nhash: {h}\ncopie_le: {jour}\n---\n"
        f"# {titre}\n\n{corps}\n{MARQUEUR.format(nom=nom_note(titre), jour=jour)}\n",
        encoding="utf-8")
    return 0, f"{verbe} : {cible.relative_to(vault)} ({len(corps.encode('utf-8'))} octets, sha256 {h[:12]}...)"


def main():
    p = argparse.ArgumentParser(description="Copie un structurant dans le vault (regime copie).")
    p.add_argument("--vault")
    p.add_argument("--source", help="fichier source ; facultatif pour un fil_structurant")
    p.add_argument("--type", dest="typ", help="un type de donnees.structurants")
    p.add_argument("--domaine", help="nom de la note de domaine, sans crochets")
    p.add_argument("--titre")
    p.add_argument("--texte", help="fichier portant le texte deja converti ou le resume anonymise")
    p.add_argument("--max-octets", type=int, default=200_000)
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not (a.vault and a.typ and a.domaine):
        p.error("--vault, --type et --domaine sont requis")
    vault = Path(a.vault).expanduser().resolve()
    conf = cortex_config.charger(vault / "config.yaml")
    texte = Path(a.texte).read_text(encoding="utf-8") if a.texte else None
    code, msg = copier(vault, conf, a.typ, a.domaine, a.source, a.titre, texte, a.max_octets)
    print(("✓ " if code == 0 else "[X] ") + msg, file=sys.stdout if code == 0 else sys.stderr)
    return code


def _autotest():
    import tempfile
    conf = {"donnees": {"regime": "copie", "structurants": ["process", "fil_structurant"]},
            "sante": {"max_structurants": 2}}
    j = date(2026, 9, 19)
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp) / "vault"
        v.mkdir()
        src = Path(tmp) / "PROCESS-affaire.md"
        src.write_text("# Process\n\nversion 1\n", encoding="utf-8")
        code, msg = copier(v, conf, "process", "Ops", src, jour=j)
        assert code == 0 and msg.startswith("ecrite"), msg
        note = v / STRUCTURANTS / "process" / "PROCESS-affaire.md"
        t = note.read_text(encoding="utf-8")
        assert t.startswith("---\ntype: structurant\nstructurant: process\ndomaine: \"[[Ops]]\"\nsource_path: ")
        assert f"hash: {sha256_fichier(src)}" in t and "copie_le: 2026-09-19" in t
        assert "<!-- cortex-5-ingest: structurant:PROCESS-affaire 2026-09-19 -->" in t
        # Idempotent, puis rafraichi quand la source change.
        assert copier(v, conf, "process", "Ops", src, jour=j)[1].startswith("a jour")
        src.write_text("# Process\n\nversion 2\n", encoding="utf-8")
        assert copier(v, conf, "process", "Ops", src, jour=j)[1].startswith("rafraichie")
        # Refus : regime pointeur, type inconnu, note ecrite a la main, plafond.
        assert copier(v, {"donnees": {"regime": "pointeur"}}, "process", "Ops", src)[0] == 2
        assert copier(v, conf, "organigramme", "Ops", src)[0] == 2
        note.write_text("---\ntype: structurant\n---\n# a la main\n", encoding="utf-8")
        assert "a la main" in copier(v, conf, "process", "Ops", src, jour=j)[1]
        code, _ = copier(v, conf, "fil_structurant", "Ops", titre="Revue fournisseurs",
                         texte="Fil de 38 messages entre l'entreprise et un fournisseur. Resume.", jour=j)
        assert code == 0
        assert "plafond" in copier(v, conf, "fil_structurant", "Ops", titre="Autre", texte="x", jour=j)[1]
        fil = (v / STRUCTURANTS / "fil_structurant" / "Revue fournisseurs.md").read_text(encoding="utf-8")
        assert 'source_path: ""' in fil
        assert "fil_structurant" in copier(v, conf, "process", "Ops", titre="Sans source", texte="x")[1]
    print("OK copie_structurant.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
