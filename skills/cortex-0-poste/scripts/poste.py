#!/usr/bin/env python3
"""poste.py — équipe le poste pour un second cerveau. stdlib pure, jamais sans accord.

Quatre gestes, tous explicites :
  --dry-run                    une ligne par outil du kit absent, avec la commande de l'OS courant
  --installer a,b              installe CES outils, et seulement ceux-là (l'accord a été donné avant)
  --mail adresse [...]         reconnaît le fournisseur (MX) et propose la voie de branchement
  --ecrire --atelier <_cortex> écrit _cortex/poste.json et le bloc `poste` de config.yaml, puis
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
KIT = ["obsidian", "uv", "markitdown", "git", "gh", "github-desktop", "buzz"]
OPTIONS = ["wispr-flow", "superwhisper", "noota", "graphify"]

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
    "node": {"cmd": "node", "install": {"macos": "brew install node",
                                         "windows": "winget install --id OpenJS.NodeJS.LTS -e",
                                         "linux": "sudo apt-get install -y nodejs"}},
}


def os_courant():
    return {"Darwin": "macos", "Windows": "windows"}.get(platform.system(), "linux")


def _version(cmd):
    try:
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=10)
        m = re.search(r"\d+(\.\d+)+", r.stdout + r.stderr)
        return m.group(0) if m else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _uvx(args):
    """Sonde un outil servi par uvx : `uvx --from "paquet[extra]" outil --version`."""
    if not shutil.which("uvx"):
        return {"present": False, "version": ""}
    try:
        r = subprocess.run(["uvx", *args, "--version"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return {"present": False, "version": ""}
    m = re.search(r"\d+(\.\d+)+", r.stdout + r.stderr)
    return {"present": r.returncode == 0, "version": m.group(0) if m and r.returncode == 0 else ""}


def _app(nom, systeme):
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
    return bool(shutil.which(nom)), _version(nom) if shutil.which(nom) else ""


def detecter(systeme=None):
    """Mesure chaque outil. Rend {nom: {present, version}}. Ne modifie rien."""
    systeme = systeme or os_courant()
    etat = {}
    for nom, o in OUTILS.items():
        if "uvx" in o:
            etat[nom] = _uvx(o["uvx"])
        elif "cmd" in o:
            present = bool(shutil.which(o["cmd"]))
            etat[nom] = {"present": present, "version": _version(o["cmd"]) if present else ""}
        else:
            present, version = _app(o["app"].get(systeme, ""), systeme)
            etat[nom] = {"present": present, "version": version}
    return etat


def gh_connecte():
    try:
        return subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=15).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def lignes_dry_run(etat, systeme):
    return [f"{nom} : absent → {OUTILS[nom]['install'][systeme]}"
            for nom in KIT if not etat[nom]["present"]]


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


def bloc_mail(a):
    domaine = a.mail.rsplit("@", 1)[-1].strip().lower() if a.mail else ""
    hotes = mx(domaine) if domaine and not a.fournisseur else []
    four = a.fournisseur or (fournisseur(domaine, hotes) if domaine else "")
    return {"fournisseur": four, "boites": a.boites, "voie": voie(four, a.boites, a.admin, a.imap),
            "domaine": domaine, "mx": hotes[0] if hotes else ""}


# ── Écriture ────────────────────────────────────────────────────────────────

def bloc_poste_yaml(poste):
    presents = [n for n in KIT if poste["outils"][n]["present"]]
    return ("poste:\n"
            f"  os: {poste['os']}\n"
            f"  outils: [{', '.join(presents)}]\n"
            f"  mail_fournisseur: {poste['mail']['fournisseur'] or '\"\"'}\n"
            f"  mail_boites: {poste['mail']['boites']}\n"
            f"  mail_voie: {poste['mail']['voie']}\n")


def ecrire_bloc_poste(config, bloc):
    """Remplace ou ajoute le bloc `poste` de config.yaml. Crée le fichier s'il manque."""
    texte = config.read_text(encoding="utf-8") if config.is_file() else "version: 1\n"
    lignes, garde, dans_poste = texte.splitlines(), [], False
    for l in lignes:
        if re.match(r"^poste:\s*(#.*)?$", l):
            dans_poste = True
            continue
        if dans_poste and l.strip() and not l.startswith((" ", "\t")):
            dans_poste = False
        if not dans_poste:
            garde.append(l)
    texte = "\n".join(garde).rstrip("\n") + "\n\n" + bloc
    config.write_text(texte, encoding="utf-8")
    return texte


def _cortex4():
    for cand in (_ICI, _ICI.parent.parent / "cortex-4-installation" / "scripts"):
        if (cand / "notice.py").is_file():
            return cand
    return None


def ecrire(a, systeme, etat):
    atelier = Path(a.atelier).expanduser()
    atelier.mkdir(parents=True, exist_ok=True)
    chemin = atelier / "poste.json"
    ancien = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
    par_cortex = set(ancien.get("installe_par_cortex", [])) | set(a.installes)
    outils = {n: {"present": e["present"], "version": e["version"], "installe_par_cortex": n in par_cortex}
              for n, e in etat.items()}
    if etat["gh"]["present"]:
        outils["gh"]["connecte"] = gh_connecte()
    maintenant = datetime.now().isoformat(timespec="seconds")
    poste = {"format": "cortex/poste", "version": 1, "genere_le": maintenant, "os": systeme,
             "outils": outils, "options_proposees": a.options.split(",") if a.options else OPTIONS,
             "mail": bloc_mail(a), "notice_ouverte_le": maintenant}
    chemin.write_text(json.dumps(poste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ecrire_bloc_poste(atelier / "config.yaml", bloc_poste_yaml(poste))
    print(f"OK — {chemin} et bloc poste de config.yaml écrits ; voie mail : {poste['mail']['voie']}")
    if poste["mail"]["voie"] in ("softeria", "mcp-email") and not etat["node"]["present"]:
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
    etat = {n: {"present": n in ("git", "uv"), "version": ""} for n in OUTILS}
    lignes = lignes_dry_run(etat, "macos")
    assert len(lignes) == 5 and lignes[0] == "obsidian : absent → brew install --cask obsidian"
    assert lignes[1] == 'markitdown : absent → uv tool install "markitdown[all]"'
    assert OUTILS["markitdown"]["uvx"] == ["--from", "markitdown[all]", "markitdown"]
    assert all(" : absent → " in l for l in lignes_dry_run(etat, "windows"))
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "config.yaml"
        config.write_text("version: 1\nprofil: employe\nposte:\n  os: linux\n  outils: []\n\nmode: solo\n",
                          encoding="utf-8")
        poste = {"os": "macos", "outils": {n: {"present": n in ("git", "uv")} for n in KIT},
                 "mail": {"fournisseur": "gmail", "boites": 1, "voie": "connecteur"}}
        texte = ecrire_bloc_poste(config, bloc_poste_yaml(poste))
        assert texte.count("poste:") == 1 and "os: macos" in texte and "mode: solo" in texte
        sys.path.insert(0, str(_ICI.parent.parent / "cortex-4-installation" / "scripts"))
        import cortex_config
        conf = cortex_config.charger(config)
        assert conf["poste"]["outils"] == ["uv", "git"] and conf["poste"]["mail_voie"] == "connecteur"
        assert conf["profil"] == "employe"
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
    p.add_argument("--options", default="", help="options proposées, séparées par des virgules")
    p.add_argument("--ecrire", action="store_true", help="écrire poste.json et le bloc poste, ouvrir la notice")
    p.add_argument("--atelier", default="", help="chemin du dossier _cortex/")
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
