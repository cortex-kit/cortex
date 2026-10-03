#!/usr/bin/env python3
"""miroir.py — fait descendre la phase et le statut de la base de projets vers les fiches.

Sens unique : la base fait foi, le vault se recale. Rien ne remonte jamais vers
la base (Architecture - Vue d'ensemble, liens interdits). Seuls les champs à
liste fermée descendent, et une valeur hors du vocabulaire du vault se signale
au lieu de s'écrire : une phase devinée est indistinguable d'une phase lue.

Configuration (config.yaml du vault) :
    miroir:
      outil: notion                         # "" = pas de miroir
      jeton: "~/.config/cortex/notion_token" # chemin du fichier du jeton, jamais le jeton
      phase: "Phase en cours"               # nom de la propriété dans la base
      statut: "Statut"
    miroir_statuts:
      - { source: "En cours", vault: actif }

Une fiche se relie à sa ligne de base par `url_canonique` (l'identifiant de 32
caractères hexadécimaux qu'elle contient). Dans un vault adopté, le bloc `alias`
de config.yaml dit sous quel nom chaque clé se lit et s'écrit (`url_canonique:
notion_bdd`, `cycle: nature`) : le miroir écrit sous la clé présente dans la fiche.

Usage :
  python3 .claude/skills/miroir/miroir.py --vault .            # constat, n'écrit rien
  python3 .claude/skills/miroir/miroir.py --vault . --ecrire   # recale les fiches
  python3 .claude/skills/miroir/miroir.py --autotest
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lint"))
if len(Path(__file__).resolve().parents) > 5:  # gabarit dans le dépôt : cortex_config.py dans scripts/
    sys.path.insert(1, str(Path(__file__).resolve().parents[5] / "scripts"))
import cortex_config  # noqa: E402  (déposé par l'installation dans .claude/skills/lint/)

ID = re.compile(r"([0-9a-f]{32})(?:[?#]|$)")
VERSION_NOTION = "2022-06-28"


def identifiant(url):
    m = ID.search(str(url or "").replace("-", "").lower())
    return m.group(1) if m else ""


def lire_jeton(fichier):
    """Le jeton d'un fichier qui ne contient que lui, ou d'un .env (NOTION_TOKEN=…)."""
    t = fichier.read_text(encoding="utf-8").strip() if fichier.is_file() else ""
    m = re.search(r"^(?:export\s+)?NOTION_TOKEN\s*=\s*['\"]?([^'\"\s]+)", t, re.M)
    return m.group(1) if m else (t.splitlines()[0].strip() if t and "=" not in t.splitlines()[0] else "")


def notion(jeton):
    """Lecteur de page Notion : rend {propriété: valeur} pour les listes fermées."""
    def lire(page_id):
        req = urllib.request.Request(f"https://api.notion.com/v1/pages/{page_id}", headers={
            "Authorization": f"Bearer {jeton}", "Notion-Version": VERSION_NOTION})
        with urllib.request.urlopen(req, timeout=20) as r:
            props = json.load(r).get("properties", {})
        out = {}
        for nom, p in props.items():
            v = p.get(p.get("type", ""))
            if isinstance(v, dict) and "name" in v:      # select, status
                out[nom] = v["name"]
        return out
    return lire


def frontmatter(texte):
    m = re.match(r"^---\n(.*?)\n---\n", texte, re.S)
    return m.group(1) if m else ""


def champ(fm, cle):
    m = re.search(rf"^{cle}:\s*(.*)$", fm, re.M)
    return m.group(1).split("#")[0].strip().strip("\"'") if m else ""


def cles(fm):
    return set(re.findall(r"^([\w_]+):", fm, re.M))


def remplacer(texte, cle, valeur):
    """Remplace la ligne `cle:` du frontmatter, ou l'ajoute en fin de frontmatter
    si la fiche ne la porte pas : sans cet ajout, la fiche était annoncée recalée
    sans qu'aucune ligne n'ait changé."""
    fm = frontmatter(texte)
    if cle in cles(fm):
        neuf = re.sub(rf"^{cle}:.*$", lambda _: f"{cle}: {valeur}", fm, count=1, flags=re.M)
    else:
        neuf = f"{fm}\n{cle}: {valeur}"
    return texte.replace(fm, neuf, 1)


def recaler(vault, conf, lire):
    """Rend (changements, constats). Un changement : (fiche, champ, avant, après)."""
    m = conf.get("miroir") or {}
    statuts = {str(x.get("source")): str(x.get("vault")) for x in conf.get("miroir_statuts") or []}
    progressions = {(c.get("cycle"), c.get("phase")): c.get("progression") for c in conf.get("cycles") or []}
    changements, constats = [], []
    for md in sorted((vault / "20 - Projets").glob("*.md")):
        texte = md.read_text(encoding="utf-8")
        fm = frontmatter(texte)
        presentes = cles(fm)

        def nom(canon):
            return cortex_config.cle_effective(presentes, canon, conf)
        pid = identifiant(champ(fm, nom("url_canonique")))
        if champ(fm, "type") != "projet" or not pid:
            continue
        try:
            source = lire(pid)
        except Exception as e:  # réseau, droits, page supprimée : constat, jamais arrêt
            constats.append(f"{md.stem} : base injoignable ({type(e).__name__})")
            continue
        cycle = champ(fm, nom("cycle"))
        phase, progression, statut = nom("phase"), nom("progression"), nom("statut")
        if m.get("phase"):
            v = source.get(m["phase"], "")
            if v and v != champ(fm, phase):
                if v in cortex_config.phases_autorisees(conf, cycle):
                    changements.append((md, phase, champ(fm, phase), v))
                    p = progressions.get((cycle, v))
                    if p is not None and str(p) != champ(fm, progression):
                        changements.append((md, progression, champ(fm, progression), str(p)))
                else:
                    constats.append(f"{md.stem} : phase « {v} » hors du cycle {cycle or 'aucun'}, non recopiée")
        if m.get("statut"):
            v = source.get(m["statut"], "")
            if v and v not in statuts:
                constats.append(f"{md.stem} : statut « {v} » sans correspondance dans miroir_statuts")
            elif v and statuts[v] != champ(fm, statut):
                changements.append((md, statut, champ(fm, statut), statuts[v]))
    return changements, constats


def ecrire(changements):
    par_fiche = {}
    for md, cle, _, apres in changements:
        par_fiche.setdefault(md, []).append((cle, apres))
    for md, champs in par_fiche.items():
        texte = md.read_text(encoding="utf-8")
        for cle, apres in champs:
            # Guillemets dès que la valeur n'est pas un mot simple (« Phase D ») :
            # la règle tient quel que soit le nom de la clé dans un vault adopté.
            texte = remplacer(texte, cle, apres if re.fullmatch(r"[\w-]+", apres) else f'"{apres}"')
        md.write_text(texte, encoding="utf-8")
    return len(par_fiche)


def main():
    p = argparse.ArgumentParser(description="Miroir descendant base de projets → fiches.")
    p.add_argument("--vault", default=".")
    p.add_argument("--ecrire", action="store_true")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    vault = Path(a.vault).expanduser().resolve()
    conf = cortex_config.charger(vault / "config.yaml")
    m = conf.get("miroir") or {}
    # Un alias mal écrit relierait zéro fiche, et « Fiches alignées » mentirait.
    erreurs = cortex_config.erreurs_alias(conf)
    if erreurs:
        print("\n".join(erreurs), file=sys.stderr)
        return 2
    if m.get("outil") != "notion":
        print("Aucun miroir configuré (miroir.outil vide) : rien à faire.")
        return 0
    jeton = os.environ.get("CORTEX_NOTION_TOKEN", "")
    if not jeton and m.get("jeton"):
        jeton = lire_jeton(Path(str(m["jeton"])).expanduser())
    if not jeton:
        print(f"Jeton introuvable ({m.get('jeton') or 'miroir.jeton vide'}) : rien n'a été lu.", file=sys.stderr)
        return 2
    changements, constats = recaler(vault, conf, notion(jeton))
    for md, cle, avant, apres in changements:
        print(f"{md.stem} : {cle} « {avant} » → « {apres} »")
    for c in constats:
        print(f"[!] {c}")
    if not changements:
        print("Fiches alignées sur la base.")
    elif a.ecrire:
        print(f"✓ {ecrire(changements)} fiche(s) recalée(s). Dites « clôture » pour l'enregistrer.")
    else:
        print(f"{len(changements)} changement(s) à appliquer : relancer avec --ecrire.")
    return 0


def _autotest():
    import tempfile
    conf = {"cycles": [{"cycle": "mission", "phase": "Phase A", "progression": 10},
                       {"cycle": "mission", "phase": "Phase D", "progression": 90}],
            "miroir": {"outil": "notion", "phase": "Phase en cours", "statut": "Statut"},
            "miroir_statuts": [{"source": "En cours", "vault": "actif"}, {"source": "Terminee", "vault": "termine"}]}
    fiche = ('---\ntype: projet\nstatut: actif\ncycle: mission\nphase: "Phase A"\nprogression: 10\n'
             'url_canonique: "https://app.notion.com/p/{id}"\n---\n# X\n')
    base = {"a" * 32: {"Phase en cours": "Phase D", "Statut": "Terminee"},
            "b" * 32: {"Phase en cours": "Phase Z", "Statut": "Inconnu"},
            "c" * 32: {"Phase en cours": "Phase A", "Statut": "En cours"}}

    def lire(pid):
        if pid not in base:
            raise OSError("404")
        return base[pid]
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        (v / "20 - Projets").mkdir()
        for nom, pid in (("Alpha", "a" * 32), ("Beta", "b" * 32), ("Gamma", "c" * 32), ("Delta", "d" * 32)):
            (v / "20 - Projets" / f"{nom}.md").write_text(fiche.format(id=pid), encoding="utf-8")
        ch, co = recaler(v, conf, lire)
        assert sorted((md.stem, k, a, b) for md, k, a, b in ch) == [
            ("Alpha", "phase", "Phase A", "Phase D"), ("Alpha", "progression", "10", "90"),
            ("Alpha", "statut", "actif", "termine")], ch
        assert len(co) == 3 and any("Phase Z" in c for c in co) and any("Inconnu" in c for c in co) \
            and any("injoignable" in c for c in co), co
        assert ecrire(ch) == 1
        t = (v / "20 - Projets" / "Alpha.md").read_text(encoding="utf-8")
        assert 'phase: "Phase D"' in t and "progression: 90" in t and "statut: termine" in t, t
        assert recaler(v, conf, lire)[0] == []                       # rejoué : rien à faire
        assert identifiant("https://www.notion.so/Titre-" + "e" * 32 + "?pvs=4") == "e" * 32
        assert identifiant("https://app.notion.com/p/3c00ef92-eb03-81cf-8578-fa88013e1a97") \
            == "3c00ef92eb0381cf8578fa88013e1a97"
        # Vault adopté : la fiche se relie par `notion_bdd`, porte son cycle dans
        # `nature` et son avancement dans `avancement`. Le recalage s'écrit sous
        # ces clés, aucune clé canonique n'apparaît.
        ca = dict(conf, alias={"cycle": "nature", "url_canonique": "notion_bdd",
                               "progression": "avancement"})
        (v / "20 - Projets" / "Epsilon.md").write_text(
            '---\ntype: projet\nstatut: actif\nnature: mission\nphase: "Phase A"\navancement: 10\n'
            'notion_bdd: "https://app.notion.com/' + "a" * 32 + '"\n---\n# E\n', encoding="utf-8")
        ch, _ = recaler(v, ca, lire)
        assert sorted((md.stem, k, a, b) for md, k, a, b in ch if md.stem == "Epsilon") == [
            ("Epsilon", "avancement", "10", "90"), ("Epsilon", "phase", "Phase A", "Phase D"),
            ("Epsilon", "statut", "actif", "termine")], ch
        sans, _ = recaler(v, conf, lire)
        assert not [c for c in sans if c[0].stem == "Epsilon"], "sans alias, la fiche n'est pas reliée"
        ecrire([c for c in ch if c[0].stem == "Epsilon"])
        t = (v / "20 - Projets" / "Epsilon.md").read_text(encoding="utf-8")
        assert "avancement: 90" in t and 'phase: "Phase D"' in t and "statut: termine" in t, t
        assert "progression" not in t and "cycle" not in t and "url_canonique" not in t, t
        # Une clé absente de la fiche s'ajoute au lieu d'être annoncée sans être écrite.
        assert "progression: 90" in remplacer("---\ntype: projet\n---\n# X\n", "progression", "90")
        (v / "jeton").write_text("secret_abc\n", encoding="utf-8")
        (v / ".env").write_text("AUTRE=1\nNOTION_TOKEN='ntn_xyz'\n", encoding="utf-8")
        (v / "vide.env").write_text("AUTRE=1\n", encoding="utf-8")
        assert lire_jeton(v / "jeton") == "secret_abc" and lire_jeton(v / ".env") == "ntn_xyz"
        assert lire_jeton(v / "vide.env") == "" and lire_jeton(v / "absent") == ""
    print("OK miroir.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
