#!/usr/bin/env python3
"""range.py : l'étape 3 bis de Cortex, ranger les dossiers de travail sur accord. stdlib pure.

C'est le seul code de la chaîne qui écrit hors du vault et de l'atelier
(doctrine §12). Il propose une liste de changements, applique les lignes
acceptées, vérifie, et défait. Il ne supprime jamais un fichier de la personne,
n'écrase jamais une destination, ne duplique rien, ne convertit rien, et ne
déplace jamais entre deux racines déclarées : ce geste-là s'écrit `manuel`, la
personne le fait dans l'interface de son outil de partage.

Ce qu'il lit : les racines de `collecte.racines`, nommées en entier, jamais par
un changement de dossier courant ; pour proposer un nom, le titre d'un document
local (première ligne d'un texte, premier paragraphe d'un .docx, objet d'un
.eml), jamais celui d'un fichier présent seulement en ligne (G6). Pour vérifier
un geste, il compare taille et date de modification, jamais le contenu (T3).

Ce qu'il écrit, dans l'atelier : `03-rangement.json` (la liste),
`03-rangement.md` (lisible, frontmatter `statut` et `acceptees`),
`03-rangement-journal.jsonl` (une ligne par geste tenté, jamais réécrite).
Contrat : chantiers/cortex-2.3-rangement/04-contrat.md §3 à §6 et A1 à A5.

Usage (`py` sous Windows vaut `python3`) :
    range.py --atelier <_cortex> --proposer [--referentiel <chemin ~>]
    range.py --atelier <_cortex> --classer r004=entreprise,r005=personnelle
    range.py --atelier <_cortex> --nommer r001="Accueil d'un nouveau client"
    range.py --atelier <_cortex> --appliquer --ids r001,r003 [--renforce] [--proprietaire "Procédures/X.docx=Nom"]
    range.py --atelier <_cortex> --verifier
    range.py --atelier <_cortex> --annuler [--ids r003]
    range.py --atelier <_cortex> --publier <SKILL.md de l'atelier> --nom <assistant> --renforce
    range.py --atelier <_cortex> --chemins
    range.py --atelier <_cortex> --montrer-index --ids r005,r006,r007 [--proprietaire …]   # rien n'est écrit
    range.py --atelier <_cortex> --autorise <chemin>      # remplissage : une fiche peut-elle pointer ici ?
    range.py --atelier <_cortex> --clore applique|refuse
    range.py --autotest

Codes de sortie : 0 fait ; 1 erreur ou écart constaté ; 2 usage ; 3 garde levée, rien n'a bougé.
"""

import argparse
import errno
import hashlib
import html
import json
import os
import re
import sys
import tempfile
import unicodedata
import zipfile
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

_ICI = Path(__file__).resolve().parent
for _p in (_ICI, _ICI.parent.parent / "cortex-4-installation" / "scripts"):
    if (_p / "cortex_config.py").is_file():
        sys.path.insert(0, str(_p))
        break
import cortex_config  # noqa: E402

PLAN, LISIBLE, JOURNAL = "03-rangement.json", "03-rangement.md", "03-rangement-journal.jsonl"
MARQUEUR = "<!-- cortex-3b-rangement: index"
OK, ECART, USAGE, GARDE = 0, 1, 2, 3
GESTES = ("renommer", "deplacer", "creer_dossier", "ecrire_index", "publier", "manuel")
CLASSES = ("", "personnelle", "entreprise", "a_demander")
PLAFOND_DEFAUT = 120
MAX_NOM = 120
MAX_LIGNES_INDEX = 200
LOT = 4
# Ordre d'exécution d'un lot : un dossier existe avant qu'on y range, l'index s'écrit en dernier.
PRIORITE = {"creer_dossier": 0, "renommer": 1, "deplacer": 1, "ecrire_index": 2}


class Garde(Exception):
    """Une garde du contrat §5 a levé : rien ne bouge, code 3."""


class Usage(ValueError):
    """Une commande mal formée (id inconnu, option manquante) : code 2. Une autre
    ValueError (journal illisible, inventaire cassé) est une erreur : code 1."""


# ── Chemins ─────────────────────────────────────────────────────────────────

def tilde(p):
    """Forme `~` d'un chemin sous le dossier personnel, sinon le chemin tel quel."""
    s = str(p).replace("\\", "/")
    home = str(Path.home()).replace("\\", "/")
    if s == home or s.startswith(home + "/"):
        return "~" + s[len(home):]
    return s


def reel(s):
    return Path(os.path.realpath(os.path.expanduser(str(s))))


def _sous(enfant, parent):
    try:
        enfant.relative_to(parent)
        return True
    except ValueError:
        return False


class Racines:
    """Les racines déclarées, comparées après résolution des liens symboliques (G4)."""

    def __init__(self, conf):
        collecte = conf.get("collecte") or {}
        brutes = collecte.get("racines") or []
        brutes = [brutes] if isinstance(brutes, str) else brutes
        part = collecte.get("partagees") or []
        part = {tilde(os.path.expanduser(p)) for p in ([part] if isinstance(part, str) else part)}
        self.liste = [(tilde(os.path.expanduser(r)), reel(r)) for r in brutes if r]
        self.partagees = part
        self._partagees_reelles = [reel(x) for x in part]

    def de(self, chemin):
        """La racine déclarée qui contient `chemin` (la plus profonde), ou None."""
        r = reel(chemin)
        candidates = [(nom, rr) for nom, rr in self.liste if _sous(r, rr)]
        if not candidates:
            return None
        return max(candidates, key=lambda c: len(c[1].parts))[0]

    def partagee(self, chemin):
        """Sous une racine partagée, même par une racine à soi déclarée plus bas (contrat §3)."""
        r = reel(chemin)
        return any(_sous(r, x) for x in self._partagees_reelles)


# ── Fichiers « en ligne seulement » (G6) ────────────────────────────────────

_SIMULES = None


def _simules():
    """Recette seulement : CORTEX_RECETTE_EN_LIGNE nomme un fichier qui liste, un par
    ligne, les chemins à traiter comme présents seulement en ligne. Un vrai fichier
    dématérialisé ne se fabrique pas sans le client de synchronisation."""
    global _SIMULES
    if _SIMULES is None:
        liste = os.environ.get("CORTEX_RECETTE_EN_LIGNE", "")
        _SIMULES = set()
        if liste and Path(liste).is_file():
            _SIMULES = {str(reel(l.strip())) for l in Path(liste).read_text(encoding="utf-8").splitlines() if l.strip()}
    return _SIMULES


def en_ligne_seulement(chemin):
    """Vrai si le fichier n'est présent qu'en ligne : le lire le téléchargerait.
    macOS : SF_DATALESS ; Windows : RECALL_ON_DATA_ACCESS ou OFFLINE. Les attributs
    seuls se lisent, jamais le contenu. Un fichier absent n'est pas en ligne ; un stat
    qui échoue pour une autre raison (droits) lève, il ne devient pas « local »."""
    try:
        st = os.stat(chemin, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if getattr(st, "st_flags", 0) & 0x40000000:
        return True
    if getattr(st, "st_file_attributes", 0) & (0x400000 | 0x1000):
        return True
    return str(reel(chemin)) in _simules()


# ── Nomenclature (contrat §6, references/nomenclature.md) ───────────────────

_DEFAUTS = re.compile(
    r"(nouveau|nouvelle) (document|classeur|presentation|dossier|fichier)( \d+)?|sans titre( \d+)?"
    r"|untitled( \d+)?|new (document|spreadsheet|presentation)( \d+)?|(document|classeur|presentation|doc|feuil)\s?\d*")
_APPAREILS = re.compile(r"(scan|img|dsc[a-z]?|pxl|photo|image|vid|mvi)\s?\d+.*|capture d.ecran.*|screenshot.*")
_COPIE_VERSION = [re.compile(p) for p in (r"\s*\(\d+\)$", r"^copie de\s+", r"^copy of\s+", r"\s+-\s+copie$",
                                          r"[\s-]+(final|def|definitif|definitive|v\d+)$")]
_PROCEDURE = re.compile(r"(^|[\s_-])(process|processus|procedure|procedures|mode operatoire|protocole)($|[\s_-])")
_DATE = re.compile(r"(20\d\d)[-_. ]?(0[1-9]|1[0-2])[-_. ]?(0[1-9]|[12]\d|3[01])")
_DATE_FINALE = re.compile(r" - \d{4}-\d{2}-\d{2}$")
_INTERDITS = re.compile(r'[/\\:*?"<>|]')
SYSTEME = {".ds_store", "thumbs.db", "desktop.ini", "icon\r"}
PAQUETS = (".app", ".bundle", ".photoslibrary", ".pages", ".numbers", ".key", ".framework", ".pkg")


def _plat(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", s.replace("_", " ")).strip()


def illisible(stem):
    """(illisible, objet) : objet est le nom débarrassé de ses marques de copie ou de
    version s'il reste parlant, "" sinon (le titre se cherche ailleurs)."""
    s = _plat(stem)
    coeur = s
    for _ in range(4):
        for motif in _COPIE_VERSION:
            coeur = motif.sub("", coeur)
    marque = coeur != s
    if not coeur or re.fullmatch(r"[\d\s.\-]+|final|def|definitif|definitive|v\d+", coeur) \
            or _DEFAUTS.fullmatch(coeur) or _APPAREILS.fullmatch(coeur):
        return True, ""
    if marque:
        # Retirer les mêmes marques sur la forme d'origine, casse et accents gardés.
        o = stem.replace("_", " ").strip()
        for _ in range(4):
            for motif in _COPIE_VERSION:
                o = re.sub(motif.pattern, "", o, flags=re.I)
        return True, o.strip(" -")
    return False, None


def est_procedure(stem):
    return bool(_PROCEDURE.search(_plat(stem)))


def date_de(stem, mtime):
    m = _DATE.search(stem)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            pass
    return date.fromtimestamp(mtime).isoformat()


def nettoyer(objet):
    o = _INTERDITS.sub(" ", objet)
    o = re.sub(r"\s+", " ", o).strip(" .")
    o = _DATE.sub("", o).strip(" -._")
    return o[:1].upper() + o[1:] if o else o


def nom_parlant(objet, jour, ext):
    o = nettoyer(objet) or "Document"
    reste = MAX_NOM - len(f" - {jour}{ext}")
    return f"{o[:reste].rstrip(' .')} - {jour}{ext}"


def titre_local(chemin):
    """Le titre lu dans un document local, borné : première ligne d'un texte, premier
    paragraphe d'un .docx, objet d'un .eml. "" si rien ne se lit."""
    ext = chemin.suffix.lower()
    try:
        if ext in (".md", ".txt", ".markdown"):
            with open(chemin, encoding="utf-8", errors="replace") as f:
                for ligne in f.read(4096).splitlines():
                    if ligne.strip():
                        return ligne.strip().lstrip("#").strip()
        elif ext == ".eml":
            with open(chemin, encoding="utf-8", errors="replace") as f:
                for ligne in f.read(4096).splitlines():
                    if ligne.lower().startswith("subject:"):
                        return ligne[8:].strip()
        elif ext == ".docx":
            with zipfile.ZipFile(chemin) as z:
                info = z.getinfo("word/document.xml")
                if info.file_size > 2_000_000:
                    return ""
                xml = z.read(info).decode("utf-8", "replace")
            for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
                t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
                if t.strip():
                    return html.unescape(t).strip()
    except (OSError, KeyError, zipfile.BadZipFile, UnicodeError) as e:
        return None   # lecture en échec (droits, archive abîmée, .docx sans corps) : à signaler
    return ""


# ── Atelier : config, plan, journal, lisible ───────────────────────────────

def charger_conf(atelier):
    return cortex_config.charger(Path(atelier) / "config.yaml")


def plafond(conf):
    v = (conf.get("sante") or {}).get("max_gestes_rangement", PLAFOND_DEFAUT)
    return v if isinstance(v, int) and v > 0 else PLAFOND_DEFAUT


def lire_plan(atelier):
    p = Path(atelier) / PLAN
    if not p.is_file():
        raise Usage(f"{PLAN} absent : lancer --proposer d'abord.")
    return json.loads(p.read_text(encoding="utf-8"))


def ecrire_plan(atelier, plan):
    (Path(atelier) / PLAN).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lire_journal(atelier):
    p = Path(atelier) / JOURNAL
    if not p.is_file():
        return []
    lignes = []
    for no, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if l.strip():
            try:
                lignes.append(json.loads(l))
            except ValueError as e:
                raise ValueError(f"{JOURNAL} ligne {no} illisible : {e}") from e
    return lignes


def journaliser(atelier, ligne):
    ligne = dict({"erreur": "", "renforce": False}, **ligne)
    ligne["fait_le"] = datetime.now().isoformat(timespec="seconds")
    with open(Path(atelier) / JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def actifs(journal):
    """{id: dernière ligne `fait`} des gestes faits et non défaits. Une ligne `echec`
    ne change pas l'état ; une ligne `annule` défait le `fait` qui la précède."""
    out = {}
    for l in journal:
        if l.get("resultat") == "fait":
            out[l["id"]] = l
        elif l.get("resultat") == "annule":
            out.pop(l["id"], None)
    return out


def retires(journal):
    """Les id dont la dernière ligne décisive est `annule` : défaits ou retirés (A5)."""
    out = set()
    for l in journal:
        if l.get("resultat") == "fait":
            out.discard(l["id"])
        elif l.get("resultat") == "annule":
            out.add(l["id"])
    return out


def lire_fm(atelier):
    p = Path(atelier) / LISIBLE
    if not p.is_file():
        return {}
    lignes = p.read_text(encoding="utf-8").splitlines()
    if not lignes or lignes[0].strip() != "---":
        return {}
    fin = next((i for i, l in enumerate(lignes[1:], 1) if l.strip() == "---"), None)
    return cortex_config.charger_texte("\n".join(lignes[1:fin])) if fin else {}


def partiel(plan_ops, fm, journal):
    """Les id acceptés ni faits ni retirés : un rangement appliqué en partie (A3)."""
    faits, ret = actifs(journal), retires(journal)
    ids = {o["id"] for o in plan_ops}
    return sorted(i for i in (fm.get("acceptees") or []) if i in ids and i not in faits and i not in ret)


def ecrire_lisible(atelier, plan, statut, acceptees, raison=""):
    """03-rangement.md, régénéré en entier à chaque geste : il ne s'édite pas à la main."""
    journal = lire_journal(atelier)
    faits, ret = actifs(journal), retires(journal)
    ops = plan["operations"]
    fm = ["---", "maillon: 3b", "produit_par: cortex-3b-rangement", f"statut: {statut}",
          "acceptees: [" + ", ".join(acceptees) + "]"]
    if raison:
        fm.append(f'raison: "{raison}"')
    construit = lire_fm(atelier).get("construit_le")
    if construit:
        fm.append(f"construit_le: {construit}")
    fm.append(f"genere_le: {plan.get('genere_le', '')}")
    fm.append("---")
    b = plan["bornes"]
    corps = [f"# Rangement des dossiers de travail", "",
             f"{len(ops)} changement(s) proposé(s), plafond {b['plafond']}"
             + (f", {b['ecartes']} écarté(s) au-delà du plafond." if b["depassement"] else "."), ""]
    if ops:
        corps += ["## La liste des changements", "", "| id | lot | geste | avant | après | raison | état |", "|---|---|---|---|---|---|---|"]
        for o in ops:
            etat = ("fait" if o["id"] in faits else "défait ou retiré" if o["id"] in ret
                    else "accepté, pas fait" if o["id"] in acceptees else "à décider")
            corps.append(f"| {o['id']} | {o['lot']} | {o['geste']} | {o.get('de', '')} | {o.get('vers', '')} "
                         f"| {o['motif']} | {etat} |")
        corps.append("")
    if plan.get("signalements"):
        corps += ["## Signalements", ""] + [f"- {s['type']} : {', '.join(s['chemins'])} ({s['motif']})"
                                           for s in plan["signalements"]] + [""]
    if plan.get("base"):
        corps += ["## Base en ligne (proposition, rien ne s'y écrit)", ""] + [
            f"- {x['objet']} : {x['constat']}. {x['proposition']}" for x in plan["base"]] + [""]
    (Path(atelier) / LISIBLE).write_text("\n".join(fm + [""] + corps), encoding="utf-8")


def dans_un_depot(chemin):
    """Vrai si le chemin, ou un dossier qui le contient, est un dépôt git ou un vault (§6)."""
    r = reel(chemin)
    return any((d / ".git").exists() or (d / ".obsidian").is_dir() for d in [r, *r.parents])


def pas_apres_construction(atelier):
    """Le rangement précède la construction (D3) : une fois le second cerveau construit
    (`construit_le`, posé par l'installation), plus rien ne se propose ni ne s'applique,
    sans quoi ses liens pointeraient vers des noms qui n'existent plus."""
    construit = lire_fm(atelier).get("construit_le")
    if construit:
        raise Garde(f"le second cerveau est construit depuis le {construit} : ranger maintenant casserait ses "
                    "liens. Ranger après la remise est hors de cette étape.")


def domaines_signes(atelier):
    """Étape 0 : les noms suivent le vocabulaire des domaines signés."""
    p = Path(atelier) / "02-ontologie.md"
    lignes = p.read_text(encoding="utf-8").splitlines() if p.is_file() else []
    fin = next((i for i, l in enumerate(lignes[1:], 1) if l.strip() == "---"), None) if lignes[:1] == ["---"] else None
    fm = cortex_config.charger_texte("\n".join(lignes[1:fin])) if fin else {}
    if fm.get("statut") != "valide":
        raise Garde("la carte des domaines n'est pas signée (02-ontologie.md en statut valide) : "
                    "les noms suivraient un vocabulaire qui va changer.")


# ── Proposer ────────────────────────────────────────────────────────────────

def _ignorer_dossier(d, nom, exclus):
    return (nom.startswith(".") or nom.lower().endswith(PAQUETS) or (d / nom / ".git").exists()
            or (d / nom / ".obsidian").is_dir() or any(_sous(reel(d / nom), x) for x in exclus))


def parcourir(racine, exclus):
    """Les fichiers de la personne sous une racine, sans suivre de lien, sans entrer
    dans un dossier caché, un dépôt git, un vault Obsidian, un paquet, l'atelier."""
    for dossier, sous, fichiers in os.walk(racine):
        d = Path(dossier)
        sous[:] = sorted(n for n in sous if not _ignorer_dossier(d, n, exclus))
        for n in sorted(fichiers):
            p = d / n
            if n.startswith((".", "~$")) or n.lower() in SYSTEME or p.is_symlink():
                continue
            yield p


def referentiel_cible(conf, racines, demande):
    """(chemin du dossier commun ou None, existe). `--referentiel` prime ; sinon la
    config s'il existe ; sinon `<seul dossier partagé>/Référentiel`."""
    ref = conf.get("referentiel") or {}
    if demande:
        chemin = demande
    elif ref.get("etat") == "existant" and ref.get("chemin"):
        chemin = ref["chemin"]
    elif len(racines.partagees) == 1:
        chemin = next(iter(racines.partagees)) + "/Référentiel"
    else:
        return None, False
    if racines.de(chemin) is None or not racines.partagee(chemin):
        raise Usage(f"le dossier commun {chemin} doit être sous un dossier de travail déclaré partagé "
                         "(collecte.partagees).")
    return tilde(os.path.expanduser(chemin)), reel(chemin).is_dir()


def proposer(atelier, demande_ref=""):
    atelier = Path(atelier)
    domaines_signes(atelier)
    pas_apres_construction(atelier)
    conf = charger_conf(atelier)
    racines = Racines(conf)
    ref, ref_existe = referentiel_cible(conf, racines, demande_ref)
    ref_reel = reel(ref) if ref else None
    # Les chemins écrits gardent la forme déclarée (pas la forme résolue) : le remplissage
    # les rapproche de l'inventaire, qui écrit la forme déclarée.
    ref_decl = Path(os.path.expanduser(ref)) if ref else None
    exclus = [reel(atelier)]          # le vault, lui, porte .obsidian/ et s'écarte comme tel
    candidats, signalements, absentes = [], [], []
    par_nom = {}
    procedures_sans_commun = []
    vus = {}   # dossier -> noms en minuscules déjà pris (existants et proposés)

    def libre(dossier, nom):
        pris = vus.setdefault(str(dossier), {p.name.lower() for p in Path(dossier).iterdir()}
                              if Path(dossier).is_dir() else set())
        stem, ext = os.path.splitext(nom)
        base, n = stem, 2
        while nom.lower() in pris:
            o, j = (base.rsplit(" - ", 1) + [""])[:2]
            nom = f"{o} {n} - {j}{ext}" if j else f"{base} {n}{ext}"
            n += 1
        pris.add(nom.lower())
        return nom

    dans_depot = []
    for nom_r, rr in racines.liste:
        if not rr.is_dir():
            absentes.append(nom_r)
            continue
        # Un dossier qui est un dépôt git ou un vault, ou qui s'y trouve, ne se touche pas (§6).
        if dans_un_depot(rr):
            dans_depot.append(nom_r)
            continue
        # Une racine déclarée sous celle-ci se parcourt pour elle-même, une seule fois.
        internes = [x for _, x in racines.liste if x != rr and _sous(x, rr)]
        for p in parcourir(Path(os.path.expanduser(nom_r)), exclus + internes):
            st = p.stat()
            par_nom.setdefault((p.name.lower(), st.st_size), []).append(p)
            dans_ref = ref_reel is not None and _sous(reel(p), ref_reel)
            if dans_ref:
                continue           # le dossier commun existant garde son organisation (D7)
            stem, ext = p.stem, p.suffix
            ligne = en_ligne_seulement(p)
            bad, objet = illisible(stem)
            proc = est_procedure(stem)
            if not bad and not proc:
                continue
            titre = "" if ligne else titre_local(p)
            if titre is None:
                signalements.append({"type": "titre_illisible", "chemins": [tilde(p)],
                                     "motif": "document non lisible (droits ou fichier abîmé) ; nom déduit du dossier"})
                titre = ""
            if titre and illisible(titre)[0]:
                titre = ""
            dossier_nom = p.parent.name if p.parent != rr else Path(nom_r).name
            if ligne:
                signalements.append({"type": "en_ligne_seulement", "chemins": [tilde(p)],
                                     "motif": "non ouvert ; nom déduit du dossier, à confirmer"})
            jour = date_de(stem, st.st_mtime)
            if proc:
                if ref is None:
                    procedures_sans_commun.append(tilde(p))
                    continue
                if _DATE_FINALE.search(stem) and not bad:
                    objet_p = stem
                    nom = p.name
                else:
                    objet_p = titre or objet or stem
                    nom = nom_parlant(objet_p, jour, ext)
                partage = racines.partagee(p)
                perso = re.search(r"\b(mon|ma|mes|perso|personnel|personnelle)\b", _plat(stem))
                # Un indice personnel dans un dossier partagé ne tranche pas : la question se pose (D6).
                classe = ("a_demander" if perso else "entreprise") if partage else \
                    ("personnelle" if perso else "a_demander")
                if classe == "personnelle":
                    if not bad:
                        continue
                    vers = p.parent / libre(p.parent, nom)
                    candidats.append({"geste": "renommer", "de": p, "vers": vers, "classe": "personnelle",
                                      "motif": "procédure à vous ; nom illisible", "st": st})
                    continue
                cible_dossier = ref_decl / "Procédures"
                vers = cible_dossier / libre(cible_dossier, nom)
                meme = racines.de(p) == racines.de(ref)
                candidats.append({"geste": "deplacer" if meme else "manuel", "de": p, "vers": vers,
                                  "classe": classe, "st": st,
                                  "motif": ("procédure établie pour toute l'entreprise" if classe == "entreprise"
                                            else "procédure : pour vous seul ou pour toute l'entreprise ?")
                                  + ("" if meme else " ; deux espaces différents : à déplacer dans l'interface de l'outil")})
                continue
            objet = titre or objet or dossier_nom
            motif = ("nom illisible ; " + ("titre lu dans le document" if titre else
                                          "nom gardé sans sa marque de copie" if objet and not titre and objet != dossier_nom
                                          else "nom déduit du dossier"))
            vers = p.parent / libre(p.parent, nom_parlant(objet, jour, ext))
            candidats.append({"geste": "renommer", "de": p, "vers": vers, "classe": "", "motif": motif, "st": st})

    if procedures_sans_commun:
        if len(racines.partagees) > 1:
            signalements.append({"type": "dossier_commun_a_choisir", "chemins": sorted(procedures_sans_commun),
                                 "motif": "plusieurs dossiers partagés : demander lequel porte le dossier commun"})
        else:
            signalements.append({"type": "dossier_commun_absent", "chemins": sorted(procedures_sans_commun),
                                 "motif": "procédures sans dossier commun où les ranger : demander où le créer"})
    if dans_depot:
        signalements.append({"type": "racine_dans_un_depot", "chemins": dans_depot,
                             "motif": "dépôt git ou vault : rien n'y est proposé"})
    if absentes:
        signalements.append({"type": "racine_absente", "chemins": absentes, "motif": "dossier déclaré introuvable"})
    for (nom, _), chemins in sorted(par_nom.items()):
        # « Deux endroits » (contrat 2.3) : au-delà, un même nom à la même taille dans
        # chaque dossier d'affaire est une convention de nommage, pas une copie oubliée.
        if len(chemins) == 2:
            signalements.append({"type": "doublon_probable", "chemins": sorted(tilde(c) for c in chemins),
                                 "motif": "même nom, même taille"})

    vers_ref = [c for c in candidats if c["classe"] in ("entreprise", "a_demander")]
    if ref is not None and dans_un_depot(ref_decl):
        signalements.append({"type": "racine_dans_un_depot", "chemins": [tilde(ref_decl)],
                             "motif": "le dossier commun serait dans un dépôt git ou un vault : rien n'y est proposé"})
    elif ref is not None and (vers_ref or not ref_existe or not (ref_decl / "AGENTS.md").exists()):
        if not ref_existe:
            candidats.append({"geste": "creer_dossier", "vers": ref_decl, "classe": "", "motif": "dossier commun de l'entreprise"})
        if vers_ref and not (ref_decl / "Procédures").is_dir():
            candidats.append({"geste": "creer_dossier", "vers": ref_decl / "Procédures", "classe": "",
                              "motif": "dossier commun des procédures"})
        agents = ref_decl / "AGENTS.md"
        candidats.append({"geste": "ecrire_index", "vers": agents, "classe": "", "motif": "sommaire pour les IA"})
        if agents.exists() and en_ligne_seulement(agents):
            signalements.append({"type": "en_ligne_seulement", "chemins": [tilde(agents)],
                                 "motif": "sommaire non ouvert : le rendre disponible sur ce poste avant de l'écrire"})
        elif agents.exists() and MARQUEUR not in lire_index(agents):
            signalements.append({"type": "index_etranger", "chemins": [tilde(agents)],
                                 "motif": "un sommaire existe déjà sans la marque de Cortex : le montrer et demander"})

    ordre = {nom: i for i, (nom, _) in enumerate(racines.liste)}
    # Un dossier se crée avant toute ligne qui y range, le sommaire s'écrit en dernier (B1).
    rang = {"creer_dossier": 0, "ecrire_index": 2}
    candidats.sort(key=lambda c: (rang.get(c["geste"], 1), ordre.get(racines.de(c.get("de") or c["vers"]), 99),
                                  len(Path(c["vers"]).parts) if c["geste"] == "creer_dossier" else 0,
                                  tilde(c.get("de") or c["vers"]), c["geste"]))
    max_g = plafond(conf)
    ecartes = max(0, len(candidats) - max_g)
    if ecartes:
        # Au-delà du plafond, la création du dossier commun et son sommaire restent ; ce
        # qui part, ce sont les dernières lignes ordinaires, déplacements vers lui compris (m7).
        prioritaires = [c for c in candidats if c["geste"] in rang] + [c for c in candidats if c["geste"] not in rang]
        garde_ = {id(c) for c in prioritaires[:max_g]}
        candidats = [c for c in candidats if id(c) in garde_]

    # Les id continuent après le plus grand id déjà journalisé : un id ne désigne
    # jamais deux gestes, même après une seconde proposition (G5).
    deja = [int(l["id"][1:]) for l in lire_journal(atelier) if re.fullmatch(r"r\d+", str(l.get("id", "")))]
    depart = max(deja, default=0) + 1
    operations = []
    for i, c in enumerate(candidats):
        o = {"id": f"r{depart + i:03d}", "geste": c["geste"]}
        if c.get("de") is not None:
            o["de"] = tilde(c["de"])
        o["vers"] = tilde(c["vers"])
        o["motif"] = c["motif"]
        o["partage"] = racines.partagee(c["vers"]) or (c.get("de") is not None and racines.partagee(c["de"]))
        o["lot"] = 0
        o["classe"] = c["classe"]
        if c.get("st") is not None:
            o["taille"], o["mtime"] = c["st"].st_size, c["st"].st_mtime
        operations.append(o)
    attribuer_lots(operations)

    plan = {"format": "cortex/rangement", "version": 1,
            "genere_le": datetime.now().isoformat(timespec="seconds"),
            "racines": [n for n, _ in racines.liste],
            "bornes": {"gestes": len(operations), "plafond": max_g, "depassement": ecartes > 0, "ecartes": ecartes},
            "operations": operations, "signalements": signalements, "base": base_en_ligne(atelier)}
    ecrire_plan(atelier, plan)
    fm = lire_fm(atelier)
    garde = [i for i in (fm.get("acceptees") or []) if i in actifs(lire_journal(atelier))]
    ecrire_lisible(atelier, plan, "propose" if operations else "rien_a_ranger", garde,
                   "" if operations else "rien à ranger")
    return plan


def attribuer_lots(ops):
    """Quatre lignes par lot : d'abord les dossiers à soi, puis ceux partagés avec des
    collègues (accord renforcé, lot à part), puis les gestes à faire soi-même."""
    lot = 0
    for groupe in ([o for o in ops if not o["partage"] and o["geste"] != "manuel"],
                   [o for o in ops if o["partage"] and o["geste"] != "manuel"],
                   [o for o in ops if o["geste"] == "manuel"]):
        for i, o in enumerate(groupe):
            if i % LOT == 0:
                lot += 1
            o["lot"] = lot


def base_en_ligne(atelier):
    """Une proposition par liste fermée trop longue d'une base en ligne, lue dans le
    schéma relevé à l'inventaire. Rien ne s'écrit dans la base (I-R4)."""
    inv = Path(atelier) / "01-inventaire.json"
    try:
        bases = json.loads(inv.read_text(encoding="utf-8")).get("bases") or [] if inv.is_file() else []
    except (ValueError, OSError) as e:
        raise ValueError(f"01-inventaire.json illisible ({e}) : la proposition pour la base en ligne "
                         "ne peut pas se faire ; relancer l'inventaire.") from e
    out = []
    for b in bases:
        for prop, valeurs in sorted(((b.get("signal_ontologique") or {}).get("enums") or {}).items()):
            if isinstance(valeurs, list) and len(valeurs) > 7:
                out.append({"objet": f"{b.get('titre', 'base')} : propriété {prop}",
                            "constat": f"{len(valeurs)} valeurs",
                            "proposition": "réduire à une liste courte, cinq valeurs au plus, à choisir avec vous"})
    return out


# ── Réécrire une ligne : classe, nom ────────────────────────────────────────

def _paires(texte):
    out = {}
    for morceau in texte.split(","):
        if "=" not in morceau:
            raise Usage(f"attendu id=valeur, lu {morceau!r}")
        k, v = morceau.split("=", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def classer(atelier, paires):
    """La réponse à « pour vous seul ou pour toute l'entreprise ? » réécrit la ligne."""
    pas_apres_construction(atelier)
    plan = lire_plan(atelier)
    ops = {o["id"]: o for o in plan["operations"]}
    for i, classe in paires.items():
        if i not in ops or classe not in ("personnelle", "entreprise"):
            raise Usage(f"{i}={classe} : id inconnu ou classe hors personnelle|entreprise")
        o = ops[i]
        o["classe"] = classe
        if classe == "personnelle":
            # Elle reste chez la personne : un renommage sur place, ou rien si son nom est parlant.
            de = Path(os.path.expanduser(o["de"]))
            if illisible(de.stem)[0]:
                o.update(geste="renommer", vers=tilde(de.parent / Path(o["vers"]).name),
                         motif="procédure à vous ; nom illisible")
                o["partage"] = Racines(charger_conf(atelier)).partagee(de)
            else:
                plan["operations"].remove(o)
        else:
            o["motif"] = o["motif"].replace("procédure : pour vous seul ou pour toute l'entreprise ?",
                                            "procédure établie pour toute l'entreprise")
    attribuer_lots(plan["operations"])
    plan["bornes"]["gestes"] = len(plan["operations"])
    ecrire_plan(atelier, plan)
    fm = lire_fm(atelier)
    ecrire_lisible(atelier, plan, fm.get("statut", "propose"), fm.get("acceptees") or [])


def nommer(atelier, paires):
    """Le nom donné par la personne remplace l'objet ; la date et l'extension restent."""
    pas_apres_construction(atelier)
    plan = lire_plan(atelier)
    ops = {o["id"]: o for o in plan["operations"]}
    for i, objet in paires.items():
        o = ops.get(i)
        if o is None or o["geste"] not in ("renommer", "deplacer", "manuel"):
            raise Usage(f"{i} : id inconnu ou ligne sans nom à donner")
        if not nettoyer(objet):
            raise Usage(f"{i} : nom vide une fois retirés les caractères interdits")
        v = Path(o["vers"])
        jour = _DATE_FINALE.search(v.stem)
        o["vers"] = str(v.parent / nom_parlant(objet, jour.group(0)[3:] if jour else date.today().isoformat(), v.suffix))
        o["motif"] = "nom donné par vous"
    ecrire_plan(atelier, plan)
    fm = lire_fm(atelier)
    ecrire_lisible(atelier, plan, fm.get("statut", "propose"), fm.get("acceptees") or [])


# ── Index du dossier commun (contrat §7) ────────────────────────────────────

def lire_index(agents):
    """Le texte d'un AGENTS.md, ou "" s'il n'existe pas. G6 : présent seulement en
    ligne, il ne s'ouvre pas, et rien de ce qui le réécrirait ne se fait."""
    agents = Path(agents)
    if not agents.is_file():
        return ""
    if en_ligne_seulement(agents):
        raise Garde(f"G6 : {tilde(agents)} n'est présent qu'en ligne ; le rendre disponible sur ce poste "
                    "dans l'outil de partage, puis relancer.")
    return agents.read_text(encoding="utf-8", errors="replace")


def _proprietaires_existants(agents):
    out = {}
    for l in lire_index(agents).splitlines():
        m = re.match(r"^\| \[(.+?)\]\((.+?)\) \| .*? \| (.*?) \| .*? \|$", l)
        if m:
            out[m.group(1)] = m.group(3)
    return out


def _description(skill):
    if en_ligne_seulement(skill):
        return "Non renseigné"
    for l in skill.read_text(encoding="utf-8", errors="replace").splitlines()[:20]:
        if l.startswith("description:"):
            d = l.split(":", 1)[1].strip().strip('"')
            return (d.split(". ")[0])[:160].replace("|", "/")
    return "Non renseigné"


def texte_index(ref, organisation, proprietaires, ajouts=None, retraits=()):
    """Le texte du sommaire. `ajouts` ({chemin: mtime}) et `retraits` projettent l'état
    du dossier après des gestes pas encore faits : c'est ce que `--montrer-index` imprime,
    et ce que le geste écrit ensuite (doctrine §10)."""
    ref = Path(ref)
    anciens = _proprietaires_existants(ref / "AGENTS.md")
    docs, assistants = [], []
    retraits = {str(x) for x in retraits}
    dates = {str(k): v for k, v in (ajouts or {}).items()}
    tous = sorted({*[p for p in ref.rglob("*") if str(p) not in retraits], *[Path(k) for k in dates]})
    for p in tous:
        rel = p.relative_to(ref)
        if (str(p) not in dates and not p.is_file()) or any(x.startswith(".") for x in rel.parts) \
                or p.name.lower() in SYSTEME:
            continue
        if rel.parts[0] == "assistants":
            if len(rel.parts) == 3 and p.name == "SKILL.md":
                assistants.append((rel.parts[1], _description(p), rel.as_posix()))
            continue
        if rel.parts[0] == "Archives" or rel.as_posix() == "AGENTS.md":
            continue
        docs.append(p)
    lignes = [f"# Dossier commun de {organisation}", "",
              "Ce dossier porte les documents de référence de l'organisation : procédures, charte graphique, "
              "signatures, modèles, assistants. Toute IA qui travaille pour l'organisation lit ce sommaire avant "
              "de répondre sur l'un de ces sujets, puis le document lui-même.", "",
              f"{MARQUEUR} {date.today().isoformat()} -->", "", "## Documents", "",
              "| Document | Objet | Propriétaire | Date |", "|---|---|---|---|"]
    for p in docs[:MAX_LIGNES_INDEX]:
        rel = p.relative_to(ref).as_posix()
        stem = p.stem
        j = _DATE_FINALE.search(stem)
        objet = stem[:j.start()] if j else stem
        jour = j.group(0)[3:] if j else date.fromtimestamp(dates.get(str(p)) or p.stat().st_mtime).isoformat()
        qui = proprietaires.get(rel) or anciens.get(p.name) or "Non renseigné"
        lignes.append(f"| [{p.name}]({quote(rel)}) | {objet} | {qui} | {jour} |")
    if len(docs) > MAX_LIGNES_INDEX:
        lignes.append(f"| … | {len(docs) - MAX_LIGNES_INDEX} autre(s) document(s) non listé(s) | | |")
    lignes += ["", "## Assistants", "", "| Assistant | Ce qu'il fait | Fichier |", "|---|---|---|"]
    lignes += [f"| {n} | {d} | [SKILL.md]({quote(r)}) |" for n, d, r in assistants]
    lignes += ["", "## Règles", "- Une procédure par fichier ; le nom dit l'objet et la date de version.",
               "- Une version nouvelle remplace l'ancienne au même endroit ; l'ancienne va dans `Archives/`.", ""]
    return "\n".join(lignes)


def sha(chemin):
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


def montrer_index(atelier, ids, proprietaires):
    """Le texte exact que la ligne du sommaire écrira si les lignes `ids` (et elle) se font
    maintenant, sans rien écrire : la skill l'affiche en entier avant l'accord (doctrine §10)."""
    plan, conf = lire_plan(atelier), charger_conf(atelier)
    ops = {o["id"]: o for o in plan["operations"]}
    faits = actifs(lire_journal(atelier))
    index = [o for o in plan["operations"] if o["geste"] == "ecrire_index"]
    if not index:
        raise Usage("la liste ne porte aucun sommaire à écrire.")
    agents = Path(os.path.expanduser(index[0]["vers"]))
    ajouts, retraits = {}, []
    for i in ids or []:
        o = ops.get(i)
        if o is None:
            raise Usage(f"id inconnu : {i}")
        if o["geste"] in ("renommer", "deplacer") and i not in faits:
            ajouts[str(Path(os.path.expanduser(o["vers"])))] = o.get("mtime")
            retraits.append(str(Path(os.path.expanduser(o["de"]))))
    return texte_index(agents.parent, (conf.get("organisation") or {}).get("nom", "l'organisation"),
                       proprietaires, ajouts, retraits)


def ecrire_index(agents, conf, proprietaires, texte=None):
    """Écrit le sommaire (ou `texte` tel quel, pour une restauration). Rend (créé,
    sha256, taille, texte d'avant). G7 : un AGENTS.md sans la marque n'est pas à
    Cortex, il ne se réécrit pas. Le texte d'avant part au journal : l'annulation
    le rend tel qu'il était, notes à la main comprises."""
    agents = Path(agents)
    avant = lire_index(agents)
    if texte is None:
        texte = texte_index(agents.parent, (conf.get("organisation") or {}).get("nom", "l'organisation"),
                            proprietaires)
    if agents.exists():
        if MARQUEUR not in avant:
            raise Garde(f"G7 : {tilde(agents)} existe sans la marque de Cortex ; le montrer et demander.")
        agents.write_text(texte, encoding="utf-8")
        cree = False
    else:
        creer_exclusif(agents, texte)
        cree = True
    return cree, sha(agents), agents.stat().st_size, avant


def creer_exclusif(chemin, texte):
    """Crée un fichier qui n'existe pas : « x » lève FileExistsError plutôt que d'écraser,
    même si le fichier apparaît entre le test d'existence et l'écriture."""
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(texte)


def dernier_sha_index(journal, chemin):
    """L'empreinte du dernier sommaire écrit par Cortex à ce chemin, réécritures
    d'annulation comprises : ce qui est à comparer pour savoir si une main l'a touché."""
    out = None
    for l in journal:
        if l.get("index") == chemin and l.get("index_sha256") and l.get("resultat") in ("fait", "annule"):
            out = l["index_sha256"]
    return out


# ── Appliquer ───────────────────────────────────────────────────────────────

def renommer_exclusif(de, vers):
    """Renomme sans jamais écraser (G1, jusque dans la fenêtre entre la garde et le geste).
    Sous POSIX, `os.rename` remplace une destination existante en silence : on passe par
    l'appel système exclusif (macOS renamex_np RENAME_EXCL, Linux renameat2
    RENAME_NOREPLACE), qui lève FileExistsError. Windows refuse déjà de lui-même. Sans
    l'appel exclusif (libc introuvable), la garde rejouée juste avant reste la seule
    barrière, et la fenêtre est celle de deux appels système."""
    de, vers = os.fsencode(str(de)), os.fsencode(str(vers))
    if sys.platform in ("darwin", "linux"):
        import ctypes
        import ctypes.util
        try:
            libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
            if sys.platform == "darwin":
                rc = libc.renamex_np(de, vers, ctypes.c_uint(0x4))                    # RENAME_EXCL
            else:
                rc = libc.renameat2(-100, de, -100, vers, ctypes.c_uint(1))          # AT_FDCWD, NOREPLACE
        except (OSError, AttributeError):
            rc = None
        if rc is not None:
            if rc != 0:
                e = ctypes.get_errno()
                raise OSError(e, os.strerror(e), os.fsdecode(vers))
            return
    if sys.platform != "win32":
        print("[avertissement] renommage exclusif indisponible sur ce système : la garde rejouée juste "
              "avant le geste reste la seule barrière contre l'écrasement.", file=sys.stderr)
    if os.path.lexists(vers):
        raise FileExistsError(errno.EEXIST, "destination existante", os.fsdecode(vers))
    os.rename(de, vers)   # exception : renommage simple, sous Windows il refuse lui-même une destination existante


def ecart_identite(chemin, taille, mtime):
    """"" si le fichier est celui du journal ; sinon « a disparu » ou « a changé (taille ou date) »."""
    if not os.path.lexists(chemin):
        return "a disparu"
    return "" if _identique(chemin, taille, mtime) else "a changé (taille ou date)"


def _identique(chemin, taille, mtime):
    """Même taille et même date (T3). Absent : faux. Illisible : l'erreur remonte telle
    quelle, elle ne se déguise pas en « changé »."""
    try:
        st = os.stat(chemin, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return st.st_size == taille and abs(st.st_mtime - mtime) < 1e-3


def controler(o, racines, renforce, a_creer):
    """Les gardes G1 à G5, G8 sur une ligne, avant tout geste. Lève Garde."""
    de = Path(os.path.expanduser(o["de"])) if o.get("de") else None
    vers = Path(os.path.expanduser(o["vers"]))
    if o["classe"] == "a_demander":
        raise Garde(f"G8 : {o['id']} attend la réponse « pour vous seul ou pour toute l'entreprise ? ».")
    if o["geste"] == "manuel":
        raise Garde(f"G3 : {o['id']} relie deux espaces différents ; la personne le fait dans son outil.")
    for c in ([de] if de else []) + [vers]:
        if racines.de(c) is None:
            raise Garde(f"G4 : {o['id']} : {tilde(c)} est hors des dossiers déclarés.")
        if dans_un_depot(c):
            raise Garde(f"{o['id']} : {tilde(c)} est dans un dépôt git ou un vault ; rien n'y bouge.")
    if de is not None and racines.de(de) != racines.de(vers):
        raise Garde(f"G3 : {o['id']} relie deux dossiers déclarés différents.")
    partage = o["partage"] or racines.partagee(vers) or (de is not None and racines.partagee(de))
    if partage and not renforce:
        raise Garde(f"G2 : {o['id']} touche un dossier partagé ; il faut l'accord renforcé (--renforce).")
    if o["geste"] != "ecrire_index" and os.path.lexists(vers):
        raise Garde(f"G1 : {o['id']} : {tilde(vers)} existe déjà ; rien n'est écrasé.")
    if o["geste"] == "ecrire_index" and vers.exists() and MARQUEUR not in lire_index(vers):
        raise Garde(f"G7 : {tilde(vers)} existe sans la marque de Cortex ; le montrer et demander.")
    if de is not None and ecart_identite(de, o["taille"], o["mtime"]):
        raise Garde(f"G5 : {o['id']} : {tilde(de)} {ecart_identite(de, o['taille'], o['mtime'])} depuis la "
                    "proposition ; reproposer.")
    if not vers.parent.is_dir() and str(vers.parent) not in a_creer:
        raise Garde(f"{o['id']} : le dossier d'arrivée {tilde(vers.parent)} n'existe pas ; cocher aussi la ligne qui le crée.")


def rafraichir_index(atelier, conf, plan, touches=None):
    """Régénère chaque sommaire de la liste déjà écrit, quand un geste fait a touché son
    dossier (`touches`), ou toujours (`touches` à None, à la clôture) : le sommaire liste
    tout le dossier commun, quel que soit l'ordre des lots (B1). Le texte d'avant part au
    journal sous un id `i…`, et l'annulation le rend."""
    for o in plan["operations"]:
        if o["geste"] != "ecrire_index":
            continue
        agents = Path(os.path.expanduser(o["vers"]))
        if not agents.is_file():
            continue            # pas encore écrit, ou décoché : rien à rafraîchir
        if touches is not None and not any(_sous(reel(t), reel(agents.parent)) for t in touches):
            continue
        neuf = texte_index(agents.parent, (conf.get("organisation") or {}).get("nom", "l'organisation"), {})
        if neuf == lire_index(agents):
            continue
        ident = _prochain_id(atelier, "i")
        _, empreinte, taille, avant = ecrire_index(agents, conf, {}, texte=neuf)
        journaliser(atelier, {"id": ident, "geste": "ecrire_index", "de": "", "vers": o["vers"], "taille": taille,
                              "sha256": empreinte, "cree": False, "avant": avant, "index": o["vers"],
                              "index_sha256": empreinte, "resultat": "fait"})
        print(f"fait  {ident} sommaire du dossier commun mis à jour")


def _prochain_id(atelier, lettre):
    return "{}{:03d}".format(lettre, 1 + max([int(l["id"][1:]) for l in lire_journal(atelier)
                                               if re.fullmatch(lettre + r"\d+", str(l.get("id", "")))], default=0))


def rafraichir_ou_dire(atelier, conf, plan, touches=None, apres="les changements sont faits"):
    """Rafraîchit le sommaire sans faire mentir le code de sortie : un échec ici arrive
    après des gestes faits, il se journalise (`i…` en `echec`) et sort 1, jamais 3."""
    try:
        rafraichir_index(atelier, conf, plan, touches)
    except (Garde, OSError) as e:
        journaliser(atelier, {"id": _prochain_id(atelier, "i"), "geste": "ecrire_index", "de": "", "vers": "",
                              "resultat": "echec", "erreur": str(e)})
        print(f"[échec] {apres} ; seul le sommaire du dossier commun n'a pas suivi : {e}", file=sys.stderr)
        return ECART
    return OK


def appliquer(atelier, ids, renforce=False, proprietaires=None):
    atelier = Path(atelier)
    pas_apres_construction(atelier)
    conf, plan = charger_conf(atelier), lire_plan(atelier)
    racines = Racines(conf)
    journal = lire_journal(atelier)
    ops = {o["id"]: o for o in plan["operations"]}
    inconnus = [i for i in ids if i not in ops]
    if inconnus:
        raise Usage(f"id inconnu(s) : {', '.join(inconnus)}")
    faits = actifs(journal)
    choisis = sorted((ops[i] for i in ids if i not in faits), key=lambda o: (PRIORITE.get(o["geste"], 1), o["id"]))
    a_creer = {str(Path(os.path.expanduser(o["vers"]))) for o in choisis if o["geste"] == "creer_dossier"}
    a_creer |= {str(Path(os.path.expanduser(faits[i]["vers"]))) for i in faits if faits[i]["geste"] == "creer_dossier"}
    for o in choisis:              # toutes les gardes avant le premier geste : code 3, rien n'a bougé
        controler(o, racines, renforce, a_creer)
    fm = lire_fm(atelier)
    acceptees = list(dict.fromkeys((fm.get("acceptees") or []) + [o["id"] for o in choisis]))
    ecrire_lisible(atelier, plan, "propose", acceptees)
    for o in choisis:
        vers = Path(os.path.expanduser(o["vers"]))
        base = {"id": o["id"], "geste": o["geste"], "de": o.get("de", ""), "vers": o["vers"], "renforce": renforce}
        try:
            # La garde se rejoue juste avant le geste : un client de synchronisation
            # peut avoir créé la destination ou touché l'origine entre-temps.
            controler(o, racines, renforce, a_creer)
            if o["geste"] in ("renommer", "deplacer"):
                renommer_exclusif(os.path.expanduser(o["de"]), vers)
                st = os.stat(vers)
                ligne = dict(base, taille=st.st_size, mtime=st.st_mtime)
            elif o["geste"] == "creer_dossier":
                os.mkdir(vers)
                ligne = dict(base, taille=0, mtime=os.stat(vers).st_mtime)
            else:   # ecrire_index
                cree, empreinte, taille, avant = ecrire_index(vers, conf, proprietaires or {})
                ligne = dict(base, taille=taille, sha256=empreinte, cree=cree, avant="" if cree else avant,
                             index=o["vers"], index_sha256=empreinte)
        except (Garde, OSError) as e:
            journaliser(atelier, dict(base, resultat="echec", erreur=str(e)))
            ecrire_lisible(atelier, plan, "propose", acceptees)
            print(f"[échec] {o['id']} : {e}. Le lot s'arrête ; ce qui précède est fait et se défait par --annuler.",
                  file=sys.stderr)
            return ECART
        journaliser(atelier, dict(ligne, resultat="fait"))
        print(f"fait  {o['id']} {o['geste']} {o.get('de', '')} -> {o['vers']}")
    code = rafraichir_ou_dire(atelier, conf, plan, [os.path.expanduser(o["vers"]) for o in choisis])
    ecrire_lisible(atelier, plan, "propose", acceptees)
    return code


# ── Publier un assistant d'entreprise (maillon 6) ───────────────────────────

def publier(atelier, source, nom, renforce):
    atelier = Path(atelier)
    conf = charger_conf(atelier)
    ref = conf.get("referentiel") or {}
    source = Path(os.path.expanduser(source))
    if not _sous(reel(source), reel(atelier)):
        raise Usage(f"--publier : {tilde(source)} n'est pas dans l'atelier ; l'assistant s'y rédige d'abord.")
    if source.name != "SKILL.md":
        raise Usage(f"--publier : {source.name} n'est pas un SKILL.md.")
    if not source.is_file():
        raise Usage(f"--publier : {tilde(source)} n'existe pas.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", nom):
        raise Usage(f"--nom {nom!r} : minuscules, chiffres et tirets.")
    if ref.get("etat") != "existant" or not ref.get("chemin"):
        raise Garde("aucun dossier commun déclaré : le créer d'abord (« rangeons mes dossiers »).")
    racines = Racines(conf)
    base = reel(ref["chemin"])
    vers = base / "assistants" / nom / "SKILL.md"
    if racines.de(vers) is None:
        raise Garde(f"G4 : {tilde(vers)} est hors des dossiers déclarés.")
    if not renforce:
        raise Garde("G2 : le dossier commun est partagé ; il faut l'accord renforcé (--renforce).")
    if os.path.lexists(vers):
        raise Garde(f"G1 : {tilde(vers)} existe déjà ; rien n'est écrasé.")
    agents = base / "AGENTS.md"
    if agents.exists() and MARQUEUR not in lire_index(agents):
        raise Garde(f"G7 : {tilde(agents)} existe sans la marque de Cortex ; le montrer et demander.")
    ident = "p{:03d}".format(1 + max([int(l["id"][1:]) for l in lire_journal(atelier)
                                      if re.fullmatch(r"p\d+", str(l.get("id", "")))], default=0))
    crees = [d for d in (base / "assistants", base / "assistants" / nom) if not d.exists()]
    ligne = {"id": ident, "geste": "publier", "de": tilde(source), "vers": tilde(vers), "renforce": True}
    if dans_un_depot(vers):
        raise Garde(f"{tilde(vers)} est dans un dépôt git ou un vault ; rien n'y est publié.")
    try:
        contenu = source.read_text(encoding="utf-8")   # lu avant tout geste : un échec ici ne laisse rien
    except (OSError, ValueError) as e:
        raise Usage(f"{tilde(source)} illisible ({e}) : rien n'a été publié.") from e
    try:
        for d in crees:
            os.mkdir(d)
        creer_exclusif(vers, contenu)
        cree, empreinte, _, avant = ecrire_index(agents, conf, {})
    except (Garde, OSError) as e:
        # Ce qui a été posé avant l'échec reste en place et se nomme : rien ne
        # disparaît en silence, et la personne sait quoi retirer à la main.
        restes = [tilde(d) for d in crees if d.exists()] + ([tilde(vers)] if vers.exists() else [])
        journaliser(atelier, dict(ligne, resultat="echec", erreur=str(e), restes=restes))
        print(f"[échec] publication : {e}" + (f" ; laissé en place : {', '.join(restes)}" if restes
                                              else " ; rien n'a été écrit"), file=sys.stderr)
        return ECART
    journaliser(atelier, dict(ligne, resultat="fait", taille=vers.stat().st_size, sha256=sha(vers),
                              dossiers_crees=[tilde(d) for d in crees], index=tilde(agents), index_cree=cree,
                              index_sha256=empreinte, index_avant="" if cree else avant))
    print(f"fait  {ident} publier {tilde(vers)} ; sommaire mis à jour")
    return OK


# ── Vérifier, annuler ───────────────────────────────────────────────────────

def verifier(atelier):
    atelier = Path(atelier)
    journal = lire_journal(atelier)
    faits, ret = actifs(journal), retires(journal)
    ecarts, attente = [], []
    for i, l in faits.items():
        vers = Path(os.path.expanduser(l["vers"]))
        if l["geste"] in ("renommer", "deplacer", "manuel"):
            ecart = ecart_identite(vers, l["taille"], l["mtime"])
            if ecart:
                ecarts.append(f"{i} : {l['vers']} {ecart}")
            if l.get("de") and os.path.lexists(os.path.expanduser(l["de"])):
                ecarts.append(f"{i} : {l['de']} existe encore")
        elif l["geste"] == "creer_dossier" and not vers.is_dir():
            ecarts.append(f"{i} : dossier {l['vers']} absent")
        elif l["geste"] in ("ecrire_index", "publier") and not vers.is_file():
            ecarts.append(f"{i} : {l['vers']} absent")
    try:
        plan = lire_plan(atelier)
    except Usage:
        plan = {"operations": []}
    for o in plan["operations"]:
        if o["geste"] != "manuel" or o["id"] in faits or o["id"] in ret:
            continue
        de, vers = Path(os.path.expanduser(o["de"])), Path(os.path.expanduser(o["vers"]))
        # A7 : la taille se compare, pas la date (l'interface d'un outil peut la changer).
        if vers.is_file() and not os.path.lexists(de) and vers.stat().st_size == o.get("taille", -1):
            st = vers.stat()
            journaliser(atelier, {"id": o["id"], "geste": "manuel", "de": o["de"], "vers": o["vers"],
                                  "taille": st.st_size, "mtime": st.st_mtime, "resultat": "fait", "renforce": True})
            print(f"constaté  {o['id']} : déplacé par vous vers {o['vers']}")
        else:
            attente.append(o["id"])
            print(f"en attente  {o['id']} : à déplacer vous-même de {o['de']} vers {o['vers']}")
    for e in ecarts:
        print(f"[écart] {e}")
    if plan["operations"]:
        fm = lire_fm(atelier)
        ecrire_lisible(atelier, plan, fm.get("statut", "propose"), fm.get("acceptees") or [], fm.get("raison", ""))
    print(f"{len(faits)} geste(s) fait(s), {len(ecarts)} écart(s), {len(attente)} geste(s) à faire vous-même")
    return ECART if ecarts else OK


def _vide_ou_systeme(d):
    reste = [p.name for p in d.iterdir()]
    return all(n.lower() in SYSTEME for n in reste), reste


def _defaire_index(index, cree, avant, journal, conf):
    """Défait une écriture du sommaire : retiré s'il a été créé, rendu tel qu'avant sinon,
    et seulement si personne ne l'a touché depuis la dernière écriture de Cortex.
    Rend (note, champs à journaliser)."""
    agents = Path(os.path.expanduser(index))
    if not agents.is_file():
        return "sommaire déjà absent", {}
    if en_ligne_seulement(agents):
        return "sommaire présent seulement en ligne : laissé tel quel", {}
    if sha(agents) != dernier_sha_index(journal, index):
        return "sommaire modifié à la main depuis son écriture : laissé tel quel", {}
    if cree:
        os.remove(agents)   # exception 2 du contrat §5 : écrit par Cortex, inchangé depuis le journal
        return "", {}
    _, empreinte, _, _ = ecrire_index(agents, conf, {}, texte=avant)
    return "", {"index": index, "index_sha256": empreinte}


def annuler(atelier, ids=None):
    """Rejoue le journal à l'envers (T4). Ne retire que ce que Cortex a créé. Avant la
    construction seulement : après, défaire casserait les liens du second cerveau."""
    atelier = Path(atelier)
    pas_apres_construction(atelier)
    journal = lire_journal(atelier)
    faits, ret = actifs(journal), retires(journal)
    fm = lire_fm(atelier)
    cibles = [l for l in reversed(journal) if l.get("resultat") == "fait" and faits.get(l["id"]) is l
              and (ids is None or l["id"] in ids)]
    conf = charger_conf(atelier)
    for l in cibles:
        vers = Path(os.path.expanduser(l["vers"]))
        base = {"id": l["id"], "geste": l["geste"], "de": l.get("de", ""), "vers": l["vers"]}
        try:
            note, extra = "", {}
            if l["geste"] in ("renommer", "deplacer"):
                de = Path(os.path.expanduser(l["de"]))
                ecart = ecart_identite(vers, l["taille"], l["mtime"])
                if ecart:
                    raise OSError(f"{l['vers']} {ecart} depuis le rangement")
                if os.path.lexists(de):
                    raise OSError(f"{l['de']} existe de nouveau ; rien n'est écrasé")
                renommer_exclusif(vers, de)
            elif l["geste"] == "manuel":
                note = "déplacé par vous : à remettre vous-même dans votre outil si vous le souhaitez"
            elif l["geste"] == "referentiel":
                _maj_config_referentiel(atelier, l.get("avant_chemin", ""), l.get("avant_etat") or "inconnu")
            elif l["geste"] == "creer_dossier":
                vide, reste = _vide_ou_systeme(vers) if vers.is_dir() else (True, [])
                if reste and not vide:
                    raise OSError(f"{l['vers']} n'est pas vide ({len(reste)} élément(s)) ; il reste en place")
                if not reste and vers.is_dir():
                    os.rmdir(vers)   # exception 1 du contrat §5 : dossier créé par Cortex et resté vide
                elif reste:
                    note = "dossier laissé : il ne contient qu'un fichier système"
            elif l["geste"] == "ecrire_index":
                note, extra = _defaire_index(l.get("index") or l["vers"], l.get("cree"), l.get("avant", ""),
                                             journal, conf)
            elif l["geste"] == "publier":
                if not vers.is_file():
                    raise OSError(f"{l['vers']} a disparu depuis sa publication : rien à retirer, l'annulation s'arrête")
                if en_ligne_seulement(vers):
                    raise OSError(f"{l['vers']} n'est présent qu'en ligne : le rendre disponible sur ce poste, puis relancer")
                if sha(vers) != l.get("sha256"):
                    raise OSError(f"{l['vers']} a été modifié depuis sa publication : laissé tel quel")
                os.remove(vers)           # exception 2 du contrat §5 : écrit par Cortex, inchangé depuis le journal
                for d in reversed(l.get("dossiers_crees") or []):
                    dd = Path(os.path.expanduser(d))
                    if dd.is_dir() and not any(dd.iterdir()):
                        os.rmdir(dd)      # exception 1 du contrat §5 : dossier créé par Cortex et resté vide
                note, extra = _defaire_index(l.get("index") or tilde(vers.parents[2] / "AGENTS.md"),
                                             l.get("index_cree"), l.get("index_avant", ""), journal, conf)
        except (OSError, Garde) as e:
            journaliser(atelier, dict(base, resultat="echec", erreur=f"annulation : {e}"))
            print(f"[échec] {l['id']} : {e}. L'annulation s'arrête là.", file=sys.stderr)
            return ECART
        fin = dict(base, resultat="annule", erreur=note, **extra)
        journaliser(atelier, fin)
        journal.append(fin)
        print(f"défait  {l['id']} {l['geste']}" + (f" ({note})" if note else ""))
    # A5 : une ligne acceptée jamais faite, ou un geste manuel en attente, se retire.
    try:
        plan = lire_plan(atelier)
    except Usage:
        return OK
    attente = set(fm.get("acceptees") or []) | {o["id"] for o in plan["operations"] if o["geste"] == "manuel"}
    for i in sorted(attente):
        if (ids is None or i in ids) and i not in faits and i not in ret:
            journaliser(atelier, {"id": i, "geste": "", "resultat": "annule", "erreur": "retirée avant d'être faite"})
            print(f"retiré  {i}")
    code = OK
    if ids is not None:
        # Une annulation partielle qui sort un document du dossier commun le sort aussi du sommaire (N6).
        touches = [os.path.expanduser(l["vers"]) for l in cibles] + \
                  [os.path.expanduser(l["de"]) for l in cibles if l.get("de")]
        code = rafraichir_ou_dire(atelier, conf, plan, touches, apres="les changements sont défaits")
    ecrire_lisible(atelier, plan, "propose" if plan["operations"] else "rien_a_ranger", fm.get("acceptees") or [])
    return code


# ── Chemins pour le remplissage (A1, A4), clôture ───────────────────────────

def chemins(atelier):
    """{"traductions": {ancien: nouveau}, "en_attente": [origine d'un geste manuel non constaté]}."""
    atelier = Path(atelier)
    journal = lire_journal(atelier)
    faits, ret = actifs(journal), retires(journal)
    trad = {l["de"]: l["vers"] for l in faits.values() if l["geste"] in ("renommer", "deplacer", "manuel")}
    fm = lire_fm(atelier)
    attente = []
    if fm.get("statut") != "refuse" and (atelier / PLAN).is_file():
        attente = [o["de"] for o in lire_plan(atelier)["operations"]
                   if o["geste"] == "manuel" and o["id"] not in faits and o["id"] not in ret]
    return {"traductions": trad, "en_attente": sorted(attente)}


def note_autorisee(atelier, chemin):
    """Le maillon 5 écrit-il une note-pointeur sur ce chemin ? Non tant qu'un geste
    manuel l'attend (A4) ; oui sur le chemin d'arrivée une fois le geste constaté."""
    c = chemins(atelier)
    return tilde(os.path.expanduser(chemin)) not in c["en_attente"]


def _maj_config_referentiel(atelier, chemin, etat="existant"):
    """Le bloc `referentiel` de config.yaml : `existant` et son chemin quand le dossier commun
    existe ; la valeur d'avant quand l'annulation l'a retiré."""
    cfg = Path(atelier) / "config.yaml"
    texte = cfg.read_text(encoding="utf-8")
    bloc = f'referentiel:\n  etat: {etat}\n  chemin: "{chemin}"\n'
    m = re.search(r"^referentiel:[^\n]*\n(?:[ \t]+[^\n]*\n?)*", texte, re.M)
    texte = (texte[:m.start()] + bloc + texte[m.end():]) if m else texte.rstrip("\n") + "\n" + bloc
    cfg.write_text(texte, encoding="utf-8")
    cortex_config.charger(cfg)   # relu : un bloc mal formé se voit ici, pas au maillon suivant


def clore(atelier, statut):
    atelier = Path(atelier)
    pas_apres_construction(atelier)
    plan, journal, fm = lire_plan(atelier), lire_journal(atelier), lire_fm(atelier)
    faits = actifs(journal)
    if statut == "refuse":
        if faits:
            raise Garde(f"{len(faits)} changement(s) déjà fait(s) : les défaire d'abord (--annuler).")
        ecrire_lisible(atelier, plan, "refuse", fm.get("acceptees") or [], "refusé")
        return OK
    reste = partiel(plan["operations"], fm, journal)
    if reste:
        raise Garde(f"rangement appliqué en partie : {', '.join(reste)} accepté(s) et pas fait(s).")
    if not faits:
        raise Garde("rien n'a été fait : clore par « refuse » si la personne n'a rien retenu.")
    if rafraichir_ou_dire(atelier, charger_conf(atelier), plan, apres="rien n'est clos") != OK:
        return ECART
    # Le dossier commun existe dès qu'un geste fait y a posé quelque chose, sommaire
    # coché ou non : sans cela, une procédure rangée là serait introuvable (M6).
    refs = {Path(os.path.expanduser(o["vers"])).parent for o in plan["operations"] if o["geste"] == "ecrire_index"}
    for ref in refs:
        if ref.is_dir() and any(_sous(reel(os.path.expanduser(l["vers"])), reel(ref)) for l in faits.values()):
            avant = charger_conf(atelier).get("referentiel") or {}
            avant = avant if isinstance(avant, dict) else {}
            if avant.get("etat") == "existant" and avant.get("chemin") == tilde(ref):
                continue
            _maj_config_referentiel(atelier, tilde(ref))
            journaliser(atelier, {"id": "c001", "geste": "referentiel", "de": "", "vers": tilde(ref),
                                  "resultat": "fait", "avant_etat": str(avant.get("etat") or "inconnu"),
                                  "avant_chemin": str(avant.get("chemin") or "")})
    ecrire_lisible(atelier, plan, "applique", fm.get("acceptees") or [])
    return OK


# ── Auto-test ───────────────────────────────────────────────────────────────

def arbre(racines):
    """Chemins, tailles et dates des fichiers, et liste des dossiers : ce qu'I-R1 et
    I-R2 comparent. Les dates des dossiers bougent avec tout renommage, elles n'y sont pas."""
    fichiers, dossiers = [], []
    for r in racines:
        for p in sorted(Path(r).rglob("*")):
            if p.is_dir():
                dossiers.append(str(p))
            else:
                st = os.stat(p, follow_symlinks=False)
                fichiers.append((str(p), st.st_size, st.st_mtime))
    return fichiers, dossiers


def _autotest():
    import subprocess
    global _SIMULES
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(os.path.realpath(tmp))
        perso, commun, ailleurs = tmp / "Travail", tmp / "Commun", tmp / "Ailleurs"
        atelier = tmp / "slug" / "_cortex"
        for d in (perso / "Clients", perso / "Divers", commun / "Divers", ailleurs, atelier):
            d.mkdir(parents=True)

        def poser(p, texte, jour):
            p.write_text(texte, encoding="utf-8")
            ts = datetime(*jour).timestamp()
            os.utime(p, (ts, ts))
            return p
        poser(perso / "Clients" / "Nouveau document (3).md", "# Accueil d'un nouveau client\n", (2026, 3, 12, 9))
        poser(perso / "Clients" / "Scan_0001.md", "# Titre qu'on ne doit jamais lire\n", (2026, 2, 1, 9))
        poser(perso / "Clients" / "Devis Malbrun.md", "devis\n", (2026, 1, 5, 9))
        poser(perso / "Process relance.md", "# Relance d'un impayé\n", (2026, 1, 20, 9))
        poser(commun / "Divers" / "Process facturation.md", "# Facturation d'une affaire\n", (2025, 11, 4, 9))
        poser(commun / "Divers" / "tarifs.md", "t\n", (2025, 6, 1, 9))
        poser(commun / "Divers" / "Mon process de devis.md", "# Mes devis\n", (2025, 7, 1, 9))  # m5
        poser(perso / "Divers" / "tarifs.md", "t\n", (2025, 6, 1, 9))
        os.symlink(ailleurs, perso / "lien")                  # G4 : un lien sous une racine qui sort
        (perso / "outil" / ".git").mkdir(parents=True)        # un dépôt git dans un dossier de travail
        poser(perso / "outil" / "Untitled.md", "x", (2026, 1, 1))
        (perso / ".git-like").mkdir()
        (atelier / "config.yaml").write_text(
            f'organisation:\n  nom: "Ateliers Exemple"\n  code: exemple\ncollecte:\n'
            f'  racines: ["{perso}", "{commun}"]\n  partagees: ["{commun}"]\n'
            f'referentiel:\n  etat: aucun\n  chemin: ""\nsante:\n  max_gestes_rangement: 120\n', encoding="utf-8")
        liste = tmp / "en-ligne.txt"
        liste.write_text(str(perso / "Clients" / "Scan_0001.md") + "\n", encoding="utf-8")
        os.environ["CORTEX_RECETTE_EN_LIGNE"] = str(liste)
        _SIMULES = None

        def ici(*args):
            return subprocess.run([sys.executable, __file__, "--atelier", str(atelier), *args],
                                  capture_output=True, text=True)
        racines = [perso, commun]
        avant = arbre(racines)
        r = ici("--proposer")
        assert r.returncode == GARDE and "carte des domaines" in r.stderr, "étape 0 : domaines signés"
        (atelier / "02-ontologie.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        r = ici("--proposer")
        assert r.returncode == 0, r.stderr
        plan = lire_plan(atelier)
        par = {Path(o.get("de") or o["vers"]).name: o for o in plan["operations"]}
        # Nomenclature : titre lu dans le document local ; fichier en ligne jamais ouvert (G6).
        assert par["Nouveau document (3).md"]["vers"].endswith("Accueil d'un nouveau client - 2026-03-12.md"), par
        assert par["Scan_0001.md"]["vers"].endswith("Clients - 2026-02-01.md"), par["Scan_0001.md"]
        assert "Devis Malbrun.md" not in par, "un nom parlant ne se renomme pas"
        assert any(s["type"] == "en_ligne_seulement" for s in plan["signalements"])
        assert any(s["type"] == "doublon_probable" for s in plan["signalements"])
        assert par["Process facturation.md"]["classe"] == "entreprise" and par["Process facturation.md"]["geste"] == "deplacer"
        assert par["Process relance.md"]["geste"] == "manuel" and par["Process relance.md"]["classe"] == "a_demander"
        assert par["Mon process de devis.md"]["classe"] == "a_demander", "m5 : un indice personnel en dossier partagé se demande"
        rangs = [o["geste"] for o in plan["operations"]]
        assert rangs.index("creer_dossier") < rangs.index("deplacer") and rangs[-1] == "ecrire_index", "B1 : ordre"
        assert par["Référentiel"]["geste"] == "creer_dossier" and par["AGENTS.md"]["geste"] == "ecrire_index"
        assert all(o["partage"] for o in plan["operations"] if o["geste"] in ("creer_dossier", "ecrire_index"))
        assert not any("/lien/" in json.dumps(o) for o in plan["operations"]), "un lien symbolique n'est pas suivi"
        assert lire_fm(atelier)["statut"] == "propose"
        # Déterminisme : deux propositions identiques hors genere_le.
        sans = lambda: [l for l in (atelier / PLAN).read_text(encoding="utf-8").splitlines() if "genere_le" not in l]
        p1 = sans()
        assert ici("--proposer").returncode == 0 and sans() == p1, "deux propositions divergent"
        assert arbre(racines) == avant, "proposer ne touche à rien"

        ids = {k: o["id"] for k, o in par.items()}
        doc, scan = ids["Nouveau document (3).md"], ids["Scan_0001.md"]
        fact, relance = ids["Process facturation.md"], ids["Process relance.md"]
        refd, procd, agents = ids["Référentiel"], ids["Procédures"], ids["AGENTS.md"]

        def garde(args, attendu=GARDE):
            av = arbre(racines)
            r = ici(*args)
            assert r.returncode == attendu and arbre(racines) == av, (args, r.returncode, r.stdout, r.stderr)
            return r
        # G2 : partagé sans accord renforcé ; témoin : avec, il passe (plus loin).
        assert "G2" in garde(["--appliquer", "--ids", f"{refd}"]).stderr
        # G3 : manuel. G8 : à demander.
        assert "G8" in garde(["--appliquer", "--ids", relance, "--renforce"]).stderr
        ici("--classer", f"{relance}=entreprise")
        r3 = garde(["--appliquer", "--ids", relance, "--renforce"])
        assert "G3" in r3.stderr and "G8" not in r3.stderr, "la réponse lève G8"
        assert "espaces différents" in r3.stderr, "G3 : une ligne manuel ne s'exécute jamais"
        # Dossier d'arrivée absent sans la ligne qui le crée.
        assert "n'existe pas" in garde(["--appliquer", "--ids", fact, "--renforce"]).stderr
        # G1 : destination existante ; témoin : le même geste passe une fois la place libre.
        bloque = Path(os.path.expanduser(par["Nouveau document (3).md"]["vers"]))
        poser(bloque, "occupe", (2020, 1, 1))
        assert "G1" in garde(["--appliquer", "--ids", doc]).stderr
        bloque.rename(tmp / "occupant")                      # auto-test : la place se libère
        # G5 : origine touchée depuis la proposition.
        src_scan = perso / "Clients" / "Scan_0001.md"
        st = src_scan.stat()
        os.utime(src_scan, (st.st_atime, st.st_mtime + 60))
        assert "G5" in garde(["--appliquer", "--ids", scan]).stderr
        os.utime(src_scan, (st.st_atime, st.st_mtime))
        # G4 : une ligne qui sort des racines par un lien symbolique.
        plan = lire_plan(atelier)
        intrus = dict(plan["operations"][0], id="r900", geste="renommer", de=str(perso / "lien" / "x.md"),
                      vers=str(perso / "lien" / "y.md"), partage=False, classe="", taille=1, mtime=0.0)
        (ailleurs / "x.md").write_text("x", encoding="utf-8")
        plan["operations"].append(intrus)
        ecrire_plan(atelier, plan)
        assert "G4" in garde(["--appliquer", "--ids", "r900"]).stderr
        plan["operations"].remove(intrus)
        # G3 : une ligne ordinaire dont l'arrivée est sous une autre racine déclarée.
        travers = dict(intrus, id="r901", de=str(perso / "Divers" / "tarifs.md"), vers=str(commun / "tarifs-2.md"),
                       taille=(perso / "Divers" / "tarifs.md").stat().st_size,
                       mtime=(perso / "Divers" / "tarifs.md").stat().st_mtime, partage=True)
        plan["operations"].append(travers)
        ecrire_plan(atelier, plan)
        r3 = garde(["--appliquer", "--ids", "r901", "--renforce"])
        assert "G3" in r3.stderr and "différents" in r3.stderr, r3.stderr
        plan["operations"].remove(travers)
        # Un geste dans un dépôt git, glissé dans la liste à la main : la garde du script le refuse.
        st_o = (perso / "outil" / "Untitled.md").stat()
        glisse = dict(intrus, id="r903", de=str(perso / "outil" / "Untitled.md"), vers=str(perso / "outil" / "Outil.md"),
                      taille=st_o.st_size, mtime=st_o.st_mtime, partage=False)
        plan["operations"].append(glisse)
        ecrire_plan(atelier, plan)
        assert "dépôt git" in garde(["--appliquer", "--ids", "r903"]).stderr
        # m4 : une ligne écrite « pas partagée » sous un dossier partagé : G2 se recalcule au geste.
        plan["operations"].remove(glisse)
        fige = dict(intrus, id="r904", de=str(commun / "Divers" / "tarifs.md"), vers=str(commun / "Divers" / "Tarifs - 2025-06-01.md"),
                    taille=(commun / "Divers" / "tarifs.md").stat().st_size,
                    mtime=(commun / "Divers" / "tarifs.md").stat().st_mtime, partage=False)
        plan["operations"].append(fige)
        ecrire_plan(atelier, plan)
        assert "G2" in garde(["--appliquer", "--ids", "r904"]).stderr
        plan["operations"].remove(fige)
        plan["operations"].append(glisse)
        plan["operations"].remove(glisse)
        ecrire_plan(atelier, plan)
        # I-R3 : appliquer sans lire un octet ; la source est rendue illisible.
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            (perso / "Clients" / "Nouveau document (3).md").chmod(0)
        n_avant = len(arbre(racines)[0])
        r = ici("--appliquer", "--ids", f"{doc},{scan}")
        assert r.returncode == 0, r.stderr
        # N10 : le sommaire montré avant l'accord est celui qui s'écrit, et le montrer n'écrit rien.
        av_montre = arbre(racines)
        montre = ici("--montrer-index", "--ids", f"{refd},{procd},{fact},{agents}",
                     "--proprietaire", "Procédures/Facturation d'une affaire - 2025-11-04.md=Direction")
        assert montre.returncode == 0 and arbre(racines) == av_montre, montre.stderr
        r = ici("--appliquer", "--ids", f"{refd},{procd},{fact},{agents}", "--renforce",
                "--proprietaire", "Procédures/Facturation d'une affaire - 2025-11-04.md=Direction")
        assert r.returncode == 0, r.stderr
        ref = commun / "Référentiel"
        index = (ref / "AGENTS.md").read_text(encoding="utf-8")
        assert index == montre.stdout, "N10 : le texte montré n'est pas celui écrit"
        assert MARQUEUR in index and "Facturation d'une affaire - 2025-11-04.md" in index and "| Direction |" in index
        assert len(arbre(racines)[0]) == n_avant + 1, "I-R1 : seuls s'ajoutent un dossier et le sommaire"
        assert ici("--verifier").returncode == 0
        # G7 par la ligne de commande : un sommaire sans la marque, code 3, arbre identique.
        etranger = plan["operations"][0] | {"id": "r902", "geste": "ecrire_index", "partage": True, "classe": ""}
        etranger.pop("de", None)
        (commun / "Divers" / "AGENTS.md").write_text("# à quelqu'un\n", encoding="utf-8")
        etranger["vers"] = str(commun / "Divers" / "AGENTS.md")
        plan = lire_plan(atelier)
        plan["operations"].append(etranger)
        ecrire_plan(atelier, plan)
        assert "G7" in garde(["--appliquer", "--ids", "r902", "--renforce"]).stderr
        plan["operations"].remove(etranger)
        ecrire_plan(atelier, plan)
        (commun / "Divers" / "AGENTS.md").unlink()           # auto-test : le témoin G7 se retire
        # G7 témoin : un sommaire sans la marque ne se réécrit pas.
        (tmp / "etranger").mkdir()
        (tmp / "etranger" / "AGENTS.md").write_text("# à quelqu'un\n", encoding="utf-8")
        try:
            ecrire_index(tmp / "etranger" / "AGENTS.md", {}, {})
            raise AssertionError("G7 aurait dû lever")
        except Garde:
            pass
        # Publication d'un assistant (maillon 6) : le dossier commun doit être déclaré.
        spec = atelier / "agents" / "lecteur-de-baux"
        spec.mkdir(parents=True)
        (spec / "SKILL.md").write_text("---\nname: lecteur-de-baux\ndescription: Relève échéances et loyers d'un bail. Suite.\n---\n# x\n", encoding="utf-8")
        assert "aucun dossier commun" in garde(["--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux", "--renforce"]).stderr
        # N1 : la marque retirée du sommaire entre deux lots ; le geste se fait, le sommaire ne suit
        # pas : code 1 (pas 3), message qui le dit, échec journalisé sous un id i….
        mon = ids["Mon process de devis.md"]
        ici("--classer", f"{mon}=entreprise")
        texte_index_ok = (ref / "AGENTS.md").read_text(encoding="utf-8")
        sans_marque = "<!-- retiré".join(texte_index_ok.split(MARQUEUR))
        (ref / "AGENTS.md").write_text(sans_marque, encoding="utf-8")
        r = ici("--appliquer", "--ids", mon, "--renforce")
        derniere = lire_journal(atelier)[-1]
        assert r.returncode == ECART and "seul le sommaire" in r.stderr, (r.returncode, r.stderr)
        assert derniere["id"].startswith("i") and derniere["resultat"] == "echec", derniere
        assert (ref / "Procédures" / "Mes devis - 2025-07-01.md").is_file(), "le geste est fait"
        (ref / "AGENTS.md").write_text(texte_index_ok, encoding="utf-8")
        # M2 : une ligne acceptée et pas faite interdit la clôture.
        md0 = (atelier / LISIBLE).read_text(encoding="utf-8")
        (atelier / LISIBLE).write_text(md0.replace("acceptees: [", f"acceptees: [{relance}, ", 1),
                                       encoding="utf-8")
        assert "appliqué en partie" in garde(["--clore", "applique"]).stderr
        (atelier / LISIBLE).write_text(md0, encoding="utf-8")
        assert ici("--clore", "applique").returncode == 0
        assert charger_conf(atelier)["referentiel"]["etat"] == "existant"
        assert ici("--clore", "applique").returncode == 0, "clore deux fois ne réécrit pas l'avant"
        assert "Mes devis" in (ref / "AGENTS.md").read_text(encoding="utf-8"), "la clôture rafraîchit le sommaire"
        # N6 : défaire un seul rangement vers le dossier commun le sort aussi du sommaire, journalisé.
        r = ici("--annuler", "--ids", mon)
        assert r.returncode == 0 and "Mes devis" not in (ref / "AGENTS.md").read_text(encoding="utf-8"), r.stderr
        assert lire_journal(atelier)[-1]["id"].startswith("i") and lire_journal(atelier)[-1]["resultat"] == "fait"
        assert ici("--clore", "applique").returncode == 0
        assert "G2" in garde(["--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux"]).stderr
        index_avant = (ref / "AGENTS.md").read_text(encoding="utf-8")
        # M3 : un sommaire présent seulement en ligne ne s'ouvre pas ; rien ne se publie (G6, code 3).
        liste.write_text(liste.read_text(encoding="utf-8") + str(ref / "AGENTS.md") + "\n", encoding="utf-8")
        assert "G6" in garde(["--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux", "--renforce"]).stderr
        liste.write_text(str(perso / "Clients" / "Scan_0001.md") + "\n", encoding="utf-8")
        assert ici("--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux", "--renforce").returncode == 0
        # m2 : publier sur un assistant déjà publié, code 3 et rien ne bouge (G1).
        assert "G1" in garde(["--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux", "--renforce"]).stderr
        # N3 : un assistant publié puis retouché par un collègue ne se retire pas : code 1, fichier intact.
        publie = ref / "assistants" / "lecteur-de-baux" / "SKILL.md"
        texte_publie = publie.read_text(encoding="utf-8")
        publie.write_text(texte_publie + "Retouche d'un collègue.\n", encoding="utf-8")
        derniere_pub = [l["id"] for l in lire_journal(atelier) if l.get("geste") == "publier" and l["resultat"] == "fait"][-1]
        r = ici("--annuler", "--ids", derniere_pub)
        assert r.returncode == ECART and "modifié" in r.stderr, (r.returncode, r.stderr)
        assert publie.read_text(encoding="utf-8").endswith("Retouche d'un collègue.\n")
        publie.write_text(texte_publie, encoding="utf-8")
        assert "lecteur-de-baux | Relève échéances et loyers d'un bail" in (ref / "AGENTS.md").read_text(encoding="utf-8")
        assert "| Direction |" in (ref / "AGENTS.md").read_text(encoding="utf-8"), "le propriétaire survit à la réécriture"
        # Défaire la publication rend le sommaire mot pour mot, quel que soit le jour (marque datée).
        r = ici("--annuler", "--ids", "p001")
        assert r.returncode == 0 and (ref / "AGENTS.md").read_text(encoding="utf-8") == index_avant, r.stderr
        assert not (ref / "assistants").exists()
        assert ici("--publier", str(spec / "SKILL.md"), "--nom", "lecteur-de-baux", "--renforce").returncode == 0
        # Geste manuel : en attente (A4), puis constaté par --verifier.
        c = json.loads(ici("--chemins").stdout)
        assert c["en_attente"] == [tilde(perso / "Process relance.md")] and not note_autorisee(atelier, perso / "Process relance.md")
        assert ici("--autorise", str(perso / "Process relance.md")).returncode == GARDE
        dest = Path(os.path.expanduser(next(o for o in lire_plan(atelier)["operations"] if o["id"] == relance)["vers"]))
        st_rel = (perso / "Process relance.md").stat()
        os.rename(perso / "Process relance.md", dest)          # auto-test : la personne, dans son outil
        with open(dest, "a", encoding="utf-8") as f:
            f.write("ajout")                                   # A7 : une autre taille n'est pas le même fichier
        assert ici("--verifier").returncode == 0 and json.loads(ici("--chemins").stdout)["en_attente"]
        poser(dest, "# Relance d'un impayé\n", (2026, 1, 20, 9))
        os.utime(dest, (st_rel.st_atime, st_rel.st_mtime + 3600))   # la date change, la taille revient
        assert ici("--verifier").returncode == 0
        c = json.loads(ici("--chemins").stdout)
        assert c["en_attente"] == [] and c["traductions"][tilde(perso / "Process relance.md")] == tilde(dest)
        assert note_autorisee(atelier, perso / "Process relance.md")
        r = ici("--autorise", str(perso / "Process relance.md"))
        assert r.returncode == OK and tilde(dest) in r.stdout, r.stdout
        # --verifier a son témoin : un fichier rangé qu'on touche est un écart.
        rangé = Path(os.path.expanduser(par["Scan_0001.md"]["vers"]))
        st = rangé.stat()
        os.utime(rangé, (st.st_atime, st.st_mtime + 5))
        assert ici("--verifier").returncode == ECART
        os.utime(rangé, (st.st_atime, st.st_mtime))
        # I-R2 : tout défaire rend l'arbre d'avant (le geste manuel, fait par la personne, se remet à la main).
        os.rename(dest, perso / "Process relance.md")          # auto-test : la personne remet le fichier
        os.utime(perso / "Process relance.md", (st_rel.st_atime, st_rel.st_mtime))
        r = ici("--annuler")
        assert r.returncode == 0, r.stdout + r.stderr
        if hasattr(os, "geteuid"):
            (perso / "Clients" / "Nouveau document (3).md").chmod(0o644)
        assert arbre(racines) == avant, "I-R2 : appliquer puis annuler doit rendre l'arbre d'avant"
        assert charger_conf(atelier)["referentiel"] == {"etat": "aucun", "chemin": ""}, \
            "défaire rend aussi la config d'avant : aucun sommaire fantôme"
        # A5 : une ligne acceptée jamais faite se retire par --annuler --ids.
        ici("--proposer")
        nouveau = {Path(o.get("de") or o["vers"]).name: o["id"] for o in lire_plan(atelier)["operations"]}
        assert int(nouveau["Nouveau document (3).md"][1:]) > int(agents[1:]), "les id ne se réutilisent pas"
        fm_txt = (atelier / LISIBLE).read_text(encoding="utf-8")
        fm_txt = fm_txt.replace("acceptees: []", f"acceptees: [{nouveau['Scan_0001.md']}]")
        (atelier / LISIBLE).write_text(fm_txt, encoding="utf-8")
        assert partiel(lire_plan(atelier)["operations"], lire_fm(atelier), lire_journal(atelier))
        ici("--annuler", "--ids", nouveau["Scan_0001.md"])
        assert not partiel(lire_plan(atelier)["operations"], lire_fm(atelier), lire_journal(atelier))
        assert ici("--clore", "refuse").returncode == 0 and lire_fm(atelier)["statut"] == "refuse"
        # G9 : au-delà du plafond, la liste s'arrête et le déclare.
        cfg = (atelier / "config.yaml").read_text(encoding="utf-8").replace("max_gestes_rangement: 120",
                                                                              "max_gestes_rangement: 3")
        (atelier / "config.yaml").write_text(cfg, encoding="utf-8")
        ici("--proposer")
        b = lire_plan(atelier)["bornes"]
        assert b["gestes"] == 3 and b["depassement"] and b["ecartes"] > 0, b
        # N4 : la troncature garde d'abord la création du dossier commun et le sommaire.
        assert sorted(o["geste"] for o in lire_plan(atelier)["operations"]) == ["creer_dossier", "creer_dossier", "ecrire_index"], \
            [o["geste"] for o in lire_plan(atelier)["operations"]]
        (atelier / "config.yaml").write_text(cfg.replace("max_gestes_rangement: 3", "max_gestes_rangement: 120"),
                                             encoding="utf-8")
        ici("--proposer")
        b = lire_plan(atelier)["bornes"]
        assert not b["depassement"] and b["ecartes"] == 0, b
        assert arbre(racines) == avant
        # D3 : une fois le second cerveau construit, plus rien ne se propose ni ne s'applique.
        md = (atelier / LISIBLE).read_text(encoding="utf-8").replace("---\n", "---\nconstruit_le: 2026-10-04\n", 1)
        (atelier / LISIBLE).write_text(md, encoding="utf-8")
        assert "construit" in garde(["--proposer"]).stderr
        assert "construit" in garde(["--appliquer", "--ids", "r001"]).stderr
        assert "construit" in garde(["--annuler"]).stderr
    os.environ.pop("CORTEX_RECETTE_EN_LIGNE", None)
    _SIMULES = None
    # M2 : une racine à soi déclarée sous une racine partagée reste partagée (contrat §3).
    rr = Racines({"collecte": {"racines": ["/x/Equipe", "/x/Equipe/Mes projets"], "partagees": ["/x/Equipe"]}})
    assert rr.partagee("/x/Equipe/Mes projets/a.pdf") and rr.de("/x/Equipe/Mes projets/a.pdf") == "/x/Equipe/Mes projets"
    with tempfile.TemporaryDirectory() as t:
        t = Path(os.path.realpath(t))
        # M1 : une racine dans un dépôt git ne reçoit aucune proposition ; témoin : la même sans .git.
        depot, at = t / "Depot", t / "w" / "_cortex"
        (depot / "src").mkdir(parents=True)
        at.mkdir(parents=True)
        (depot / "Untitled.txt").write_text("x", encoding="utf-8")
        (at / "config.yaml").write_text(f'collecte:\n  racines: ["{depot}"]\n', encoding="utf-8")
        (at / "02-ontologie.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        assert proposer(at)["operations"], "témoin : sans dépôt, le nom illisible se propose"
        (depot / ".git").mkdir()
        p = proposer(at)
        assert not p["operations"] and any(x["type"] == "racine_dans_un_depot" for x in p["signalements"]), p
        # Partagée, elle ne reçoit pas non plus de dossier commun ni de sommaire.
        (at / "config.yaml").write_text(f'collecte:\n  racines: ["{depot}"]\n  partagees: ["{depot}"]\n',
                                        encoding="utf-8")
        p = proposer(at)
        assert not p["operations"] and not (depot / "Référentiel").exists(), p["operations"]
        # M3 : un sommaire marqué, complété à la main, revient mot pour mot à l'annulation.
        ag = t / "AGENTS.md"
        ag.write_text(f"# Dossier commun\n\n{MARQUEUR} 2020-01-01 -->\n\nNote ajoutée à la main.\n", encoding="utf-8")
        texte0 = ag.read_text(encoding="utf-8")
        cree, empreinte, _, avant = ecrire_index(ag, {}, {})
        assert not cree and avant == texte0 and "Note ajoutée" not in ag.read_text(encoding="utf-8")
        note, _ = _defaire_index(str(ag), cree, avant, [{"index": str(ag), "index_sha256": empreinte,
                                                          "resultat": "fait"}], {})
        assert note == "" and ag.read_text(encoding="utf-8") == texte0
        # Témoin : touché à la main depuis, il reste tel quel.
        cree, empreinte, _, avant = ecrire_index(ag, {}, {})
        ag.write_text(ag.read_text(encoding="utf-8") + "retouche\n", encoding="utf-8")
        note, _ = _defaire_index(str(ag), cree, avant, [{"index": str(ag), "index_sha256": empreinte,
                                                          "resultat": "fait"}], {})
        assert "laissé tel quel" in note and ag.read_text(encoding="utf-8").endswith("retouche\n")
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        # m2 : la création du sommaire est exclusive, elle n'écrase pas un fichier apparu entre-temps.
        (t / "AGENTS.md").write_text("à quelqu'un", encoding="utf-8")
        try:
            creer_exclusif(t / "AGENTS.md", "écrasé")
            raise AssertionError("creer_exclusif a écrasé")
        except FileExistsError:
            assert (t / "AGENTS.md").read_text(encoding="utf-8") == "à quelqu'un"
        # m10 : un .docx sans corps se signale (None), il ne passe pas pour « sans titre ».
        with zipfile.ZipFile(t / "vide.docx", "w") as z:
            z.writestr("[Content_Types].xml", "<Types/>")
        assert titre_local(t / "vide.docx") is None
        # m10 : un stat refusé (droits) remonte, il ne devient ni « local » ni « changé ».
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            (t / "ferme").mkdir()
            (t / "ferme" / "f.txt").write_text("x", encoding="utf-8")
            (t / "ferme").chmod(0o600)
            try:
                for f in (lambda: en_ligne_seulement(t / "ferme" / "f.txt"),
                          lambda: _identique(t / "ferme" / "f.txt", 1, 0.0)):
                    try:
                        f()
                        raise AssertionError("un stat refusé a été avalé")
                    except PermissionError:
                        pass
            finally:
                (t / "ferme").chmod(0o700)
        assert en_ligne_seulement(t / "absent") is False and _identique(t / "absent", 1, 0.0) is False
    # Le renommage exclusif refuse une destination existante, même sans la garde G1 devant lui.
    with tempfile.TemporaryDirectory() as t:
        a_, b_ = Path(t) / "a", Path(t) / "b"
        a_.write_text("a", encoding="utf-8")
        b_.write_text("b", encoding="utf-8")
        try:
            renommer_exclusif(a_, b_)
            raise AssertionError("renommer_exclusif a écrasé une destination")
        except FileExistsError:
            pass
        assert b_.read_text(encoding="utf-8") == "b" and a_.is_file()
        renommer_exclusif(a_, Path(t) / "c")
        assert (Path(t) / "c").is_file() and not a_.exists()
    # Nomenclature : chaque forme illisible du contrat §6, et ses témoins parlants.
    for n in ("Nouveau document (3)", "Sans titre", "Untitled", "Document1", "Classeur1", "Scan_0042", "IMG_1234",
              "DSC01234", "Budget (1)", "Copie de tarifs", "rapport final", "devis v2", "20240312", "v2"):
        assert illisible(n)[0], n
    for n in ("Devis Malbrun", "PV-reception", "Planning chantier", "CR-2026-05", "plan-001"):
        assert not illisible(n)[0], n
    assert illisible("Budget (1)")[1] == "Budget" and illisible("Copie de tarifs")[1] == "tarifs"
    assert nom_parlant('a/b:c*d?"e<f>g|h', "2026-01-01", ".docx") == "A b c d e f g h - 2026-01-01.docx"
    assert len(nom_parlant("x" * 300, "2026-01-01", ".docx")) <= MAX_NOM
    assert date_de("CR 2025-11-04", 0) == "2025-11-04"
    print("range.py : auto-test OK (G1 à G9 dans les deux sens, I-R1 à I-R3, déterminisme, A3 à A5)")
    return OK


def main():
    p = argparse.ArgumentParser(description="Ranger les dossiers de travail sur accord (étape 3 bis).")
    p.add_argument("--atelier")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--proposer", action="store_true")
    g.add_argument("--classer", metavar="ID=CLASSE[,…]")
    g.add_argument("--nommer", metavar="ID=OBJET[,…]")
    g.add_argument("--appliquer", action="store_true")
    g.add_argument("--verifier", action="store_true")
    g.add_argument("--annuler", action="store_true")
    g.add_argument("--publier", metavar="SKILL.md")
    g.add_argument("--chemins", action="store_true")
    g.add_argument("--montrer-index", action="store_true",
                   help="imprime le sommaire exact que --appliquer écrira avec ces --ids, sans rien écrire")
    g.add_argument("--autorise", metavar="CHEMIN", help="0 si une note-pointeur peut viser ce chemin, 3 sinon (A4)")
    g.add_argument("--clore", choices=("applique", "refuse"))
    g.add_argument("--autotest", action="store_true")
    p.add_argument("--ids", help="r001,r003")
    p.add_argument("--renforce", action="store_true", help="accord renforcé : dossier partagé avec des collègues")
    p.add_argument("--referentiel", default="", help="où créer le dossier commun (forme ~)")
    p.add_argument("--proprietaire", action="append", default=[], help='"Procédures/X.docx=Nom"')
    p.add_argument("--nom", help="nom de l'assistant publié")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.atelier or not Path(a.atelier).expanduser().is_dir():
        print(f"[usage] atelier introuvable : {a.atelier}", file=sys.stderr)
        return USAGE
    atelier = Path(a.atelier).expanduser()
    ids = [i.strip() for i in a.ids.split(",") if i.strip()] if a.ids else None
    try:
        if a.proposer:
            plan = proposer(atelier, a.referentiel)
            b = plan["bornes"]
            print(f"OK : {b['gestes']} changement(s) proposé(s)" + (f", {b['ecartes']} écarté(s) au-delà du plafond"
                                                                  if b["depassement"] else "")
                  + f", {len(plan['signalements'])} signalement(s) ; {atelier / PLAN}")
            return OK
        if a.classer:
            classer(atelier, _paires(a.classer))
            return OK
        if a.nommer:
            nommer(atelier, _paires(a.nommer))
            return OK
        if a.appliquer:
            if not ids:
                print("[usage] --appliquer demande --ids", file=sys.stderr)
                return USAGE
            proprios = dict(x.split("=", 1) for x in a.proprietaire if "=" in x)
            return appliquer(atelier, ids, a.renforce, proprios)
        if a.verifier:
            return verifier(atelier)
        if a.annuler:
            return annuler(atelier, ids)
        if a.publier:
            if not a.nom:
                print("[usage] --publier demande --nom", file=sys.stderr)
                return USAGE
            return publier(atelier, a.publier, a.nom, a.renforce)
        if a.chemins:
            print(json.dumps(chemins(atelier), ensure_ascii=False, indent=2))
            return OK
        if a.montrer_index:
            proprios = dict(x.split("=", 1) for x in a.proprietaire if "=" in x)
            print(montrer_index(atelier, ids, proprios), end="")
            return OK
        if a.autorise:
            c = chemins(atelier)
            ancien = tilde(os.path.expanduser(a.autorise))
            if not note_autorisee(atelier, a.autorise):
                print(f"non : {ancien} attend un déplacement fait par la personne ; aucune fiche, "
                      "« en attente de déplacement » dans 04-ingest.md")
                return GARDE
            nouveau = c["traductions"].get(ancien)
            print(f"oui : {nouveau}" + " (chemin rangé)" if nouveau else f"oui : {ancien}")
            return OK
        if a.clore:
            return clore(atelier, a.clore)
    except Garde as e:
        print(f"[garde] {e} Rien n'a bougé.", file=sys.stderr)
        return GARDE
    except Usage as e:
        print(f"[usage] {e}", file=sys.stderr)
        return USAGE
    except (ValueError, OSError) as e:
        print(f"[erreur] {e}", file=sys.stderr)
        return ECART
    p.print_help()
    return USAGE


if __name__ == "__main__":
    sys.exit(main())
