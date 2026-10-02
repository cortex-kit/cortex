#!/usr/bin/env python3
"""poste.py — équipe le poste pour un second cerveau. stdlib pure, jamais sans accord.

Quatre gestes, tous explicites :
  --dry-run                    une ligne par outil du kit absent, avec la commande de l'OS courant
  --installer a,b              installe CES outils, et seulement ceux-là (l'accord a été donné avant)
  --mail adresse [...]         reconnaît le fournisseur (MX) et propose la voie de branchement ;
                               --voie porte la réponse de la personne : sans elle, une voie qui
                               installe quelque chose (softeria, mcp-email) s'écrit « aucune »,
                               sauf réponse déjà écrite ; --options se garde de même
  --ecrire --atelier <_cortex> écrit _cortex/poste.json, le bloc `poste` et organisation.code
                               (le slug, --slug ou déduit du chemin) de config.yaml, puis
                               régénère et ouvre la notice. notice_ouverte_le est posé ici : la
                               notice est présentée, --no-open n'évite que l'ouvreur (recette)
  --autotest                   auto-test hors ligne

Schéma de poste.json et lecture du MX : 04-contrat.md §3. `py` vaut `python3` sous Windows.
"""

import argparse
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_ICI = Path(__file__).resolve().parent
# Le kit, dans l'ordre du contrat. `node` n'en fait pas partie : il ne s'installe que si
# la voie mail l'exige (softeria ou mcp-email), il est mesuré mais jamais listé en dry-run.
KIT = ["obsidian", "uv", "markitdown", "git", "gh", "github-desktop", "buzz", "graphify"]

# cmd : exécutable cherché dans le PATH ; app : application par OS ; install : commande par OS.
OUTILS = {
    "obsidian": {"app": {"macos": "Obsidian.app", "windows": r"Obsidian\Obsidian.exe", "linux": "obsidian"},
                 "install": {"macos": "brew install --cask obsidian",
                             "windows": "winget install --id Obsidian.Obsidian -e",
                             "linux": "flatpak install -y flathub md.obsidian.Obsidian"}},
    "uv": {"cmd": "uv", "install": {"macos": "brew install uv",
                                     "windows": "winget install --id astral-sh.uv -e",
                                     "linux": "curl -LsSf https://astral.sh/uv/install.sh | sh"}},
    # Le paquet nu ne lit ni pdf ni docx : toujours l'extra [all], installé et sondé par uv.
    "markitdown": {"uvx": ["--from", "markitdown[all]", "markitdown"],
                   "install": {os_: 'uv tool install "markitdown[all]"'
                               for os_ in ("macos", "windows", "linux")}},
    "git": {"cmd": "git", "install": {"macos": "brew install git",
                                       "windows": "winget install --id Git.Git -e",
                                       "linux": "sudo apt-get install -y git"}},
    "gh": {"cmd": "gh", "install": {"macos": "brew install gh",
                                     "windows": "winget install --id GitHub.cli -e",
                                     "linux": "sudo apt-get install -y gh"}},
    "github-desktop": {"app": {"macos": "GitHub Desktop.app", "windows": r"GitHubDesktop\GitHubDesktop.exe",
                               "linux": ""},
                       "install": {"macos": "brew install --cask github",
                                   "windows": "winget install --id GitHub.GitHubDesktop -e",
                                   "linux": "aucune version officielle sur Linux, gh suffit"}},
    "buzz": {"app": {"macos": "Buzz.app", "windows": r"Programs\Buzz\Buzz.exe", "linux": "buzz"},
             "install": {"macos": "brew install --cask buzz",
                         "windows": "winget install --id ChidiWilliams.Buzz -e",
                         "linux": "uv tool install buzz-captions"}},
    # Carte d'un dossier de documents ou d'un dépôt de code : installé par uv comme markitdown,
    # optionnel dans le kit, jamais pointé sur le vault (décision 15).
    "graphify": {"cmd": "graphify", "install": {os_: 'uv tool install "graphifyy[pdf,office]"'
                                                for os_ in ("macos", "windows", "linux")}},
    "node": {"cmd": "node", "install": {"macos": "brew install node",
                                         "windows": "winget install --id OpenJS.NodeJS.LTS -e",
                                         "linux": "sudo apt-get install -y nodejs"}},
}


def os_courant():
    return {"Darwin": "macos", "Windows": "windows"}.get(platform.system(), "linux")


def _version(cmd):
    # cwd temporaire et propre : `markitdown --version` dépose un `:memory:.ses` dans le dossier courant.
    try:
        with tempfile.TemporaryDirectory() as cwd:
            r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=10, cwd=cwd)
        m = re.search(r"\d+(\.\d+)+", r.stdout + r.stderr)
        return m.group(0) if m else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _raison(sortie, prefixe):
    """Première ligne d'erreur et sa cause, chemin personnel en forme ~, bornée : la
    raison d'une sonde qui n'a rien prouvé, dite telle quelle plutôt qu'« absent »."""
    lignes = [l.strip() for l in sortie.splitlines() if l.strip()][:2]
    texte = " ; ".join(lignes).replace(str(Path.home()), "~") or "aucune sortie"
    return f"{prefixe} : {texte}"[:200]


def dossier_outils_uv():
    """Le dossier où `uv tool install` pose ses exécutables : `uv tool dir --bin` quand
    uv répond, sinon ~/.local/bin (Path.home() vaut %USERPROFILE% sous Windows)."""
    defaut = Path.home() / ".local" / "bin"
    uv = shutil.which("uv") or shutil.which("uv", path=str(defaut))
    if uv:
        try:
            r = subprocess.run([uv, "tool", "dir", "--bin"], capture_output=True, text=True, timeout=15)
            if r.returncode == 0 and r.stdout.strip():
                return Path(r.stdout.strip())
        except (OSError, subprocess.TimeoutExpired):
            pass  # repli du contrat (§2) : l'emplacement par défaut de uv, cherché quand même
    return defaut


def trouver(cmd, bin_uv):
    """Le PATH d'abord, puis le dossier des outils de uv, absent du PATH d'une session neuve."""
    return shutil.which(cmd) or shutil.which(cmd, path=str(bin_uv))


def _uvx(args, uvx):
    """Sonde un outil servi par uvx : `uvx --from "paquet[extra]" outil --version`.
    Sans uvx, l'outil est absent. Une sonde qui échoue (cache refusé par un bac à sable,
    réseau coupé, délai) ne prouve pas l'absence : present vaut None, avec sa raison."""
    if not uvx:
        return {"present": False, "version": ""}
    try:
        with tempfile.TemporaryDirectory() as cwd:
            r = subprocess.run([uvx, *args, "--version"], capture_output=True, text=True, timeout=120, cwd=cwd)
    except subprocess.TimeoutExpired:
        return {"present": None, "version": "", "raison": "sonde uvx : délai de 120 s dépassé"}
    except OSError as e:
        return {"present": None, "version": "", "raison": _raison(str(e), "sonde uvx impossible")}
    if r.returncode != 0:
        return {"present": None, "version": "", "raison": _raison(r.stderr or r.stdout, "sonde uvx en échec")}
    m = re.search(r"\d+(\.\d+)+", r.stdout + r.stderr)
    return {"present": True, "version": m.group(0) if m else ""}


def _app(nom, systeme, bin_uv):
    """Rend (présent, version) pour une application de bureau."""
    if not nom:
        return False, ""
    if systeme == "macos":
        for base in (Path("/Applications"), Path.home() / "Applications"):
            plist = base / nom / "Contents" / "Info.plist"
            if plist.is_file():
                try:
                    with plist.open("rb") as f:
                        return True, str(plistlib.load(f).get("CFBundleShortVersionString", ""))
                except Exception:  # noqa: BLE001 — un plist illisible vaut « présent, version inconnue »
                    return True, ""
        return False, ""
    if systeme == "windows":
        exe = Path(os.environ.get("LOCALAPPDATA", "")) / nom
        return exe.is_file(), ""
    chemin = trouver(nom, bin_uv)
    return bool(chemin), _version(chemin) if chemin else ""


def detecter(systeme=None):
    """Mesure chaque outil. Rend {nom: {present, version[, raison][, chemin]}}, present
    à None quand la sonde n'a pu ni prouver la présence ni l'absence. Ne modifie rien.
    Un outil trouvé par son binaire est présent, sans sonde uvx (04-contrat H2 §2)."""
    systeme = systeme or os_courant()
    bin_uv = dossier_outils_uv()
    etat = {}
    for nom, o in OUTILS.items():
        if "app" in o:
            present, version = _app(o["app"].get(systeme, ""), systeme, bin_uv)
            etat[nom] = {"present": present, "version": version}
            continue
        chemin = trouver(o.get("cmd", nom), bin_uv)
        if chemin:
            etat[nom] = {"present": True, "version": _version(chemin), "chemin": chemin}
        elif "uvx" in o:
            etat[nom] = _uvx(o["uvx"], trouver("uvx", bin_uv))
        else:
            etat[nom] = {"present": False, "version": ""}
    return etat


def gh_connecte(gh="gh"):
    """Rend (connecte, raison). « Not logged into any » prouve la déconnexion ; tout
    autre échec (trousseau illisible dans un bac à sable, réseau) vaut None, raison dite."""
    try:
        r = subprocess.run([gh, "auth", "status"], capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return None, "gh auth status : délai de 15 s dépassé"
    except OSError as e:
        return None, _raison(str(e), "gh auth status impossible")
    if r.returncode == 0:
        return True, ""
    sortie = r.stdout + r.stderr
    if "not logged into any" in sortie.lower():
        return False, ""
    # La cause, sans la ligne qui nomme le compte : poste.json n'a pas à le porter.
    causes = [l for l in sortie.splitlines() if "account" not in l.lower()
              and re.search(r"token|keyring|error|denied|timeout|network", l, re.I)]
    return None, _raison("\n".join(causes) or f"code {r.returncode}", "gh auth status illisible ici")


def lignes_dry_run(etat, systeme):
    """Une ligne par outil du kit absent, avec sa commande ; « à vérifier » pour un
    outil que la sonde n'a pas pu mesurer : jamais d'installation sur un doute."""
    lignes = []
    for nom in KIT:
        e = etat[nom]
        if e["present"] is None:
            lignes.append(f"{nom} : à vérifier ({e.get('raison') or 'sonde sans réponse'})")
        elif not e["present"]:
            lignes.append(f"{nom} : absent → {OUTILS[nom]['install'][systeme]}")
    return lignes


def installer(noms, systeme):
    """Exécute la commande d'installation de chaque outil nommé. L'accord est acquis en amont."""
    faits = []
    for nom in noms:
        if nom not in OUTILS:
            print(f"[poste] outil inconnu : {nom}", file=sys.stderr)
            continue
        cmd = OUTILS[nom]["install"][systeme]
        print(f"[poste] {nom} : {cmd}")
        if subprocess.run(cmd, shell=True).returncode == 0:
            faits.append(nom)
        else:
            print(f"[poste] {nom} : la commande a échoué, à reprendre à la main", file=sys.stderr)
    return faits


# ── Mail ────────────────────────────────────────────────────────────────────

def lire_mx(sortie_nslookup):
    """Extrait les hôtes MX d'une sortie nslookup (mac, Windows, Linux : même motif)."""
    return [m.lower().rstrip(".") for m in
            re.findall(r"mail exchanger\s*=\s*(?:\d+\s+)?(\S+)", sortie_nslookup, re.I)]


def mx(domaine):
    try:
        r = subprocess.run(["nslookup", "-type=MX", domaine], capture_output=True, text=True, timeout=15)
        return lire_mx(r.stdout)
    except (OSError, subprocess.TimeoutExpired):
        return []


def fournisseur(domaine, hotes):
    """gmail | outlook_perso | m365 | "" (inconnu : question à trois options)."""
    domaine = domaine.lower()
    if any(h.endswith(("google.com", "googlemail.com")) for h in hotes):
        return "gmail"
    if any(h.endswith(("outlook.com", "protection.outlook.com")) for h in hotes):
        perso = domaine == "outlook.com" or domaine.startswith(("hotmail.", "live."))
        return "outlook_perso" if perso else "m365"
    return ""


def voie(four, boites=1, admin=False, imap=False):
    if four == "gmail":
        return "connecteur" if boites <= 1 else "mcp-email"
    if four == "m365":
        return "connecteur" if admin else "softeria"
    if four == "outlook_perso":
        return "softeria"
    return "mcp-email" if imap else "aucune"


# Voies qui posent quelque chose sur le poste (un serveur local, node) : jamais sans accord.
VOIES_QUI_INSTALLENT = ("softeria", "mcp-email")


def bloc_mail(a, ancien=None):
    """`voie` est ce qui s'écrit : la réponse de la personne (--voie), sinon celle déjà
    écrite pour la même proposition (`ancien`, le bloc mail de poste.json), sinon la
    voie calculée si elle n'installe rien, sinon « aucune ». `voie_proposee` garde la
    voie calculée, pour que le skill sache quoi proposer (04-contrat H2 §2)."""
    ancien = ancien or {}
    if ancien and not (a.mail or a.fournisseur or a.voie):
        return ancien          # rien de neuf sur le mail : la réponse acquise reste
    domaine = a.mail.rsplit("@", 1)[-1].strip().lower() if a.mail else ""
    hotes = mx(domaine) if domaine and not a.fournisseur else []
    four = a.fournisseur or (fournisseur(domaine, hotes) if domaine else "")
    proposee = voie(four, a.boites, a.admin, a.imap)
    acquise = ancien.get("voie", "") if ancien.get("voie_proposee") == proposee else ""
    retenue = a.voie or acquise or ("aucune" if proposee in VOIES_QUI_INSTALLENT else proposee)
    return {"fournisseur": four, "boites": a.boites, "voie": retenue, "voie_proposee": proposee,
            "domaine": domaine, "mx": hotes[0] if hotes else ""}


# ── Écriture ────────────────────────────────────────────────────────────────

def paires_poste(poste):
    """Le bloc `poste` de config.yaml, miroir de poste.json. `outils` liste TOUT le
    kit (04-contrat.md §2), présent ou non : poste.json porte le présent/absent."""
    return {"os": poste["os"],
            "outils": "[" + ", ".join(KIT) + "]",
            "mail_fournisseur": poste["mail"]["fournisseur"] or '""',
            "mail_boites": poste["mail"]["boites"],
            "mail_voie": poste["mail"]["voie"]}


def fusionner_bloc(config, cle, paires):
    """Fusionne `paires` dans le bloc `cle:` de config.yaml. Les clés filles déjà
    présentes et non fournies sont conservées, le reste du fichier ne bouge pas.
    Crée le fichier s'il manque."""
    texte = config.read_text(encoding="utf-8") if config.is_file() else "version: 1\n"
    garde, dedans, filles = [], False, {}
    for l in texte.splitlines():
        if re.match(r"^" + re.escape(cle) + r":\s*(#.*)?$", l):
            dedans = True
            continue
        if dedans and l.strip() and not l.startswith((" ", "\t")):
            dedans = False
        if not dedans:
            garde.append(l)
        elif ":" in l:
            k, v = l.split(":", 1)
            filles[k.strip()] = v.strip()
    filles.update({k: str(v) for k, v in paires.items()})
    bloc = cle + ":\n" + "".join("  {}: {}\n".format(k, v) for k, v in filles.items())
    texte = "\n".join(garde).rstrip("\n") + "\n\n" + bloc
    config.write_text(texte, encoding="utf-8")
    return texte


def _cortex4():
    for cand in (_ICI, _ICI.parent.parent / "cortex-4-installation" / "scripts"):
        if (cand / "notice.py").is_file():
            return cand
    return None


def slug_de(a, atelier):
    """Le slug (`organisation.code`) : donné par --slug, sinon lu dans le chemin
    de l'atelier (`~/Cortex/<slug>/_cortex`), sinon vide."""
    if a.slug:
        return a.slug.strip().lower()
    return atelier.parent.name.lower() if atelier.name == "_cortex" else ""


def deja_par_cortex(ancien):
    """Ce que Cortex avait déjà installé, relu des DEUX traces : la clé racine
    laissée par `--installer` seul, et le drapeau par outil de l'écriture
    précédente. Sans la seconde, deux `--ecrire` successifs perdaient le lot 1."""
    vus = set(ancien.get("installe_par_cortex", []))
    return vus | {n for n, o in (ancien.get("outils") or {}).items()
                  if isinstance(o, dict) and o.get("installe_par_cortex")}


def options_choisies(texte):
    """La liste passée par --options, telle quelle ; vide sur « aucune ». Sans --options,
    ecrire() garde la liste déjà écrite."""
    noms = [n.strip() for n in texte.split(",") if n.strip()]
    return [] if noms == ["aucune"] else noms


def ecrire(a, systeme, etat):
    atelier = Path(a.atelier).expanduser()
    atelier.mkdir(parents=True, exist_ok=True)
    chemin = atelier / "poste.json"
    ancien = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
    par_cortex = deja_par_cortex(ancien) | set(a.installes)
    outils = {n: {"present": e["present"], "version": e["version"], "installe_par_cortex": n in par_cortex,
                  **({"raison": e["raison"]} if e.get("raison") else {})}
              for n, e in etat.items()}
    if etat["gh"]["present"]:
        connecte, raison = gh_connecte(etat["gh"].get("chemin") or "gh")
        outils["gh"]["connecte"] = connecte
        if raison:
            outils["gh"]["raison"] = raison
    maintenant = datetime.now().isoformat(timespec="seconds")
    slug = slug_de(a, atelier) or (ancien.get("organisation") or {}).get("code", "")
    poste = {"format": "cortex/poste", "version": 1, "genere_le": maintenant, "os": systeme,
             "organisation": {"code": slug},
             "outils": outils,
             "options_proposees": options_choisies(a.options) if a.options
             else ancien.get("options_proposees", []),
             "mail": bloc_mail(a, ancien.get("mail")), "notice_ouverte_le": maintenant}
    chemin.write_text(json.dumps(poste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    config = atelier / "config.yaml"
    if slug:
        fusionner_bloc(config, "organisation", {"code": slug})
    fusionner_bloc(config, "poste", paires_poste(poste))
    print(f"OK — {chemin} et bloc poste de config.yaml écrits ; voie mail : {poste['mail']['voie']}")
    if poste["mail"]["voie"] in VOIES_QUI_INSTALLENT and not etat["node"]["present"]:
        print(f"node : absent → {OUTILS['node']['install'][systeme]} (requis par la voie {poste['mail']['voie']})")
    c4 = _cortex4()
    if c4 is None:
        print("[poste] notice.py introuvable : la notice se régénère au maillon suivant")
        return 0
    sys.stdout.flush()
    cmd = [sys.executable, str(c4 / "notice.py"), "--atelier", str(atelier)] + (["--no-open"] if a.no_open else [])
    return subprocess.run(cmd).returncode


def _autotest():
    mac = "gmail.com\tmail exchanger = 10 alt1.gmail-smtp-in.l.google.com.\n"
    win = "gmail.com\tMX preference = 5, mail exchanger = gmail-smtp-in.l.google.com\n"
    assert lire_mx(mac) == ["alt1.gmail-smtp-in.l.google.com"]
    assert lire_mx(win) == ["gmail-smtp-in.l.google.com"]
    assert fournisseur("exemple.test", ["aspmx.l.google.com"]) == "gmail"
    assert fournisseur("acme.fr", ["acme-fr.mail.protection.outlook.com"]) == "m365"
    assert fournisseur("hotmail.fr", ["hotmail-fr.olc.protection.outlook.com"]) == "outlook_perso"
    assert fournisseur("outlook.com", ["outlook-com.olc.protection.outlook.com"]) == "outlook_perso"
    assert fournisseur("ovh.test", ["mx1.mail.ovh.net"]) == ""
    assert voie("gmail", 1) == "connecteur" and voie("gmail", 2) == "mcp-email"
    assert voie("m365", admin=True) == "connecteur" and voie("m365") == "softeria"
    assert voie("outlook_perso") == "softeria"
    assert voie("", imap=True) == "mcp-email" and voie("") == "aucune"
    assert options_choisies("") == [] and options_choisies("aucune") == []
    assert options_choisies("wispr-flow, noota") == ["wispr-flow", "noota"]
    etat = {n: {"present": n in ("git", "uv"), "version": ""} for n in OUTILS}
    lignes = lignes_dry_run(etat, "macos")
    assert len(lignes) == 6 and lignes[0] == "obsidian : absent → brew install --cask obsidian"
    assert lignes[-1] == 'graphify : absent → uv tool install "graphifyy[pdf,office]"'
    assert lignes[1] == 'markitdown : absent → uv tool install "markitdown[all]"'
    assert OUTILS["markitdown"]["uvx"] == ["--from", "markitdown[all]", "markitdown"]
    assert all(" : absent → " in l for l in lignes_dry_run(etat, "windows"))
    # H2 défaut 7 : un outil non mesurable se dit « à vérifier », jamais une installation.
    etat["markitdown"] = {"present": None, "version": "", "raison": "sonde uvx en échec : cache refusé"}
    lignes = lignes_dry_run(etat, "macos")
    assert "markitdown : à vérifier (sonde uvx en échec : cache refusé)" in lignes, lignes
    assert not any(l.startswith("markitdown : absent") for l in lignes)
    if os.name != "nt":                      # faux exécutables en shell : hors Windows
        with tempfile.TemporaryDirectory() as tmp:
            def faux(nom, corps):
                f = Path(tmp) / nom
                f.write_text("#!/bin/sh\n" + corps + "\n", encoding="utf-8")
                f.chmod(0o755)
                return str(f)
            faux("cortex-outil-temoin", "exit 0")
            assert trouver("cortex-outil-temoin", Path(tmp)), "dossier des outils de uv non lu"
            assert not trouver("cortex-outil-temoin", Path(tmp) / "vide")
            assert _uvx(["x"], None) == {"present": False, "version": ""}
            refus = _uvx(["x"], faux("uvx-refus", "echo \"error: Failed to initialize cache\" >&2\n"
                                                  "echo \"  Caused by: Permission denied (os error 13)\" >&2; exit 2"))
            assert refus["present"] is None and "Permission denied" in refus["raison"], refus
            assert _uvx(["x"], faux("uvx-ok", "echo markitdown 0.1.7")) == {"present": True, "version": "0.1.7"}
            assert gh_connecte(faux("gh-ok", "exit 0")) == (True, "")
            assert gh_connecte(faux("gh-non", "echo 'You are not logged into any GitHub hosts.' >&2; exit 1")) \
                == (False, "")
            illisible = gh_connecte(faux("gh-trousseau", "echo '- The token in keyring is invalid.' >&2; exit 1"))
            assert illisible[0] is None and "illisible" in illisible[1], illisible
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "config.yaml"
        config.write_text("version: 1\nprofil: employe\nposte:\n  os: linux\n  outils: []\n\nmode: solo\n",
                          encoding="utf-8")
        poste = {"os": "macos", "outils": {n: {"present": n in ("git", "uv")} for n in KIT},
                 "mail": {"fournisseur": "gmail", "boites": 1, "voie": "connecteur"}}
        texte = fusionner_bloc(config, "poste", paires_poste(poste))
        assert texte.count("poste:") == 1 and "os: macos" in texte and "mode: solo" in texte
        # Défaut 14 : le slug arrive dans organisation.code, et la fusion garde `nom`.
        fusionner_bloc(config, "organisation", {"nom": '"Acme"'})
        texte = fusionner_bloc(config, "organisation", {"code": "acme"})
        assert texte.count("organisation:") == 1 and "nom:" in texte and "code: acme" in texte
        sys.path.insert(0, str(_ICI.parent.parent / "cortex-4-installation" / "scripts"))
        import cortex_config
        conf = cortex_config.charger(config)
        # Défaut 13 : le bloc liste TOUT le kit, pas les seuls présents.
        assert conf["poste"]["outils"] == KIT, conf["poste"]["outils"]
        assert conf["poste"]["mail_voie"] == "connecteur" and conf["profil"] == "employe"
        assert conf["organisation"]["code"] == "acme" and conf["organisation"]["nom"] == "Acme"

    # Défaut 2 : deux --ecrire successifs conservent installe_par_cortex du lot 1.
    with tempfile.TemporaryDirectory() as tmp:
        atelier = Path(tmp) / "Cortex" / "acme" / "_cortex"
        faux = {n: {"present": n in ("git", "gh"), "version": ""} for n in OUTILS}
        faux["gh"]["present"] = False            # pas d'appel réseau à `gh auth status`
        def args(installes, fournisseur="gmail", voie=""):
            return argparse.Namespace(atelier=str(atelier), installes=installes, options="",
                                      mail="jane@exemple.test", boites=1, admin=False, imap=False,
                                      fournisseur=fournisseur, voie=voie, no_open=True, slug="")
        assert ecrire(args(["git"]), "macos", faux) == 0
        assert ecrire(args(["uv"]), "macos", faux) == 0
        poste = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))
        par_cortex = sorted(n for n, o in poste["outils"].items() if o["installe_par_cortex"])
        assert par_cortex == ["git", "uv"], par_cortex
        assert poste["options_proposees"] == []        # H2 : sans --options, aucune option inventée
        assert poste["organisation"]["code"] == "acme"        # slug déduit du chemin
        assert poste["notice_ouverte_le"]
        conf = cortex_config.charger(atelier / "config.yaml")
        assert conf["organisation"]["code"] == "acme" and conf["poste"]["outils"] == KIT
        # H2 défaut 6 : Microsoft non administrateur, sans réponse de la personne, rien ne
        # s'écrit qui installe ; la voie calculée reste proposée. Sa réponse, elle, s'écrit.
        assert ecrire(args([], "m365"), "macos", faux) == 0
        mail = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))["mail"]
        assert mail["voie"] == "aucune" and mail["voie_proposee"] == "softeria", mail
        assert cortex_config.charger(atelier / "config.yaml")["poste"]["mail_voie"] == "aucune"
        assert ecrire(args([], "m365", "softeria"), "macos", faux) == 0
        mail = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))["mail"]
        assert mail["voie"] == "softeria" and mail["voie_proposee"] == "softeria", mail
        # Reprise m5 : un second --ecrire sans --voie ni --options garde la réponse acquise.
        a = args([], "m365")
        a.options = "noota"
        assert ecrire(a, "macos", faux) == 0
        assert ecrire(args([], "m365"), "macos", faux) == 0
        poste = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))
        assert poste["mail"]["voie"] == "softeria" and poste["options_proposees"] == ["noota"], poste
        assert cortex_config.charger(atelier / "config.yaml")["poste"]["mail_voie"] == "softeria"
        a = args([], "")
        a.mail = ""
        assert ecrire(a, "macos", faux) == 0                            # sans --mail : bloc gardé
        assert json.loads((atelier / "poste.json").read_text(encoding="utf-8"))["mail"]["voie"] == "softeria"
        a = args([], "m365", "aucune")
        a.options = "aucune"
        assert ecrire(a, "macos", faux) == 0                            # une réponse neuve l'emporte
        poste = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))
        assert poste["mail"]["voie"] == "aucune" and poste["options_proposees"] == [], poste
        assert ecrire(args([], "gmail"), "macos", faux) == 0          # connecteur : rien à installer
        assert json.loads((atelier / "poste.json").read_text(encoding="utf-8"))["mail"]["voie"] == "connecteur"
    print("poste.py : auto-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description="Équipe le poste pour un second cerveau, sur accord.")
    p.add_argument("--dry-run", action="store_true", help="lister les outils du kit absents, sans rien installer")
    p.add_argument("--installer", default="", help="outils à installer, séparés par des virgules (accord acquis)")
    p.add_argument("--mail", default="", help="adresse utilisée pour le travail")
    p.add_argument("--boites", type=int, default=1, help="nombre de boîtes à brancher")
    p.add_argument("--admin", action="store_true", help="Microsoft 365 avec droits d'administration")
    p.add_argument("--imap", action="store_true", help="fournisseur autre, accès IMAP disponible")
    p.add_argument("--fournisseur", default="", choices=["", "gmail", "m365", "outlook_perso", "autre"],
                   help="réponse à la question à trois options quand le MX ne suffit pas")
    p.add_argument("--voie", default="", choices=["", "connecteur", "softeria", "mcp-email", "imap", "aucune"],
                   help="voie mail acceptée par la personne ; sans elle, la réponse déjà écrite pour la même "
                        "proposition reste, sinon softeria et mcp-email s'écrivent « aucune »")
    p.add_argument("--options", default="", help="options retenues par la personne, séparées par des virgules ; « aucune » : liste vide ; "
                   "sans --options : la liste déjà écrite reste")
    p.add_argument("--ecrire", action="store_true", help="écrire poste.json et le bloc poste, ouvrir la notice")
    p.add_argument("--atelier", default="", help="chemin du dossier _cortex/")
    p.add_argument("--slug", default="", help="nom court du second cerveau (organisation.code) ; "
                                              "déduit du chemin de l'atelier s'il manque")
    p.add_argument("--no-open", action="store_true", help="ne pas ouvrir la notice (recette)")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    systeme = os_courant()
    a.installes = []
    if a.dry_run:
        if systeme == "macos" and not shutil.which("brew"):
            print("[prérequis] Homebrew absent → /bin/bash -c \"$(curl -fsSL "
                  "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", file=sys.stderr)
        for l in lignes_dry_run(detecter(systeme), systeme):
            print(l)
        return 0
    if a.installer:
        a.installes = installer([n.strip() for n in a.installer.split(",") if n.strip()], systeme)
        if a.atelier and not a.ecrire:
            atelier = Path(a.atelier).expanduser()
            atelier.mkdir(parents=True, exist_ok=True)
            chemin = atelier / "poste.json"
            memo = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
            memo["installe_par_cortex"] = sorted(set(memo.get("installe_par_cortex", [])) | set(a.installes))
            chemin.write_text(json.dumps(memo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if a.mail and not a.ecrire:
        m = bloc_mail(a)
        print(json.dumps(m, ensure_ascii=False))
        if not m["fournisseur"]:
            print("Fournisseur non reconnu : demander « votre messagerie est-elle Google, Microsoft, ou autre ? » "
                  "puis relancer avec --fournisseur gmail|m365|autre [--imap]")
    if a.ecrire:
        if not a.atelier:
            p.error("--ecrire exige --atelier")
        return ecrire(a, systeme, detecter(systeme))
    if not (a.installer or a.mail):
        p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
