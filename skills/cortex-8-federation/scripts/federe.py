#!/usr/bin/env python3
"""federe.py : agrège les exports de plusieurs vaults en un vault commun généré. stdlib pure.

Le commun n'a pas de rédacteur. Il se vide et se régénère à chaque passage,
depuis `_export/<slug>/` de chaque membre (contrat 04 §6). Deux passages sur
les mêmes exports rendent les mêmes fichiers, à `genere_le` près.

Ce que le script refuse, avant de toucher au commun :
  - moins de deux membres, un export absent, un index.json incohérent
    (format, `version` inconnue, `slug` qui ne nomme pas le membre) ;
  - un `federation.yaml` d'une `version` inconnue ;
  - une note `visibilite: prive` dans un export ;
  - un dossier cible non vide qui ne porte pas `.cortex-genere`.

Ce qu'il signale sans refuser : une note trouvée dans un export mais absente de
son `index.json`. Elle n'est jamais copiée ; l'export du membre est périmé.

Usage :
    python3 federe.py --config <commun>/federation.yaml
    python3 federe.py --fixtures <dossier>     # trois exports fictifs + federation.yaml
    python3 federe.py --autotest
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_ICI = Path(__file__).resolve().parent
_CORTEX4 = _ICI.parent.parent / "cortex-4-installation"
sys.path.insert(0, str(_CORTEX4 / "scripts"))
import cortex_config  # noqa: E402
import lint_sante  # noqa: E402

MARQUE = "# <!-- généré par federe.py, ne pas éditer -->"
CONSERVES = {"federation.yaml", ".git", ".obsidian"}
RE_LIEN = re.compile(r"\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]+))?\]\]")

# Versions lues (contrat 04 §6). Une version inconnue est refusée : mieux vaut
# un arrêt net qu'un commun agrégé depuis un format qu'on ne comprend pas.
VERSION_FEDERATION = 1
VERSION_EXPORT = 1

# Libellé du README, contrat 04 §6. Le préfixe sert aussi au sceau : c'est la
# seule autre ligne générée qui porte la date.
PREFIXE_README = "Généré par `federe.py` le "


class Refus(Exception):
    pass


def sha256(octets):
    return hashlib.sha256(octets).hexdigest()


def _yaml_liste(valeurs):
    return "[" + ", ".join(valeurs) + "]"


def _fm(lignes):
    return "---\n" + MARQUE + "\n" + "\n".join(lignes) + "\n---\n"


# ── Lecture des exports ─────────────────────────────────────────────────────


def lire_export(slug, racine):
    """(notes listées par index.json et vérifiées, notes trouvées hors index).

    Une note hors index n'est jamais copiée ; elle est signalée, parce qu'elle
    signifie un export périmé, et qu'une note privée déposée là
    échapperait sinon au refus."""
    index = racine / "index.json"
    if not index.is_file():
        raise Refus(f"{slug} : {index} introuvable, ce vault n'a pas encore fait de clôture")
    idx = json.loads(index.read_text(encoding="utf-8"))
    if idx.get("format") != "cortex/export":
        raise Refus(f"{slug} : index.json n'est pas au format cortex/export")
    if idx.get("version") != VERSION_EXPORT:
        raise Refus(f"{slug} : index.json est en version {idx.get('version')!r}, "
                    f"cette fédération lit la version {VERSION_EXPORT}")
    if str(idx.get("slug", "")) != slug:
        raise Refus(f"{slug} : index.json porte slug {idx.get('slug')!r} ; federation.yaml "
                    "et l'export désignent deux rédacteurs différents, aucune note n'est attribuée")
    notes = []
    for entree in sorted(idx.get("notes", []), key=lambda n: n["chemin"]):
        chemin = racine / entree["chemin"]
        if not chemin.is_file():
            raise Refus(f"{slug} : {entree['chemin']} listé dans index.json mais absent")
        brut = chemin.read_bytes()
        if sha256(brut) != entree.get("hash"):
            raise Refus(f"{slug} : {entree['chemin']} ne correspond pas au hash de index.json, relancer la clôture")
        texte = brut.decode("utf-8")
        fm = lint_sante.parse_frontmatter(texte)
        if fm.get("visibilite") == "prive":
            raise Refus(f"{slug} : {entree['chemin']} porte visibilite: prive, une note privée ne passe jamais au commun")
        notes.append({"slug": slug, "chemin": entree["chemin"], "texte": texte, "fm": fm})
    indexees = {n["chemin"] for n in notes}
    hors_index = sorted(f"{slug}/{p.relative_to(racine)}" for p in racine.rglob("*.md")
                        if str(p.relative_to(racine)) not in indexees)
    return notes, hors_index


def separer(texte):
    """(lignes du frontmatter, corps). Même découpe que lint_sante."""
    if not texte.startswith("---"):
        return [], texte
    fin = texte.find("\n---", 3)
    if fin == -1:
        return [], texte
    return texte[3:fin].strip("\n").splitlines(), texte[fin + 4:]


def assembler(lignes_fm, corps, source_vault):
    """Frontmatter du membre, sans exporte_le, avec source_vault posé par le commun."""
    out, dans_liste = [], False
    for ligne in lignes_fm:
        if re.match(r"^(exporte_le|source_vault)\s*:", ligne):
            dans_liste = ligne.rstrip().endswith(":")
            continue
        if dans_liste and ligne.strip().startswith("- "):
            continue
        dans_liste = False
        out.append(ligne)
    sv = source_vault if isinstance(source_vault, str) else _yaml_liste(source_vault)
    return _fm([f"source_vault: {sv}"] + out) + corps.lstrip("\n")


def relier(corps, renommage, presents, neutralises, renommes):
    """Renomme les liens vers les projets préfixés, neutralise ceux qui sortent du commun."""
    def rempl(m):
        cible, ancre, alias = m.group(1).strip(), m.group(2) or "", m.group(3)
        if cible in renommage:
            renommes.append(renommage[cible])  # la cible dans le commun : unique par rédacteur
            return f"[[{renommage[cible]}{ancre}|{alias or cible}]]"
        if cible in presents:
            return m.group(0)
        neutralises.append(cible)
        return alias or cible
    return RE_LIEN.sub(rempl, corps)


def _retrograder(corps):
    """Titres d'un cran sous « Vu par », sauf « ## Journal » : lint_sante.py le
    reconnaît au motif `^## Journal$` et cesserait d'auditer la fiche fusionnée."""
    return re.sub(r"^(#{1,5}) (?![ \t]*Journal[ \t]*$)", r"#\1 ", corps, flags=re.M)


def _codes(fm):
    return sorted(t[2:] for t in lint_sante.en_liste(fm.get("tags")) if t.startswith("d/"))


def _domaine_de(fm):
    liens = lint_sante.liens_sortants(str(fm.get("domaine") or ""))
    return liens[0].strip() if liens else ""


# ── Génération ──────────────────────────────────────────────────────────────


def vider(commun):
    commun.mkdir(parents=True, exist_ok=True)
    contenu = [p for p in commun.iterdir() if p.name not in CONSERVES]
    if contenu and not (commun / ".cortex-genere").is_file():
        raise Refus(f"{commun} n'est pas vide et ne porte pas .cortex-genere : "
                    "ce n'est pas un commun généré, rien n'est effacé")
    for p in contenu:
        shutil.rmtree(p) if p.is_dir() else p.unlink()


def _horodate(ligne):
    """Vrai pour les deux lignes générées qui portent la date, reconnues par leur
    début. Pas pour un corps de note qui prononce le mot `genere_le` : sinon la
    note sortirait du sceau sans bruit."""
    return ligne.lstrip().startswith("genere_le:") or ligne.startswith(PREFIXE_README)


def empreinte(commun):
    """sha256 de tous les fichiers, hors .cortex-genere et hors la clé genere_le."""
    h = hashlib.sha256()
    for p in sorted(commun.rglob("*")):
        if not p.is_file() or p.name == ".cortex-genere" or {".git", ".obsidian"} & set(p.parts):
            continue
        h.update(str(p.relative_to(commun)).encode("utf-8") + b"\0")
        for ligne in p.read_bytes().splitlines(keepends=True):
            if not _horodate(ligne.decode("utf-8", "replace")):
                h.update(ligne)
        h.update(b"\0")
    return h.hexdigest()


def config_commun(nom, domaines, cycles):
    """config.yaml du commun, dérivé des exports, pour que lint_sante.py le lise.

    `profil: societe` avec `mode: federe` (contrat §2) ; `commun.racine` reste
    vide parce que le commun n'a pas de commun, ce qui suffit à ne pas armer
    `commun_edite_main` (lint_sante.py : il exige une racine non vide)."""
    lignes = ["# généré par federe.py, ne pas éditer : ce que lint_sante.py doit connaître du commun",
              "version: 1", "conduite: consultant", "profil: societe",
              "organisation:", f'  nom: "{nom}"', "  code: commun", '  redacteur: ""', '  courriel: ""',
              "mode: federe", "commun:", '  racine: ""', '  export: "_export"', "  visibilite_defaut: commun",
              "donnees:", "  regime: pointeur", "  structurants: []",
              "chemins:", '  dossiers_projets: ""',
              "marque:", '  produit_nom: "Cortex"', "  mentions_interdites: []",
              "domaines:"]
    lignes += [f'  - {{ code: {code}, nom: "{nom_d}" }}' for code, nom_d in domaines]
    lignes.append("cycles:")
    lignes += [f'  - {{ cycle: "{c}", phase: "{p}", progression: {g} }}' for c, p, g in cycles]
    lignes += ['  - { cycle: "aucun", phase: "", progression: 0 }',
               "sante:", "  max_lignes_entree_journal: 10", "  max_lignes_journal: 60",
               "  journal_perime_jours: 14", "  pointeur_canonique_obligatoire: true",
               "  interdire_orphelins: true", "  agent_metier_revue_mois: 6",
               "collecte:", f"  plafond_domaines: {max(6, len(domaines))}",
               "agents:", "  skills: []", "  sousagents: []", "  metier: []", "  hooks: []"]
    return "\n".join(lignes) + "\n"


def generer(conf, commun, quand):
    if conf.get("version") != VERSION_FEDERATION:
        raise Refus(f"federation.yaml est en version {conf.get('version')!r}, "
                    f"cette fédération lit la version {VERSION_FEDERATION}")
    membres = sorted(conf.get("membres") or [], key=lambda m: str(m.get("slug", "")))
    if len(membres) < 2:
        raise Refus("federation.yaml : au moins deux membres sont nécessaires, la fédération commence à deux vaults remplis")
    nom = str(conf.get("nom") or "Commun")
    notes, hors_index = [], []
    for m in membres:
        lues, hors = lire_export(str(m["slug"]), commun / Path(str(m["export"])).expanduser())
        notes += lues
        hors_index += hors

    par_type = {"10 - Domaines": [], "20 - Projets": [], "40 - Acteurs": [], "60 - Journal": []}
    for n in notes:
        dossier = n["chemin"].split("/", 1)[0]
        if dossier in par_type:
            par_type[dossier].append(n)

    # Projets et journal : un fichier par (membre, note), préfixé par le slug.
    renommage = {}
    for n in par_type["20 - Projets"] + par_type["60 - Journal"]:
        stem = Path(n["chemin"]).stem
        n["stem"] = f"{n['slug'].upper()} - {stem}"
        renommage.setdefault(n["slug"], {})[stem] = n["stem"]

    # Acteurs : fusion par nom.
    acteurs = {}
    for n in par_type["40 - Acteurs"]:
        acteurs.setdefault(Path(n["chemin"]).stem, []).append(n)

    # Domaines : fusion par nom, codes tirés des tags, sources et rattachements.
    domaines = {}

    def dom(nom_d):
        return domaines.setdefault(nom_d, {"codes": set(), "sources": set(), "projets": [], "acteurs": []})

    for n in par_type["10 - Domaines"]:
        d = dom(Path(n["chemin"]).stem)
        d["codes"].update(_codes(n["fm"]))
        d["sources"].add(n["slug"])
    for n in par_type["20 - Projets"]:
        nom_d = _domaine_de(n["fm"])
        if nom_d:
            d = dom(nom_d)
            d["projets"].append(n)
            d["sources"].add(n["slug"])
            if not d["codes"]:
                d["codes"].update(_codes(n["fm"]))
    for nom_a, groupe in sorted(acteurs.items()):
        nom_d = _domaine_de(groupe[0]["fm"])
        if nom_d:
            d = dom(nom_d)
            d["acteurs"].append(nom_a)
            d["sources"].update(n["slug"] for n in groupe)
            if not d["codes"]:
                d["codes"].update(_codes(groupe[0]["fm"]))

    # Codes pour config.yaml : chaque tag d/ vu doit être déclaré.
    codes_domaines, vus = [], set()
    for nom_d, d in sorted(domaines.items()):
        code = sorted(d["codes"])[0] if d["codes"] else (re.sub(r"[^a-z]", "", nom_d.lower())[:3] or "dom").ljust(2, "x")
        d["code"] = code
        if code not in vus:
            codes_domaines.append((code, nom_d))
            vus.add(code)
    for n in notes:
        for code in _codes(n["fm"]):
            if code not in vus:
                codes_domaines.append((code, code))
                vus.add(code)
    cycles = sorted({(str(n["fm"].get("cycle") or "aucun"), str(n["fm"].get("phase") or ""),
                      int(n["fm"].get("progression") or 0))
                     for n in par_type["20 - Projets"] if n["fm"].get("phase")})

    presents = ({"Centre"} | set(domaines) | set(acteurs)
                | {n["stem"] for n in par_type["20 - Projets"] + par_type["60 - Journal"]})
    neutralises, renommes = [], []

    # Tout est lu et vérifié : on peut vider.
    vider(commun)
    for dossier in ("00 - Centre", "10 - Domaines", "20 - Projets", "40 - Acteurs", "60 - Journal"):
        (commun / dossier).mkdir()

    for dossier in ("20 - Projets", "60 - Journal"):
        for n in par_type[dossier]:
            fm, corps = separer(n["texte"])
            corps = relier(corps, renommage.get(n["slug"], {}), presents, neutralises, renommes)
            (commun / dossier / f"{n['stem']}.md").write_text(assembler(fm, corps, n["slug"]), encoding="utf-8")

    fusionnes = 0
    for nom_a, groupe in sorted(acteurs.items()):
        groupe.sort(key=lambda n: n["slug"])
        sources = [n["slug"] for n in groupe]
        fm, corps = separer(groupe[0]["texte"])
        if len(groupe) == 1:
            corps = relier(corps, renommage.get(sources[0], {}), presents, neutralises, renommes)
            texte = assembler(fm, corps, sources[0])
        else:
            fusionnes += 1
            morceaux = [f"\n# {nom_a}\n"]
            for n in groupe:
                _, c = separer(n["texte"])
                c = re.sub(r"^# .*\n?", "", c.lstrip("\n"), count=1, flags=re.M)
                c = _retrograder(c)
                morceaux.append(f"\n## Vu par {n['slug']}\n\n" + relier(c, renommage.get(n["slug"], {}), presents, neutralises, renommes).strip("\n") + "\n")
            texte = assembler(fm, "".join(morceaux), sources)
        (commun / "40 - Acteurs" / f"{nom_a}.md").write_text(texte, encoding="utf-8")

    for nom_d, d in sorted(domaines.items()):
        lignes = ["type: domaine", "statut: actif", f"source_vault: {_yaml_liste(sorted(d['sources']))}",
                  "tags:", f"  - d/{d['code']}"]
        corps = [f"# {nom_d}", "", "Domaine fusionné depuis les vaults membres. Remonte vers [[Centre]].", "",
                 "## Projets", ""]
        corps += [f"- [[{n['stem']}]] ({n['slug']})" for n in sorted(d["projets"], key=lambda n: n["stem"])] or ["- aucun"]
        corps += ["", "## Acteurs", ""]
        corps += [f"- [[{a}]]" for a in sorted(d["acteurs"])] or ["- aucun"]
        (commun / "10 - Domaines" / f"{nom_d}.md").write_text(_fm(lignes) + "\n".join(corps) + "\n", encoding="utf-8")

    centre = [f"# Centre, {nom}", "",
              f"Vault commun généré depuis {len(membres)} vaults. Lecture seule : chaque fait appartient au vault qui l'a exporté.", "",
              "## Par rédacteur", ""]
    for m in membres:
        slug = str(m["slug"])
        centre += [f"### {slug}", ""]
        centre += [f"- [[{n['stem']}]]" for n in sorted(par_type["20 - Projets"], key=lambda n: n["stem"]) if n["slug"] == slug]
        centre += [f"- [[{a}]]" for a, g in sorted(acteurs.items()) if any(n["slug"] == slug for n in g)]
        centre += [f"- [[{n['stem']}]]" for n in sorted(par_type["60 - Journal"], key=lambda n: n["stem"]) if n["slug"] == slug]
        centre.append("")
    centre += ["## Par domaine", ""]
    for nom_d, d in sorted(domaines.items()):
        centre += [f"### [[{nom_d}]]", ""]
        centre += [f"- [[{n['stem']}]]" for n in sorted(d["projets"], key=lambda n: n["stem"])] or ["- aucun projet"]
        centre.append("")
    (commun / "00 - Centre" / "Centre.md").write_text(_fm(["type: hub", "tags:", "  - hub"]) + "\n".join(centre), encoding="utf-8")

    (commun / "config.yaml").write_text(config_commun(nom, codes_domaines, cycles), encoding="utf-8")
    (commun / "README.md").write_text(
        "---\n" + MARQUE + f"\ngenere_le: {quand}\n---\n"
        f"# {nom}, vault commun\n\n"
        + PREFIXE_README + f"{quand}, ne pas éditer.\n\n"
        "Chaque note vient de l'export d'un vault membre et porte `source_vault`. Pour corriger un fait, "
        "on l'édite dans le vault qui le possède, on clôture, puis on relance la fédération. "
        "Toute modification faite ici disparaît au passage suivant.\n\n"
        "Membres : " + ", ".join(str(m["slug"]) for m in membres) + ".\n", encoding="utf-8")
    sceau = empreinte(commun)
    (commun / ".cortex-genere").write_text(sceau + "\n", encoding="utf-8")
    return {"membres": [str(m["slug"]) for m in membres], "notes": len(notes),
            "journal": len(par_type["60 - Journal"]), "domaines": len(domaines),
            "projets": len(par_type["20 - Projets"]), "acteurs": len(acteurs), "fusionnes": fusionnes,
            # Les deux comptes sont des cibles distinctes, pas des occurrences :
            # une même unité des deux côtés de la virgule affichée.
            "liens_renommes": sorted(set(renommes)), "liens_neutralises": sorted(set(neutralises)),
            "hors_index": hors_index, "empreinte": sceau}


# ── Exports fictifs (recette) ───────────────────────────────────────────────


def _note(fm, corps):
    return "---\n" + "\n".join(fm) + "\n---\n" + corps


def fixtures(dossier):
    """Trois exports au format §6, dans <dossier>/<slug>/_export/<slug>/, et <dossier>/commun/federation.yaml.
    Les noms viennent de recette/fixtures.py (profil société)."""
    sys.path.insert(0, str(_CORTEX4 / "recette"))
    import fixtures as fx
    dossier = Path(dossier)
    partages = fx.CLIENTS[:2]
    membres = {"camille": partages + fx.CLIENTS[2:5], "yasmine": partages + fx.CLIENTS[5:8],
               "marc": fx.CLIENTS[8:11] + [partages[0]]}
    phases = [("Devis envoyé", 10), ("Signé", 30), ("En fabrication", 60), ("Réceptionné", 100)]
    for slug, clients in membres.items():
        exp = dossier / slug / "_export" / slug
        shutil.rmtree(exp, ignore_errors=True)
        commun_fm = ["visibilite: commun", f"source_vault: {slug}", "exporte_le: 2026-09-19T09:00:00"]
        notes = {"10 - Domaines/Affaires.md": _note(
            ["type: domaine", "statut: actif"] + commun_fm + ["tags:", "  - d/aff"],
            "# Affaires\n\nLes affaires de l'atelier, du devis à la réception. Remonte vers [[Centre]].\n")}
        titres = []
        for i, client in enumerate(clients):
            phase, prog = phases[i % 4]
            titre = f"AFF - {2024 + i % 3}-{i + 1:03d} {fx.TYPES[i % len(fx.TYPES)]} {client}"
            titres.append(titre)
            corps = (f"# {titre}\n\nDomaine : [[Affaires]]. Client : [[{client}]].\n\n## Journal\n\n"
                     f"### 2026-09-0{1 + i % 9}\n\nPhase {phase} parce que le client a répondu.\n")
            if i == 1:
                corps += f"\nVoir aussi [[{titres[0]}]] et la [[Note interne]] du rédacteur.\n"
            notes[f"20 - Projets/{titre}.md"] = _note(
                ["type: projet", 'domaine: "[[Affaires]]"', f"statut: {'termine' if prog == 100 else 'actif'}",
                 "cycle: affaire", f'phase: "{phase}"', f"progression: {prog}", "priorite: P2",
                 f'dossier_local: "{titre[6:]}"', "dernier_journal: 2026-09-01", "blocages_actifs: 0"]
                + commun_fm + ["tags:", "  - d/aff"], corps)
            notes[f"40 - Acteurs/{client}.md"] = _note(
                ["type: acteur", "categorie: client", 'domaine: "[[Affaires]]"', "statut: actif"]
                + commun_fm + ["tags:", "  - d/aff"],
                f"# {client}\n\nActeur rattaché à [[Affaires]].\n\n## Historique\n\n- 2026-09-01 : devis envoyé par {slug}.\n")
        if slug == "yasmine":
            notes["10 - Domaines/Bureau d'études.md"] = _note(
                ["type: domaine", "statut: actif"] + commun_fm + ["tags:", "  - d/bet"],
                "# Bureau d'études\n\nLes études techniques. Remonte vers [[Centre]].\n")
        notes["60 - Journal/2026-09-01 - Choix du commun.md"] = _note(
            ["type: decision", 'domaine: "[[Affaires]]"'] + commun_fm,
            "# 2026-09-01 - Choix du commun\n\nUn commun généré plutôt qu'un vault partagé.\n")
        index = []
        for chemin, texte in sorted(notes.items()):
            p = exp / chemin
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texte, encoding="utf-8")
            index.append({"chemin": chemin, "hash": sha256(texte.encode("utf-8"))})
        (exp / "index.json").write_text(json.dumps(
            {"format": "cortex/export", "version": 1, "slug": slug, "exporte_le": "2026-09-19T09:00:00",
             "notes": index}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    commun = dossier / "commun"
    commun.mkdir(parents=True, exist_ok=True)
    (commun / "federation.yaml").write_text(
        'version: 1\nnom: "Ateliers Roumier"\nmembres:\n'
        + "".join(f'  - {{ slug: {s}, export: "../{s}/_export/{s}" }}\n' for s in membres), encoding="utf-8")
    return commun / "federation.yaml"


# ── Auto-test ───────────────────────────────────────────────────────────────


def _instantane(commun):
    return {str(p.relative_to(commun)): "\n".join(l for l in p.read_text(encoding="utf-8").splitlines()
                                                 if not _horodate(l))
            for p in commun.rglob("*") if p.is_file()}


def _autotest():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = fixtures(tmp)
        conf = cortex_config.charger(cfg)
        commun = cfg.parent
        b1 = generer(conf, commun, "2026-01-01T00:00:00")
        s1 = _instantane(commun)
        b2 = generer(conf, commun, "2026-01-02T00:00:00")
        s2 = _instantane(commun)
        assert s1 == s2, "deux générations divergent hors genere_le"
        assert b1["empreinte"] == b2["empreinte"] == (commun / ".cortex-genere").read_text().strip()
        readme = (commun / "README.md").read_text(encoding="utf-8")
        assert PREFIXE_README + "2026-01-02T00:00:00, ne pas éditer." in readme, readme
        cc = cortex_config.charger(commun / "config.yaml")
        assert cc["profil"] == "societe" and cc["mode"] == "federe" and cc["commun"]["racine"] == "", cc
        assert cc["donnees"]["regime"] == "pointeur" and cc["donnees"]["structurants"] == [], cc["donnees"]
        assert not cortex_config.valider_installable(cc), cortex_config.valider_installable(cc)
        assert b2["hors_index"] == [], b2["hors_index"]
        assert b2["journal"] == 3 and (commun / "60 - Journal" / "MARC - 2026-09-01 - Choix du commun.md").is_file()
        assert b2["projets"] == 14 and b2["acteurs"] == 11 and b2["fusionnes"] == 2, b2
        assert b2["liens_renommes"] == ["CAMILLE - AFF - 2024-001 Agencement magasin Malbrun",
                                        "MARC - AFF - 2024-001 Agencement magasin Tissot",
                                        "YASMINE - AFF - 2024-001 Agencement magasin Malbrun"], b2
        fm = lint_sante.parse_frontmatter((commun / "40 - Acteurs" / "Malbrun.md").read_text(encoding="utf-8"))
        assert fm["source_vault"] == ["camille", "marc", "yasmine"], fm["source_vault"]
        fm = lint_sante.parse_frontmatter((commun / "40 - Acteurs" / "Vinci.md").read_text(encoding="utf-8"))
        assert fm["source_vault"] == "camille" and "exporte_le" not in fm, fm
        p = (commun / "20 - Projets" / "CAMILLE - AFF - 2025-002 Aménagement bureau Kervran.md").read_text(encoding="utf-8")
        assert "[[CAMILLE - AFF - 2024-001 Agencement magasin Malbrun|AFF - 2024-001" in p, "lien projet non renommé"
        assert "[[Note interne]]" not in p and "Note interne" in p and b2["liens_neutralises"] == ["Note interne"]
        assert all("<!-- généré" in q.read_text(encoding="utf-8")[:400] for q in commun.rglob("*.md"))
        assert not any("visibilite: prive" in q.read_text(encoding="utf-8") for q in commun.rglob("*.md"))
        f = lint_sante.lint(commun, cortex_config.charger(commun / "config.yaml"))
        durs = {k: f[k] for k in lint_sante.DURS if f.get(k)}
        assert not durs, f"lint_sante v1 rouge sur le commun : {durs}"

        # Une note privée glissée dans un export : refus, et le commun reste intact.
        exp = commun.parent / "camille" / "_export" / "camille"
        prive = exp / "20 - Projets" / "AFF - secret.md"
        prive.write_text("---\ntype: projet\nvisibilite: prive\n---\n# secret\n", encoding="utf-8")
        idx = json.loads((exp / "index.json").read_text(encoding="utf-8"))
        idx["notes"].append({"chemin": "20 - Projets/AFF - secret.md", "hash": sha256(prive.read_bytes())})
        (exp / "index.json").write_text(json.dumps(idx), encoding="utf-8")
        try:
            generer(conf, commun, "2026-01-03T00:00:00")
            raise AssertionError("une note prive aurait dû être refusée")
        except Refus as e:
            assert "prive" in str(e)
        assert _instantane(commun) == s2, "un refus a modifié le commun"
        idx["notes"] = [e for e in idx["notes"] if e["chemin"] != "20 - Projets/AFF - secret.md"]

        # La même note privée, hors index.json : non copiée, mais signalée.
        (exp / "index.json").write_text(json.dumps(idx), encoding="utf-8")
        b3 = generer(conf, commun, "2026-01-04T00:00:00")
        assert b3["hors_index"] == ["camille/20 - Projets/AFF - secret.md"], b3["hors_index"]
        assert not any("secret" in q.read_text(encoding="utf-8") for q in commun.rglob("*.md"))
        prive.unlink()

        # index.json qui désigne un autre rédacteur, et versions inconnues : refus.
        for cle, valeur in (("slug", "yasmine"), ("version", 2)):
            casse = dict(idx, **{cle: valeur})
            (exp / "index.json").write_text(json.dumps(casse), encoding="utf-8")
            try:
                generer(conf, commun, "2026-01-05T00:00:00")
                raise AssertionError(f"index.json avec {cle}={valeur!r} aurait dû être refusé")
            except Refus as e:
                assert cle in str(e) or "version" in str(e), e
        (exp / "index.json").write_text(json.dumps(idx), encoding="utf-8")
        try:
            generer(dict(conf, version=2), commun, "2026-01-05T00:00:00")
            raise AssertionError("federation.yaml en version 2 aurait dû être refusé")
        except Refus as e:
            assert "version" in str(e), e

        # Un « ## Journal » reste au niveau 2 sous « Vu par », le reste descend.
        assert _retrograder("## Journal\n### 2026-09-01\n## Historique\n") == \
            "## Journal\n#### 2026-09-01\n### Historique\n"

        # Un dossier cible non généré et non vide n'est jamais effacé.
        autre = Path(tmp) / "pas-un-commun"
        autre.mkdir()
        (autre / "travail.md").write_text("humain\n", encoding="utf-8")
        try:
            vider(autre)
            raise AssertionError("un dossier humain aurait dû être protégé")
        except Refus:
            pass
        assert (autre / "travail.md").is_file()
    print(f"OK : commun de {b2['projets']} projets, {b2['acteurs']} acteurs ({b2['fusionnes']} fusionnés), "
          f"{b2['domaines']} domaines, identique sur deux générations, lint v1 vert")
    return 0


def main():
    p = argparse.ArgumentParser(description="Régénère un vault commun depuis les exports de ses membres.")
    p.add_argument("--config", help="<commun>/federation.yaml")
    p.add_argument("--fixtures", help="écrit trois exports fictifs et un federation.yaml dans ce dossier")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if a.fixtures:
        print(f"exports fictifs écrits, fédération : {fixtures(a.fixtures)}")
        return 0
    if not a.config:
        p.error("--config, --fixtures ou --autotest")
    cfg = Path(a.config).expanduser().resolve()
    try:
        conf = cortex_config.charger(cfg)
        bilan = generer(conf, cfg.parent, datetime.now().isoformat(timespec="seconds"))
    except (Refus, FileNotFoundError, ValueError, KeyError) as e:
        print(f"[X] {e}", file=sys.stderr)
        return 1
    print(f"Commun régénéré : {cfg.parent}\n"
          f"  membres   : {', '.join(bilan['membres'])}\n"
          f"  notes lues: {bilan['notes']} (dont {bilan['journal']} de journal)\n"
          f"  domaines  : {bilan['domaines']}   projets : {bilan['projets']}   "
          f"acteurs : {bilan['acteurs']} (dont {bilan['fusionnes']} fusionnés)\n"
          f"  liens     : {len(bilan['liens_renommes'])} cibles renommées, "
          f"{len(bilan['liens_neutralises'])} neutralisées"
          + (f" ({', '.join(bilan['liens_neutralises'])})" if bilan["liens_neutralises"] else "") + "\n"
          f"  empreinte : {bilan['empreinte']}")
    if bilan["hors_index"]:
        print(f"  [i] {len(bilan['hors_index'])} note(s) hors index.json, non reprises : "
              f"{', '.join(bilan['hors_index'])}\n"
              "      relancer la clôture du membre concerné pour les indexer ou les retirer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
