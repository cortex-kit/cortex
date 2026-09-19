#!/usr/bin/env python3
"""fixtures.py — trois arbres de fichiers fictifs pour la recette. stdlib, déterministe.

employe/    Camille Perrin, cheffe de projet chez Nordaline (PME fictive) : ~150 fichiers,
            cinq écarts injectés, listés dans ECARTS.json (ce que l'entretien du maillon 3
            doit relever entre ce que la personne déclare et ce que l'inventaire montre).
dirigeant/  Ateliers Roumier, menuiserie d'agencement : ~374 fichiers.
societe/    Ateliers Roumier vus par trois rédacteurs (camille, yasmine, marc), pour la
            fédération : deux affaires apparaissent chez deux rédacteurs.

Contenu minimal généré, jamais un document réel. Les .docx, .xlsx et .pdf sont valides
(un titre dedans, de quoi être lus par un convertisseur), les .eml portent des en-têtes
et une ligne, les .md une phrase. Dates fixées par os.utime, graine fixe : deux
générations donnent le même arbre.

Usage : python3 fixtures.py [--out <dossier>]
        défaut : <ce dossier>/fixtures/, ignoré par git.
"""

import argparse
import json
import os
import random
import shutil
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

GRAINE = 20260919
BASE = datetime(2026, 9, 1, 9, 0)
_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


# ── Générateurs de contenu minimal ──────────────────────────────────────────

def _ooxml(chemin, parties):
    with zipfile.ZipFile(chemin, "w", zipfile.ZIP_DEFLATED) as z:
        for nom, xml in parties.items():
            z.writestr(nom, _XML + xml)


def docx(chemin, titre):
    _ooxml(chemin, {
        "[Content_Types].xml":
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        "_rels/.rels":
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        "word/document.xml":
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            f'<w:p><w:r><w:t>{titre}</w:t></w:r></w:p><w:p><w:r><w:t>Document fictif de recette.</w:t></w:r></w:p>'
            '</w:body></w:document>',
    })


def xlsx(chemin, titre):
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    _ooxml(chemin, {
        "[Content_Types].xml":
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels":
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/_rels/workbook.xml.rels":
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/workbook.xml":
            f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Feuil1" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/worksheets/sheet1.xml":
            f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>{titre}</t></is></c></row>'
            '<row r="2"><c r="A2" t="inlineStr"><is><t>Montant</t></is></c><c r="B2"><v>1000</v></c></row></sheetData></worksheet>',
    })


def pdf(chemin, titre):
    texte = titre.encode("latin-1", "replace")
    flux = b"BT /F1 12 Tf 72 720 Td (" + texte.replace(b"(", b"[").replace(b")", b"]") + b") Tj ET"
    objets = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(flux)).encode() + b" >>\nstream\n" + flux + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objets, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objets) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    out += f"trailer\n<< /Size {len(objets) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    chemin.write_bytes(bytes(out))


def eml(chemin, de, a, objet, quand):
    chemin.write_text(
        f"From: {de}\nTo: {a}\nSubject: {objet}\nDate: {quand.strftime('%a, %d %b %Y %H:%M:%S +0200')}\n"
        f"Message-ID: <{abs(hash((de, objet, quand))) % 10**12}@recette.test>\nContent-Type: text/plain; charset=utf-8\n\n"
        "Message fictif de recette, sans contenu réel.\n", encoding="utf-8")


def md(chemin, titre):
    chemin.write_text(f"# {titre}\n\nNote fictive de recette.\n", encoding="utf-8")


def csv(chemin, titre):
    chemin.write_text(f"Nom,Statut,Date\n{titre},En cours,2026-06-01\n", encoding="utf-8")


ECRIVAINS = {".docx": docx, ".xlsx": xlsx, ".pdf": pdf, ".md": md, ".csv": csv}


# ── Squelette d'arbre ───────────────────────────────────────────────────────

class Arbre:
    def __init__(self, racine, alea):
        self.racine = Path(racine)
        self.alea = alea
        self.fichiers = []

    def _date(self):
        return BASE - timedelta(days=self.alea.randint(0, 420), hours=self.alea.randint(0, 9))

    def fichier(self, rel, titre=None, quand=None):
        chemin = self.racine / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        titre = titre or chemin.stem
        if chemin.suffix == ".eml":
            raise ValueError("utiliser .mail() pour un .eml")
        ECRIVAINS[chemin.suffix](chemin, titre)
        self._date_fixe(chemin, quand)
        return chemin

    def mail(self, rel, de, a, objet, quand=None):
        chemin = self.racine / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        quand = quand or self._date()
        eml(chemin, de, a, objet, quand)
        self._date_fixe(chemin, quand)
        return chemin

    def serie(self, dossier, motif, n, ext, debut=1):
        """`serie("Devis", "devis-{i:03d}", 40, ".pdf")` → 40 fichiers numérotés."""
        for i in range(debut, debut + n):
            self.fichier(f"{dossier}/{motif.format(i=i)}{ext}")

    def _date_fixe(self, chemin, quand):
        ts = (quand or self._date()).timestamp()
        os.utime(chemin, (ts, ts))
        self.fichiers.append(chemin)


# ── Profil employé : Camille Perrin, Nordaline ──────────────────────────────

def employe(racine, alea):
    a = Arbre(racine, alea)
    moi = "c.perrin@nordaline.test"
    a.fichier("Projets/PARTIES-PRENANTES.md")
    (racine / "Projets/PARTIES-PRENANTES.md").write_text(
        "# Parties prenantes déclarées\n\n- N+1 : Hélène Vasseur, directrice générale\n"
        "- Équipe : Sami Benali, Inès Roche\n- Client interne : direction commerciale\n"
        "- Prestataire : Alto Conseil\n", encoding="utf-8")
    a._date_fixe(racine / "Projets/PARTIES-PRENANTES.md", None)
    (racine / "Projets/PROJETS.md").write_text(
        "# Projets que je porte\n\n- Refonte intranet\n- Migration CRM\n- Onboarding 2026\n", encoding="utf-8")
    a._date_fixe(racine / "Projets/PROJETS.md", None)

    p = "Projets/Refonte intranet"
    for f in ("cahier-des-charges.docx", "planning.xlsx", "budget.xlsx", "maquettes.pdf",
              "risques.md", "comite-de-pilotage.pdf"):
        a.fichier(f"{p}/{f}")
    a.serie(p, "CR-2026-{i:02d}", 6, ".md")

    p = "Projets/Migration CRM"
    for f in ("cadrage.docx", "lots.xlsx", "contrat-integrateur.pdf", "recette.md",
              "plan-de-migration.docx", "reprise-donnees.xlsx", "formation.md", "go-live.md", "risques.md"):
        a.fichier(f"{p}/{f}")
    a.serie(p, "export-notion-2026-{i:02d}", 5, ".csv")          # écart 5 : base déportée non déclarée

    p = "Projets/Onboarding 2026"
    for f in ("parcours.docx", "checklist.xlsx", "kit-arrivant.pdf", "retours.md",
              "planning.xlsx", "tuteurs.md", "budget.xlsx", "bilan-2025.docx", "sondage.csv", "notes.md"):
        a.fichier(f"{p}/{f}")

    p = "Projets/Audit qualité"                                   # écart 4 : projet sur disque, non déclaré
    for f in ("referentiel.pdf", "plan-audit.docx", "constats.xlsx", "actions.md",
              "CR-2026-05.md", "CR-2026-06.md", "rapport-final.docx", "suivi.xlsx"):
        a.fichier(f"{p}/{f}")

    a.serie("Réunions/Comité projet hebdo", "CR-comite-2026-S{i:02d}", 12, ".md", 20)
    a.serie("Réunions/Point équipe", "point-equipe-2026-{i:02d}", 8, ".md")
    a.serie("Réunions/Revue fournisseurs", "revue-fournisseurs-2026-{i:02d}", 10, ".md")  # écart 3

    a.serie("RH/Entretiens annuels", "entretien-2025-{i:02d}", 6, ".docx")
    for f in ("cheffe-de-projet.docx", "developpeur.docx", "chargee-de-clientele.docx",
              "assistante-direction.docx", "responsable-qualite.docx"):
        a.fichier(f"RH/Fiches de poste/{f}")
    a.fichier("RH/Organigramme.pdf", "Organigramme Nordaline 2026")

    for f in ("recette-tarte.md", "liste-courses.md", "vacances-2026.xlsx", "assurance-voiture.pdf",
              "photos-index.md", "devis-cuisine.pdf", "livres.md", "sport.md", "budget-perso.xlsx"):
        a.fichier(f"Divers/{f}")                                  # écart 2 : dossier sans domaine

    exp = [("h.vasseur@nordaline.test", 10, "Point direction"), ("s.benali@nordaline.test", 8, "Refonte intranet"),
           ("i.roche@nordaline.test", 6, "Onboarding 2026"), ("contact@alto-conseil.test", 6, "Migration CRM"),
           ("r.lemaitre@fournitech.test", 12, "Revue fournisseurs"),                     # écart 1
           ("noreply@ticketing.test", 4, "Ticket"), ("rh@nordaline.test", 4, "Paie")]
    n = 0
    for de, k, sujet in exp:
        for j in range(k):
            n += 1
            a.mail(f"Mails/{n:03d}.eml", de, moi, f"{sujet} — {j + 1}")

    ecarts = [
        {"id": 1, "type": "correspondant_non_declare", "indice": "Mails/ : r.lemaitre@fournitech.test, 12 messages",
         "question": "Qui est ce correspondant, et quel rôle tient-il dans votre travail ?"},
        {"id": 2, "type": "dossier_sans_domaine", "indice": "Divers/ : 9 fichiers sans lien avec un projet ou une fonction déclarés",
         "question": "Ce dossier relève-t-il de votre travail ? Sinon, il sort du périmètre."},
        {"id": 3, "type": "reunion_recurrente_sans_projet", "indice": "Réunions/Revue fournisseurs/ : 10 comptes rendus, aucun projet déclaré ne s'y rattache",
         "question": "Quelle responsabilité cette réunion sert-elle ? Est-ce un projet, une fonction, ou une charge héritée ?"},
        {"id": 4, "type": "projet_non_declare", "indice": "Projets/Audit qualité/ : 8 fichiers, absent de PROJETS.md",
         "question": "Ce projet est-il à vous, subi, ou terminé ?"},
        {"id": 5, "type": "base_deportee_non_declaree", "indice": "Projets/Migration CRM/export-notion-*.csv : 5 exports d'un outil non déclaré",
         "question": "Suivez-vous vos projets dans un outil ? Si oui, il devient la base déportée et le régime passe à pointeur."},
    ]
    (racine / "ECARTS.json").write_text(json.dumps(ecarts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    a._date_fixe(racine / "ECARTS.json", None)
    return len(a.fichiers)


# ── Profil dirigeant : Ateliers Roumier ─────────────────────────────────────

CLIENTS = ["Malbrun", "Kervran", "Vinci", "Desroches", "Aubert", "Lenoir", "Perez", "Garnier", "Tissot", "Moreau",
           "Blanchet", "Rousseau", "Fabre", "Gauthier", "Simon", "Renard", "Lambert", "Dupuis", "Colin", "Martel",
           "Faure", "Roy", "Chevalier", "Gillet", "Marchand", "Brunet", "Leroux", "Riviere", "Picard", "Barbier"]
TYPES = ["Agencement magasin", "Aménagement bureau", "Cuisine pro", "Accueil hôtel", "Bibliothèque", "Vestiaire"]


def affaires(a, dossier, noms, fichiers_par_affaire):
    for i, nom in enumerate(noms):
        annee = 2024 + i % 3
        d = f"{dossier}/{annee}-{i + 1:03d} {TYPES[i % len(TYPES)]} {nom}"
        for f in fichiers_par_affaire:
            a.fichier(f"{d}/{f}")


def dirigeant(racine, alea):
    a = Arbre(racine, alea)
    a.fichier("README.md", "Ateliers Roumier — espace de travail")
    a.fichier("ORGANIGRAMME.pdf", "Organigramme Ateliers Roumier")
    a.fichier("PROCESS-affaire.md", "Process d'une affaire, du devis à la réception")
    affaires(a, "Affaires", CLIENTS, ("devis.pdf", "commande.pdf", "plans.pdf", "planning.xlsx",
                                      "PV-reception.docx", "echanges.md", "facture.pdf", "fournitures.xlsx"))
    a.serie("Devis", "devis-2026-{i:03d}", 40, ".pdf")
    for i in range(10):
        a.fichier(f"Fournisseurs/contrat-fournisseur-{i + 1:02d}.docx")
        a.fichier(f"Fournisseurs/tarifs-fournisseur-{i + 1:02d}.xlsx")
    a.serie("Atelier/Plans", "plan-{i:03d}", 30, ".pdf")
    a.serie("Administratif/Compta", "grand-livre-2026-{i:02d}", 12, ".xlsx")
    a.serie("Administratif/RH", "contrat-salarie-{i:02d}", 8, ".docx")
    a.serie("Administratif/Assurances", "police-{i:02d}", 6, ".pdf")
    a.serie("Bureau d'études", "etude-{i:02d}", 12, ".md")
    moi = "c.roumier@exemple.test"
    for j, de in enumerate(("expert-comptable@cabinet.test", "banque@agence.test", "malbrun@client.test")):
        a.mail(f"Mails/{j + 1:03d}.eml", de, moi, "Suivi")
    return len(a.fichiers)


# ── Profil société : trois rédacteurs, deux affaires partagées ──────────────

def societe(racine, alea):
    total = 0
    partages = CLIENTS[:2]
    for redacteur, propres in (("camille", CLIENTS[2:5]), ("yasmine", CLIENTS[5:8]), ("marc", CLIENTS[8:11])):
        a = Arbre(racine / redacteur, alea)
        noms = list(partages) + list(propres) if redacteur != "marc" else list(propres) + [partages[0]]
        affaires(a, "Affaires", noms, ("devis.pdf", "planning.xlsx", "echanges.md", "PV-reception.docx"))
        a.serie("Notes", "note-{i:02d}", 6, ".md")
        moi = f"{redacteur}@roumier.test"
        for j in range(10):
            a.mail(f"Mails/{j + 1:03d}.eml", f"{CLIENTS[j].lower()}@client.test", moi, f"Affaire {CLIENTS[j]}")
        total += len(a.fichiers)
    return total


PROFILS = {"employe": employe, "dirigeant": dirigeant, "societe": societe}


def generer(sortie):
    sortie = Path(sortie)
    comptes = {}
    for nom, fabrique in PROFILS.items():
        racine = sortie / nom
        shutil.rmtree(racine, ignore_errors=True)
        racine.mkdir(parents=True)
        comptes[nom] = fabrique(racine, random.Random(GRAINE))
    return comptes


def main():
    p = argparse.ArgumentParser(description="Génère les trois arbres fictifs de la recette.")
    p.add_argument("--out", default=str(Path(__file__).resolve().parent / "fixtures"))
    a = p.parse_args()
    comptes = generer(a.out)
    for nom, n in comptes.items():
        print(f"{nom:10s} {n:4d} fichiers")
    # Auto-vérification : déterminisme (même liste de chemins et de dates sur deux générations).
    empreinte = lambda r: sorted((str(f.relative_to(r)), int(f.stat().st_mtime))  # noqa: E731
                                 for f in Path(r).rglob("*") if f.is_file())
    avant = empreinte(a.out)
    generer(a.out)
    assert avant == empreinte(a.out), "deux générations divergent : la graine ne tient pas"
    assert 140 <= comptes["employe"] <= 160 and 360 <= comptes["dirigeant"] <= 390, comptes
    print("déterminisme vérifié")
    return 0


if __name__ == "__main__":
    sys.exit(main())
