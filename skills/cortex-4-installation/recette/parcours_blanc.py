#!/usr/bin/env python3
"""Recette de non-regression de la chaine Cortex, v2 (lane G, 2026-09-19).

Sections 1 a 9 : la recette v1 (parcours a blanc du 2026-08-17, phase 5 du
2026-08-23), conservee telle quelle. Chaque assertion y correspond a un defaut
REEL deja paye.

Criteres C1 a C10 : la cible v2 (chantiers/cortex-v2/04-contrat.md) ; C11 : le rangement 2.3. Chaque
controle cite la section du contrat qu'il verifie et porte son defaut PLAUSIBLE.
Tant que les lanes B a F ne sont pas mergees, ces criteres sont rouges : c'est
attendu, la recette est la cible, pas le constat. Un script d'une lane absente
se signale par une ligne « attendu au merge de la lane X ».

Trois controles restent manuels et vivent dans 06-verification.md : l'installation
vivante du plugin, la sonde Cowork bureau, le maillon 0 sur la machine Windows.

    python3 recette/parcours_blanc.py        # sortie 0 = recette verte
    (`py` vaut `python3` sous Windows)

Stdlib seule, aucun reseau. Ecrit dans un dossier temporaire et dans
recette/fixtures/ (ignore par git), rien d'autre.
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import zipfile
from pathlib import Path

RECETTE = Path(__file__).resolve().parent
RACINE = RECETTE.parent                       # skills/cortex-4-installation
SCRIPTS = RACINE / "scripts"
DEPOT = RACINE.parent.parent
SKILLS = DEPOT / "skills"
PAQUET = DEPOT / "fabricant"
FIXTURES = RECETTE / "fixtures"
ATELIER_RECETTE = FIXTURES / "_recette"       # sous ~ : les chemins en forme ~ y sont possibles
# Le depot peut etre clone hors du dossier personnel (CI, dossier temporaire) :
# `scan.py` ecrit alors des chemins absolus, legitimes (§4, amendement).
SOUS_HOME = FIXTURES.is_relative_to(Path.home())
POSTE = SKILLS / "cortex-0-poste" / "scripts" / "poste.py"
SCAN = SKILLS / "cortex-2-inventaire" / "scripts" / "scan.py"
FEDERE = SKILLS / "cortex-8-federation" / "scripts" / "federe.py"
RANGE = SKILLS / "cortex-3b-rangement" / "scripts" / "range.py"
COPIE = SKILLS / "cortex-5-ingest" / "scripts" / "copie_structurant.py"
GABARIT = RACINE / "template" / "vault"

sys.path.insert(0, str(SCRIPTS))
import cortex_config  # noqa: E402
import etat as m_etat  # noqa: E402
import rend_notice as m_rend  # noqa: E402
sys.path.insert(0, str(RECETTE))
import fixtures as m_fixtures  # noqa: E402
sys.path.insert(0, str(PAQUET / "scripts"))
import fabrique as m_fabrique  # noqa: E402

MARQUES = ["Cabinet-Exemple", "ClientAnterieurA", "ClientAnterieurB"]
# Marques interdites (01-cadrage.md §Marques interdites) : sha256 tronque de la
# forme normalisee (minuscules, sans accent, mots separes par une espace). Le
# depot est public : la liste en clair y serait elle-meme la fuite. La liste en
# clair vit chez le chef d'orchestre ; recalculer une empreinte :
#   python3 -c "import hashlib;print(hashlib.sha256(b'mot').hexdigest()[:16])"
MARQUES_EMPREINTES = {
    "2d697f1957a17471", "1e194652dcdd105b", "4025a3e9f03aa9b1", "6cd31a74b6e31ff0",
    "f597568fba670b35", "06349320320a2272", "be428d22548ae2ea", "e3dfc76ed288d592",
    "4cbe19716b1aa73a", "35f85825b9016fcc", "93a8567601604723", "2be94190c1fc7991",
}
PERIMETRE_WHITE_LABEL = [SKILLS, DEPOT / "notice", DEPOT / "outils", DEPOT / "README.md"]
# Une ligne qui DEFINIT le motif « chemin absolu » (regex Python, chaine brute,
# commande grep de la passation) n'est pas un chemin de machine : sans cette
# exclusion, le controle C9 se mord la queue sur parcours_blanc.py, lint_sante.py
# et cortex-7-passation/SKILL.md. Les fragments entre backticks sont retires de
# la ligne avant la recherche, pour la meme raison.
MOTIF_DE_DETECTION = re.compile(r"""re\.(compile|search|match|findall|finditer|sub)\s*\(|(?<![A-Za-z0-9_])r["']|\bgrep\b""")
# H2 lane C : le harnais de Claude Code laisse `<dossier>/.claude/.cc-writes`
# dans tout dossier où une commande entre par `cd`. Aucun SKILL.md ne prescrit
# donc un `cd` vers un chemin (racine, `~`, variable, gabarit `<…>`).
CD_VERS_UN_CHEMIN = re.compile(r"""(?:^|[\s;&|(`])cd\s+["']?(?:~|\$|<|/|\.\.)""")
# H2 lane C, Q-vocab : la mécanique de la chaîne dans un récapitulatif de fin
# (« Fais tourner `cloture` », « le scaffold », « le contrôle est marqué arbitré »).
MOTS_DE_LA_CHAINE = re.compile(r"`[^`\n]+`|\.py\b|cortex-\d|\bmaillons?\b|\bscaffold|\bskills?\b"
                               r"|\b(?:contrôles?|marqués?)\s+arbitrés?|\bconsultant|\bsolo\b|\bfédéré"
                               r"|\brégime\b|\bpointeur|\bécarts?\b|\bprofil\b", re.I)
BINAIRES = {".zip", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".xlsx", ".pyc", ".woff", ".woff2", ".ttf"}
PROFILS = ("employe", "dirigeant", "societe")
ETAPES_CONTRAT = {0: "poste.json", 1: "00-cadrage.md", 2: "01-inventaire.md", 3: "02-ontologie.md",
                  "3b": "03-rangement.md", 4: None, 5: "04-ingest.md", 6: "05-agents-metier.md", 7: "06-passation.md",
                  8: "07-federation.md"}
CRITERES = [
    ("C1", "Dix étapes, maillon 0, notice", "§3 §5 §10", "B"),
    ("C2", "Trois profils, régime, section Notice", "§2 §10", "C"),
    ("C3", "Inventaire outillé sur les fixtures", "§4", "D"),
    ("C4", "Couche vault : permissions, hooks, skills, agents", "§9", "E"),
    ("C5", "Régimes pointeur et copie, structurant périmé", "§2", "E"),
    ("C6", "Fédération sur trois exports fictifs", "§6", "F"),
    ("C7", "Manifestes plugin", "§11", "chef"),
    ("C8", "White-label", "01-cadrage", "toutes"),
    ("C9", "Zéro chemin absolu", "I2, §11", "toutes"),
    ("C10", "Paquet, notice hors ligne, README", "§11", "B"),
    ("C11", "Rangement, dossier commun, procédures", "2.3 §1-§8", "rangement"),
]
MANUELS = [("M1", "Installation vivante du plugin (marketplace add, install, details)"),
           ("M2", "Sonde Cowork bureau : uvx --from \"markitdown[all]\" markitdown --version dans le bac à sable"),
           ("M3", "Maillon 0 et installation du plugin sur la machine Windows"),
           ("M4", "Permissions du vault en session interactive (allow, additionalDirectories, deny)")]

succes, echecs = [], []
BILAN = {}
CRITERE = "v1"


def verifie(nom, condition, detail=""):
    (succes if condition else echecs).append(f"{CRITERE} {nom}")
    BILAN.setdefault(CRITERE, [0, 0])[0 if condition else 1] += 1
    print(f"  [{'ok' if condition else 'XX'}] {nom}" + (f" : {detail}" if detail and not condition else ""))


def section(critere, titre):
    global CRITERE
    CRITERE = critere
    print(f"\n{critere}. {titre}")


def lancer(script, *args, timeout=120):
    return subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, timeout=timeout)


def scaffold(*args):
    return lancer(SCRIPTS / "scaffold.py", *args)


def lint(vault, *args):
    return lancer(SCRIPTS / "lint_sante.py", "--vault", str(vault), *args)


def tilde(chemin):
    """Forme ~ d'un chemin sous le dossier personnel, sinon le chemin tel quel."""
    try:
        return "~/" + Path(chemin).resolve().relative_to(Path.home()).as_posix()
    except ValueError:
        return str(chemin)


def sha256(chemin):
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


def frontmatter(texte):
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        return None
    fin = next((i for i, l in enumerate(lignes[1:], 1) if l.strip() == "---"), None)
    if fin is None:
        return None
    return {l.split(":", 1)[0].strip(): l.split(":", 1)[1].strip()
            for l in lignes[1:fin] if ":" in l}


def blocs_recapitulatif(texte):
    """Les blocs de code des sections « Message de clôture » et « Récap » : le
    texte que la personne lit en fin d'étape, mot pour mot."""
    blocs = []
    for section_ in re.split(r"^(?=## )", texte, flags=re.M):
        if re.match(r"## .*(Message de clôture|Récap)", section_):
            blocs += re.findall(r"^```[a-z]*\n(.*?)^```", section_, re.M | re.S)
    return blocs


def vocabulaire_des_recaps(texte):
    return [m.group(0) for b in blocs_recapitulatif(texte) for m in MOTS_DE_LA_CHAINE.finditer(b)]


def fichiers_texte(perimetre):
    for base in perimetre:
        cibles = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.is_file())
        for p in cibles:
            rel = p.relative_to(DEPOT).as_posix()
            if "__pycache__" in rel or rel.startswith("skills/cortex-4-installation/recette/fixtures/") \
                    or p.suffix.lower() in BINAIRES or p.name == ".DS_Store":
                continue
            yield p, rel


def cles_recursives(obj, acc=None):
    acc = set() if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(k)
            cles_recursives(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            cles_recursives(v, acc)
    return acc


# ── Configs ─────────────────────────────────────────────────────────────────

CONFIG = """version: 1
organisation:
  nom: "Ateliers Roumier"
  code: roumier
  redacteur: "Camille Roumier"
  courriel: "c.roumier@exemple.test"
mode: solo
commun:
  racine: ""
chemins:
  dossiers_projets: "~/Documents/Affaires"
marque:
  produit_nom: "Cortex"
  mentions_interdites: [{marques}]
{domaines}
cycles:
  - {{ cycle: affaire, phase: "Devis envoyé",   progression: 10 }}
  - {{ cycle: affaire, phase: "Signé",          progression: 30 }}
  - {{ cycle: affaire, phase: "En fabrication", progression: 60 }}
  - {{ cycle: affaire, phase: "Réceptionné",    progression: 100 }}
sante:
  max_lignes_entree_journal: 10
  max_lignes_journal: 60
  journal_perime_jours: 14
  pointeur_canonique_obligatoire: true
  interdire_orphelins: true
  agent_metier_revue_mois: 6
agents:
  skills: [cloture, nouveau-projet, ingest, lint]
  sousagents: [chercheur-vault, auditeur-ontologie]
  metier: []
  hooks: []
vehicules: []
payeurs: []
substrats:
  espace_documentaire: "//srv-roumier/Espace documentaire"
  base_projets: "https://base.exemple.test/affaires"
  git_remote: ""
collecte:
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  plafond_projets: 60
  plafond_acteurs: 80
  plafond_domaines: 6
"""

DOMAINES_OK = """domaines:
  - { code: mag, nom: "Agencement magasin",   couleur: "#1c42da" }
  - { code: bur, nom: "Aménagement bureau",   couleur: "#0f8a6a" }"""
DOMAINES_VIDE = "domaines: []"


def config_v2(profil, regime, racines, mode="solo", commun_racine="", code="roumier",
              nom="Ateliers Roumier", redacteur="Camille Roumier", base_projets=""):
    """Une config.yaml complete selon 04-contrat.md §2, telle que le maillon 1 l'ecrit."""
    liste_racines = ", ".join(f'"{r}"' for r in racines)
    return f"""version: 1
conduite: solo
profil: {profil}
organisation:
  nom: "{nom}"
  code: {code}
  redacteur: "{redacteur}"
  courriel: "{code}@exemple.test"
mode: {mode}
commun:
  racine: "{commun_racine}"
  export: "_export"
  visibilite_defaut: prive
chemins:
  dossiers_projets: "~/Documents/Affaires"
donnees:
  regime: {regime}
  structurants: [organigramme, fiche_de_poste, contrat, projet, acteur, tenants_aboutissants, fil_structurant]
marque:
  produit_nom: "Cortex"
  mentions_interdites: [{", ".join(MARQUES)}]
{DOMAINES_OK}
cycles:
  - {{ cycle: affaire, phase: "Devis envoyé",   progression: 10 }}
  - {{ cycle: affaire, phase: "Signé",          progression: 30 }}
  - {{ cycle: affaire, phase: "En fabrication", progression: 60 }}
  - {{ cycle: affaire, phase: "Réceptionné",    progression: 100 }}
sante:
  max_lignes_entree_journal: 10
  max_lignes_journal: 60
  journal_perime_jours: 14
  pointeur_canonique_obligatoire: true
  interdire_orphelins: true
  agent_metier_revue_mois: 6
  max_notes_parle: 12
  max_structurants: 40
  jours_sans_cloture_alerte: 7
agents:
  skills: [cloture, nouveau-projet, ingest, lint, parle, bilan, agenda, miroir]
  sousagents: [chercheur-vault, auditeur-ontologie]
  metier: []
  hooks: [session-start, stop]
vehicules: []
payeurs: []
substrats:
  espace_documentaire: ""
  base_projets: "{base_projets}"
  git_remote: ""
collecte:
  racines: [{liste_racines}]
  profondeur_arbre: 3
  max_dossiers: 200
  mail_mois: 12
  mail_optin: false
  plafond_projets: 60
  plafond_acteurs: 80
  plafond_domaines: 6
poste:
  os: macos
  outils: [obsidian, uv, markitdown, git, gh, github-desktop, buzz]
  mail_fournisseur: gmail
  mail_boites: 1
  mail_voie: connecteur
"""


AFFAIRES = [("2026-001 Siege Malbrun", "mag", "Agencement magasin", "Signé", 30),
            ("2026-006 Bureaux Kervran", "bur", "Aménagement bureau", "En fabrication", 60),
            ("2025-002 Hotel Vinci", "mag", "Agencement magasin", "Réceptionné", 100)]


def note_projet(titre, code, dom, phase, prog):
    fini = prog == 100
    return f"""---
type: projet
domaine: "[[{dom}]]"
statut: {'termine' if fini else 'actif'}
cycle: affaire
facturable: true
phase: "{phase}"
progression: {prog}
priorite: P2
dossier_local: "{titre}"
substrat_canonique: "base Affaires"
url_canonique: "https://base.exemple.test/affaires/{titre.split()[0]}"
dernier_journal: 2026-08-17
blocages_actifs: 0
tags:
  - d/{code}
---
# {code.upper()} - {titre}

Domaine : [[{dom}]]

## Journal

### 2026-08-17

Fiche creee a l'installation. Les montants restent dans la base.

## Pointeurs

- Substrat canonique : base « Affaires »

<!-- cortex-5-ingest: affaire:{titre} 2026-08-17 -->
"""


def poste_json(notice_ouverte=True):
    p = {"format": "cortex/poste", "version": 1, "genere_le": "2026-09-19T10:12:00", "os": "macos",
         "outils": {o: {"present": True, "version": "1", "installe_par_cortex": False}
                    for o in ("obsidian", "uv", "markitdown", "git", "gh")},
         "options_proposees": [],
         "mail": {"fournisseur": "gmail", "boites": 1, "voie": "connecteur",
                  "domaine": "exemple.test", "mx": "aspmx.l.google.com"},
         "notice_ouverte_le": "2026-09-19T10:12:03" if notice_ouverte else ""}
    return json.dumps(p, ensure_ascii=False, indent=2)


RANGEMENT_APPLIQUE = "---\nmaillon: 3b\nstatut: applique\nacceptees: []\n---\n# x\n"
FM_ATELIER = ("---\nmaillon: {m}\nproduit_par: {p}\nstatut: {s}\ncontroles:\n"
              "  premier_controle: passe\n  second_controle: {v}\n---\n# x\n")
ARTEFACTS_MD = (("00-cadrage", 1, "cortex-1-cadrage"), ("01-inventaire", 2, "cortex-2-inventaire"),
                ("02-ontologie", 3, "cortex-3-ontologie"), ("04-ingest", 5, "cortex-5-ingest"),
                ("05-agents-metier", 6, "cortex-6-agents-metier"), ("06-passation", 7, "cortex-7-passation"),
                ("07-federation", 8, "cortex-8-federation"))


def note_export(chemin, titre, type_, slug, visibilite="commun", extra=""):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(f"---\ntype: {type_}\nvisibilite: {visibilite}\nsource_vault: {slug}\n"
                      f"exporte_le: 2026-09-19\n{extra}---\n# {titre}\n\nNote fictive exportée.\n",
                      encoding="utf-8")
    return chemin


def export_fictif(racine_vaults, slug, affaires):
    """Un _export/<slug>/ selon 04-contrat.md §6, depuis les noms des fixtures societe/."""
    exp = racine_vaults / slug / "_export" / slug
    shutil.rmtree(exp, ignore_errors=True)
    notes = [note_export(exp / "10 - Domaines" / "Agencement magasin.md", "Agencement magasin", "domaine", slug)]
    for i, nom in enumerate(affaires):
        notes.append(note_export(exp / "20 - Projets" / f"MAG - 2026-{i + 1:03d} {nom}.md",
                                 f"2026-{i + 1:03d} {nom}", "projet", slug,
                                 extra='domaine: "[[Agencement magasin]]"\n'))
        notes.append(note_export(exp / "40 - Acteurs" / f"{nom}.md", nom, "acteur", slug,
                                 extra="role: client\n"))
    notes.append(note_export(exp / "60 - Journal" / "2026-09-19.md", "2026-09-19", "journal", slug))
    ecrire_index(exp, slug)
    return exp


def ecrire_index(exp, slug):
    notes = [{"chemin": p.relative_to(exp).as_posix(), "hash": sha256(p)}
             for p in sorted(exp.rglob("*.md"))]
    (exp / "index.json").write_text(json.dumps(
        {"format": "cortex/export", "version": 1, "slug": slug, "exporte_le": "2026-09-19T18:00:00",
         "notes": notes}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_reel(racine_vaults, slug):
    """Un export écrit par le vrai export.py du gabarit, depuis des notes de vault.

    Défaut de Phase H : les exports fictifs ci-dessus sont fabriqués par la
    recette elle-même, et ne voyaient pas qu'export.py et federe.py hashaient
    deux contenus différents. Ce chemin-ci passe par la clôture réelle."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "export_cloture", GABARIT / ".claude" / "skills" / "cloture" / "export.py")
    m_export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m_export)
    v = racine_vaults / f"reel-{slug}"
    shutil.rmtree(v, ignore_errors=True)
    for rel, texte in (
            ("20 - Projets/OPE - Belvédère.md", "---\ntype: projet\nvisibilite: commun\n---\n# Belvédère\n"),
            ("40 - Acteurs/Direction commerciale.md", "---\ntype: acteur\nvisibilite: commun\n---\n# Direction commerciale\n"),
            ("40 - Acteurs/Banque.md", "---\ntype: acteur\nvisibilite: prive\n---\n# Banque\n")):
        (v / rel).parent.mkdir(parents=True, exist_ok=True)
        (v / rel).write_text(texte, encoding="utf-8")
    conf = {"mode": "federe", "organisation": {"code": slug},
            "commun": {"export": "_export", "visibilite_defaut": "prive"}}
    cible, _ = m_export.exporter(v, conf)
    return cible


def empreinte_commun(commun):
    """Contenu du commun, hors horodatages : ce qui doit etre identique d'une generation a l'autre."""
    out = {}
    for p in sorted(Path(commun).rglob("*")):
        if p.is_file():
            texte = p.read_text(encoding="utf-8", errors="replace")
            out[p.relative_to(commun).as_posix()] = "\n".join(
                l for l in texte.splitlines()
                if "genere_le" not in l and "généré par" not in l.lower())
    return out


# ── Recette v1 (sections 1 a 9), conservee ──────────────────────────────────

def recette_v1(tmp):
    cfg = tmp / "config.yaml"
    cfg.write_text(CONFIG.format(marques=", ".join(MARQUES), domaines=DOMAINES_OK), encoding="utf-8")
    vault = tmp / "vault"

    section("v1", "1. Config incomplete refusee (defaut : vault sans domaine valide partout)")
    vide = tmp / "config-vide.yaml"
    vide.write_text(CONFIG.format(marques="", domaines=DOMAINES_VIDE), encoding="utf-8")
    conf_vide = cortex_config.charger(vide)
    verifie("charger() accepte encore la config du maillon 1", cortex_config.charger(cfg) is not None)
    verifie("valider_installable() refuse domaines vide",
            any("domaines" in e for e in cortex_config.valider_installable(conf_vide)))
    r = scaffold("--config", str(vide), "--out", str(tmp / "refus"))
    verifie("scaffold refuse une config incomplete", r.returncode == 2, r.stderr[:200])

    section("v1", "2. Installation")
    r = scaffold("--config", str(cfg), "--out", str(vault))
    verifie("scaffold reussit", r.returncode == 0, r.stderr[:300])

    section("v1", "3. Fuite de white-label (defaut : mentions_interdites livree au client)")
    fuites = [str(p) for p in vault.rglob("*") if p.is_file() and any(
        m.lower() in p.read_text(encoding="utf-8", errors="replace").lower() for m in MARQUES)]
    verifie("aucune mention interdite dans le vault livre", not fuites, str(fuites[:3]))

    section("v1", "4. Liens morts (defaut : Centre.md pointait vers des notes inexistantes)")
    domaines = sorted(p.name for p in (vault / "10 - Domaines").glob("*.md") if p.name != "_README.md")
    verifie("une note par domaine est generee", len(domaines) == 2, str(domaines))
    verifie("lint vert sur vault neuf", lint(vault).returncode == 0)
    sonde = vault / "20 - Projets" / "MAG - Sonde.md"
    sonde.write_text(note_projet("Sonde", "mag", "Agencement magasin", "Signé", 30)
                     .replace("## Journal", "Voir [[Note Absente]].\n\n## Journal"), encoding="utf-8")
    verifie("le lint detecte un lien mort reel", lint(vault).returncode == 1)
    sonde.unlink()
    verifie("aucun faux positif sur la syntaxe citee entre backticks",
            lint(vault).returncode == 0, lint(vault).stdout[-400:])

    section("v1", "5. Vault peuple : ingest puis protections")
    for titre, code, dom, phase, prog in AFFAIRES:
        (vault / "20 - Projets" / f"{code.upper()} - {titre}.md").write_text(
            note_projet(titre, code, dom, phase, prog), encoding="utf-8")
    verifie("lint vert sur vault peuple", lint(vault).returncode == 0, lint(vault).stdout[-500:])

    section("v1", "6. rm -rf sur vault peuple (defaut : --force detruisait le travail client)")
    r = scaffold("--config", str(cfg), "--out", str(vault), "--force")
    verifie("--force refuse d'ecraser un vault peuple", r.returncode == 2)
    verifie("les notes du client sont intactes",
            len(list((vault / "20 - Projets").glob("*.md"))) == len(AFFAIRES) + 1)

    section("v1", "7. Mise a jour de l'outillage (defaut : aucun chemin vers les vaults livres)")
    embarque = vault / ".claude" / "skills" / "lint" / "lint_sante.py"
    embarque.write_text("# version perimee\n", encoding="utf-8")
    r = scaffold("--config", str(cfg), "--out", str(vault), "--outillage-seul")
    verifie("--outillage-seul reussit", r.returncode == 0, r.stderr[:200])
    verifie("le lint embarque est reactualise",
            embarque.read_text(encoding="utf-8") == (SCRIPTS / "lint_sante.py").read_text(encoding="utf-8"))
    verifie("le contenu du client a survecu",
            len(list((vault / "20 - Projets").glob("*.md"))) == len(AFFAIRES) + 1)

    section("v1", "8. Divers")
    restes = [str(p.relative_to(vault)) for p in vault.rglob("*.md") if "Templates" not in p.parts
              and any(c in p.read_text(encoding="utf-8", errors="replace") for c in cortex_config.CLES_SCAFFOLD)]
    verifie("aucune moustache de scaffold residuelle", not restes, str(restes[:3]))
    absolus = [str(p.relative_to(vault)) for p in vault.rglob("*.md")
               if "/Users/" in p.read_text(encoding="utf-8", errors="replace")]
    verifie("aucun chemin absolu dans les notes", not absolus, str(absolus[:3]))
    verifie("aucun plugin communautaire requis", not (vault / ".obsidian" / "community-plugins.json").exists())

    section("v1", "9. Conduite (defaut plausible : le mode solo reinterprete l'existant)")
    conf = cortex_config.charger(cfg)
    verifie("une config sans cle conduite s'installe en consultant",
            cortex_config.conduite(conf) == "consultant"
            and not any("conduite" in e for e in cortex_config.valider_installable(conf)))
    gabarit = cortex_config.charger(RACINE / "template" / "config.example.yaml")
    quotes = {"commun.racine": gabarit.get("commun", {}).get("racine", "")}
    quotes.update({f"substrats.{c}": gabarit.get("substrats", {}).get(c, "")
                   for c in ("espace_documentaire", "base_projets", "git_remote")})
    verifie("un substrat vide suivi d'un commentaire est lu vide", all(v == "" for v in quotes.values()), str(quotes))
    verifie("un # entre guillemets survit au retrait des commentaires",
            cortex_config._scalaire('"a # b"  # com') == "a # b")
    inconnu = tmp / "config-conduite.yaml"
    inconnu.write_text(cfg.read_text(encoding="utf-8") + "conduite: duo\n", encoding="utf-8")
    erreurs = cortex_config.valider_installable(cortex_config.charger(inconnu))
    verifie("une conduite inconnue est refusee et le message nomme la cle",
            any(e.startswith("conduite") for e in erreurs), str(erreurs[:2]))
    r = scaffold("--config", str(inconnu), "--out", str(tmp / "refus-conduite"))
    verifie("scaffold s'arrete sur une conduite inconnue", r.returncode == 2, r.stderr[:200])

    section("v1", "10. Vault existant adopte (defaut : ses cles et ses codes refuses sans reecriture)")
    conf = cortex_config.charger(cfg)
    six = dict(conf, domaines=[{"code": "bureau", "nom": "Socle"}])
    sept = dict(conf, domaines=[{"code": "bureaux", "nom": "Socle"}])
    verifie("un code de domaine de 6 lettres est accepte",
            not any(e.startswith("domaines") for e in cortex_config.valider_installable(six)))
    verifie("un code de domaine de 7 lettres est refuse",
            any("2 à 6 lettres" in e for e in cortex_config.valider_installable(sept)))
    adoptee = vault / "20 - Projets" / "MAG - Adoptee.md"
    adoptee.write_text(note_projet("Adoptee", "mag", "Agencement magasin", "Signé", 30)
                       .replace("cycle: affaire", "nature: affaire")
                       .replace("url_canonique:", "notion_bdd:")
                       .replace('dossier_local: "Adoptee"\n', ""), encoding="utf-8")
    sans = lint(vault, "--json")
    verifie("sans alias, une fiche a cles d'origine echoue (phase hors cycle, pointeur absent)",
            sans.returncode == 1 and '"phase_hors_enum": [\n    {' in sans.stdout
            and "MAG - Adoptee.md" in sans.stdout, sans.stdout[-300:])
    avec = tmp / "config-alias.yaml"
    avec.write_text(cfg.read_text(encoding="utf-8")
                    + "alias:\n  cycle: nature\n  url_canonique: notion_bdd\n", encoding="utf-8")
    r = lint(vault, "--config", str(avec))
    verifie("avec alias, la meme fiche passe le lint", r.returncode == 0, r.stdout[-400:])
    faux = tmp / "config-alias-faux.yaml"
    faux.write_text(cfg.read_text(encoding="utf-8") + "alias:\n  cycle: natrue\n", encoding="utf-8")
    r = lint(vault, "--config", str(faux))
    verifie("un alias qu'aucune fiche ne porte est signale", r.returncode == 1 and "natrue" in r.stdout,
            r.stdout[-300:])
    double = tmp / "config-alias-double.yaml"
    double.write_text(cfg.read_text(encoding="utf-8")
                      + "alias:\n  cycle: nature\n  statut: nature\n", encoding="utf-8")
    erreurs = cortex_config.valider_installable(cortex_config.charger(double))
    verifie("deux cles lues sous le meme alias sont refusees",
            any("se lisent toutes sous 'nature'" in e for e in erreurs), str(erreurs[:2]))
    adoptee.unlink()
    return cfg


# ── C1 : neuf etapes ────────────────────────────────────────────────────────

def c1_neuf_etapes(tmp, cfg):
    section("C1", "Dix étapes, maillon 0, notice (§3 §5 §10, 2.3 §8 ; lanes B et rangement) : défaut plausible : "
                  "un tableau de bord qui compte neuf quand la chaîne en a dix")
    verifie("etat.py porte dix étapes : 0 à 3, « 3b », 4 à 8",
            [e[0] for e in m_etat.ETAPES] == [0, 1, 2, 3, "3b", 4, 5, 6, 7, 8], str([e[0] for e in m_etat.ETAPES]))
    verifie("les artefacts des dix étapes sont ceux du contrat §5 et du contrat 2.3 §8",
            {e[0]: e[3] for e in m_etat.ETAPES} == ETAPES_CONTRAT)

    atelier = tmp / "_cortex"
    atelier.mkdir()
    shutil.copyfile(cfg, atelier / "config.yaml")
    (atelier / "poste.json").write_text(poste_json(), encoding="utf-8")
    (atelier / "00-cadrage.md").write_text(FM_ATELIER.format(m=1, p="cortex-1-cadrage", s="valide", v="passe"),
                                           encoding="utf-8")
    (atelier / "04-ingest.md").write_text(FM_ATELIER.format(m=5, p="cortex-5-ingest", s="brouillon", v="arbitre"),
                                          encoding="utf-8")

    def sans_horodatage(p):
        return "\n".join(l for l in p.read_text(encoding="utf-8").splitlines() if '"genere_le"' not in l)

    p1, pivot = m_etat.ecrire(atelier, tmp / "pivot-1.json")
    p2, _ = m_etat.ecrire(atelier, tmp / "pivot-2.json")
    etapes = {e["numero"]: e for e in pivot["etapes"]}
    verifie("le pivot porte les dix étapes", len(pivot["etapes"]) == 10, str(len(pivot["etapes"])))
    verifie("le pivot se régénère à l'identique hors horodatage", sans_horodatage(p1) == sans_horodatage(p2))
    e0 = etapes.get(0, {})
    verifie("le maillon 0 est lu depuis poste.json : fait quand notice_ouverte_le est renseigné",
            e0.get("etat") == "faite", str(e0))
    (atelier / "poste.json").write_text(poste_json(notice_ouverte=False), encoding="utf-8")
    e0_sans = {e["numero"]: e for e in m_etat.generer(atelier)["etapes"]}.get(0, {})
    verifie("un poste.json sans notice_ouverte_le ne compte pas comme fait", e0_sans.get("etat") != "faite",
            str(e0_sans.get("etat")))
    (atelier / "poste.json").write_text(poste_json(), encoding="utf-8")
    e8 = etapes.get(8, {})
    verifie("l'étape 8 vaut arbitre avec la raison « vault solo » en mode solo",
            e8.get("etat") == "arbitre" and "solo" in str(e8.get("raison", "")).lower(), str(e8))
    verifie("le pivot porte profil, regime, phrase_suivante et notice_ouverte_le",
            all(k in pivot for k in ("profil", "regime", "phrase_suivante", "notice_ouverte_le"))
            and pivot.get("profil") == "dirigeant" and pivot.get("regime") == "pointeur"
            and pivot.get("notice_ouverte_le") == "2026-09-19T10:12:03",
            str({k: pivot.get(k) for k in ("profil", "regime", "phrase_suivante", "notice_ouverte_le")}))
    phrase = str(pivot.get("phrase_suivante", ""))
    verifie("la phrase suivante est en langage ordinaire, jamais un nom de maillon",
            phrase.strip() != "" and "cortex-" not in phrase and "python" not in phrase.lower(), phrase)
    e4 = etapes.get(4, {})
    verifie("le trou en 03 est porté avec sa raison en clair",
            e4.get("artefact") is None and "second cerveau" in e4.get("raison", "")
            and "contrôle de santé" in e4.get("raison", "")
            and not {"vault", "lint"} & set(e4.get("raison", "").lower().split()), str(e4))
    verifie("l'étape 4 se déduit d'un artefact aval, jamais devinée",
            e4.get("etat") == "faite_deduite"
            and {e["numero"]: e for e in m_etat.generer(tmp)["etapes"]}.get(4, {}).get("etat") == "a_faire")

    complet = tmp / "_cortex-complet"
    complet.mkdir()
    shutil.copyfile(cfg, complet / "config.yaml")
    (complet / "poste.json").write_text(poste_json(), encoding="utf-8")
    for nom, m, p in ARTEFACTS_MD:
        (complet / f"{nom}.md").write_text(FM_ATELIER.format(m=m, p=p, s="valide", v="passe"), encoding="utf-8")
    (complet / "03-rangement.md").write_text(RANGEMENT_APPLIQUE, encoding="utf-8")
    pivot_complet = m_etat.generer(complet)
    etats = [e["etat"] for e in pivot_complet["etapes"]]
    # §5 amende : en mode solo l'etape 8 vaut `arbitre`. Un atelier solo complet
    # annonce donc « 9 faites et 1 arbitree », jamais 10/10, et n'a plus de suite.
    verifie("atelier solo complet : 9 faites et 1 arbitrée (§5 amendé), jamais 10/10",
            m_etat.faites(pivot_complet) == 9 and etats[-1] == "arbitre"
            and m_etat.suivante(pivot_complet["etapes"]) is None, str(etats))
    # Le 9/9 se mesure la ou il existe : un atelier `mode: federe`, ou l'etape 8
    # porte un artefact comme les huit autres.
    federe = tmp / "_cortex-complet-federe"
    federe.mkdir()
    (federe / "config.yaml").write_text(
        cfg.read_text(encoding="utf-8").replace("mode: solo", "mode: federe")
           .replace('racine: ""', 'racine: "~/Cortex/commun"'), encoding="utf-8")
    (federe / "poste.json").write_text(poste_json(), encoding="utf-8")
    for nom, m, pr in ARTEFACTS_MD:
        (federe / f"{nom}.md").write_text(FM_ATELIER.format(m=m, p=pr, s="valide", v="passe"), encoding="utf-8")
    (federe / "03-rangement.md").write_text(RANGEMENT_APPLIQUE, encoding="utf-8")
    pivot_federe = m_etat.generer(federe)
    verifie("atelier fédéré complet : le compteur annonce 10 sur 10",
            m_etat.faites(pivot_federe) == 10, str([e["etat"] for e in pivot_federe["etapes"]]))
    (federe / "03-rangement.md").unlink()
    e3b = {e["numero"]: e for e in m_etat.generer(federe)["etapes"]}["3b"]
    verifie("2.3 A2 : un rangement jamais fait alors que la suite l'est vaut arbitré, « passée sans rangement »",
            e3b["etat"] == "arbitre" and e3b.get("raison") == m_etat.RAISON_PASSEE, str(e3b))

    # H2 §3 : en groupe, l'étape 8 attend que chaque rédacteur soit remis.
    groupe = tmp / "groupe-h2"
    commun_g = groupe / "commun"
    attend = tmp / "_cortex-groupe"
    attend.mkdir()
    (attend / "config.yaml").write_text(
        cfg.read_text(encoding="utf-8").replace("mode: solo", "mode: federe")
           .replace('racine: ""', f'racine: "{commun_g}"'), encoding="utf-8")
    (attend / "poste.json").write_text(poste_json(), encoding="utf-8")
    for nom, m, pr in ARTEFACTS_MD[:-1]:
        (attend / f"{nom}.md").write_text(FM_ATELIER.format(m=m, p=pr, s="valide", v="passe"), encoding="utf-8")
    commun_g.mkdir(parents=True)

    def membre(slug, remis):
        v = groupe / slug / "vault"
        (v / "_cortex").mkdir(parents=True, exist_ok=True)
        (v / "_cortex" / "06-passation.md").write_text(
            "---\nremis_le: " + ("2026-09-27" if remis else '""') + "\n---\n", encoding="utf-8")
        return f'  - {{ slug: {slug}, export: "{v / "_export" / slug}" }}\n'

    def huit():
        p = m_etat.generer(attend)
        return {e["numero"]: e for e in p["etapes"]}[8], p["phrase_suivante"]
    (commun_g / "federation.yaml").write_text(
        "version: 1\nmembres:\n" + membre("helene", True) + 'attendus: ["Karim B"]\n', encoding="utf-8")
    e8, phrase = huit()
    verifie("H2 : un rédacteur remis, un autre attendu : étape 8 arbitrée en nommant l'attendu, pas « relie les cerveaux »",
            e8["etat"] == "arbitre" and "Karim B" in e8.get("raison", "") and phrase != "relie les cerveaux",
            f"{e8['etat']} / {e8.get('raison')} / {phrase}")
    (commun_g / "federation.yaml").write_text(
        "version: 1\nmembres:\n" + membre("helene", True) + membre("karim", False), encoding="utf-8")
    e8, phrase = huit()
    verifie("H2 : deux membres, un seul remis : étape 8 arbitrée en nommant le membre en attente",
            e8["etat"] == "arbitre" and "karim" in e8.get("raison", "") and phrase != "relie les cerveaux",
            f"{e8['etat']} / {e8.get('raison')} / {phrase}")
    ligne8 = next((l for l in m_rend.rendre(m_etat.generer(attend)).splitlines() if "en attente de karim" in l), "")
    verifie("H2 : la notice dit « en attente de karim », sans « sans objet » devant",
            ligne8 != "" and "sans objet" not in ligne8, ligne8[:200] or "ligne absente de la notice")
    membre("karim", True)
    e8, phrase = huit()
    verifie("H2 témoin : les deux membres remis, « relie les cerveaux »",
            e8["etat"] == "a_faire" and phrase == "relie les cerveaux", f"{e8['etat']} / {phrase}")
    (attend / "07-federation.md").write_text(FM_ATELIER.format(m=8, p="cortex-8-federation", s="en_cours", v="passe"),
                                             encoding="utf-8")
    e8, _ = huit()
    verifie("H2 : un 07-federation.md en statut en_cours se lit « En cours », pas « Illisible »",
            m_etat.LIBELLES.get(e8["etat"]) == "En cours", e8["etat"])

    vierge = tmp / "atelier-vierge"
    vierge.mkdir()
    html_vierge = m_rend.rendre(m_etat.generer(vierge))
    # §5 amende : l'etape courante est rendue en tete, hors tableau ; il reste
    # donc neuf pastilles « A faire » sur les dix etapes d'une page vierge.
    verifie("le tableau de bord vierge affiche 9 pastilles « À faire », la 10e étant la courante en tête",
            html_vierge.count("À faire") == 9 and "courante" in html_vierge,
            str(html_vierge.count("À faire")))
    verifie("aucune URL distante dans la notice",
            not re.search(r"https?://", html_vierge) and not re.search(r"""(href|src)\s*=\s*["']//""", html_vierge))
    r = lancer(SCRIPTS / "notice.py", "--atelier", str(vierge), "--no-open")
    verifie("notice.py --no-open régénère etat.json et notice.html et sort en 0",
            r.returncode == 0 and (vierge / "etat.json").is_file() and (vierge / "notice.html").is_file(),
            r.stderr[:200])

    if POSTE.is_file():
        r = lancer(POSTE, "--dry-run")
        lignes = [l for l in r.stdout.splitlines() if l.strip()]
        # La commande est libre : `uvx --from "markitdown[all]" markitdown` comme `brew install x` passent.
        # H2 : un outil que la sonde n'a pas pu mesurer sort en « à vérifier (raison) ».
        motif = re.compile(r"^\S.*? : (absent → .+|à vérifier \(.+\))$")
        verifie("poste.py --dry-run sort en 0 et n'imprime qu'une ligne par outil absent ou à vérifier",
                r.returncode == 0 and all(motif.match(l) for l in lignes),
                (r.stderr[:200] or str([l for l in lignes if not motif.match(l)][:3])))
        c1_poste_h2(tmp)
    else:
        verifie("poste.py présent", False, "attendu au merge de la lane B")


def poste_isole(tmp, *args, outils_uv=(), uvx=""):
    """poste.py dans un dossier personnel neuf, PATH réduit au système : seuls les faux
    exécutables posés dans ~/.local/bin (le dossier des outils de uv) existent."""
    home = tmp / "home-poste"
    shutil.rmtree(home, ignore_errors=True)
    bin_uv = home / ".local" / "bin"
    bin_uv.mkdir(parents=True)
    for nom, corps in [(n, "exit 0") for n in outils_uv] + ([("uvx", uvx)] if uvx else []):
        (bin_uv / nom).write_text("#!/bin/sh\n" + corps + "\n", encoding="utf-8")
        (bin_uv / nom).chmod(0o755)
    poses = sorted(f.name for f in bin_uv.iterdir() if os.access(f, os.X_OK))
    env = dict(os.environ, HOME=str(home), PATH="/usr/bin:/bin")
    r = subprocess.run([sys.executable, str(POSTE), *args], env=env, capture_output=True, text=True, timeout=120)
    return r, poses


def c1_poste_h2(tmp):
    """Phase H2, défauts 6 et 7 : un outil posé par uv est vu, un outil non mesurable est
    « à vérifier », une voie mail qui installe ne s'écrit que sur la réponse de la personne,
    les options sont celles qu'elle a retenues."""
    if sys.platform == "win32":
        verifie("poste.py H2 : faux exécutables en shell, contrôle joué hors Windows", True)
        return
    r, poses = poste_isole(tmp, "--dry-run", outils_uv=["graphify"])
    verifie("H2 : un outil posé par uv dans ~/.local/bin, hors PATH, est vu présent",
            poses == ["graphify"] and r.returncode == 0 and "graphify" not in r.stdout, str(poses) + r.stdout[-300:])
    r, poses = poste_isole(tmp, "--dry-run")
    verifie("H2 témoin : sans le binaire, graphify est listé absent avec sa commande",
            poses == [] and re.search(r"^graphify : absent → ", r.stdout, re.M) is not None, r.stdout[-300:])
    refus = ("echo \"error: Failed to initialize cache at \\`$HOME/.cache/uv\\`\" >&2\n"
             "echo \"  Caused by: Permission denied (os error 13)\" >&2\nexit 2")
    r, poses = poste_isole(tmp, "--dry-run", uvx=refus)
    ligne = next((l for l in r.stdout.splitlines() if l.startswith("markitdown")), "")
    verifie("H2 : une sonde uvx refusée (cache) donne « markitdown : à vérifier », jamais une installation",
            poses == ["uvx"] and ligne.startswith("markitdown : à vérifier (") and "Permission denied" in ligne,
            ligne or r.stdout[-300:])
    atelier = tmp / "home-poste-atelier" / "_cortex"
    commun = ("--ecrire", "--atelier", str(atelier), "--mail", "dir@alcyon.test", "--fournisseur", "m365", "--no-open")
    r, _ = poste_isole(tmp, *commun)
    mail = (json.loads((atelier / "poste.json").read_text(encoding="utf-8")).get("mail", {})
            if (atelier / "poste.json").is_file() else {})
    verifie("H2 : Microsoft non administrateur sans --voie écrit « aucune », softeria seulement proposée",
            r.returncode == 0 and mail.get("voie") == "aucune" and mail.get("voie_proposee") == "softeria",
            str(mail) + r.stderr[-200:])
    r, _ = poste_isole(tmp, *commun, "--voie", "softeria")
    mail = json.loads((atelier / "poste.json").read_text(encoding="utf-8")).get("mail", {})
    verifie("H2 témoin : la réponse --voie softeria s'écrit telle quelle",
            r.returncode == 0 and mail.get("voie") == "softeria", str(mail))
    poste = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))
    verifie("H2 : sans --options, options_proposees est vide (la personne n'a rien retenu)",
            poste.get("options_proposees") == [], str(poste.get("options_proposees")))
    r, _ = poste_isole(tmp, *commun, "--options", "noota")
    poste = json.loads((atelier / "poste.json").read_text(encoding="utf-8"))
    verifie("H2 témoin : --options noota donne exactement [noota]",
            r.returncode == 0 and poste.get("options_proposees") == ["noota"], str(poste.get("options_proposees")))


# ── C2 : trois profils ──────────────────────────────────────────────────────

def c2_profils(tmp, configs):
    section("C2", "Trois profils, régime, section Notice (§2 §10 ; lane C) : défaut plausible : "
                  "un profil inconnu accepté, un régime hybride inventé")
    t0 = time.monotonic()
    comptes = m_fixtures.generer(FIXTURES)
    verifie("fixtures.py génère trois arbres en moins de 10 s", time.monotonic() - t0 < 10 and len(comptes) == 3,
            str(comptes))
    for profil in PROFILS:
        verifie(f"cortex-1-cadrage/references/profils/{profil}.md existe",
                (SKILLS / "cortex-1-cadrage" / "references" / "profils" / f"{profil}.md").is_file())
    for profil, (cfg, regime) in configs.items():
        erreurs = cortex_config.valider_installable(cortex_config.charger(cfg))
        verifie(f"la config {profil} (régime {regime}) est installable", not erreurs, str(erreurs[:2]))
    base = configs["dirigeant"][0].read_text(encoding="utf-8")
    mauvais_profil = tmp / "config-profil.yaml"
    mauvais_profil.write_text(base.replace("profil: dirigeant", "profil: autre"), encoding="utf-8")
    erreurs = cortex_config.valider_installable(cortex_config.charger(mauvais_profil))
    verifie("profil: autre est refusé et le message nomme la clé",
            any(e.startswith("profil") for e in erreurs), str(erreurs[:2]))
    mauvais_regime = tmp / "config-regime.yaml"
    mauvais_regime.write_text(base.replace("regime: pointeur", "regime: mixte"), encoding="utf-8")
    erreurs = cortex_config.valider_installable(cortex_config.charger(mauvais_regime))
    verifie("regime: mixte est refusé et le message nomme la clé",
            any("regime" in e for e in erreurs), str(erreurs[:2]))
    maillons = sorted(SKILLS.glob("cortex-*/SKILL.md"))
    sans_notice = [m.parent.name for m in maillons
                   if "## Notice" not in m.read_text(encoding="utf-8") or "notice.py" not in m.read_text(encoding="utf-8")]
    verifie("dix SKILL.md maillons (3 bis compris), chacun avec la section Notice et l'appel de notice.py (I10)",
            len(maillons) == 10 and not sans_notice, f"{len(maillons)} maillons, sans notice : {sans_notice}")
    longs = [(m.parent.name, len(m.read_text(encoding="utf-8").splitlines())) for m in maillons
             if len(m.read_text(encoding="utf-8").splitlines()) >= 300]
    verifie("chaque SKILL.md maillon fait moins de 300 lignes", not longs, str(longs))
    fautifs = []
    for m in maillons:
        texte = m.read_text(encoding="utf-8")
        for motif in ("On enchaîne", "lance `cortex-"):
            if motif in texte:
                fautifs.append(f"{m.parent.name} : {motif}")
    verifie("aucun maillon n'enchaîne, la section Notice seule propose la suite "
            "(I10, arbitrage 2026-09-19)", not fautifs, str(fautifs))
    recaps = maillons + sorted((GABARIT / ".claude" / "skills").glob("*/SKILL.md"))
    vus = [(m.parent.name, len(blocs_recapitulatif(m.read_text(encoding="utf-8")))) for m in recaps]
    mots = {m.parent.name: v for m in recaps if (v := vocabulaire_des_recaps(m.read_text(encoding="utf-8")))}
    verifie(f"H2 : les récapitulatifs de fin ({sum(n for _, n in vus)} blocs, {len(recaps)} SKILL.md) ne nomment "
            "ni skill, ni script, ni mot de la chaîne (doctrine §8)",
            sum(n for _, n in vus) >= 16 and not mots, str(mots) if mots else str(vus))


# ── C3 : inventaire outille ─────────────────────────────────────────────────

def c3_inventaire(tmp, configs):
    section("C3", "Inventaire outillé sur les fixtures (§4 ; lane D) : défaut plausible : "
                  "un inventaire qui copie du contenu ou ment sur ses bornes")
    if not SCAN.is_file():
        verifie("scan.py présent", False, "attendu au merge de la lane D")
        return
    racines = {"employe": FIXTURES / "employe", "dirigeant": FIXTURES / "dirigeant",
               "societe": FIXTURES / "societe" / "camille"}
    for profil, (cfg, regime) in configs.items():
        out = tmp / f"inv-{profil}.json"
        t0 = time.monotonic()
        try:
            r = lancer(SCAN, "--racine", tilde(racines[profil]), "--config", str(cfg), "--out", str(out), timeout=120)
        except subprocess.TimeoutExpired:
            verifie(f"scan {profil} : sort en 0 en moins de 60 s", False, "délai de 120 s dépassé")
            continue
        duree = time.monotonic() - t0
        verifie(f"scan {profil} : sort en 0 en moins de 60 s", r.returncode == 0 and duree < 60 and out.is_file(),
                f"code {r.returncode}, {duree:.1f} s, {r.stderr[:200]}")
        if not out.is_file():
            continue
        texte = out.read_text(encoding="utf-8")
        inv = json.loads(texte)
        verifie(f"scan {profil} : format cortex/inventaire v2, profil et régime portés",
                inv.get("format") == "cortex/inventaire" and inv.get("version") == 2
                and inv.get("profil") == profil and inv.get("regime") == regime,
                str({k: inv.get(k) for k in ("format", "version", "profil", "regime")}))
        bornes = inv.get("bornes") or {}
        verifie(f"scan {profil} : bornes en entiers, depassement booléen, max_dossiers respecté",
                bornes and all(isinstance(v, int) and not isinstance(v, bool)
                               for k, v in bornes.items() if k != "depassement")
                and isinstance(bornes.get("depassement"), bool)
                and bornes.get("dossiers_vus", 0) <= bornes.get("max_dossiers", 200), str(bornes))
        verifie(f"scan {profil} : aucun champ contenu, nulle part", "contenu" not in cles_recursives(inv))
        disque = inv.get("disque") or []
        # §4 amende : la forme ~ n'est exigible que si les fixtures vivent sous le
        # dossier personnel ; un depot clone ailleurs produit des absolus legitimes.
        if SOUS_HOME:
            verifie(f"scan {profil} : disque non vide, chemins en forme ~, source_id et substrat portés",
                    disque and all(str(d.get("chemin", "")).startswith("~/") and d.get("source_id") and d.get("substrat")
                                   for d in disque), str(disque[:1]))
        else:
            verifie(f"scan {profil} : disque non vide, chemins absolus admis (fixtures hors du dossier "
                    f"personnel : {FIXTURES}), source_id et substrat portés",
                    disque and all(str(d.get("chemin", "")) and d.get("source_id") and d.get("substrat")
                                   for d in disque), str(disque[:1]))
        if profil == "employe":
            verifie("employé : export-notion-*.csv apparaît comme signal de base déportée",
                    "export-notion" in texte and "base_deportee" in texte)

    # H2 : un dossier de photos hors projets, trois fichiers, devient candidat ; trois
    # documents hors projets restent sous le seuil de l'agent (témoin).
    medias = tmp / "partage-h2"
    for dossier, ext in (("Divers/Photos", "jpg"), ("Divers/Notes", "docx")):
        (medias / dossier).mkdir(parents=True)
        for i in range(1, 4):
            (medias / dossier / f"f{i}.{ext}").write_text("x", encoding="utf-8")
    poses = sorted(q.relative_to(medias).as_posix() for q in medias.rglob("*.*"))
    out = tmp / "inv-medias.json"
    r = lancer(SCAN, "--racine", str(medias), "--out", str(out))
    sans = ([x.get("indice", "") for x in json.loads(out.read_text(encoding="utf-8")).get("ecarts_candidats", [])
             if x.get("type") == "dossier_sans_domaine"] if out.is_file() else [])
    verifie("H2 : trois .jpg dans Divers/Photos donnent un candidat dossier_sans_domaine, trois .docx aucun",
            len(poses) == 6 and r.returncode == 0 and len(sans) == 1 and "Divers/Photos : 3 fichier(s)" in sans[0],
            f"{len(poses)} fichiers posés, code {r.returncode}, {sans} {r.stderr[:200]}")


# ── C4 et C5 : couche vault, regimes ────────────────────────────────────────

def c4_couche_vault(tmp, configs):
    section("C4", "Couche vault (§9 ; lane E) : défaut plausible : un agent qui peut écrire "
                  "dans les dossiers de travail")
    cfg, _ = configs["dirigeant"]
    conf = cortex_config.charger(cfg)
    racines = list((conf.get("collecte") or {}).get("racines") or [])
    vault = tmp / "vault-pointeur"
    r = scaffold("--config", str(cfg), "--out", str(vault))
    verifie("scaffold accepte une config v2 complète", r.returncode == 0, r.stderr[:300])
    if r.returncode != 0:
        return None
    # Phase H : sans identité locale, l'identité globale du poste signait l'historique livré.
    attendu = (conf.get("organisation") or {}).get("redacteur") or "Cortex"
    ident = subprocess.run(["git", "-C", str(vault), "config", "--local", "user.name"],
                           capture_output=True, text=True).stdout.strip()
    auteurs = subprocess.run(["git", "-C", str(vault), "log", "--format=%an"],
                             capture_output=True, text=True).stdout.split("\n")
    verifie("le vault porte une identité git locale, celle qui signe son premier commit",
            ident == attendu and auteurs[0] == attendu, f"{ident!r} / {auteurs[:1]}")
    # H2 lane C : chaque commit du vault portait `Co-Authored-By` et `Claude-Session`,
    # un lien vers la session de qui installait. La clôture commite par cloture.py.
    (vault / "_recette-cloture.txt").write_text("clôture de recette\n", encoding="utf-8")
    r_clot = lancer(vault / ".claude" / "skills" / "cloture" / "cloture.py", "--vault", str(vault), "--message",
                    "Clôture : recette\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n"
                    "Claude-Session: https://claude.ai/code/session_recette", "_recette-cloture.txt")
    dernier = subprocess.run(["git", "-C", str(vault), "log", "-1", "--format=%an%n%B"],
                             capture_output=True, text=True).stdout
    verifie("H2 : un commit de clôture (cloture.py du vault) signe sous l'identité du vault, "
            "sans Co-Authored-By ni Claude-Session",
            r_clot.returncode == 0 and dernier.startswith(attendu + "\nClôture : recette")
            and not re.search(r"co-authored-by|claude-session|claude\.ai", dernier, re.I),
            f"code {r_clot.returncode}, {dernier[:200]!r}, {r_clot.stderr[:200]}")
    settings_path = vault / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        verifie("settings.json présent et parsable", False, str(e))
        return vault
    perm = settings.get("permissions") or {}
    deny = perm.get("deny") or []
    allow = perm.get("allow") or []
    verifie("additionalDirectories reprend collecte.racines", perm.get("additionalDirectories") == racines,
            str(perm.get("additionalDirectories")))
    # Phase H : Claude Code ignore une règle Write(...) ; Edit(...) couvre tous
    # les outils d'écriture, et seul le sandbox arrête Bash.
    verifie("une règle deny Edit par racine, aucune règle Write inopérante",
            racines and all(f"Edit({r}/**)" in deny for r in racines)
            and not any(d.startswith("Write(") for d in deny), str(deny))
    verifie("H2 : git commit tapé refusé (deny), la clôture passe par cloture.py (allow)",
            "Bash(git commit:*)" in deny and "Bash(git commit:*)" not in allow
            and "Bash(python3 .claude/skills/cloture/cloture.py:*)" in allow, str(deny))
    verifie("aucune règle allow n'ouvre Write, Edit ni un Bash libre",
            not any(a in ("Write", "Edit", "Bash") or a.startswith(("Write(", "Edit(")) for a in allow), str(allow))
    if sys.platform != "win32":
        sb = settings.get("sandbox") or {}
        verifie("Bash confiné : sandbox actif, sans échappatoire, racines en denyWrite",
                sb.get("enabled") is True and sb.get("allowUnsandboxedCommands") is False
                and all(r in (sb.get("filesystem") or {}).get("denyWrite", []) for r in racines), str(sb))
    hooks = settings.get("hooks") or {}
    verifie("hooks SessionStart et Stop présents dans settings.json",
            bool(hooks.get("SessionStart")) and bool(hooks.get("Stop")), str(list(hooks)))
    # §9 amende : les hooks sont deux scripts stdlib auto-testes, settings.json
    # ne fait que les appeler. On verifie les scripts, pas une commande inline.
    dossier_hooks = vault / ".claude" / "hooks"
    scripts_hooks = {n: dossier_hooks / f"{n}.py" for n in ("session_start", "stop")}
    verifie("settings.json appelle .claude/hooks/session_start.py et stop.py",
            all(f"hooks/{n}.py" in json.dumps(hooks.get(ev, ""))
                for n, ev in (("session_start", "SessionStart"), ("stop", "Stop"))), str(hooks))
    verifie("les deux scripts de hook sont livrés dans .claude/hooks/",
            all(c.is_file() for c in scripts_hooks.values()),
            str({n: c.is_file() for n, c in scripts_hooks.items()}))
    src_ss = scripts_hooks["session_start"].read_text(encoding="utf-8") if scripts_hooks["session_start"].is_file() else ""
    src_stop = scripts_hooks["stop"].read_text(encoding="utf-8") if scripts_hooks["stop"].is_file() else ""
    verifie("session_start.py lance lint_sante.py --bref",
            "lint_sante.py" in src_ss and "--bref" in src_ss)
    verifie("stop.py rappelle la clôture",
            re.search(r"cl[oô]ture", src_stop, re.I) is not None)
    for nom, chemin in scripts_hooks.items():
        if not chemin.is_file():
            verifie(f"{nom}.py --autotest sort en 0", False, "script absent")
            continue
        r_hook = lancer(chemin, "--autotest")
        verifie(f"{nom}.py --autotest sort en 0",
                r_hook.returncode == 0, f"code {r_hook.returncode}, {(r_hook.stderr or r_hook.stdout)[:200]}")
    # H2 : une commande relative cassait après un `cd` de la session. La commande de
    # settings.json, jouée depuis un autre dossier, doit trouver le hook et le lint.
    commandes = {ev: ((hooks.get(ev) or [{}])[0].get("hooks") or [{}])[0].get("command", "")
                 for ev in ("SessionStart", "Stop")}
    verifie("H2 : les deux commandes de hook sont ancrées sur ${CLAUDE_PROJECT_DIR}",
            all(c.startswith('python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/') for c in commandes.values()),
            str(commandes))
    ailleurs = tmp / "ailleurs-hooks"
    ailleurs.mkdir(exist_ok=True)
    argv = [x.replace("${CLAUDE_PROJECT_DIR}", str(vault)) for x in shlex.split(commandes["SessionStart"])]
    r_ss = subprocess.run([sys.executable] + argv[1:], cwd=ailleurs, capture_output=True, text=True, timeout=120,
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(vault)))
    verifie("H2 : la commande SessionStart lancée depuis un autre dossier lit le lint du vault",
            r_ss.returncode == 0 and "Contrôle de santé" in r_ss.stdout, f"code {r_ss.returncode}, {(r_ss.stderr or r_ss.stdout)[:200]}")
    sans_env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    r_ss = subprocess.run([sys.executable, str(scripts_hooks["session_start"])], cwd=ailleurs,
                          capture_output=True, text=True, timeout=120, env=sans_env)
    verifie("H2 : sans CLAUDE_PROJECT_DIR, le hook se repère sur son emplacement, pas sur le dossier courant",
            r_ss.returncode == 0 and "Contrôle de santé" in r_ss.stdout, f"code {r_ss.returncode}, {(r_ss.stderr or r_ss.stdout)[:200]}")
    r_stop = subprocess.run([sys.executable, str(scripts_hooks["stop"]), "--autotest"], cwd=ailleurs,
                            capture_output=True, text=True, timeout=120, env=dict(os.environ, CLAUDE_PROJECT_DIR=str(vault)))
    verifie("H2 : stop.py --autotest lancé hors du vault sort en 0", r_stop.returncode == 0,
            (r_stop.stderr or r_stop.stdout)[:200])
    for nom in ("agenda", "miroir"):
        script = vault / ".claude" / "skills" / nom / f"{nom}.py"
        r_s = lancer(script, "--autotest") if script.is_file() else None
        verifie(f"{nom}.py est livré et son --autotest sort en 0",
                r_s is not None and r_s.returncode == 0, "absent" if r_s is None else (r_s.stderr or r_s.stdout)[:200])
    verifie("agenda et miroir se lancent sans permission (allow)",
            all(f"Bash(python3 .claude/skills/{n}/{n}.py:*)" in allow for n in ("agenda", "miroir")), str(allow))
    verifie("session_start.py affiche l'agenda en bref", "agenda.py" in src_ss and "--bref" in src_ss)
    skills_livrees = {p.name for p in (vault / ".claude" / "skills").iterdir() if p.is_dir()} \
        if (vault / ".claude" / "skills").is_dir() else set()
    attendues = set((conf.get("agents") or {}).get("skills") or [])
    verifie("les skills de agents.skills sont livrées, parle et bilan comprises",
            attendues <= skills_livrees and {"parle", "bilan"} <= skills_livrees, str(sorted(skills_livrees)))
    agents = sorted((vault / ".claude" / "agents").glob("*.md")) if (vault / ".claude" / "agents").is_dir() else []
    outils = {a.name: (frontmatter(a.read_text(encoding="utf-8")) or {}).get("tools", "") for a in agents}
    verifie("les sous-agents sont en lecture seule (tools : Read, Grep, Glob)",
            len(agents) == 2 and all({t.strip() for t in v.split(",")} <= {"Read", "Grep", "Glob"} and v
                                     for v in outils.values()), str(outils))
    runbook = vault / "90 - Meta" / "Runbook - Sessions de travail.md"
    texte = runbook.read_text(encoding="utf-8") if runbook.is_file() else ""
    verifie("{{DOSSIERS_PROJETS}} est substitué en forme ~ (défaut n°7 v1)",
            "~/Documents/Affaires" in texte and "/Users/" not in texte)

    # Defaut REEL paye le 2026-09-19 : `outillage_seul()` lit chaque fichier du
    # gabarit `.claude/` en UTF-8. Un `python3 -m py_compile` sur les hooks du
    # gabarit depose un `__pycache__`, et le rafraichissement d'outillage d'un
    # vault deja livre sort en 1 sur une UnicodeDecodeError illisible. Le mode
    # installation, lui, filtre deja par suffixe : c'est la forme a reprendre.
    pycache = GABARIT / ".claude" / "hooks" / "__pycache__"
    temoin = pycache / "stop.cpython-000.pyc"
    embarque = vault / ".claude" / "skills" / "lint" / "lint_sante.py"
    try:
        pycache.mkdir(parents=True, exist_ok=True)
        temoin.write_bytes(b"\xae\x0d\x0d\x0a\x00binaire, pas de l'UTF-8\x00\xff")
        embarque.write_text("# version perimee\n", encoding="utf-8")
        r = scaffold("--config", str(cfg), "--out", str(vault), "--outillage-seul")
        verifie("un fichier binaire sous le gabarit .claude/ ne casse pas --outillage-seul",
                r.returncode == 0, f"code {r.returncode}, {r.stderr[-300:]}")
        verifie("le lint embarqué est réactualisé malgré le fichier binaire",
                embarque.read_text(encoding="utf-8") == (SCRIPTS / "lint_sante.py").read_text(encoding="utf-8"))
    finally:
        shutil.rmtree(pycache, ignore_errors=True)
    return vault


def c5_regimes(tmp, configs, vault_pointeur):
    section("C5", "Régimes pointeur et copie (§2 ; lane E) : défaut plausible : une copie qui dérive "
                  "de sa source sans que personne le voie")
    if vault_pointeur is not None:
        r = lint(vault_pointeur)
        verifie("lint 0 en régime pointeur", r.returncode == 0, r.stdout[-400:])
    else:
        verifie("lint 0 en régime pointeur", False, "vault pointeur non scaffoldé")
    cfg, _ = configs["employe"]
    vault = tmp / "vault-copie"
    r = scaffold("--config", str(cfg), "--out", str(vault))
    verifie("scaffold en régime copie", r.returncode == 0, r.stderr[:300])
    if r.returncode != 0:
        return
    source = ATELIER_RECETTE / "sources" / "organigramme.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("# Organigramme\n\nDirection, atelier, bureau d'études.\n", encoding="utf-8")
    note = vault / "50 - Ressources" / "Structurants" / "organigramme" / "Organigramme.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    corps = "\n".join(f"- ligne {i} de l'organigramme copié" for i in range(1, 16))
    note.write_text(f"---\ntype: structurant\nstructurant: organigramme\ndomaine: \"[[Agencement magasin]]\"\n"
                    f"source_path: \"{tilde(source)}\"\n"
                    f"hash: {sha256(source)}\ncopie_le: 2026-09-19\n---\n# Organigramme\n\n## Journal\n\n"
                    f"### 2026-09-19\n\n{corps}\n", encoding="utf-8")
    r = lint(vault)
    verifie("lint 0 en régime copie : le contrôle « 10 lignes » est suspendu sur Structurants/",
            r.returncode == 0, r.stdout[-400:])
    source.write_text("# Organigramme\n\nDirection, atelier, bureau d'études, magasin.\n", encoding="utf-8")
    r = lint(vault, "--json")
    try:
        rapport = json.loads(r.stdout)
    except ValueError:
        rapport = {}
    verifie("un structurant modifié à la source lève structurant_perime",
            bool(rapport.get("structurant_perime")), r.stdout[-300:] if not rapport else str(list(rapport)))


# ── C6 : federation ─────────────────────────────────────────────────────────

def c6_federation(tmp):
    section("C6", "Fédération sur trois exports fictifs (§6 ; lane F) : défaut plausible : un commun "
                  "qui change à chaque génération ou qui publie une note privée")
    if not FEDERE.is_file():
        verifie("federe.py présent", False, "attendu au merge de la lane F")
        return
    vaults = ATELIER_RECETTE / "vaults"
    commun = ATELIER_RECETTE / "commun"
    shutil.rmtree(vaults, ignore_errors=True)
    shutil.rmtree(commun, ignore_errors=True)
    commun.mkdir(parents=True)
    C = m_fixtures.CLIENTS
    membres = {"camille": C[:5], "yasmine": C[:2] + C[5:8], "marc": C[8:11] + [C[0]]}
    exports = {slug: export_fictif(vaults, slug, noms) for slug, noms in membres.items()}
    (commun / "federation.yaml").write_text(
        "version: 1\nnom: \"Ateliers Roumier\"\nmembres:\n"
        + "".join(f'  - {{ slug: {s}, export: "{tilde(e)}" }}\n' for s, e in exports.items()), encoding="utf-8")
    verifie("federation.yaml est lisible par cortex_config.charger",
            len(cortex_config.charger(commun / "federation.yaml").get("membres") or []) == 3)
    r1 = lancer(FEDERE, "--config", str(commun / "federation.yaml"))
    verifie("federe.py génère le commun et sort en 0", r1.returncode == 0, r1.stderr[:300])
    if r1.returncode != 0:
        return
    e1 = empreinte_commun(commun)
    r2 = lancer(FEDERE, "--config", str(commun / "federation.yaml"))
    e2 = empreinte_commun(commun)
    verifie("deux générations ne diffèrent que sur genere_le", r2.returncode == 0 and e1 == e2,
            str([k for k in set(e1) | set(e2) if e1.get(k) != e2.get(k)][:5]))
    verifie("Centre, README « généré, ne pas éditer » et empreinte .cortex-genere présents",
            (commun / "00 - Centre" / "Centre.md").is_file() and (commun / ".cortex-genere").is_file()
            and (commun / "README.md").is_file()
            and re.search(r"ne pas [ée]diter", (commun / "README.md").read_text(encoding="utf-8"), re.I))
    projets = sorted(p.name for p in (commun / "20 - Projets").glob("*.md")) if (commun / "20 - Projets").is_dir() else []
    verifie("les projets portent le slug du rédacteur en préfixe",
            projets and all(re.match(r"^(CAMILLE|YASMINE|MARC) - ", n) for n in projets), str(projets[:3]))
    acteurs = [p for p in commun.rglob("40 - Acteurs/*.md") if C[0] in p.name]
    texte = acteurs[0].read_text(encoding="utf-8") if acteurs else ""
    verifie("un acteur présent chez trois rédacteurs donne une note unique avec source_vault multiple",
            len(acteurs) == 1 and all(s in texte for s in membres), f"{len(acteurs)} note(s) : {texte[:200]}")
    domaines = list(commun.rglob("10 - Domaines/*.md"))
    verifie("un domaine porté par trois rédacteurs est fusionné en une note",
            len([d for d in domaines if "Agencement magasin" in d.name]) == 1, str([d.name for d in domaines]))
    verifie("chaque note du commun porte source_vault",
            all("source_vault" in p.read_text(encoding="utf-8") for p in commun.rglob("*.md")
                if p.name not in ("README.md", "Centre.md")))
    exp = exports["camille"]
    note_export(exp / "20 - Projets" / "MAG - Secret Roumier.md", "Secret Roumier", "projet", "camille",
                visibilite="prive")
    ecrire_index(exp, "camille")
    r3 = lancer(FEDERE, "--config", str(commun / "federation.yaml"))
    verifie("une note visibilite: prive dans un export est refusée et absente du commun",
            r3.returncode != 0 and not list(commun.rglob("*Secret Roumier*")), f"code {r3.returncode}")

    # La chaîne réelle : deux clôtures par export.py, puis federe.py.
    reel = ATELIER_RECETTE / "commun-reel"
    shutil.rmtree(reel, ignore_errors=True)
    reel.mkdir(parents=True)
    exports_reels = {s: export_reel(vaults, s) for s in ("helene", "karim")}
    (reel / "federation.yaml").write_text(
        "version: 1\nnom: \"Chaîne réelle\"\nmembres:\n"
        + "".join(f'  - {{ slug: {s}, export: "{tilde(e)}" }}\n' for s, e in exports_reels.items()),
        encoding="utf-8")
    r4 = lancer(FEDERE, "--config", str(reel / "federation.yaml"))
    fusion = list(reel.rglob("40 - Acteurs/Direction commerciale.md"))
    verifie("deux exports écrits par export.py se fédèrent, l'acteur commun en une note",
            r4.returncode == 0 and len(fusion) == 1 and not list(reel.rglob("*Banque*")),
            (r4.stderr or r4.stdout)[:300])

    # H2 §4 : le groupe s'inscrit rédacteur par rédacteur, puis se fédère.
    inscrit = ATELIER_RECETTE / "commun-inscrit"
    shutil.rmtree(inscrit, ignore_errors=True)
    fy = inscrit / "federation.yaml"

    def inscrire(slug, nom, *attendus, config=fy):
        return lancer(FEDERE, "--inscrire", slug, "--redacteur", nom, "--export", str(exports_reels[slug]),
                      "--config", str(config), "--nom", "Chaîne réelle",
                      *[x for a_ in attendus for x in ("--attendu", a_)])
    r5, r6 = inscrire("helene", "Hélène V", "Karim B"), inscrire("helene", "Hélène V", "Karim B")
    lu = cortex_config.charger(fy) if fy.is_file() else {}
    verifie("H2 : --inscrire deux fois le même slug donne un seul membre, l'autre rédacteur attendu",
            r5.returncode == r6.returncode == 0 and [m.get("slug") for m in lu.get("membres", [])] == ["helene"]
            and lu.get("attendus") == ["Karim B"], (r5.stderr or r6.stderr)[:200] + str(lu))
    r7 = inscrire("karim", "Karim B", "Hélène V")
    lu = cortex_config.charger(fy) if fy.is_file() else {}
    r8 = lancer(FEDERE, "--config", str(fy))
    verifie("H2 : le second inscrit sort des attendus, un --attendu déjà membre est ignoré avec un message, "
            "et federe.py fédère ce federation.yaml",
            r7.returncode == 0 and lu.get("attendus") == [] and len(lu.get("membres", [])) == 2
            and "Hélène V est déjà membre" in r7.stdout
            and r8.returncode == 0 and (inscrit / ".cortex-genere").is_file(), (r7.stderr or r8.stderr)[:300])
    etranger = vaults / "reel-helene"
    avant = sorted((q.relative_to(etranger).as_posix(), sha256(q)) for q in etranger.rglob("*") if q.is_file())
    r9 = inscrire("helene", "Hélène V", config=etranger / "federation.yaml")
    apres = sorted((q.relative_to(etranger).as_posix(), sha256(q)) for q in etranger.rglob("*") if q.is_file())
    verifie("H2 : --inscrire sur un dossier étranger non vide sort en 1 et n'y écrit rien",
            r9.returncode == 1 and avant == apres and len(avant) > 0, f"code {r9.returncode}, {len(avant)} fichiers")

    # H2 défaut 10 : une note du commun éditée en gardant son en-tête « généré ».
    membre = vaults / "reel-helene"
    cfg_membre = membre / "config-lint.yaml"
    cfg_membre.write_text(
        f'version: 1\norganisation:\n  nom: "Chaîne réelle"\n  code: helene\n  redacteur: "H"\n'
        f'mode: federe\ncommun:\n  racine: "{tilde(reel)}"\nchemins:\n  dossiers_projets: ""\n'
        f'donnees:\n  regime: pointeur\ndomaines:\n  - {{ code: ope, nom: "Opérations" }}\n'
        f'cycles:\n  - {{ cycle: mission, phase: "Cadrage", progression: 20 }}\n', encoding="utf-8")

    def commun_signale():
        r = lint(membre, "--config", str(cfg_membre), "--json")
        try:
            return json.loads(r.stdout).get("commun_edite_main")
        except ValueError:
            return f"sortie illisible : {(r.stderr or r.stdout)[:200]}"
    temoin = commun_signale()
    verifie("H2 témoin : le commun tel que généré n'est pas signalé par le lint d'un membre", temoin == [], str(temoin))
    for nom in (".DS_Store", "20 - Projets/.DS_Store", "Thumbs.db", "20 - Projets/desktop.ini"):
        if (reel / nom).parent.is_dir():
            (reel / nom).write_bytes(b"\x00\x00\x00\x01Bud1")
    finder = commun_signale()
    verifie("H2 reprise M1 : un .DS_Store du Finder (et Thumbs.db, desktop.ini) posé dans le commun n'est pas signalé",
            finder == [] and (reel / "20 - Projets" / ".DS_Store").is_file(), str(finder))
    belvedere = next(reel.rglob("20 - Projets/*Belvédère.md"), None)
    if belvedere is not None:
        avant = belvedere.read_text(encoding="utf-8")
        belvedere.write_text(avant + "\nPrécision ajoutée à la main dans le commun.\n", encoding="utf-8")
    signale = commun_signale() if belvedere is not None else []
    verifie("H2 : une note du commun éditée en gardant son en-tête est signalée (empreinte)",
            belvedere is not None and "<!-- généré" in belvedere.read_text(encoding="utf-8")[:400]
            and any("empreinte" in str(it) for it in (signale or [])), str(signale))


# ── C7 a C9 : manifestes, white-label, chemins absolus ──────────────────────

def c7_manifestes():
    section("C7", "Manifestes plugin (§11) : défaut plausible : un plugin qui s'installe et n'expose "
                  "aucune skill")
    try:
        plugin = json.loads((DEPOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marche = json.loads((DEPOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        verifie("plugin.json et marketplace.json parsables", False, str(e))
        return
    verifie("plugin.json : name cortex, version, description", plugin.get("name") == "cortex"
            and plugin.get("version") and plugin.get("description"), str(plugin)[:200])
    entrees = marche.get("plugins") or []
    verifie("marketplace.json : le dépôt est sa propre marketplace (source ./, plugin cortex)",
            marche.get("name") == "cortex-kit" and len(entrees) == 1
            and entrees[0].get("name") == "cortex" and entrees[0].get("source") == "./", str(entrees))
    dossiers = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    defauts = []
    for d in dossiers:
        fm = frontmatter((d / "SKILL.md").read_text(encoding="utf-8")) if (d / "SKILL.md").is_file() else None
        if fm is None:
            defauts.append(f"{d.name} : SKILL.md absent ou sans frontmatter")
        elif not fm.get("description") or fm.get("name") != d.name:
            defauts.append(f"{d.name} : name={fm.get('name')!r}, description={'oui' if fm.get('description') else 'non'}")
    verifie(f"un SKILL.md par dossier de skills/ ({len(dossiers)}), name = dossier, description présente",
            dossiers and not defauts, str(defauts[:3]))
    lien = DEPOT / ".claude" / "skills" / "fabricant"
    verifie("la skill fabricant reste hors plugin (lien .claude/skills/fabricant, absente de skills/)",
            lien.is_symlink() and not (SKILLS / "fabricant").exists())


def _tokens(texte):
    plat = unicodedata.normalize("NFKD", texte)
    plat = "".join(c for c in plat if not unicodedata.combining(c)).lower()
    return re.findall(r"[a-z0-9]+", plat)


def c8_white_label():
    section("C8", "White-label (01-cadrage §Marques interdites) : défaut plausible : une marque du "
                  "fabricant héritée de la v1 livrée à un tiers")
    fuites = []
    for p, rel in fichiers_texte(PERIMETRE_WHITE_LABEL):
        for no, ligne in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            t = _tokens(ligne)
            formes = t + [" ".join(t[i:i + 2]) for i in range(len(t) - 1)] + [" ".join(t[i:i + 3]) for i in range(len(t) - 2)]
            touches = {hashlib.sha256(f.encode()).hexdigest()[:16] for f in formes} & MARQUES_EMPREINTES
            if touches:
                fuites.append(f"{rel}:{no}")
    verifie("aucune marque interdite dans skills/ notice/ outils/ README.md", not fuites,
            f"{len(fuites)} ligne(s) : {fuites[:6]}")


def c9_chemins_absolus():
    section("C9", "Zéro chemin absolu (I2, §11) : défaut plausible : un chemin de la machine du "
                  "fabricant qui rend le kit inopérant ailleurs")
    motif = re.compile(r"(/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|\b[A-Z]:\\[A-Za-z])")
    print("  — exclus : les lignes qui définissent le motif de détection (re.compile, chaîne brute r\"…\", "
          "commande grep) et les fragments cités entre backticks ; un motif montré n'est pas un chemin de machine.")
    hits = [f"{rel}:{no}" for p, rel in fichiers_texte(PERIMETRE_WHITE_LABEL)
            for no, l in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if not MOTIF_DE_DETECTION.search(l) and motif.search(re.sub(r"`[^`]*`", "", l))]
    verifie("aucun chemin absolu (/Users/, /home/, lettre de lecteur) dans skills/ notice/ outils/ README.md",
            not hits, f"{len(hits)} ligne(s) : {hits[:6]}")
    tous = sorted(SKILLS.glob("**/SKILL.md"))
    cd = [f"{m.relative_to(DEPOT)}:{no}" for m in tous
          for no, l in enumerate(m.read_text(encoding="utf-8").splitlines(), 1) if CD_VERS_UN_CHEMIN.search(l)]
    verifie(f"H2 : aucun SKILL.md ({len(tous)}, skills du vault comprises) ne prescrit un cd vers un chemin",
            len(tous) >= 16 and not cd, f"{len(cd)} ligne(s) : {cd[:6]}")
    skills_md = list(SKILLS.glob("cortex-*/SKILL.md"))
    durs = [m.parent.name for m in skills_md if re.search(r"\$HOME/\.claude|~/\.claude/skills/cortex", m.read_text(encoding="utf-8"))]
    verifie("les maillons se référencent par ${CLAUDE_SKILL_DIR}, jamais par ~/.claude/skills", not durs, str(durs))


# ── C10 : paquet ────────────────────────────────────────────────────────────

def c10_paquet(tmp):
    section("C10", "Paquet, notice hors ligne, README (§11 ; lane B) : défaut plausible : un kit muet, "
                   "une fuite de licence, une notice qui renvoie en ligne")
    maillons = sorted(p.name for p in SKILLS.glob("cortex-*") if p.is_dir())
    kit = [l.strip() for l in (PAQUET / "kit.txt").read_text(encoding="utf-8").splitlines()
           if l.strip() and not l.startswith("#")]
    attendus = set(maillons) | set(kit)
    zip_temoin = tmp / "cortex-temoin.zip"
    verifie("la fabrication sort en 0", m_fabrique.fabriquer(zip_temoin, version="recette") == 0)
    if not zip_temoin.is_file():
        return
    with zipfile.ZipFile(zip_temoin) as z:
        noms = z.namelist()
        dossiers = {n.split("/")[0] for n in noms if "/" in n}
        racine = {n for n in noms if "/" not in n}
        skills_md = [n for n in noms if n.endswith("SKILL.md")]
        prof1 = sorted(n.split("/")[0] for n in skills_md if len(n.split("/")) == 2)
        trop_bas = [n for n in skills_md if len(n.split("/")) > 2
                    and not n.startswith("cortex-4-installation/template/")]
        verifie(f"le zip compte les maillons présents par glob ({len(maillons)}) plus le kit ({len(kit)}) "
                "et deux fichiers à la racine",
                dossiers == attendus and racine == {"LISEZ-MOI.html", "PROVENANCE.md"},
                f"{sorted(dossiers ^ attendus)}, racine {sorted(racine)}")
        verifie("un SKILL.md à la bonne profondeur par dossier", prof1 == sorted(attendus), str(prof1))
        verifie("zéro SKILL.md en profondeur 2 dans le zip, le critère qui décide si le kit est vu ou muet",
                not trop_bas, str(trop_bas))
        manquants = []
        for skill in kit:
            chemin = f"{skill}/SKILL.md"
            if chemin not in noms:
                manquants.append(chemin)
                continue
            fm = frontmatter(z.read(chemin).decode("utf-8"))
            if not fm or not {"name", "description"} <= set(fm):
                manquants.append(f"{chemin} (frontmatter incomplet)")
        verifie("chaque entrée du manifeste est dans le zip avec un frontmatter valide", not manquants, str(manquants))
        provenance = z.read("PROVENANCE.md").decode("utf-8")
        decouverts = [s for s in kit if not re.search(rf"^\|\s*{re.escape(s)}\s*\|.*\|\s*\**Oui\**.*\|\s*$",
                                                      provenance, re.M)]
        verifie("chaque emprunt du zip est couvert par PROVENANCE.md", not decouverts, str(decouverts))
        lisezmoi = z.read("LISEZ-MOI.html").decode("utf-8")
        # §5 amende : neuf pastilles « A faire », la courante etant en tete hors tableau.
        verifie("LISEZ-MOI.html du zip : 9 pastilles « À faire » (la 10e en tête), zéro URL distante",
                lisezmoi.count("À faire") == 9 and not re.search(r"https?://", lisezmoi)
                and not re.search(r"""(href|src)\s*=\s*["']//""", lisezmoi), str(lisezmoi.count("À faire")))
    notice = DEPOT / "notice" / "LISEZ-MOI.html"
    verifie("notice/LISEZ-MOI.html présente, hors ligne (zéro URL)",
            notice.is_file() and not re.search(r"https?://", notice.read_text(encoding="utf-8", errors="replace")))
    verifie("outils/OUTILS.md présent avec une ligne par outil du maillon 0",
            (DEPOT / "outils" / "OUTILS.md").is_file()
            and all(o in (DEPOT / "outils" / "OUTILS.md").read_text(encoding="utf-8", errors="replace").lower()
                    for o in ("obsidian", "uv", "markitdown", "git", "gh", "buzz")))
    readme = (DEPOT / "README.md").read_text(encoding="utf-8") if (DEPOT / "README.md").is_file() else ""
    verifie("README.md porte les trois gestes : install du plugin, la phrase d'entrée, la clôture",
            "claude plugin install cortex@cortex-kit" in readme
            and "installe mon second cerveau" in readme.lower() and "clôture" in readme.lower())


# ── C11 : rangement (contrat 2.3) ──────────────────────────────────────────

# m1 : Path.unlink, Path.rename, Path.replace et os.rename comptent aussi ; `.replace("…")` d'une
# chaîne n'est pas un appel de fichier. Les mentions entre accents graves (docstrings) sont retirées.
INTERDITS_RANGE = re.compile(r"os\.(remove|unlink|replace|chdir|rename)\b|shutil\.(rmtree|copy|move)"
                             r"|\.(unlink|rename)\(|\.replace\((?![\"'])")


def appels_interdits(texte):
    return [l for l in texte.splitlines() if INTERDITS_RANGE.search(re.sub(r"`[^`]*`", "", l))]


def arbre_fichiers(*racines):
    """Chemins, tailles et dates des fichiers ; liste des dossiers (I-R1, I-R2)."""
    fichiers, dossiers = [], []
    for r in racines:
        for q in sorted(Path(r).rglob("*")):
            if q.is_dir():
                dossiers.append(str(q))
            else:
                st = q.stat()
                fichiers.append((str(q), st.st_size, st.st_mtime))
    return fichiers, dossiers


def c11_rangement(tmp, configs):
    section("C11", "Rangement, dossier commun, procédures (contrat 2.3 ; lane rangement) : défaut plausible : "
                   "un rangement qui supprime, écrase, copie une procédure ou casse les liens")
    if not RANGE.is_file():
        verifie("range.py présent", False, "attendu au merge de la lane rangement")
        return
    r = lancer(RANGE, "--autotest", timeout=180)
    verifie("range.py --autotest sort en 0 (G1 à G9 dans les deux sens, I-R1 à I-R3)", r.returncode == 0,
            (r.stdout + r.stderr)[-400:])

    # Appels interdits : seules les exceptions d'annulation, chacune commentée ; témoin sur un fichier jetable.
    lignes = appels_interdits(RANGE.read_text(encoding="utf-8"))
    fautives = [l for l in lignes if not (("os.remove(" in l and "exception 2 du contrat §5" in l)
                                          or ("os.rename(" in l and "# exception :" in l)
                                          or "# auto-test :" in l)]
    verifie("range.py : aucun appel interdit (remove, unlink, replace, rename, chdir, rmtree, copy, move, "
            "Path compris) hors des exceptions commentées et des gestes de l'auto-test",
            lignes and not fautives, str(fautives or lignes))
    jetable = tmp / "jetable.py"
    jetable.write_text("import os\nos.remove(x)\np.unlink()\np.replace(q)\nos.rename(a, b)\n"
                       "s.replace('a', 'b')\n", encoding="utf-8")
    verifie("témoin : le même motif trouve os.remove, Path.unlink, Path.replace et os.rename dans un fichier "
            "jetable, pas str.replace", len(appels_interdits(jetable.read_text(encoding="utf-8"))) == 4)

    # Garde mordante : G1 désactivée dans une copie jetable de range.py, l'auto-test rougit.
    copie = tmp / "range-perturbe"
    copie.mkdir()
    shutil.copyfile(SCRIPTS / "cortex_config.py", copie / "cortex_config.py")
    src = RANGE.read_text(encoding="utf-8")
    perturbe = src.replace('if o["geste"] != "ecrire_index" and os.path.lexists(vers):',
                           'if False and o["geste"] != "ecrire_index" and os.path.lexists(vers):')
    (copie / "range.py").write_text(perturbe, encoding="utf-8")
    r = lancer(copie / "range.py", "--autotest", timeout=180)
    verifie("témoin : G1 désactivée dans une copie jetable, l'auto-test rougit", perturbe != src and r.returncode != 0,
            f"code {r.returncode}")

    # La fixture dirigeant, copiée hors du dépôt : un arbre en désordre et un dossier partagé.
    # Hors du dépôt, parce qu'un dossier qui se trouve dans un dépôt git ne se range pas (§6) :
    # copiée sous recette/fixtures/, elle ne recevrait aucune proposition.
    base = tmp / "rangement"
    shutil.rmtree(base, ignore_errors=True)
    perso, commun = base / "dirigeant", base / "dirigeant-commun"
    shutil.copytree(FIXTURES / "dirigeant", perso)
    shutil.copytree(FIXTURES / "dirigeant-commun", commun)
    attendu = json.loads((perso / "RANGEMENT.json").read_text(encoding="utf-8"))
    atelier = base / "_cortex"
    atelier.mkdir()
    cfg_txt = configs["dirigeant"][0].read_text(encoding="utf-8").replace(
        'racines: ["' + tilde(FIXTURES / "dirigeant") + '", "~/Desktop/Travail"]',
        f'racines: ["{tilde(perso)}", "{tilde(commun)}"]\n  partagees: ["{tilde(commun)}"]')
    cfg_txt += 'referentiel:\n  etat: aucun\n  chemin: ""\n'
    (atelier / "config.yaml").write_text(cfg_txt, encoding="utf-8")
    (atelier / "02-ontologie.md").write_text(FM_ATELIER.format(m=3, p="cortex-3-ontologie", s="valide", v="passe"),
                                             encoding="utf-8")
    verifie("la config de la fixture rangement est installable", not cortex_config.valider_installable(
        cortex_config.charger(atelier / "config.yaml")), str(cortex_config.valider_installable(
            cortex_config.charger(atelier / "config.yaml"))[:2]))
    liste = base / "en-ligne.txt"
    liste.write_text("\n".join(str(perso / c) for c in attendu["en_ligne_seulement"]) + "\n", encoding="utf-8")
    env = dict(os.environ, CORTEX_RECETTE_EN_LIGNE=str(liste))

    def ranger(*args):
        return subprocess.run([sys.executable, str(RANGE), "--atelier", str(atelier), *args],
                              capture_output=True, text=True, timeout=120, env=env)
    avant = arbre_fichiers(perso, commun)
    r1 = ranger("--proposer")
    t1 = [l for l in (atelier / "03-rangement.json").read_text(encoding="utf-8").splitlines() if "genere_le" not in l]
    r2 = ranger("--proposer")
    t2 = [l for l in (atelier / "03-rangement.json").read_text(encoding="utf-8").splitlines() if "genere_le" not in l]
    verifie("deux propositions sur la même fixture rendent la même liste, genere_le excepté",
            r1.returncode == r2.returncode == 0 and t1 == t2, (r1.stderr or r2.stderr)[:200])
    verifie("proposer ne touche à rien", arbre_fichiers(perso, commun) == avant)
    plan = json.loads((atelier / "03-rangement.json").read_text(encoding="utf-8"))
    par = {}
    for o in plan["operations"]:
        par[Path(os.path.expanduser(o.get("de") or o["vers"])).relative_to(base).as_posix()] = o
    texte_plan = json.dumps(plan, ensure_ascii=False)
    verifie("la liste relève les noms illisibles, la procédure à demander, celle de l'entreprise, le dossier commun",
            all(f"dirigeant/{c}" in par and par[f"dirigeant/{c}"]["geste"] == "renommer" for c in attendu["renommer"])
            and par["dirigeant/PROCESS-affaire.md"]["classe"] == "a_demander"
            and par["dirigeant/PROCESS-affaire.md"]["geste"] == "manuel"
            and par["dirigeant-commun/Divers/Process facturation.docx"]["classe"] == "entreprise"
            and par["dirigeant-commun/Divers/Process facturation.docx"]["geste"] == "deplacer"
            and any(o["geste"] == "creer_dossier" for o in plan["operations"])
            and any(o["geste"] == "ecrire_index" for o in plan["operations"]), str(sorted(par))[:300])
    verifie("aucun champ contenu dans la liste, aucun lot de plus de quatre lignes",
            "contenu" not in cles_recursives(plan)
            and max(sum(1 for o in plan["operations"] if o["lot"] == n) for n in {o["lot"] for o in plan["operations"]}) <= 4)
    scan = par["dirigeant/Clients/Scan_0042.pdf"]
    doc = par["dirigeant/Clients/Nouveau document (3).docx"]
    verifie("G6 : le fichier en ligne seulement n'est pas ouvert (nom tiré du dossier), le fichier local l'est (titre lu)",
            Path(scan["vers"]).name.startswith("Clients - ") and "Accueil d'un nouveau client" in doc["vers"]
            and any(x["type"] == "en_ligne_seulement" for x in plan["signalements"]), scan["vers"] + " / " + doc["vers"])
    verifie("le doublon probable se signale, il ne devient pas un geste",
            any(x["type"] == "doublon_probable" and all(attendu["doublon"] in c for c in x["chemins"])
                for x in plan["signalements"]) and "tarifs" not in " ".join(o["vers"] for o in plan["operations"]))
    verifie("I-R4 : la liste ne porte aucune adresse de base en ligne", "http" not in texte_plan)

    # Refus entier : statut refuse, étape arbitrée.
    r = ranger("--clore", "refuse")
    e3b = {e["numero"]: e for e in m_etat.generer(atelier)["etapes"]}["3b"]
    verifie("un refus entier écrit statut: refuse, l'étape vaut arbitré « refusé »",
            r.returncode == 0 and "statut: refuse" in (atelier / "03-rangement.md").read_text(encoding="utf-8")
            and e3b["etat"] == "arbitre" and e3b.get("raison") == "refusé", f"{r.stderr[:200]} {e3b}")

    # Appliquer tout ce qui est à soi, puis le lot partagé avec accord renforcé.
    ranger("--proposer")
    plan = json.loads((atelier / "03-rangement.json").read_text(encoding="utf-8"))
    a_soi = [o["id"] for o in plan["operations"] if not o["partage"] and o["geste"] == "renommer"]
    partages = [o["id"] for o in plan["operations"] if o["partage"] and o["geste"] != "manuel"]
    rg = ranger("--appliquer", "--ids", ",".join(partages))
    verifie("G2 : le lot partagé sans accord renforcé rend 3 et laisse l'arbre identique",
            rg.returncode == 3 and arbre_fichiers(perso, commun) == avant, rg.stderr[:200])
    n_avant = len(avant[0])
    # B1 : lot par lot, comme la skill les présente ; chaque lot s'applique seul.
    codes = []
    for lot in sorted({o["lot"] for o in plan["operations"]}):
        ids_lot = [o for o in plan["operations"] if o["lot"] == lot and o["geste"] != "manuel"
                   and o["classe"] != "a_demander"]
        if ids_lot:
            r = ranger("--appliquer", "--ids", ",".join(o["id"] for o in ids_lot),
                       *(["--renforce"] if any(o["partage"] for o in ids_lot) else []))
            codes.append((lot, r.returncode, r.stderr[:150]))
    apres = arbre_fichiers(perso, commun)
    verifie("B1 : chaque lot s'applique seul, dans l'ordre de la liste (la création précède ce qui en dépend)",
            codes and all(c == 0 for _, c, _ in codes), str(codes))
    sommaire = (commun / "Référentiel" / "AGENTS.md").read_text(encoding="utf-8") \
        if (commun / "Référentiel" / "AGENTS.md").is_file() else ""
    objets = ["Facturation d'une affaire", "Relance d'un client", "Commande à un fournisseur",
              "Réception d'un chantier", "Archivage d'une affaire"]
    verifie("B1 : après le passage lot par lot, le sommaire liste les cinq procédures d'entreprise",
            len(attendu["entreprise"]) >= 5 and all(o in sommaire for o in objets),
            str([o for o in objets if o not in sommaire]))
    verifie("I-R1 : autant de fichiers après l'application, plus le seul sommaire du dossier commun",
            len(apres[0]) == n_avant + 1 and bool(sommaire), f"{len(apres[0])} contre {n_avant} + 1")
    pivot = m_etat.generer(atelier)
    verifie("etat.json d'un atelier de recette compte dix étapes", len(pivot["etapes"]) == 10)
    rv = ranger("--verifier")
    verifie("--verifier sort en 0 après application", rv.returncode == 0, rv.stdout[-300:])

    # A4 : le geste manuel en attente prive la source de note ; constaté, elle la reçoit.
    sys.path.insert(0, str(RANGE.parent))
    import importlib
    m_range = importlib.import_module("range")   # note_autorisee : la décision du remplissage (A4)
    ranger("--classer", par["dirigeant/PROCESS-affaire.md"]["id"] + "=entreprise")
    proc = perso / "PROCESS-affaire.md"
    sans_note = not m_range.note_autorisee(atelier, proc)
    manuel = next(o for o in json.loads((atelier / "03-rangement.json").read_text(encoding="utf-8"))["operations"]
                  if o["id"] == par["dirigeant/PROCESS-affaire.md"]["id"])
    dest = Path(os.path.expanduser(manuel["vers"]))
    os.rename(proc, dest)                         # la personne, dans son outil de partage
    rv = ranger("--verifier")
    trad = json.loads(ranger("--chemins").stdout)["traductions"]
    verifie("A4 : un geste manuel en attente prive la source de note ; constaté par --verifier, elle la reçoit "
            "sur le nouveau chemin",
            sans_note and rv.returncode == 0 and m_range.note_autorisee(atelier, proc)
            and trad.get(tilde(proc)) == tilde(dest), f"{sans_note} {rv.stdout[-200:]} {trad}")
    os.rename(dest, proc)

    # Le maillon 4 refuse un rangement appliqué en partie ; il construit une fois la ligne retirée.
    fm = (atelier / "03-rangement.md").read_text(encoding="utf-8")
    suspendue = "r999"           # une ligne acceptée, jamais faite
    (atelier / "03-rangement.md").write_text(re.sub(r"acceptees: \[(.*?)\]", lambda m: f"acceptees: [{m.group(1)}, {suspendue}]",
                                                    fm, count=1), encoding="utf-8")
    plan = json.loads((atelier / "03-rangement.json").read_text(encoding="utf-8"))
    plan["operations"].append(dict(plan["operations"][0], id=suspendue))
    (atelier / "03-rangement.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    vault = tmp / "vault-rangement"
    r4 = scaffold("--config", str(atelier / "config.yaml"), "--out", str(vault))
    e3b = {e["numero"]: e for e in m_etat.generer(atelier)["etapes"]}["3b"]
    verifie("le maillon 4 refuse quand le rangement est appliqué en partie (une ligne faite, une acceptée non faite)",
            r4.returncode == 2 and "rangement" in r4.stderr and e3b["etat"] == "en_cours" and not vault.exists(),
            f"code {r4.returncode} {e3b['etat']} {r4.stderr[:200]}")
    ranger("--annuler", "--ids", suspendue)
    plan["operations"].pop()
    (atelier / "03-rangement.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

    # M1 (scénario x1 de l'audit) : tout est fait, rien en suspens, pas de clôture.
    e3b = {e["numero"]: e for e in m_etat.generer(atelier)["etapes"]}["3b"]
    r4 = scaffold("--config", str(atelier / "config.yaml"), "--out", str(vault))
    verifie("M1 : fait sans clôture, l'étape vaut en_cours ; le maillon 4 refuse et donne « rangeons mes dossiers »",
            e3b["etat"] == "en_cours" and "pas encore conclu" in e3b.get("raison", "")
            and r4.returncode == 2 and "rangeons mes dossiers" in r4.stderr and not vault.exists(),
            f"{e3b} {r4.returncode} {r4.stderr[:200]}")

    # Clôture : le dossier commun créé s'inscrit dans config.yaml ; le vault le cite en forme ~.
    rc = ranger("--clore", "applique")
    conf = cortex_config.charger(atelier / "config.yaml")
    verifie("--clore applique inscrit le dossier commun créé (existant, chemin ~), config toujours installable",
            rc.returncode == 0 and conf["referentiel"]["etat"] == "existant"
            and conf["referentiel"]["chemin"] == tilde(commun / "Référentiel")
            and not cortex_config.valider_installable(conf), rc.stderr[:200] + str(conf.get("referentiel")))
    # La construction se fait sur une copie de l'atelier : l'original sert ensuite à défaire (I-R2).
    construit = base / "_cortex-construit"
    shutil.copytree(atelier, construit)
    r4 = scaffold("--config", str(construit / "config.yaml"), "--out", str(vault))
    verifie("témoin : la ligne retirée et le rangement clos, le maillon 4 construit", r4.returncode == 0, r4.stderr[:300])
    apres_construction = [subprocess.run([sys.executable, str(RANGE), "--atelier", str(construit), *a],
                                         capture_output=True, text=True, timeout=120, env=env)
                          for a in (["--proposer"], ["--annuler"])]
    fm3 = (construit / "03-rangement.md").read_text(encoding="utf-8")
    verifie("D3 : la construction inscrit construit_le ; le rangement refuse ensuite de proposer et de défaire (code 3)",
            "construit_le:" in fm3 and "statut: applique" in fm3
            and all(r.returncode == 3 and "construit" in r.stderr for r in apres_construction),
            str([(r.returncode, r.stderr[:100]) for r in apres_construction]))
    claude = (vault / "CLAUDE.md").read_text(encoding="utf-8") if (vault / "CLAUDE.md").is_file() else ""
    moustaches = [str(q.relative_to(vault)) for q in vault.rglob("*.md")
                  if "Templates" not in q.parts and re.search(r"\{\{[A-Z_]+\}\}", q.read_text(encoding="utf-8"))]
    verifie("scaffold avec dossier commun : aucun {{…}} de scaffold, le chemin du dossier commun en forme ~ dans CLAUDE.md",
            r4.returncode == 0 and not moustaches and tilde(commun / "Référentiel") in claude
            and "/Users/" not in claude, f"{r4.stderr[:200]} {moustaches[:3]}")
    # M4 : sur le même vault, la note Référentiel commun existe et aucune note ne porte une procédure
    # d'entreprise ; témoin : une note jetable qui en porte une est vue par le même contrôle.
    def notes_de_procedure(racine):
        return [str(q.relative_to(racine)) for q in Path(racine).rglob("*.md")
                if any(o in q.read_text(encoding="utf-8", errors="replace") for o in objets)]
    note_ref = vault / "50 - Ressources" / "Référentiel commun.md"
    lv = lint(vault)
    verifie("M4 : le vault construit porte la note Référentiel commun et aucune note par procédure d'entreprise ; "
            "lint à 0",
            note_ref.is_file() and "ressource: referentiel" in note_ref.read_text(encoding="utf-8")
            and not notes_de_procedure(vault) and lv.returncode == 0, f"{notes_de_procedure(vault)} {lv.stdout[-300:]}")
    copie_v = tmp / "vault-temoin-procedure"
    (copie_v / "50 - Ressources" / "Procédures").mkdir(parents=True)
    (copie_v / "50 - Ressources" / "Procédures" / "Facturation.md").write_text(
        f"---\ntype: ressource\n---\n# {objets[0]}\n", encoding="utf-8")
    verifie("témoin M4 : une note de procédure d'entreprise posée dans un vault jetable est trouvée",
            notes_de_procedure(copie_v) == [str(Path("50 - Ressources") / "Procédures" / "Facturation.md")])
    temoin = tmp / "gabarit-jetable.md"
    temoin.write_text("Dossier commun : {{REFERENTIEL}}\n", encoding="utf-8")
    verifie("témoin : un gabarit jetable qui garde {{REFERENTIEL}} est vu par le même contrôle",
            bool(re.search(r"\{\{[A-Z_]+\}\}", temoin.read_text(encoding="utf-8"))))
    sans_ref = tmp / "vault-sans-referentiel"
    r4 = scaffold("--config", str(configs["dirigeant"][0]), "--out", str(sans_ref))
    claude = (sans_ref / "CLAUDE.md").read_text(encoding="utf-8") if (sans_ref / "CLAUDE.md").is_file() else ""
    verifie("scaffold sans dossier commun : « Aucun dossier commun déclaré. », aucun {{…}}",
            r4.returncode == 0 and "Aucun dossier commun déclaré." in claude and "{{REFERENTIEL}}" not in claude,
            r4.stderr[:200])

    # I-R2 : appliquer puis annuler rend l'arbre d'avant ; témoin, un touch entre les deux.
    jalon = perso / "README.md"
    st = jalon.stat()
    os.utime(jalon, (st.st_atime, st.st_mtime + 30))
    ru = ranger("--annuler")
    touche = arbre_fichiers(perso, commun) != avant
    os.utime(jalon, (st.st_atime, st.st_mtime))
    verifie("I-R2 : appliquer puis annuler rend chemins, tailles et dates d'avant ; témoin : un fichier touché "
            "entre les deux fait différer la comparaison",
            ru.returncode == 0 and touche and arbre_fichiers(perso, commun) == avant, (ru.stdout + ru.stderr)[-300:])
    conf_apres = cortex_config.charger(atelier / "config.yaml")
    verifie("le dossier commun créé par Cortex et son sommaire disparaissent à l'annulation, et la config "
            "reprend sa valeur d'avant (aucun sommaire fantôme pour le vault)",
            not (commun / "Référentiel").exists() and conf_apres.get("referentiel") == {"etat": "aucun", "chemin": ""},
            str(conf_apres.get("referentiel")))

    # Config : les refus du contrat §1 et leur témoin.
    conf0 = cortex_config.charger(configs["dirigeant"][0])
    def refus(conf, cle):
        return any(e.startswith(cle) or cle in e for e in cortex_config.valider_installable(conf))
    struct = dict(conf0["donnees"], structurants=["organigramme", "process"])
    hors = dict(conf0, referentiel={"etat": "existant", "chemin": "~/Ailleurs/Référentiel"})
    sous = dict(conf0, collecte=dict(conf0["collecte"], partagees=["~/Pas/Declare"]))
    exemple = cortex_config.charger(RACINE / "template" / "config.example.yaml")
    verifie("cortex_config refuse un dossier commun hors racine, des dossiers partagés non déclarés ; accepte "
            "config.example.yaml, qui ne porte plus process",
            refus(hors, "referentiel") and refus(sous, "partagees")
            and not cortex_config.valider_installable(exemple)
            and "process" not in (exemple.get("donnees") or {}).get("structurants", []),
            str(cortex_config.valider_installable(exemple)[:2]))

    # T5 amendé : une config 2.2 qui porte encore process reste valide et verte au lint, avec un avertissement.
    conf22 = dict(conf0, donnees=struct)
    cfg22 = tmp / "config-2.2-process.yaml"
    cfg22.write_text(configs["dirigeant"][0].read_text(encoding="utf-8").replace(
        "structurants: [organigramme,", "structurants: [organigramme, process,"), encoding="utf-8")
    v22 = tmp / "vault-2.2"
    r22 = scaffold("--config", str(cfg22), "--out", str(v22))
    l22 = lint(v22) if r22.returncode == 0 else r22
    verifie("une config 2.2 avec process : validation sans erreur, avertissement « retiré en 2.3.0, ignoré », "
            "liste effective sans process, installation et lint à 0",
            not cortex_config.valider_installable(conf22)
            and any("retiré en 2.3.0, ignoré" in x for x in cortex_config.avertissements(conf22))
            and "process" not in cortex_config.structurants_effectifs(conf22)
            and "process" in cortex_config.charger(cfg22)["donnees"]["structurants"]
            and r22.returncode == 0 and "retiré en 2.3.0" in r22.stdout and l22.returncode == 0,
            f"{r22.returncode} {r22.stderr[:200]} lint {l22.returncode} {l22.stdout[-200:]}")

    # Une procédure ne se copie jamais ; un contrat, si (assertion négative et sa positive).
    vault_copie = tmp / "vault-copie"
    source = ATELIER_RECETTE / "sources" / "Process relance.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("# Relance d'un impayé\n\nÉtapes.\n", encoding="utf-8")
    rp = lancer(COPIE, "--vault", str(vault_copie), "--source", str(source), "--type", "process", "--domaine", "Agencement magasin")
    rc = lancer(COPIE, "--vault", str(vault_copie), "--source", str(source), "--type", "contrat", "--domaine", "Agencement magasin")
    structurants = vault_copie / "50 - Ressources" / "Structurants"
    verifie("copie_structurant refuse --type process en nommant la règle ; --type contrat sur la même source réussit (I-R5)",
            rp.returncode != 0 and "ne se copie jamais" in (rp.stderr + rp.stdout)
            and not (structurants / "process").exists()
            and rc.returncode == 0 and any((structurants / "contrat").glob("*.md")),
            f"{rp.returncode} {(rp.stderr + rp.stdout)[:200]} / {rc.returncode} {rc.stderr[:200]}")

    # Fédération : la clé referentiel donne la note et la ligne du Centre ; sans elle, ni l'une ni l'autre.
    groupe = ATELIER_RECETTE / "commun-referentiel"
    shutil.rmtree(groupe, ignore_errors=True)
    groupe.mkdir(parents=True)
    exps = {slug: export_fictif(ATELIER_RECETTE / "vaults-ref", slug, m_fixtures.CLIENTS[i:i + 2])
            for i, slug in ((0, "camille"), (2, "yasmine"))}
    fy = groupe / "federation.yaml"
    entete = 'version: 1\nnom: "Ateliers Roumier"\n'
    membres = "membres:\n" + "".join(f'  - {{ slug: {sl}, export: "{tilde(e)}" }}\n' for sl, e in exps.items())
    fy.write_text(entete + f'referentiel: "{tilde(commun / "Référentiel")}"\n' + membres, encoding="utf-8")
    g1 = lancer(FEDERE, "--config", str(fy))
    e1 = empreinte_commun(groupe)
    g2 = lancer(FEDERE, "--config", str(fy))
    note = groupe / "50 - Ressources" / "Référentiel commun.md"
    centre = (groupe / "00 - Centre" / "Centre.md").read_text(encoding="utf-8") if (groupe / "00 - Centre" / "Centre.md").is_file() else ""
    verifie("federe.py avec referentiel : la note Référentiel commun et sa ligne au Centre, deux générations identiques "
            "hors genere_le, aucune note par procédure",
            g1.returncode == g2.returncode == 0 and note.is_file() and "Référentiel commun" in centre
            and "ressource: referentiel" in note.read_text(encoding="utf-8") and empreinte_commun(groupe) == e1
            and not (groupe / "50 - Ressources" / "Procédures").exists(), (g1.stderr or g2.stderr)[:300])
    fy.write_text(entete + membres, encoding="utf-8")
    g3 = lancer(FEDERE, "--config", str(fy))
    centre = (groupe / "00 - Centre" / "Centre.md").read_text(encoding="utf-8")
    verifie("federe.py sans referentiel : ni la note ni la ligne du Centre",
            g3.returncode == 0 and not note.exists() and "Référentiel commun" not in centre, g3.stderr[:200])

    # Prose : Notice identique, doctrine, cd, white-label et chemins absolus sur la nouvelle skill.
    def notice(p):
        t = p.read_text(encoding="utf-8")
        return t[t.index("## Notice"):]
    skill3b = SKILLS / "cortex-3b-rangement" / "SKILL.md"
    verifie("la section Notice de cortex-3b-rangement est identique octet pour octet à celle de cortex-3-ontologie",
            notice(skill3b) == notice(SKILLS / "cortex-3-ontologie" / "SKILL.md"))
    doctrine = (SKILLS / "cortex-1-cadrage" / "references" / "doctrine.md").read_text(encoding="utf-8")
    s5 = doctrine[doctrine.index("## 5."):doctrine.index("## 6.")]
    verifie("doctrine : un §12, et un amendement daté 2026-10-04 au §5",
            len(re.findall(r"^## 12", doctrine, re.M)) == 1 and "2026-10-04" in s5)
    cd = [l for l in skill3b.read_text(encoding="utf-8").splitlines() if re.search(r"(^|[ ;&])cd [^.]", l)]
    verifie("cortex-3b-rangement/SKILL.md ne cite cd que pour l'interdire",
            all(re.search(r"\b(jamais|aucune|n'entre)\b", l, re.I) for l in cd), str(cd))
    couverts = [rel for _, rel in fichiers_texte(PERIMETRE_WHITE_LABEL) if rel.startswith("skills/cortex-3b-rangement/")]
    verifie("les contrôles white-label et « zéro chemin absolu » parcourent skills/cortex-3b-rangement/",
            {"skills/cortex-3b-rangement/SKILL.md", "skills/cortex-3b-rangement/scripts/range.py",
             "skills/cortex-3b-rangement/references/nomenclature.md"} <= set(couverts), str(couverts))
    verifie("la notice propose « rangeons mes dossiers » après la carte des domaines",
            m_etat.PHRASES.get("3b") == "rangeons mes dossiers"
            and "rangeons mes dossiers" in (SKILLS / "cortex-3-ontologie" / "SKILL.md").read_text(encoding="utf-8"))
    shutil.rmtree(base, ignore_errors=True)


# ── Tableau ─────────────────────────────────────────────────────────────────

def tableau():
    print("\nTableau C1 à C11 (contrôles passés / total)")
    for code, titre, contrat, lane in CRITERES:
        ok, xx = BILAN.get(code, [0, 0])
        etat = "VERT" if xx == 0 and ok else "ROUGE"
        print(f"  {code:<4} {titre:<50} {contrat:<12} lane {lane:<7} {ok:>2}/{ok + xx:<2} {etat}")
    for code, titre in MANUELS:
        print(f"  {code:<4} {titre:<50} manuel, sortie collée dans 06-verification.md")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="cortex-recette-"))
    print(f"Recette Cortex v2 : parcours à blanc\n(dossier temporaire : {tmp})\n")
    try:
        cfg_v1 = recette_v1(tmp)

        shutil.rmtree(ATELIER_RECETTE, ignore_errors=True)
        configs = {}
        for profil, regime, racine, extra in (
                ("employe", "copie", FIXTURES / "employe", {}),
                ("dirigeant", "pointeur", FIXTURES / "dirigeant",
                 {"base_projets": "https://base.exemple.test/affaires"}),
                ("societe", "pointeur", FIXTURES / "societe" / "camille",
                 {"mode": "federe", "commun_racine": tilde(ATELIER_RECETTE / "commun"), "code": "camille",
                  "redacteur": "Camille Roumier", "base_projets": "https://base.exemple.test/affaires"})):
            cfg = tmp / f"config-{profil}.yaml"
            racines = [tilde(racine)] + (["~/Desktop/Travail"] if profil == "dirigeant" else [])
            cfg.write_text(config_v2(profil, regime, racines, **extra), encoding="utf-8")
            configs[profil] = (cfg, regime)

        c1_neuf_etapes(tmp, configs["dirigeant"][0])
        c2_profils(tmp, configs)
        c3_inventaire(tmp, configs)
        vault_pointeur = c4_couche_vault(tmp, configs)
        c5_regimes(tmp, configs, vault_pointeur)
        c6_federation(tmp)
        c7_manifestes()
        c8_white_label()
        c9_chemins_absolus()
        c10_paquet(tmp)
        c11_rangement(tmp, configs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(ATELIER_RECETTE, ignore_errors=True)

    tableau()
    print(f"\n{len(succes)} contrôle(s) passé(s), {len(echecs)} en échec.")
    if echecs:
        print("EN ÉCHEC : " + ", ".join(echecs))
        return 1
    print("Recette verte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
