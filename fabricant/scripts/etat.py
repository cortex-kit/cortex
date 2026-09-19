#!/usr/bin/env python3
"""etat.py — projette l'atelier `_cortex/` en un pivot JSON d'état. stdlib pure.

Le pivot est une PROJECTION : il se régénère en lisant les frontmatter
`statut` et `controles` des artefacts, et ne s'édite jamais à la main.
Sa valeur tient à ce qu'il ne peut pas mentir — deux générations successives
sur un `_cortex/` inchangé rendent le même fichier, à l'horodatage près.

Les deux rendus (tableau de bord `notice.html`, deck) lisent CE fichier et
n'ont aucune source secondaire : une divergence entre eux est impossible par
construction.

Usage (`py` sous Windows vaut `python3`) :
    python3 etat.py --atelier <chemin de _cortex/>          # écrit <atelier>/etat.json
    python3 etat.py --atelier <...> --sortie <etat.json>    # écrit ailleurs
"""

import argparse
import json
import sys
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

# Les sept étapes de la chaîne et l'artefact que chacune écrit dans _cortex/.
# `None` en 4 : la sortie du maillon 4 est le vault lui-même, pas un fichier
# d'atelier — voir RAISON_TROU_03, portée en clair dans le pivot.
ETAPES = [
    (1, "cortex-1-cadrage", "Cadrage", "00-cadrage.md"),
    (2, "cortex-2-inventaire", "Inventaire", "01-inventaire.md"),
    (3, "cortex-3-ontologie", "Ontologie", "02-ontologie.md"),
    (4, "cortex-4-installation", "Installation", None),
    (5, "cortex-5-ingest", "Remplissage", "04-ingest.md"),
    (6, "cortex-6-agents-metier", "Agents métier", "05-agents-metier.md"),
    (7, "cortex-7-passation", "Passation", "06-passation.md"),
]

RAISON_TROU_03 = (
    "Cette étape ne produit aucun fichier de suivi, et ce n'est pas un oubli : "
    "ce qu'elle produit est votre second cerveau lui-même, et sa preuve est le "
    "contrôle de santé qui sort sans une seule erreur.")

# Libellés d'affichage, partagés par les DEUX rendus (tableau de bord et deck).
# Ils vivent ici, dans la source commune, pour qu'aucun rendu n'invente le sien.
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


def _etape(numero, maillon, nom, artefact, atelier):
    e = {"numero": numero, "maillon": maillon, "nom": nom, "artefact": artefact,
         "present": False, "statut": "", "etat": "a_faire", "controles": [],
         "modifie_le": ""}
    if artefact is None:
        # Le trou en 03 : projeté quand même, jamais deviné. La chaîne est
        # strictement ordonnée (l'étape 0 du maillon 5 exige le vault), donc
        # un artefact aval présent prouve que l'installation a eu lieu.
        aval = any((atelier / a).is_file()
                   for _, _, _, a in ETAPES[numero:] if a)
        e["etat"] = "faite_deduite" if aval else "a_faire"
        e["raison"] = RAISON_TROU_03
        return e
    chemin = atelier / artefact
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


def generer(atelier, paquet=None):
    """Lit `_cortex/` et rend le pivot (dict). N'écrit rien."""
    atelier = Path(atelier)
    organisation, conduite = "", ""
    config = atelier / "config.yaml"
    if config.is_file():
        try:
            conf = cortex_config.charger(config)
            organisation = (conf.get("organisation") or {}).get("nom", "")
            conduite = cortex_config.conduite(conf)
        except ValueError:
            organisation, conduite = "(config illisible)", ""
    if paquet is None:
        version = _ICI / "VERSION"
        paquet = version.read_text(encoding="utf-8").strip() if version.is_file() else "dev"
    return {
        "format": "cortex/etat",
        "version": 1,
        "paquet": paquet,
        "organisation": organisation,
        "conduite": conduite,
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "etapes": [_etape(*args, atelier) for args in ETAPES],
    }


def ecrire(atelier, sortie=None, paquet=None):
    pivot = generer(atelier, paquet=paquet)
    sortie = Path(sortie) if sortie else Path(atelier) / "etat.json"
    sortie.write_text(json.dumps(pivot, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return sortie, pivot


def faites(pivot):
    """Nombre d'étapes faites. `faite_deduite` compte : l'étape 4 ne produit
    aucun artefact, et l'ignorer annonce 6/7 quand les sept sont faites."""
    return sum(1 for e in pivot["etapes"] if e["etat"].startswith("faite"))


def main():
    p = argparse.ArgumentParser(description="Projette _cortex/ en pivot JSON.")
    p.add_argument("--atelier", required=True, help="chemin du dossier _cortex/")
    p.add_argument("--sortie", help="fichier JSON à écrire (défaut : <atelier>/etat.json)")
    a = p.parse_args()
    if not Path(a.atelier).is_dir():
        print(f"[erreur] atelier introuvable : {a.atelier}", file=sys.stderr)
        return 2
    sortie, pivot = ecrire(a.atelier, a.sortie)
    print(f"OK — {sortie} : {faites(pivot)}/7 étape(s) faite(s), "
          f"conduite {pivot['conduite'] or 'non fixée'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
