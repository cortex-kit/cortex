#!/usr/bin/env python3
"""Recette de non-regression de la chaine Cortex.

Rejoue en une commande ce que le parcours a blanc du 2026-08-17 a fait a la
main. Chaque assertion correspond a un defaut REEL trouve ce jour-la : si l'une
d'elles casse, c'est qu'un defaut deja paye est revenu.

Etendue le 2026-08-23 (phase 5, plug and play) : sections 9 a 11 — la conduite
solo/consultant, le pivot d'etat et ses rendus, le paquet distribuable. Chaque
controle neuf est attache a un defaut PLAUSIBLE, jamais a une intention.

    python3 recette/parcours_blanc.py        # sortie 0 = tout va bien
    (`py` vaut `python3` sous Windows)

Stdlib seule, aucun reseau, aucune ecriture hors d'un dossier temporaire —
le zip temoin de la section 11 compris.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPTS = RACINE / "scripts"
PAQUET = RACINE.parent / "cortex-paquet"
sys.path.insert(0, str(SCRIPTS))
import cortex_config  # noqa: E402

sys.path.insert(0, str(PAQUET / "scripts"))
import etat as m_etat          # noqa: E402
import fabrique as m_fabrique  # noqa: E402
import rend_deck as m_deck     # noqa: E402
import rend_notice as m_rend   # noqa: E402

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

        print("\n9. Conduite (defaut plausible : le mode solo reinterprete l'existant)")
        conf = cortex_config.charger(cfg)
        verifie("une config sans cle conduite s'installe en consultant",
                cortex_config.conduite(conf) == "consultant"
                and not any("conduite" in e
                            for e in cortex_config.valider_installable(conf)))
        # Defaut n5 (parcours a blanc novice, 2026-08-24) : un substrat declare
        # absent par `cle: ""  # aucun` etait lu non vide, donc pris pour present.
        gabarit = cortex_config.charger(RACINE / "template" / "config.example.yaml")
        quotes = {"commun.racine": gabarit.get("commun", {}).get("racine", "")}
        quotes.update({f"substrats.{c}": gabarit.get("substrats", {}).get(c, "")
                       for c in ("espace_documentaire", "base_projets", "git_remote")})
        verifie("un substrat vide suivi d'un commentaire est lu vide",
                all(v == "" for v in quotes.values()), str(quotes))
        verifie("un # entre guillemets survit au retrait des commentaires",
                cortex_config._scalaire('"a # b"  # com') == "a # b")

        inconnu = tmp / "config-conduite.yaml"
        inconnu.write_text(cfg.read_text(encoding="utf-8") + "conduite: duo\n",
                           encoding="utf-8")
        erreurs = cortex_config.valider_installable(cortex_config.charger(inconnu))
        verifie("une conduite inconnue est refusee et le message nomme la cle",
                any(e.startswith("conduite") for e in erreurs), str(erreurs[:2]))
        r = scaffold("--config", str(inconnu), "--out", str(tmp / "refus-conduite"))
        verifie("scaffold s'arrete sur une conduite inconnue", r.returncode == 2,
                r.stderr[:200])

        print("\n10. Pivot d'etat (defaut plausible : un tableau de bord qui ment)")
        atelier = tmp / "_cortex"
        atelier.mkdir()
        shutil.copyfile(cfg, atelier / "config.yaml")
        fm = ("---\nmaillon: {m}\nproduit_par: {p}\nstatut: {s}\ncontroles:\n"
              "  premier_controle: passe\n  second_controle: {v}\n---\n# x\n")
        (atelier / "00-cadrage.md").write_text(
            fm.format(m=1, p="cortex-1-cadrage", s="valide", v="passe"),
            encoding="utf-8")
        (atelier / "04-ingest.md").write_text(
            fm.format(m=5, p="cortex-5-ingest", s="brouillon", v="arbitre"),
            encoding="utf-8")

        def sans_horodatage(p):
            return "\n".join(l for l in p.read_text(encoding="utf-8").splitlines()
                             if '"genere_le"' not in l)

        p1, pivot = m_etat.ecrire(atelier, tmp / "pivot-1.json")
        p2, _ = m_etat.ecrire(atelier, tmp / "pivot-2.json")
        verifie("le pivot porte les sept etapes", len(pivot["etapes"]) == 7)
        verifie("le pivot se regenere a l'identique hors horodatage",
                sans_horodatage(p1) == sans_horodatage(p2))
        e4 = pivot["etapes"][3]
        # La raison s'adresse au novice : elle nomme ce que l'etape produit et
        # ce qui le prouve, sans les mots d'atelier (« vault », « lint »), que
        # la notice ne definit nulle part.
        verifie("le trou en 03 est porte avec sa raison en clair",
                e4["artefact"] is None
                and "second cerveau" in e4.get("raison", "")
                and "contrôle de santé" in e4.get("raison", "")
                and not {"vault", "lint"} & set(
                    e4.get("raison", "").lower().split()), str(e4))
        verifie("l'etape 4 se deduit d'un artefact aval, jamais devinee",
                e4["etat"] == "faite_deduite"
                and m_etat.generer(tmp)["etapes"][3]["etat"] == "a_faire")

        # Defaut n6 (parcours a blanc novice, 2026-08-24) : le compteur ignorait
        # `faite_deduite` et annoncait 6/7 quand les sept lignes etaient faites.
        complet = tmp / "_cortex-complet"
        complet.mkdir()
        shutil.copyfile(cfg, complet / "config.yaml")
        for nom, m, p in (("00-cadrage", 1, "cortex-1-cadrage"),
                          ("01-inventaire", 2, "cortex-2-inventaire"),
                          ("02-ontologie", 3, "cortex-3-ontologie"),
                          ("04-ingest", 5, "cortex-5-ingest"),
                          ("05-agents-metier", 6, "cortex-6-agents-metier"),
                          ("06-passation", 7, "cortex-7-passation")):
            (complet / f"{nom}.md").write_text(
                fm.format(m=m, p=p, s="valide", v="passe"), encoding="utf-8")
        pivot_complet = m_etat.generer(complet)
        verifie("le compteur annonce 7/7 quand les sept lignes sont faites",
                m_etat.faites(pivot_complet) == 7,
                str([e["etat"] for e in pivot_complet["etapes"]]))

        vierge = tmp / "atelier-vierge"
        vierge.mkdir()
        html_vierge = m_rend.rendre(m_etat.generer(vierge))
        verifie("le tableau de bord vierge affiche sept lignes a faire",
                html_vierge.count("À faire") == 7)
        verifie("aucune URL distante dans la notice",
                not re.search(r"https?://", html_vierge)
                and not re.search(r"""(href|src)\s*=\s*["']//""", html_vierge))

        deck = tmp / "deck.bento.html"
        m_deck.rendre(pivot, deck)
        doc = json.loads(re.search(
            r'<script type="application/bento\+json" id="bento-doc"[^>]*>(.*?)'
            r"</script>", deck.read_text(encoding="utf-8"), re.S)
            .group(1).replace("\\u003c", "<"))
        attendu = [{"numero": e["numero"], "nom": e["nom"], "etat": e["etat"],
                    "libelle": m_etat.LIBELLES.get(e["etat"], e["etat"])}
                   for e in pivot["etapes"]]
        corps = " ".join(el.get("html", "")
                         for s in doc["slides"] for el in s["elements"])
        verifie("le deck porte les memes etapes et les memes statuts que le "
                "tableau de bord",
                doc["meta"]["cortex_etapes"] == attendu
                and all(e["nom"] in corps for e in pivot["etapes"]))

        print("\n11. Le paquet (defaut plausible : un kit muet ou une fuite de licence)")
        zip_temoin = tmp / "cortex-temoin.zip"
        verifie("la fabrication sort en 0",
                m_fabrique.fabriquer(zip_temoin, version="recette") == 0)
        with zipfile.ZipFile(zip_temoin) as z:
            noms = z.namelist()
            dossiers = {n.split("/")[0] for n in noms if "/" in n}
            racine = {n for n in noms if "/" not in n}
            skills_md = [n for n in noms if n.endswith("SKILL.md")]
            prof1 = [n for n in skills_md if len(n.split("/")) == 2]
            prof2 = [n for n in skills_md if len(n.split("/")) == 3]
            plus_bas = [n for n in skills_md if len(n.split("/")) > 2
                        and not n.startswith("cortex-4-installation/template/")]
            verifie("le zip donne 13 dossiers et deux fichiers a la racine",
                    len(dossiers) == 13
                    and racine == {"LISEZ-MOI.html", "PROVENANCE.md"},
                    f"{len(dossiers)} dossiers, racine {sorted(racine)}")
            verifie("13 SKILL.md a la bonne profondeur", len(prof1) == 13,
                    str(sorted(prof1)))
            verifie("zero SKILL.md en profondeur 2 dans le zip — le critere "
                    "qui decide si le kit est vu ou muet",
                    not prof2 and not plus_bas, str(prof2 + plus_bas))

            kit = [l.strip() for l in (PAQUET / "kit.txt")
                   .read_text(encoding="utf-8").splitlines() if l.strip()]
            manquants = []
            for skill in kit:
                chemin = f"{skill}/SKILL.md"
                if chemin not in noms:
                    manquants.append(chemin)
                    continue
                lignes = z.read(chemin).decode("utf-8").splitlines()
                fin = next((i for i, l in enumerate(lignes[1:], 1)
                            if l.strip() == "---"), 0)
                cles = {l.split(":", 1)[0].strip()
                        for l in lignes[1:fin] if ":" in l}
                if not {"name", "description"} <= cles:
                    manquants.append(f"{chemin} (frontmatter incomplet)")
            verifie("chaque entree du manifeste est dans le zip avec un "
                    "frontmatter valide", not manquants, str(manquants))

            provenance = z.read("PROVENANCE.md").decode("utf-8")
            decouverts = [s for s in kit if not re.search(
                rf"^\|\s*{re.escape(s)}\s*\|.*\|\s*\**Oui\**.*\|\s*$",
                provenance, re.M)]
            verifie("chaque emprunt du zip est couvert par PROVENANCE.md",
                    not decouverts, str(decouverts))

            lisezmoi = z.read("LISEZ-MOI.html").decode("utf-8")
            verifie("LISEZ-MOI.html : sept etapes a faire, zero URL distante",
                    lisezmoi.count("À faire") == 7
                    and not re.search(r"https?://", lisezmoi)
                    and not re.search(r"""(href|src)\s*=\s*["']//""", lisezmoi))
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
