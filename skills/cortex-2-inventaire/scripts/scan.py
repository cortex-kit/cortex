#!/usr/bin/env python3
"""scan.py : mesure le disque pour le maillon 2, sans rien copier. stdlib pure.

Parcourt les racines de `collecte.racines` (ou `--racine`), dans les bornes du
contrat (`profondeur_arbre`, `max_dossiers`), et écrit `_cortex/01-inventaire.json`
v2 : `disque`, `depots`, `bornes` en entiers, signaux de base déportée, écarts
candidats observables sur disque. Le bloc `mail` reste un squelette : l'agent le
remplit selon `04-contrat.md` §7. Aucune entrée ne porte de champ `contenu` ;
l'écriture le refuse.

Le texte des candidats structurants (organigramme, process, contrat…) passe par
`uvx --from "markitdown[all]" markitdown` s'il est present, borné en octets, et n'en sort que des
mots-signaux comptés : le texte lui-même n'est jamais écrit.

Usage :
    python3 scan.py --config <config.yaml> --out <01-inventaire.json>
    python3 scan.py --racine ~/Documents [--racine …] --out <fichier>
    python3 scan.py --autotest
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

_ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(_ICI.parent.parent / "cortex-4-installation" / "scripts"))
try:
    import cortex_config          # maillon 4, interne au dépôt (contrat §6, « stdlib seule » hors imports internes)
except ImportError:               # zip partiel, dépôt de lane isolé : --config devient indisponible, le reste tourne
    cortex_config = None

PLAFOND_MAIL = 2000
OCTETS_PAR_FICHIER = 65536          # texte lu par candidat, au plus
OCTETS_TOTAL = 2 * 1024 * 1024      # texte lu sur tout le scan, au plus
SEUIL_GRAPHIFY = 500                # documents dans un dossier, sous-arbre compris
DOSSIERS_IGNORES = {"node_modules", "__pycache__", "venv"}
EXT_TEXTE = {".md", ".txt", ".csv"}
EXT_CONVERTIR = {".docx", ".pdf", ".xlsx", ".pptx"}
EXT_LIEN = {".url", ".webloc"}      # `.lnk` exclu : un raccourci Windows n'est pas une base déportée
LANGAGES = {"py": "python", "js": "javascript", "ts": "typescript", "sh": "shell", "rb": "ruby",
            "go": "go", "rs": "rust", "java": "java", "php": "php", "swift": "swift", "kt": "kotlin",
            "c": "c", "h": "c", "cpp": "cpp", "cs": "csharp", "sql": "sql", "html": "html", "css": "css"}
# mot du nom de fichier → type de structurant du contrat (donnees.structurants)
STRUCTURANTS = {"organigramme": "organigramme", "process": "process", "processus": "process",
                "procedure": "process", "fiche-de-poste": "fiche_de_poste", "fiches-de-poste": "fiche_de_poste",
                "poste": "fiche_de_poste", "contrat": "contrat", "convention": "contrat",
                "cahier-des-charges": "projet", "cadrage": "projet", "projet": "projet",
                "organisation": "organigramme", "annuaire": "acteur", "parties-prenantes": "acteur"}
VIDES = {"les", "des", "une", "pour", "avec", "dans", "sur", "par", "aux", "est", "son", "ses",
         "the", "and", "not", "que", "qui", "pas", "plus", "sans", "sous", "entre", "ainsi",
         "cette", "ces", "elle", "ils", "nous", "vous", "leur", "tout", "tous", "fictif",
         "recette", "document", "note", "fichier", "copy", "copie", "final", "new", "old"}


# ── Utilitaires ─────────────────────────────────────────────────────────────

def tilde(chemin):
    """Forme `~` pour tout chemin sous le dossier personnel (invariant I2).

    Hors du dossier personnel, l'absolu est toléré : le contrat amendé (§4, chemins)
    l'admet pour un dépôt cloné ailleurs, recette lancée depuis un dossier temporaire
    comprise. Pas de `.resolve()` : une racine liée symboliquement vers un volume
    externe sortirait du dossier personnel et rendrait un absolu là où `~` existe.
    """
    s = os.path.abspath(str(Path(chemin).expanduser()))
    maison = str(Path.home())
    return "~" + s[len(maison):] if s == maison or s.startswith(maison + os.sep) else s


def plat(s):
    """Minuscules, sans accent, lettres et chiffres séparés par `-`."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def mots(texte):
    """Mots-signaux d'un texte : au moins 4 lettres, hors mots vides."""
    return [m for m in re.findall(r"[a-z]{4,}", plat(texte).replace("-", " ")) if m not in VIDES]


def date(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def refuser_contenu(obj, chemin="$"):
    """Le schéma interdit `contenu` : on refuse d'écrire plutôt que de faire confiance."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "contenu":
                raise ValueError(f"champ `contenu` interdit ({chemin}.{k}) : l'inventaire pointe, il ne copie pas")
            refuser_contenu(v, f"{chemin}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            refuser_contenu(v, f"{chemin}[{i}]")


# ── Extraction bornée ───────────────────────────────────────────────────────

class Extracteur:
    """Lit le texte d'un candidat structurant, borné en octets, et ne garde que ses mots."""

    def __init__(self, actif=True):
        self.uvx = shutil.which("uvx") if actif else None
        self.octets = 0
        self.fichiers = 0
        self.echecs = 0

    def texte(self, chemin):
        reste = OCTETS_TOTAL - self.octets
        if reste <= 0:
            return ""
        borne = min(OCTETS_PAR_FICHIER, reste)
        try:
            if chemin.suffix.lower() in EXT_TEXTE:
                brut = chemin.read_bytes()[:borne]
            elif self.uvx and chemin.suffix.lower() in EXT_CONVERTIR:
                # `markitdown` seul ne lit ni pdf ni docx : les extras sont indispensables.
                # cwd hors du vault : le convertisseur laisse parfois un fichier de télémétrie dans le dossier courant.
                r = subprocess.run([self.uvx, "--from", "markitdown[all]", "markitdown", str(chemin.resolve())],
                                   capture_output=True, timeout=60, cwd=tempfile.gettempdir())
                if r.returncode != 0:
                    self.echecs += 1
                    return ""
                brut = r.stdout[:borne]
            else:
                return ""
        except (OSError, subprocess.SubprocessError):
            self.echecs += 1
            return ""
        self.octets += len(brut)
        self.fichiers += 1
        return brut.decode("utf-8", "replace")


# ── Parcours ────────────────────────────────────────────────────────────────

def candidat_structurant(nom, types):
    base = plat(Path(nom).stem)
    for mot, type_ in STRUCTURANTS.items():
        if type_ in types and (mot in base.split("-") or mot in base):
            return type_
    return None


def signal_base(nom):
    ext = Path(nom).suffix.lower()
    base = plat(Path(nom).stem)
    return ext == ".base" or ext in EXT_LIEN or (ext == ".csv" and base.startswith("export"))


def dernier_commit(dossier):
    git = shutil.which("git")
    if not git:
        return ""
    try:
        r = subprocess.run([git, "-C", str(dossier), "log", "-1", "--format=%cs"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def readme_20_lignes(dossier):
    for nom in ("README.md", "readme.md", "README", "README.txt"):
        f = dossier / nom
        if f.is_file():
            try:
                return "\n".join(f.read_text(encoding="utf-8", errors="replace").splitlines()[:20])
            except OSError:
                return ""
    return ""


def prefixes(racines):
    """Préfixe de `source_id` par racine, unique entre racines (contrat §4, rejeu du scan).

    Deux racines de même nom de base (`A/Travail` et `B/Travail`) sont désambiguïsées
    par le dernier segment de leur parent, sans quoi `ecarts_candidats[].source_id` et
    `preuve_de` pointeraient sur deux dossiers différents.
    """
    noms = [plat(Path(r).expanduser().name) for r in racines]
    out = []
    for r, nom in zip(racines, noms):
        parent = plat(Path(r).expanduser().parent.name)
        out.append("-".join(x for x in (parent, nom) if x) if noms.count(nom) > 1 else nom)
    return out


def scanner(racines, profondeur_arbre, max_dossiers, types_structurants, extracteur,
            max_extractions, budget_secondes):
    """Parcourt les racines ; renvoie (disque, depots, bornes)."""
    disque, depots = [], []
    bornes = {"profondeur_max_vue": 0, "dossiers_vus": 0, "fichiers_vus": 0, "octets_extraits": 0,
              "profondeur_arbre": profondeur_arbre, "max_dossiers": max_dossiers,
              "dossiers_au_dela": 0, "extractions": 0, "depassement": False}
    extractions = 0
    debut = time.monotonic()

    def hors_budget():
        return time.monotonic() - debut > budget_secondes

    for racine, prefixe in zip(racines, prefixes(racines)):
        racine = Path(racine).expanduser()
        if not racine.is_dir():
            raise FileNotFoundError(f"racine introuvable : {tilde(racine)}")
        if hors_budget():
            bornes["dossiers_au_dela"] += 1      # au moins cette racine n'a pas été ouverte
            bornes["depassement"] = True
            continue
        pile = [(racine, 0)]
        entrees = {}   # chemin → entrée, pour cumuler fichiers_arbre
        while pile:
            if hors_budget():
                # arrêt propre : le budget de temps est une borne comme une autre (contrat §2)
                bornes["dossiers_au_dela"] += len(pile)
                bornes["depassement"] = True
                break
            dossier, prof = pile.pop(0)
            if bornes["dossiers_vus"] >= max_dossiers:
                bornes["dossiers_au_dela"] += 1
                bornes["depassement"] = True
                continue
            try:
                items = sorted(os.scandir(dossier), key=lambda e: e.name)
            except OSError:
                continue
            bornes["dossiers_vus"] += 1
            bornes["profondeur_max_vue"] = max(bornes["profondeur_max_vue"], prof)
            fichiers, sous, ext, mtimes, sig, cand, bases, depot = 0, 0, Counter(), [], Counter(), [], [], False
            for e in items:
                # une permission retirée ou un volume démonté en cours de parcours ne doit
                # pas avorter le scan : `is_dir`, `is_file` et `stat` lèvent tous `OSError`
                try:
                    if e.name == ".git":
                        depot = True
                        continue
                    if e.name.startswith(".") or e.name in DOSSIERS_IGNORES:
                        continue
                    if e.is_dir(follow_symlinks=False):
                        sous += 1
                        if prof < profondeur_arbre:
                            pile.append((Path(e.path), prof + 1))
                        else:
                            bornes["dossiers_au_dela"] += 1
                            bornes["depassement"] = True
                        continue
                    if not e.is_file(follow_symlinks=False):
                        continue
                    fichiers += 1
                    bornes["fichiers_vus"] += 1
                    suffixe = Path(e.name).suffix.lower().lstrip(".")
                    ext[suffixe or "sans"] += 1
                    mtimes.append(e.stat().st_mtime)
                except OSError:
                    continue
                sig.update(mots(Path(e.name).stem))
                if signal_base(e.name):
                    bases.append(e.name)
                type_ = candidat_structurant(e.name, types_structurants)
                if type_:
                    cand.append(e.name)
                    if extractions < max_extractions and not hors_budget():
                        extractions += 1
                        sig.update(mots(extracteur.texte(Path(e.path))))
                    else:
                        bornes["depassement"] = True
            sig.update(mots(dossier.name))
            rel = dossier.relative_to(racine)
            entree = {
                "source_id": "-".join(x for x in (prefixe, plat(str(rel)) if str(rel) != "." else "") if x),
                "substrat": "espace_documentaire", "type": "dossier", "chemin": tilde(dossier),
                "profondeur": prof, "fichiers": fichiers, "fichiers_arbre": fichiers, "sous_dossiers": sous,
                "extensions": dict(sorted(ext.items())),
                "derniere_maj": date(max(mtimes)) if mtimes else "", "premiere_maj": date(min(mtimes)) if mtimes else "",
                "depot_git": depot,
                "signal_ontologique": {"mots": [m for m, _ in sig.most_common(8)], "structurant_candidat": cand},
                "signaux_base_deportee": bases, "resume": "", "preuve_de": [],
            }
            disque.append(entree)
            entrees[dossier] = entree
            for parent in dossier.parents:
                if parent in entrees:
                    entrees[parent]["fichiers_arbre"] += fichiers
                if parent == racine:
                    break
            if depot:
                depots.append({"source_id": "depot-" + entree["source_id"], "type": "depot", "chemin": tilde(dossier),
                               "langages": [], "dernier_commit": dernier_commit(dossier),
                               "readme_20_lignes": readme_20_lignes(dossier), "graphify_propose": False})
    # langages d'un dépôt : extensions vues dans son sous-arbre, dans les bornes.
    # Hors de la boucle des racines : le calcul est le même à chaque tour, sur un `disque` qui grandit.
    for d in depots:
        racine_depot = Path(d["chemin"]).expanduser()
        vus = Counter()
        for e in disque:
            p = Path(e["chemin"]).expanduser()
            if p == racine_depot or racine_depot in p.parents:
                for x, n in e["extensions"].items():
                    if x in LANGAGES:
                        vus[LANGAGES[x]] += n
        d["langages"] = [l for l, _ in vus.most_common(5)]
        # un dépôt sans code (vault versionné, dossier de notes sous git) ne gagne rien à un graphe
        d["graphify_propose"] = bool(d["langages"])
    # une proposition par sous-arbre : le seuil porte sur `fichiers_arbre`, cumulé chez tous les parents
    proposes = []
    for e in disque:
        if e["fichiers_arbre"] > SEUIL_GRAPHIFY and not any(e["chemin"].startswith(p + "/") for p in proposes):
            e["graphify_propose"] = True
            proposes.append(e["chemin"])
    bornes["octets_extraits"] = extracteur.octets
    bornes["extractions"] = extracteur.fichiers
    return disque, depots, bornes


def ecarts(disque, depots, base_declaree):
    """Écarts observables sur le disque seul ; l'agent ajoute ceux qui confrontent le cadrage."""
    out = []
    if not base_declaree:
        for e in disque:
            if e["signaux_base_deportee"]:
                out.append({"type": "base_deportee_non_declaree",
                            "indice": f"{e['chemin']} : {', '.join(e['signaux_base_deportee'][:3])}"
                                      + (f" (+{len(e['signaux_base_deportee']) - 3})" if len(e["signaux_base_deportee"]) > 3 else ""),
                            "source_id": e["source_id"]})
    for d in depots:
        out.append({"type": "depot_non_declare", "indice": f"{d['chemin']} : dépôt git, dernier commit {d['dernier_commit'] or 'inconnu'}",
                    "source_id": d["source_id"]})
    return out


def inventaire(conf, racines, extracteur):
    collecte = conf.get("collecte") or {}
    donnees = conf.get("donnees") or {}
    types = donnees.get("structurants") or list(dict.fromkeys(STRUCTURANTS.values()))
    racines = racines or collecte.get("racines") or []
    if not racines:
        raise ValueError("aucune racine : passer --racine ou une config avec collecte.racines")
    # `collecte.max_extractions` est le plafond de conversion du maillon 2 ; `sante.max_structurants`
    # est celui de la copie du maillon 5, et n'est plus lu ici (contrat §2, amendement `collecte`).
    disque, depots, bornes = scanner(
        racines, int(collecte.get("profondeur_arbre", 3)), int(collecte.get("max_dossiers", 200)),
        set(types), extracteur, int(collecte.get("max_extractions", 40)),
        float(collecte.get("budget_secondes", 120)))
    poste = conf.get("poste") or {}
    return {
        "format": "cortex/inventaire", "version": 2, "genere_le": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "profil": conf.get("profil", ""), "regime": donnees.get("regime", ""),
        "racines": [tilde(Path(r).expanduser()) for r in racines],
        "bornes": bornes, "extraction": {"outil": "markitdown" if extracteur.uvx else "", "echecs": extracteur.echecs},
        "disque": disque, "bases": [], "depots": depots,
        "mail": {"voie": (poste.get("mail_voie") or "aucune") if collecte.get("mail_optin") else "aucune",
                 "periode_mois": int(collecte.get("mail_mois", 12)), "en_tetes_lus": 0, "plafond": PLAFOND_MAIL,
                 "agregats": [], "acteurs": [], "sujets_recurrents": [], "fils_structurants": []},
        "agenda": [],
        "ecarts_candidats": ecarts(disque, depots, bool((conf.get("substrats") or {}).get("base_projets"))),
    }


CLES_REJEU = ("format", "version", "genere_le", "racines", "bornes", "extraction", "disque", "depots")
ECARTS_DU_DISQUE = {"base_deportee_non_declaree", "depot_non_declare"}


def fusionner(neuf, ancien):
    """Rejeu du scan sur un `--out` existant (contrat §4, amendement « rejeu du scan »).

    Le disque se remplace ; le travail de l'agent survit : `mail`, `bases`, `agenda`,
    les `resume` et `preuve_de` posés par entrée, et les écarts qu'il a dérivés du
    cadrage. `SKILL.md` fait du rejeu du disque seul un geste normal de validation par
    substrat : il ne doit pas coûter une campagne de lecture d'en-têtes.
    """
    garde = {e.get("source_id"): e for e in (ancien.get("disque") or []) if isinstance(e, dict)}
    for e in neuf["disque"]:
        vieux = garde.get(e["source_id"])
        if vieux:
            e["resume"] = vieux.get("resume", "")
            e["preuve_de"] = vieux.get("preuve_de", [])
    out = dict(ancien)
    out.update({k: neuf[k] for k in CLES_REJEU})
    out["ecarts_candidats"] = [x for x in (ancien.get("ecarts_candidats") or [])
                               if not (isinstance(x, dict) and x.get("type") in ECARTS_DU_DISQUE)]
    out["ecarts_candidats"] += neuf["ecarts_candidats"]
    return out


def ecrire(inv, sortie):
    sortie = Path(sortie).expanduser()
    if sortie.is_file():
        try:
            ancien = json.loads(sortie.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ancien = None
        if isinstance(ancien, dict) and inv.get("format") == "cortex/inventaire":
            inv = fusionner(inv, ancien)
    refuser_contenu(inv)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return inv


# ── Auto-test ───────────────────────────────────────────────────────────────

def _autotest():
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp) / "Travail"
        (r / "Projets/CRM").mkdir(parents=True)
        (r / "Projets/CRM/export-outil-2026-01.csv").write_text("Nom,Statut\nX,En cours\n")
        (r / "Projets/CRM/ORGANIGRAMME.md").write_text("# Organigramme\n\nDirection commerciale, direction technique.\n")
        (r / "Outil/.git").mkdir(parents=True)
        (r / "Outil/main.py").write_text("print(1)\n")
        (r / "Outil/README.md").write_text("# Outil\nligne 2\n")
        (r / "a/b/c/d/e").mkdir(parents=True)
        (r / "a/b/c/d/e/profond.txt").write_text("x")
        conf = {"profil": "employe", "donnees": {"regime": "copie"}, "collecte": {"profondeur_arbre": 2, "max_dossiers": 200}}
        inv = inventaire(conf, [str(r)], Extracteur(actif=False))
        refuser_contenu(inv)
        b = inv["bornes"]
        # `isinstance(False, int)` vaut True : les compteurs se testent à part du drapeau
        assert all(isinstance(v, int) and not isinstance(v, bool)
                   for k, v in b.items() if k != "depassement"), b
        assert isinstance(b["depassement"], bool), b
        assert b["profondeur_max_vue"] == 2 and b["depassement"] is True and b["dossiers_au_dela"] == 1, b
        assert b["fichiers_vus"] == 4, b   # profond.txt est au-delà de la profondeur
        crm = next(e for e in inv["disque"] if e["source_id"] == "travail-projets-crm")
        assert crm["signaux_base_deportee"] == ["export-outil-2026-01.csv"], crm
        assert crm["signal_ontologique"]["structurant_candidat"] == ["ORGANIGRAMME.md"], crm
        assert "commerciale" in crm["signal_ontologique"]["mots"], crm["signal_ontologique"]
        assert crm["extensions"] == {"csv": 1, "md": 1} and crm["chemin"].startswith(("~", "/")), crm
        assert inv["depots"] and inv["depots"][0]["langages"] == ["python"] and inv["depots"][0]["graphify_propose"], inv["depots"]
        assert inv["depots"][0]["readme_20_lignes"].startswith("# Outil"), inv["depots"]
        assert {e["type"] for e in inv["ecarts_candidats"]} == {"base_deportee_non_declaree", "depot_non_declare"}
        assert next(e for e in inv["disque"] if e["profondeur"] == 0)["fichiers_arbre"] == 4
        assert inv["mail"]["voie"] == "aucune" and inv["mail"]["plafond"] == PLAFOND_MAIL
        sortie = Path(tmp) / "inv.json"
        ecrire(inv, sortie)
        assert json.loads(sortie.read_text())["version"] == 2

        # témoin du rejeu (contrat §4) : le travail de l'agent survit au second scan
        pose = json.loads(sortie.read_text())
        pose["mail"].update({"voie": "connecteur", "en_tetes_lus": 1840,
                             "agregats": [{"domaine": "client.test", "volume": 612}]})
        pose["bases"] = [{"source_id": "base-projets", "substrat": "base_projets", "resume": "à la main"}]
        pose["agenda"] = [{"titre": "Comité hebdo", "recurrence": "hebdomadaire", "occurrences": 40}]
        pose["ecarts_candidats"].append({"type": "correspondant_non_declare",
                                         "indice": "client.test, 612 messages", "source_id": "mail"})
        for e in pose["disque"]:
            e["resume"], e["preuve_de"] = "résumé de l'agent", ["projet-crm"]
        sortie.write_text(json.dumps(pose, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (r / "Projets/CRM/ajout.md").write_text("x")
        rejeu = ecrire(inventaire(conf, [str(r)], Extracteur(actif=False)), sortie)
        assert rejeu["mail"]["en_tetes_lus"] == 1840 and rejeu["mail"]["agregats"], rejeu["mail"]
        assert rejeu["bases"] and rejeu["agenda"], rejeu["bases"]
        assert all(e["resume"] == "résumé de l'agent" and e["preuve_de"] == ["projet-crm"]
                   for e in rejeu["disque"]), rejeu["disque"]
        assert [x["type"] for x in rejeu["ecarts_candidats"]].count("correspondant_non_declare") == 1
        assert [x["type"] for x in rejeu["ecarts_candidats"]].count("depot_non_declare") == 1
        assert rejeu["bornes"]["fichiers_vus"] == 5, rejeu["bornes"]   # le disque, lui, est bien relu

        # témoin de l'unicité des `source_id` entre deux racines de même nom (contrat §4)
        for cote in ("A", "B"):
            (Path(tmp) / cote / "Travail" / "Projets").mkdir(parents=True)
            (Path(tmp) / cote / "Travail" / "Projets" / "note.md").write_text("x")
        deux = inventaire(conf, [str(Path(tmp) / "A" / "Travail"), str(Path(tmp) / "B" / "Travail")],
                          Extracteur(actif=False))
        ids = [e["source_id"] for e in deux["disque"]]
        assert ids == ["a-travail", "a-travail-projets", "b-travail", "b-travail-projets"], ids

        try:
            ecrire({"disque": [{"contenu": "x"}]}, sortie)
            raise AssertionError("un champ contenu aurait dû être refusé")
        except ValueError:
            pass
    print("OK scan.py : bornes en entiers, `depassement` booléen, base déportée, dépôt, "
          "profondeur, rejeu non destructif, `source_id` unique entre racines, refus de `contenu`")
    return 0


def main():
    p = argparse.ArgumentParser(description="Mesure le disque pour le maillon 2 (jamais de copie).")
    p.add_argument("--racine", action="append", default=[], help="dossier à parcourir, répétable ; forme ~ admise")
    p.add_argument("--config", help="config.yaml de l'atelier (collecte.racines, bornes, profil, régime)")
    p.add_argument("--out", help="fichier JSON à écrire (par défaut : sortie standard)")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    conf = {}
    if a.config:
        if cortex_config is None:
            print("scan.py : --config a besoin de cortex_config.py, livré par le maillon 4 dans "
                  "skills/cortex-4-installation/scripts/. Dépôt incomplet : passer --racine à la place.",
                  file=sys.stderr)
            return 1
        conf = cortex_config.charger(a.config)
    try:
        inv = inventaire(conf, a.racine, Extracteur())
    except (FileNotFoundError, ValueError) as e:
        print(f"scan.py : {e}", file=sys.stderr)
        return 1
    if a.out:
        inv = ecrire(inv, a.out)
        b = inv["bornes"]
        print(f"{tilde(a.out)} : {b['dossiers_vus']} dossiers, {b['fichiers_vus']} fichiers, "
              f"{len(inv['depots'])} dépôt(s), {b['extractions']} extraction(s), "
              f"{len(inv['ecarts_candidats'])} écart(s), dépassement={str(b['depassement']).lower()}")
    else:
        refuser_contenu(inv)
        print(json.dumps(inv, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
