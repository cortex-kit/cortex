#!/usr/bin/env python3
"""etat.py — projette l'atelier `_cortex/` en un pivot JSON d'état. stdlib pure.

Le pivot est une PROJECTION : il se régénère en lisant `poste.json` (étape 0)
et les frontmatter `statut` et `controles` des artefacts markdown (étapes 1 à
8), et ne s'édite jamais à la main. Sa valeur tient à ce qu'il ne peut pas
mentir : deux générations successives sur un `_cortex/` inchangé rendent le
même fichier, à l'horodatage près.

Le rendu (tableau de bord `notice.html`) lit CE fichier et n'a aucune source
secondaire. Il y trouve aussi la phrase à prononcer pour l'étape suivante :
la notice la propose, elle ne l'exécute jamais (invariant I10).

Usage (`py` sous Windows vaut `python3`) :
    python3 etat.py --atelier <chemin de _cortex/>          # écrit <atelier>/etat.json
    python3 etat.py --atelier <...> --sortie <etat.json>    # écrit ailleurs
    python3 etat.py --autotest                              # auto-test hors ligne
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, date
from pathlib import Path

# cortex_config vit dans cortex-4-installation/scripts/ dans le dépôt, et dans
# le MÊME dossier que ce script une fois embarqué dans le zip (fabrique.py l'y
# dépose à côté). On sonde, on ne code jamais le chemin en dur.
_ICI = Path(__file__).resolve().parent


def _scripts_cortex4():
    for cand in (_ICI, _ICI.parent.parent / "cortex-4-installation" / "scripts"):
        if (cand / "cortex_config.py").is_file():
            return cand
    raise FileNotFoundError(
        "cortex_config.py introuvable : ni à côté de etat.py, ni dans "
        "cortex-4-installation/scripts/. L'atelier est incomplet.")


sys.path.insert(0, str(_scripts_cortex4()))
import cortex_config  # noqa: E402

# Les dix étapes de la chaîne et l'artefact que chacune écrit dans _cortex/
# (04-contrat.md §5, et §8 du contrat 2.3 pour « 3b »). `poste.json` est un JSON,
# les autres des markdown à frontmatter. `None` en 4 : la sortie du maillon 4 est
# le vault lui-même, pas un fichier d'atelier — voir RAISON_TROU_03, portée en
# clair dans le pivot. « 3b », le rangement, est facultatif : il ne renumérote rien.
ETAPES = [
    (0, "cortex-0-poste", "Poste", "poste.json"),
    (1, "cortex-1-cadrage", "Cadrage", "00-cadrage.md"),
    (2, "cortex-2-inventaire", "Inventaire", "01-inventaire.md"),
    (3, "cortex-3-ontologie", "Ontologie", "02-ontologie.md"),
    ("3b", "cortex-3b-rangement", "Rangement", "03-rangement.md"),
    (4, "cortex-4-installation", "Installation", None),
    (5, "cortex-5-ingest", "Remplissage", "04-ingest.md"),
    (6, "cortex-6-agents-metier", "Agents métier", "05-agents-metier.md"),
    (7, "cortex-7-passation", "Passation", "06-passation.md"),
    (8, "cortex-8-federation", "Fédération", "07-federation.md"),
]

# La phrase à prononcer pour lancer chaque étape, en langage ordinaire. La
# notice l'affiche, la personne la dit ou non. `fin` : quand tout est fait.
PHRASES = {
    0: "installe mon second cerveau",
    1: "faisons le cadrage",
    2: "lance l'inventaire",
    3: "décidons mes domaines",
    "3b": "rangeons mes dossiers",
    4: "construis mon second cerveau",
    5: "remplis mon second cerveau",
    6: "voyons mes assistants métier",
    7: "prépare la remise",
    8: "relie les cerveaux",
    "fin": "clôture",
}

RAISON_TROU_03 = (
    "Cette étape ne produit aucun fichier de suivi, et ce n'est pas un oubli : "
    "ce qu'elle produit est votre second cerveau lui-même, et sa preuve est le "
    "contrôle de santé qui sort sans une seule erreur.")

RAISON_SOLO = "vault solo"
RAISON_PASSEE = "passée sans rangement"
RANGEMENT_ARBITRE = {"refuse": "refusé", "rien_a_ranger": "rien à ranger", "passee": RAISON_PASSEE}
RAISON_NON_INSCRIT = "groupe non inscrit"
RAISON_SEUL = "en attente d'un second rédacteur"

# Libellés d'affichage du rendu. Ils vivent ici, dans la source commune, pour
# qu'aucun rendu n'invente les siens.
LIBELLES = {
    "a_faire": "À faire",
    "en_cours": "En cours",
    "faite": "Faite",
    "faite_deduite": "Faite (déduite)",
    "arbitre": "Arbitré",
    "illisible": "Illisible",
}


def _frontmatter(texte):
    """Rend le dict du frontmatter YAML, ou None si absent/illisible."""
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        return None
    try:
        fin = next(i for i, l in enumerate(lignes[1:], 1) if l.strip() == "---")
        return cortex_config.charger_texte("\n".join(lignes[1:fin]))
    except (StopIteration, ValueError):
        return None


def _poste(atelier):
    """Lit poste.json. Rend (dict ou None, illisible)."""
    chemin = atelier / "poste.json"
    if not chemin.is_file():
        return None, False
    try:
        return json.loads(chemin.read_text(encoding="utf-8")), False
    except ValueError:
        return None, True


def _remis(vault):
    """Vrai quand le vault porte `remis_le` dans `_cortex/06-passation.md`, la ligne
    que le maillon 7 y laisse, atelier dans le vault ou copie réduite."""
    p = vault / "_cortex" / "06-passation.md"
    fm = _frontmatter(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else None
    return bool(str((fm or {}).get("remis_le", "") or "").strip())


def attente_groupe(conf):
    """Pourquoi l'étape 8 d'un groupe attend (04-contrat H2 §3), ou None quand
    chaque membre de `federation.yaml` est remis. ValueError si le fichier est mal
    formé, OSError s'il ne se lit pas (lui ou la passation d'un membre)."""
    racine = str((conf.get("commun") or {}).get("racine", "") or "")
    fy = Path(racine).expanduser() / "federation.yaml" if racine else None
    if fy is None or not fy.is_file():
        return RAISON_NON_INSCRIT
    groupe = cortex_config.charger(fy)
    attendus = groupe.get("attendus") or []
    # Un seul nom écrit en scalaire reste un nom, pas une suite de lettres.
    attendus = [str(a) for a in ([attendus] if isinstance(attendus, str) else attendus)]
    if attendus:
        return "en attente de " + ", ".join(attendus)
    membres = groupe.get("membres") or []
    if not isinstance(membres, list) or not all(isinstance(m, dict) and m.get("export") for m in membres):
        raise ValueError("chaque membre doit porter slug et export")
    # Le vault d'un membre : le parent de son dossier d'export (<vault>/_export/<slug>).
    absents = [str(m.get("slug", "?")) for m in membres
               if not _remis((fy.parent / Path(str(m.get("export", ""))).expanduser()).parent.parent)]
    if absents:
        return "en attente de " + ", ".join(absents)
    return RAISON_SEUL if len(membres) < 2 else None


def _groupe(e, conf):
    """Étape 8 d'un groupe : arbitrée tant qu'un rédacteur n'est pas remis, pour que
    la notice ne propose « relie les cerveaux » qu'une fois tout le monde remis."""
    if e["numero"] != 8 or not conf or conf.get("mode") != "federe" or e["etat"] == "faite":
        return e
    try:
        attente = attente_groupe(conf)
    except (ValueError, OSError) as err:
        e["etat"], e["raison"] = "illisible", f"federation.yaml illisible : {err}"
        return e
    if attente:
        e["etat"], e["raison"] = "arbitre", attente
    return e


def _aval(atelier, numero):
    """Un artefact d'une étape postérieure (hors 8) est-il présent ? Par rang dans
    ETAPES, pas par numéro : « 3b » n'est pas un nombre."""
    rang = [n for n, _, _, _ in ETAPES].index(numero)
    return any((atelier / a).is_file() for n, _, _, a in ETAPES[rang + 1:] if a and n != 8)


def _journal_rangement(atelier):
    """(faits, retirés) du journal de l'étape 3b : les id dont la dernière ligne
    décisive est `fait`, et ceux dont elle est `annule`. ValueError si illisible."""
    p = atelier / "03-rangement-journal.jsonl"
    faits, retires = set(), set()
    if p.is_file():
        for l in p.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            ligne = json.loads(l)
            if ligne.get("resultat") == "fait":
                faits.add(ligne["id"]); retires.discard(ligne["id"])
            elif ligne.get("resultat") == "annule":
                retires.add(ligne["id"]); faits.discard(ligne["id"])
    return faits, retires


def _rangement(e, atelier, fm):
    """Étape 3b (contrat 2.3 §8, A2, A3). Facultative : refusée ou sans objet, elle est
    arbitrée ; appliquée en partie, elle est `en_cours` et le maillon 4 refuse."""
    statut = e["statut"]
    if statut in RANGEMENT_ARBITRE:
        e["etat"] = "arbitre"
        e["raison"] = str(fm.get("raison") or RANGEMENT_ARBITRE[statut])
        return e
    try:
        faits, retires = _journal_rangement(atelier)
    except (ValueError, KeyError) as err:
        e["etat"], e["raison"] = "illisible", f"journal du rangement illisible : {err}"
        return e
    acceptees = [str(i) for i in (fm.get("acceptees") or [])]
    reste = [i for i in acceptees if i not in faits and i not in retires]
    if faits and reste:
        e["etat"], e["raison"] = "en_cours", "appliqué en partie : " + ", ".join(reste)
    elif statut == "applique":
        e["etat"] = "faite"
    elif _aval(atelier, e["numero"]):
        e["etat"], e["raison"] = "arbitre", RAISON_PASSEE
    else:
        e["etat"] = "a_faire"
    return e


def _etape(numero, maillon, nom, artefact, atelier, conf):
    e = {"numero": numero, "maillon": maillon, "nom": nom, "artefact": artefact,
         "present": False, "statut": "", "etat": "a_faire", "controles": [],
         "modifie_le": ""}
    if artefact is None:
        # Le trou en 03 : projeté quand même, jamais deviné. La chaîne est
        # strictement ordonnée (l'étape 0 du maillon 5 exige le vault), donc
        # un artefact aval présent prouve que l'installation a eu lieu.
        e["etat"] = "faite_deduite" if _aval(atelier, numero) else "a_faire"
        e["raison"] = RAISON_TROU_03
        return e
    if numero == "3b" and not (atelier / artefact).is_file():
        if _aval(atelier, numero):
            e["etat"], e["raison"] = "arbitre", RAISON_PASSEE
        return e
    chemin = atelier / artefact
    if numero == 0:
        poste, illisible = _poste(atelier)
        if illisible:
            e["present"], e["etat"] = True, "illisible"
        elif poste is not None:
            e["present"] = True
            e["modifie_le"] = date.fromtimestamp(chemin.stat().st_mtime).isoformat()
            e["etat"] = "faite" if poste.get("notice_ouverte_le") else "en_cours"
        return e
    # `profil` est posé au maillon 1 : avant lui, `mode` vaut son défaut et
    # n'arbitre rien. Sans cette garde, un futur `societe` voit « sans objet »
    # dès le maillon 0, puis le voit repasser « À faire ».
    if numero == 8 and conf and conf.get("profil") and conf.get("mode", "solo") == "solo":
        e["etat"], e["raison"] = "arbitre", RAISON_SOLO
        return e
    if not chemin.is_file():
        return _groupe(e, conf)
    e["present"] = True
    e["modifie_le"] = date.fromtimestamp(chemin.stat().st_mtime).isoformat()
    fm = _frontmatter(chemin.read_text(encoding="utf-8", errors="replace"))
    if fm is None:
        e["etat"] = "illisible"
        return _groupe(e, conf)
    e["statut"] = str(fm.get("statut", ""))
    e["controles"] = [{"nom": k, "verdict": str(v)}
                      for k, v in (fm.get("controles") or {}).items()]
    if numero == "3b":
        return _rangement(e, atelier, fm)
    # `en_cours` se lit comme `brouillon` (H2 §3) : le maillon 8 l'écrit ainsi.
    e["etat"] = {"brouillon": "en_cours", "en_cours": "en_cours", "valide": "faite",
                 "arbitre": "arbitre"}.get(e["statut"], "illisible")
    return _groupe(e, conf)


def suivante(etapes):
    """Numéro de la première étape ni faite ni arbitrée, ou None si tout est fait."""
    for e in etapes:
        if not (e["etat"].startswith("faite") or e["etat"] == "arbitre"):
            return e["numero"]
    return None


def generer(atelier, paquet=None):
    """Lit `_cortex/` et rend le pivot (dict). N'écrit rien."""
    atelier = Path(atelier)
    organisation, conduite, profil, regime = "", "", "", ""
    conf = None
    config = atelier / "config.yaml"
    if config.is_file():
        try:
            conf = cortex_config.charger(config)
            organisation = (conf.get("organisation") or {}).get("nom", "")
            conduite = cortex_config.conduite(conf)
            profil = str(conf.get("profil", "") or "")
            regime = str((conf.get("donnees") or {}).get("regime", "") or "")
        except ValueError:
            organisation, conduite, conf = "(config illisible)", "", None
    if paquet is None:
        version = _ICI / "VERSION"
        paquet = version.read_text(encoding="utf-8").strip() if version.is_file() else "dev"
    poste, _ = _poste(atelier)
    etapes = [_etape(*args, atelier, conf) for args in ETAPES]
    prochaine = suivante(etapes)
    return {
        "format": "cortex/etat",
        "version": 2,
        "paquet": paquet,
        "organisation": organisation,
        "conduite": conduite,
        "profil": profil,
        "regime": regime,
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "notice_ouverte_le": str((poste or {}).get("notice_ouverte_le", "") or ""),
        "etape_suivante": prochaine,
        "phrase_suivante": PHRASES["fin" if prochaine is None else prochaine],
        "etapes": etapes,
    }


def ecrire(atelier, sortie=None, paquet=None):
    pivot = generer(atelier, paquet=paquet)
    sortie = Path(sortie) if sortie else Path(atelier) / "etat.json"
    sortie.write_text(json.dumps(pivot, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return sortie, pivot


def faites(pivot):
    """Nombre d'étapes faites. `faite_deduite` compte : l'étape 4 ne produit
    aucun artefact, et l'ignorer en annonce une de moins quand toutes sont faites."""
    return sum(1 for e in pivot["etapes"] if e["etat"].startswith("faite"))


def compte(pivot):
    """Le compteur en clair. §5 amendé : une étape arbitrée n'est pas une étape
    faite, et « 9/9 » serait un mensonge en solo. Les deux comptes se nomment
    séparément. `etat.py` et `notice.py` passent tous deux par ici : deux
    formulations pour un même compte finiraient par diverger."""
    arbitrees = sum(1 for e in pivot["etapes"] if e["etat"] == "arbitre")
    texte = f"{faites(pivot)} faite(s)"
    if arbitrees:
        texte += f" et {arbitrees} arbitrée(s)"
    return texte + f" sur {len(pivot['etapes'])}"


def _autotest():
    def par(p, n):
        return next(e for e in p["etapes"] if e["numero"] == n)

    with tempfile.TemporaryDirectory() as tmp:
        atelier = Path(tmp)
        p = generer(atelier)
        assert len(p["etapes"]) == 10 and faites(p) == 0
        assert p["etape_suivante"] == 0 and p["phrase_suivante"] == PHRASES[0]
        (atelier / "poste.json").write_text('{"notice_ouverte_le": ""}', encoding="utf-8")
        assert generer(atelier)["etapes"][0]["etat"] == "en_cours"
        (atelier / "poste.json").write_text(
            '{"notice_ouverte_le": "2026-09-19T10:00:00"}', encoding="utf-8")
        p = generer(atelier)
        assert p["etapes"][0]["etat"] == "faite" and p["notice_ouverte_le"]
        assert p["etape_suivante"] == 1 and p["phrase_suivante"] == PHRASES[1]
        # Défaut 6 : sans profil, l'étape 8 reste « À faire », elle ne s'arbitre pas.
        (atelier / "config.yaml").write_text("conduite: solo\nmode: solo\n", encoding="utf-8")
        assert par(generer(atelier), 8)["etat"] == "a_faire"
        (atelier / "config.yaml").write_text(
            "conduite: solo\nprofil: employe\nmode: solo\ndonnees:\n  regime: copie\n",
            encoding="utf-8")
        p = generer(atelier)
        assert p["profil"] == "employe" and p["regime"] == "copie"
        assert par(p, 8)["etat"] == "arbitre" and par(p, 8)["raison"] == RAISON_SOLO
        assert par(p, 4)["etat"] == "a_faire"
        (atelier / "04-ingest.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        assert par(generer(atelier), 4)["etat"] == "faite_deduite"
        # A2 : le rangement facultatif, passé sans être fait, ne reste pas « à faire » à vie.
        assert par(generer(atelier), "3b")["etat"] == "arbitre" and par(generer(atelier), "3b")["raison"] == RAISON_PASSEE
        for a in ("00-cadrage", "01-inventaire", "02-ontologie",
                  "05-agents-metier", "06-passation"):
            (atelier / f"{a}.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        p = generer(atelier)
        assert faites(p) == 8 and p["etape_suivante"] is None
        assert p["phrase_suivante"] == PHRASES["fin"]
        s1, _ = ecrire(atelier, atelier / "a.json")
        s2, _ = ecrire(atelier, atelier / "b.json")
        sans = lambda s: [l for l in s.read_text().splitlines() if "genere_le" not in l]
        assert sans(s1) == sans(s2)

        # H2 §3 : l'étape 8 d'un groupe attend que chaque rédacteur soit remis.
        racine = Path(tmp) / "groupe"
        commun = racine / "commun"
        (atelier / "config.yaml").write_text(
            f'profil: societe\nmode: federe\ncommun:\n  racine: "{commun}"\n', encoding="utf-8")

        def huit():
            p = generer(atelier)
            return par(p, 8)["etat"], par(p, 8).get("raison", ""), p["phrase_suivante"]
        assert huit() == ("arbitre", RAISON_NON_INSCRIT, PHRASES["fin"]), huit()
        commun.mkdir(parents=True)
        fy = commun / "federation.yaml"

        def membre(slug, remis):
            v = racine / slug / "vault"
            (v / "_export" / slug).mkdir(parents=True, exist_ok=True)
            (v / "_cortex").mkdir(exist_ok=True)
            (v / "_cortex" / "06-passation.md").write_text(
                f"---\nremis_le: {'2026-09-27' if remis else ''}\n---\n", encoding="utf-8")
            return f'  - {{ slug: {slug}, export: "{v / "_export" / slug}" }}\n'
        fy.write_text("version: 1\nmembres:\n" + membre("helene", True) + 'attendus: ["Karim B"]\n',
                      encoding="utf-8")
        assert huit() == ("arbitre", "en attente de Karim B", PHRASES["fin"]), huit()
        fy.write_text("version: 1\nmembres:\n" + membre("helene", True) + membre("karim", False)
                      + "attendus: []\n", encoding="utf-8")
        assert huit() == ("arbitre", "en attente de karim", PHRASES["fin"]), huit()
        assert compte(generer(atelier)) == "8 faite(s) et 2 arbitrée(s) sur 10", compte(generer(atelier))
        membre("karim", True)
        assert huit() == ("a_faire", "", PHRASES[8]), huit()
        (atelier / "07-federation.md").write_text("---\nstatut: en_cours\n---\n", encoding="utf-8")
        assert huit() == ("en_cours", "", PHRASES[8]), huit()
        assert LIBELLES[par(generer(atelier), 8)["etat"]] == "En cours"
        (atelier / "07-federation.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        assert huit() == ("faite", "", PHRASES["fin"]) and faites(generer(atelier)) == 9, huit()
        fy.write_text("version: 1\nmembres:\n" + membre("helene", True) + "attendus: []\n", encoding="utf-8")
        (atelier / "07-federation.md").unlink()
        assert huit() == ("arbitre", RAISON_SEUL, PHRASES["fin"]), huit()
        # Reprise m1 à m3 : un federation.yaml mal formé ou illisible ne fait jamais planter
        # etat.py ; l'étape 8 passe « illisible » avec la raison, la notice se régénère.
        for mal in ("membres: [helene]\n", "membres:\n  - { slug: karim }\n", "membres: helene\n"):
            fy.write_text("version: 1\n" + mal, encoding="utf-8")
            etat, raison, _ = huit()
            assert etat == "illisible" and raison.startswith("federation.yaml illisible : "), (mal, huit())
        fy.write_text("version: 1\nmembres:\n" + membre("helene", True) + "attendus: Karim B\n", encoding="utf-8")
        assert huit()[1] == "en attente de Karim B", huit()
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            fy.chmod(0)
            try:
                assert huit()[0] == "illisible" and "Permission" in huit()[1], huit()
            finally:
                fy.chmod(0o644)

    # Contrat 2.3 §8 : les quatre lignes du tableau de l'étape 3b, puis A2 et A3.
    with tempfile.TemporaryDirectory() as tmp:
        atelier = Path(tmp)
        for a in ("00-cadrage", "01-inventaire", "02-ontologie"):
            (atelier / f"{a}.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        (atelier / "poste.json").write_text('{"notice_ouverte_le": "x"}', encoding="utf-8")

        def trois_b(fm, journal=""):
            (atelier / "03-rangement.md").write_text(f"---\n{fm}\n---\n", encoding="utf-8")
            (atelier / "03-rangement-journal.jsonl").write_text(journal, encoding="utf-8")
            p = generer(atelier)
            return par(p, "3b")["etat"], par(p, "3b").get("raison", ""), p["phrase_suivante"]
        p = generer(atelier)
        assert par(p, "3b")["etat"] == "a_faire" and p["phrase_suivante"] == PHRASES["3b"], "03-rangement.md absent"
        assert trois_b("statut: refuse\nacceptees: []") == ("arbitre", "refusé", PHRASES[4])
        assert trois_b("statut: rien_a_ranger\nacceptees: []") == ("arbitre", "rien à ranger", PHRASES[4])
        fait = '{"id": "r001", "resultat": "fait"}\n'
        etat3, raison, phrase = trois_b("statut: propose\nacceptees: [r001, r002]", fait)
        assert etat3 == "en_cours" and "r002" in raison and phrase == PHRASES["3b"], (etat3, raison, phrase)
        assert trois_b("statut: propose\nacceptees: [r001, r002]",
                       fait + '{"id": "r002", "resultat": "annule"}\n')[0] == "a_faire", "A5 : une ligne retirée"
        assert trois_b("statut: applique\nacceptees: [r001]", fait) == ("faite", "", PHRASES[4])
        assert trois_b("statut: passee\nacceptees: []")[:2] == ("arbitre", RAISON_PASSEE), "posé par l'installation"
        assert trois_b("statut: propose\nacceptees: [r001]", "pas du json\n")[0] == "illisible"
    print("etat.py : auto-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description="Projette _cortex/ en pivot JSON.")
    p.add_argument("--atelier", help="chemin du dossier _cortex/")
    p.add_argument("--sortie", help="fichier JSON à écrire (défaut : <atelier>/etat.json)")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.atelier or not Path(a.atelier).expanduser().is_dir():
        print(f"[erreur] atelier introuvable : {a.atelier}", file=sys.stderr)
        return 2
    sortie, pivot = ecrire(Path(a.atelier).expanduser(), a.sortie)
    print(f"OK — {sortie} : {compte(pivot)}, "
          f"conduite {pivot['conduite'] or 'non fixée'}, "
          f"suivante : « {pivot['phrase_suivante']} »")
    return 0


if __name__ == "__main__":
    sys.exit(main())
