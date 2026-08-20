#!/usr/bin/env python3
"""Recette de non-regression de la chaine Cortex.

Rejoue en une commande ce que le parcours a blanc du 2026-08-17 a fait a la
main. Chaque assertion correspond a un defaut REEL trouve ce jour-la : si l'une
d'elles casse, c'est qu'un defaut deja paye est revenu.

    python3 recette/parcours_blanc.py        # sortie 0 = tout va bien

Stdlib seule, aucun reseau, aucune ecriture hors d'un dossier temporaire.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPTS = RACINE / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cortex_config  # noqa: E402

MARQUES = ["Cabinet-Exemple", "ClientAnterieurA", "ClientAnterieurB"]
succes, echecs = [], []


def verifie(nom, condition, detail=""):
    (succes if condition else echecs).append(nom)
    print(f"  [{'ok' if condition else 'XX'}] {nom}" + (f" — {detail}" if detail and not condition else ""))


def scaffold(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / "scaffold.py"), *args],
                          capture_output=True, text=True)


def lint(vault):
    return subprocess.run([sys.executable, str(SCRIPTS / "lint_sante.py"),
                           "--vault", str(vault)], capture_output=True, text=True)


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


def main():
    tmp = Path(tempfile.mkdtemp(prefix="cortex-recette-"))
    print(f"Recette Cortex — parcours a blanc\n(dossier temporaire : {tmp})\n")
    try:
        cfg = tmp / "config.yaml"
        cfg.write_text(CONFIG.format(marques=", ".join(MARQUES), domaines=DOMAINES_OK),
                       encoding="utf-8")
        vault = tmp / "vault"

        print("1. Config incomplete refusee (defaut : vault sans domaine valide partout)")
        vide = tmp / "config-vide.yaml"
        vide.write_text(CONFIG.format(marques="", domaines=DOMAINES_VIDE), encoding="utf-8")
        conf_vide = cortex_config.charger(vide)
        verifie("charger() accepte encore la config du maillon 1",
                cortex_config.charger(cfg) is not None)
        verifie("valider_installable() refuse domaines vide",
                any("domaines" in e for e in cortex_config.valider_installable(conf_vide)))
        r = scaffold("--config", str(vide), "--out", str(tmp / "refus"))
        verifie("scaffold refuse une config incomplete", r.returncode == 2, r.stderr[:200])

        print("\n2. Installation")
        r = scaffold("--config", str(cfg), "--out", str(vault))
        verifie("scaffold reussit", r.returncode == 0, r.stderr[:300])

        print("\n3. Fuite de white-label (defaut : mentions_interdites livree au client)")
        fuites = [str(p) for p in vault.rglob("*")
                  if p.is_file() and any(
                      m.lower() in p.read_text(encoding="utf-8", errors="replace").lower()
                      for m in MARQUES)]
        verifie("aucune mention interdite dans le vault livre", not fuites, str(fuites[:3]))

        print("\n4. Liens morts (defaut : Centre.md pointait vers des notes inexistantes)")
        domaines = sorted(p.name for p in (vault / "10 - Domaines").glob("*.md")
                          if p.name != "_README.md")
        verifie("une note par domaine est generee", len(domaines) == 2, str(domaines))
        verifie("lint vert sur vault neuf", lint(vault).returncode == 0)

        sonde = vault / "20 - Projets" / "MAG - Sonde.md"
        sonde.write_text(note_projet("Sonde", "mag", "Agencement magasin", "Signé", 30)
                         .replace("## Journal", "Voir [[Note Absente]].\n\n## Journal"),
                         encoding="utf-8")
        verifie("le lint detecte un lien mort reel", lint(vault).returncode == 1)
        sonde.unlink()
        verifie("aucun faux positif sur la syntaxe citee entre backticks",
                lint(vault).returncode == 0, lint(vault).stdout[-400:])

        print("\n5. Vault peuple : ingest puis protections")
        for titre, code, dom, phase, prog in AFFAIRES:
            (vault / "20 - Projets" / f"{code.upper()} - {titre}.md").write_text(
                note_projet(titre, code, dom, phase, prog), encoding="utf-8")
        verifie("lint vert sur vault peuple", lint(vault).returncode == 0,
                lint(vault).stdout[-500:])

        print("\n6. rm -rf sur vault peuple (defaut : --force detruisait le travail client)")
        r = scaffold("--config", str(cfg), "--out", str(vault), "--force")
        verifie("--force refuse d'ecraser un vault peuple", r.returncode == 2)
        verifie("les notes du client sont intactes",
                len(list((vault / "20 - Projets").glob("*.md"))) == len(AFFAIRES) + 1)

        print("\n7. Mise a jour de l'outillage (defaut : aucun chemin vers les vaults livres)")
        embarque = vault / ".claude" / "skills" / "lint" / "lint_sante.py"
        embarque.write_text("# version perimee\n", encoding="utf-8")
        r = scaffold("--config", str(cfg), "--out", str(vault), "--outillage-seul")
        verifie("--outillage-seul reussit", r.returncode == 0, r.stderr[:200])
        verifie("le lint embarque est reactualise",
                embarque.read_text(encoding="utf-8") ==
                (SCRIPTS / "lint_sante.py").read_text(encoding="utf-8"))
        verifie("le contenu du client a survecu",
                len(list((vault / "20 - Projets").glob("*.md"))) == len(AFFAIRES) + 1)

        print("\n8. Divers")
        restes = [str(p.relative_to(vault)) for p in vault.rglob("*.md")
                  if "Templates" not in p.parts
                  and any(c in p.read_text(encoding="utf-8", errors="replace")
                          for c in cortex_config.CLES_SCAFFOLD)]
        verifie("aucune moustache de scaffold residuelle", not restes, str(restes[:3]))
        absolus = [str(p.relative_to(vault)) for p in vault.rglob("*.md")
                   if "/Users/" in p.read_text(encoding="utf-8", errors="replace")]
        verifie("aucun chemin absolu dans les notes", not absolus, str(absolus[:3]))
        verifie("aucun plugin communautaire requis",
                not (vault / ".obsidian" / "community-plugins.json").exists())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{len(succes)} controle(s) passe(s), {len(echecs)} en echec.")
    if echecs:
        print("EN ECHEC : " + ", ".join(echecs))
        return 1
    print("Recette verte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
