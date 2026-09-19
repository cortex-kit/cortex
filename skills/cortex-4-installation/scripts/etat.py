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

# Les neuf étapes de la chaîne et l'artefact que chacune écrit dans _cortex/
# (04-contrat.md §5). `poste.json` est un JSON, les autres des markdown à
# frontmatter. `None` en 4 : la sortie du maillon 4 est le vault lui-même, pas
# un fichier d'atelier — voir RAISON_TROU_03, portée en clair dans le pivot.
ETAPES = [
    (0, "cortex-0-poste", "Poste", "poste.json"),
    (1, "cortex-1-cadrage", "Cadrage", "00-cadrage.md"),
    (2, "cortex-2-inventaire", "Inventaire", "01-inventaire.md"),
    (3, "cortex-3-ontologie", "Ontologie", "02-ontologie.md"),
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


def _etape(numero, maillon, nom, artefact, atelier, conf):
    e = {"numero": numero, "maillon": maillon, "nom": nom, "artefact": artefact,
         "present": False, "statut": "", "etat": "a_faire", "controles": [],
         "modifie_le": ""}
    if artefact is None:
        # Le trou en 03 : projeté quand même, jamais deviné. La chaîne est
        # strictement ordonnée (l'étape 0 du maillon 5 exige le vault), donc
        # un artefact aval présent prouve que l'installation a eu lieu.
        aval = any((atelier / a).is_file()
                   for n, _, _, a in ETAPES[numero + 1:] if a and n != 8)
        e["etat"] = "faite_deduite" if aval else "a_faire"
        e["raison"] = RAISON_TROU_03
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
        return e
    e["present"] = True
    e["modifie_le"] = date.fromtimestamp(chemin.stat().st_mtime).isoformat()
    fm = _frontmatter(chemin.read_text(encoding="utf-8", errors="replace"))
    if fm is None:
        e["etat"] = "illisible"
        return e
    e["statut"] = str(fm.get("statut", ""))
    e["controles"] = [{"nom": k, "verdict": str(v)}
                      for k, v in (fm.get("controles") or {}).items()]
    e["etat"] = {"brouillon": "en_cours", "valide": "faite",
                 "arbitre": "arbitre"}.get(e["statut"], "illisible")
    return e


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


def _autotest():
    with tempfile.TemporaryDirectory() as tmp:
        atelier = Path(tmp)
        p = generer(atelier)
        assert len(p["etapes"]) == 9 and faites(p) == 0
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
        assert generer(atelier)["etapes"][8]["etat"] == "a_faire"
        (atelier / "config.yaml").write_text(
            "conduite: solo\nprofil: employe\nmode: solo\ndonnees:\n  regime: copie\n",
            encoding="utf-8")
        p = generer(atelier)
        assert p["profil"] == "employe" and p["regime"] == "copie"
        assert p["etapes"][8]["etat"] == "arbitre" and p["etapes"][8]["raison"] == RAISON_SOLO
        assert p["etapes"][4]["etat"] == "a_faire"
        (atelier / "04-ingest.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
        assert generer(atelier)["etapes"][4]["etat"] == "faite_deduite"
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
    # §5 amendé : une étape arbitrée n'est pas une étape faite, et 9/9 serait
    # un mensonge en solo. On nomme les deux comptes séparément.
    arbitrees = sum(1 for e in pivot["etapes"] if e["etat"] == "arbitre")
    compte = f"{faites(pivot)} faite(s)"
    if arbitrees:
        compte += f" et {arbitrees} arbitrée(s)"
    compte += f" sur {len(ETAPES)}"
    print(f"OK — {sortie} : {compte}, "
          f"conduite {pivot['conduite'] or 'non fixée'}, "
          f"suivante : « {pivot['phrase_suivante']} »")
    return 0


if __name__ == "__main__":
    sys.exit(main())
