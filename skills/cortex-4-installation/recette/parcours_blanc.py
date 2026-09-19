#!/usr/bin/env python3
"""Recette de non-regression de la chaine Cortex, v2 (lane G, 2026-09-19).

Sections 1 a 9 : la recette v1 (parcours a blanc du 2026-08-17, phase 5 du
2026-08-23), conservee telle quelle. Chaque assertion y correspond a un defaut
REEL deja paye.

Criteres C1 a C10 : la cible v2 (chantiers/cortex-v2/04-contrat.md). Chaque
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
import re
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
POSTE = SKILLS / "cortex-0-poste" / "scripts" / "poste.py"
SCAN = SKILLS / "cortex-2-inventaire" / "scripts" / "scan.py"
FEDERE = SKILLS / "cortex-8-federation" / "scripts" / "federe.py"

sys.path.insert(0, str(SCRIPTS))
import cortex_config  # noqa: E402
import etat as m_etat  # noqa: E402
import rend_notice as m_rend  # noqa: E402
sys.path.insert(0, str(RECETTE))
import fixtures as m_fixtures  # noqa: E402
sys.path.insert(0, str(PAQUET / "scripts"))
import fabrique as m_fabrique  # noqa: E402
try:
    import rend_deck as m_deck  # noqa: E402
except SystemExit:
    m_deck = None  # la skill presentation est sortie du kit le 2026-09-19

MARQUES = ["Cabinet-Exemple", "ClientAnterieurA", "ClientAnterieurB"]
# Marques interdites (01-cadrage.md §Marques interdites) : sha256 tronque de la
# forme normalisee (minuscules, sans accent, mots separes par une espace). Le
# depot est public : la liste en clair y serait elle-meme la fuite. La liste en
# clair vit chez le chef d'orchestre ; recalculer une empreinte :
#   python3 -c "import hashlib;print(hashlib.sha256(b'mot').hexdigest()[:16])"
MARQUES_EMPREINTES = {
    "2d697f1957a17471", "1e194652dcdd105b", "4025a3e9f03aa9b1", "6cd31a74b6e31ff0",
    "f597568fba670b35", "06349320320a2272", "be428d22548ae2ea", "e3dfc76ed288d592",
    "4cbe19716b1aa73a", "35f85825b9016fcc",
}
PERIMETRE_WHITE_LABEL = [SKILLS, DEPOT / "notice", DEPOT / "outils", DEPOT / "README.md"]
BINAIRES = {".zip", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".xlsx", ".pyc", ".woff", ".woff2", ".ttf"}
PROFILS = ("employe", "dirigeant", "societe")
ETAPES_CONTRAT = {0: "poste.json", 1: "00-cadrage.md", 2: "01-inventaire.md", 3: "02-ontologie.md",
                  4: None, 5: "04-ingest.md", 6: "05-agents-metier.md", 7: "06-passation.md",
                  8: "07-federation.md"}
CRITERES = [
    ("C1", "Neuf étapes, maillon 0, notice", "§3 §5 §10", "B"),
    ("C2", "Trois profils, régime, section Notice", "§2 §10", "C"),
    ("C3", "Inventaire outillé sur les fixtures", "§4", "D"),
    ("C4", "Couche vault : permissions, hooks, skills, agents", "§9", "E"),
    ("C5", "Régimes pointeur et copie, structurant périmé", "§2", "E"),
    ("C6", "Fédération sur trois exports fictifs", "§6", "F"),
    ("C7", "Manifestes plugin", "§11", "chef"),
    ("C8", "White-label", "01-cadrage", "toutes"),
    ("C9", "Zéro chemin absolu", "I2, §11", "toutes"),
    ("C10", "Paquet, notice hors ligne, README", "§11", "B"),
]
MANUELS = [("M1", "Installation vivante du plugin (marketplace add, install, details)"),
           ("M2", "Sonde Cowork bureau : uvx markitdown --version dans le bac à sable"),
           ("M3", "Maillon 0 et installation du plugin sur la machine Windows")]

succes, echecs, ignores = [], [], []
BILAN = {}
CRITERE = "v1"


def verifie(nom, condition, detail=""):
    (succes if condition else echecs).append(f"{CRITERE} {nom}")
    BILAN.setdefault(CRITERE, [0, 0])[0 if condition else 1] += 1
    print(f"  [{'ok' if condition else 'XX'}] {nom}" + (f" : {detail}" if detail and not condition else ""))


def ignore(nom, raison):
    ignores.append(nom)
    print(f"  [--] {nom} : {raison}")


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
  structurants: [organigramme, process, fiche_de_poste, contrat, projet, acteur, tenants_aboutissants, fil_structurant]
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
  skills: [cloture, nouveau-projet, ingest, lint, parle, bilan]
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
         "options_proposees": ["wispr-flow", "superwhisper", "noota", "graphify"],
         "mail": {"fournisseur": "gmail", "boites": 1, "voie": "connecteur",
                  "domaine": "exemple.test", "mx": "aspmx.l.google.com"},
         "notice_ouverte_le": "2026-09-19T10:12:03" if notice_ouverte else ""}
    return json.dumps(p, ensure_ascii=False, indent=2)


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


def empreinte_commun(commun):
    """Contenu du commun, hors horodatages : ce qui doit etre identique d'une generation a l'autre."""
    out = {}
    for p in sorted(Path(commun).rglob("*")):
        if p.is_file():
            texte = p.read_text(encoding="utf-8", errors="replace")
            out[p.relative_to(commun).as_posix()] = "\n".join(
                l for l in texte.splitlines() if "genere_le" not in l and "généré par" not in l)
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
    return cfg


# ── C1 : neuf etapes ────────────────────────────────────────────────────────

def c1_neuf_etapes(tmp, cfg):
    section("C1", "Neuf étapes, maillon 0, notice (§3 §5 §10 ; lane B) : défaut plausible : "
                  "un tableau de bord qui compte sept quand la chaîne en a neuf")
    verifie("etat.py porte neuf étapes numérotées 0 à 8", [e[0] for e in m_etat.ETAPES] == list(range(9)),
            str([e[0] for e in m_etat.ETAPES]))
    verifie("les artefacts des neuf étapes sont ceux du contrat §5",
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
    verifie("le pivot porte les neuf étapes", len(pivot["etapes"]) == 9, str(len(pivot["etapes"])))
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
    pivot_complet = m_etat.generer(complet)
    verifie("le compteur annonce 9/9 quand les neuf lignes sont faites", m_etat.faites(pivot_complet) == 9,
            str([e["etat"] for e in pivot_complet["etapes"]]))

    vierge = tmp / "atelier-vierge"
    vierge.mkdir()
    html_vierge = m_rend.rendre(m_etat.generer(vierge))
    verifie("le tableau de bord vierge affiche neuf lignes à faire", html_vierge.count("À faire") == 9,
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
        motif = re.compile(r"^\S.*? : absent → .+$")
        verifie("poste.py --dry-run sort en 0 et n'imprime qu'une ligne par outil absent, avec sa commande",
                r.returncode == 0 and all(motif.match(l) for l in lignes),
                (r.stderr[:200] or str([l for l in lignes if not motif.match(l)][:3])))
    else:
        verifie("poste.py présent", False, "attendu au merge de la lane B")

    if m_deck is None:
        ignore("le deck porte les mêmes étapes que le tableau de bord",
               "skill presentation retirée du kit le 2026-09-19, rend_deck.py sans rendu")
    else:
        deck = tmp / "deck.bento.html"
        m_deck.rendre(pivot, deck)
        doc = json.loads(re.search(r'<script type="application/bento\+json" id="bento-doc"[^>]*>(.*?)</script>',
                                   deck.read_text(encoding="utf-8"), re.S).group(1).replace("\\u003c", "<"))
        attendu = [{"numero": e["numero"], "nom": e["nom"], "etat": e["etat"],
                    "libelle": m_etat.LIBELLES.get(e["etat"], e["etat"])} for e in pivot["etapes"]]
        corps = " ".join(el.get("html", "") for s in doc["slides"] for el in s["elements"])
        verifie("le deck porte les mêmes étapes et les mêmes statuts que le tableau de bord",
                doc["meta"]["cortex_etapes"] == attendu and all(e["nom"] in corps for e in pivot["etapes"]))


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
    verifie("neuf SKILL.md maillons, chacun avec la section Notice et l'appel de notice.py (I10)",
            len(maillons) == 9 and not sans_notice, f"{len(maillons)} maillons, sans notice : {sans_notice}")
    longs = [(m.parent.name, len(m.read_text(encoding="utf-8").splitlines())) for m in maillons
             if len(m.read_text(encoding="utf-8").splitlines()) >= 300]
    verifie("chaque SKILL.md maillon fait moins de 300 lignes", not longs, str(longs))


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
        verifie(f"scan {profil} : disque non vide, chemins en forme ~, source_id et substrat portés",
                disque and all(str(d.get("chemin", "")).startswith("~/") and d.get("source_id") and d.get("substrat")
                               for d in disque), str(disque[:1]))
        if profil == "employe":
            verifie("employé : export-notion-*.csv apparaît comme signal de base déportée",
                    "export-notion" in texte and "base_deportee" in texte)


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
    verifie("une règle deny Write et Edit par racine",
            racines and all(f"Write({r}/**)" in deny and f"Edit({r}/**)" in deny for r in racines), str(deny))
    verifie("aucune règle allow n'ouvre Write, Edit ni un Bash libre",
            not any(a in ("Write", "Edit", "Bash") or a.startswith(("Write(", "Edit(")) for a in allow), str(allow))
    hooks = settings.get("hooks") or {}
    verifie("hooks SessionStart et Stop présents dans settings.json",
            bool(hooks.get("SessionStart")) and bool(hooks.get("Stop")), str(list(hooks)))
    verifie("SessionStart lance le lint bref, Stop rappelle la clôture",
            "lint_sante.py" in json.dumps(hooks.get("SessionStart", ""))
            and "--bref" in json.dumps(hooks.get("SessionStart", ""))
            and re.search(r"cl[oô]ture", json.dumps(hooks.get("Stop", ""), ensure_ascii=False), re.I) is not None)
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
    hits = [f"{rel}:{no}" for p, rel in fichiers_texte(PERIMETRE_WHITE_LABEL)
            for no, l in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if motif.search(l)]
    verifie("aucun chemin absolu (/Users/, /home/, lettre de lecteur) dans skills/ notice/ outils/ README.md",
            not hits, f"{len(hits)} ligne(s) : {hits[:6]}")
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
        verifie("LISEZ-MOI.html du zip : neuf étapes à faire, zéro URL distante",
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


# ── Tableau ─────────────────────────────────────────────────────────────────

def tableau():
    print("\nTableau C1 à C10 (contrôles passés / total)")
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(ATELIER_RECETTE, ignore_errors=True)

    tableau()
    print(f"\n{len(succes)} contrôle(s) passé(s), {len(echecs)} en échec, {len(ignores)} ignoré(s).")
    if echecs:
        print("EN ÉCHEC : " + ", ".join(echecs))
        return 1
    print("Recette verte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
