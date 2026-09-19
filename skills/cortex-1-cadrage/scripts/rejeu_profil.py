#!/usr/bin/env python3
"""rejeu_profil.py : rejoue le cadrage (maillon 1) et l'entretien de compréhension
(maillon 3, section « Ce que l'inventaire a révélé ») sur un arbre de fichiers, sans
personne pour répondre. stdlib pure.

Sert à la recette : les réponses qu'une personne donnerait sont remplacées par le bloc
config proposé de references/profils/<profil>.md, et chaque écart d'un ECARTS.json à la
racine devient un bloc [?] sans réponse. Ce que produit une vraie session, ce script le
produit à l'identique dans sa forme, avec des trous visibles là où il faudrait une réponse.

Usage :
    python3 rejeu_profil.py --profil employe --racine <dossier> --atelier <dossier/_cortex>
                            [--slug recette] [--nom "Organisation"] [--base-projets <url>]
    python3 rejeu_profil.py --autotest
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ICI = Path(__file__).resolve().parent
SKILL = ICI.parent
INSTALLATION = SKILL.parent / "cortex-4-installation"
sys.path.insert(0, str(INSTALLATION / "scripts"))
import cortex_config  # noqa: E402


# ── YAML : émission du sous-ensemble que cortex_config lit ─────────────────

def _y(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_y(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k}: {_y(x)}" for k, x in v.items()) + " }"
    return '"' + str(v) + '"'


def emettre(conf):
    """dict -> texte YAML relisible par cortex_config.charger_texte (quatre formes)."""
    lignes = []
    for k, v in conf.items():
        if isinstance(v, dict):
            lignes.append(f"{k}:")
            lignes += [f"  {sk}: {_y(sv)}" for sk, sv in v.items()]
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            lignes.append(f"{k}:")
            lignes += [f"  - {_y(d)}" for d in v]
        else:
            lignes.append(f"{k}: {_y(v)}")
    return "\n".join(lignes) + "\n"


def bloc_profil(profil):
    """Le premier bloc ```yaml de references/profils/<profil>.md, chargé."""
    texte = (SKILL / "references" / "profils" / f"{profil}.md").read_text(encoding="utf-8")
    m = re.search(r"```yaml\n(.*?)```", texte, re.S)
    if not m:
        raise ValueError(f"aucun bloc yaml dans profils/{profil}.md")
    return cortex_config.charger_texte(m.group(1))


def forme_tilde(chemin):
    chemin = str(Path(chemin).expanduser().resolve())
    maison = str(Path.home())
    return "~" + chemin[len(maison):] if chemin.startswith(maison) else chemin


# ── Le rejeu ────────────────────────────────────────────────────────────────

def cadrage(profil, racine, slug, nom, base_projets, poste, existant=None):
    """Fusionne dans `existant` (le config.yaml laissé par le maillon 0) ; sinon part du gabarit."""
    conf = cortex_config.charger(INSTALLATION / "template" / "config.example.yaml")
    if existant:
        for k, v in existant.items():
            if isinstance(v, dict) and isinstance(conf.get(k), dict):
                conf[k].update(v)
            else:
                conf[k] = v
    for k, v in bloc_profil(profil).items():
        if isinstance(v, dict) and isinstance(conf.get(k), dict):
            conf[k].update(v)
        else:
            conf[k] = v
    conf["conduite"] = "solo"
    conf["organisation"] = {"nom": nom, "code": slug, "redacteur": "Rédacteur de recette",
                            "courriel": f"{slug}@exemple.test"}
    conf["chemins"] = {"dossiers_projets": forme_tilde(racine)}
    conf["collecte"]["racines"] = [forme_tilde(racine)]
    conf["substrats"] = {"espace_documentaire": "", "base_projets": base_projets, "git_remote": ""}
    conf["donnees"]["regime"] = "pointeur" if base_projets else "copie"
    conf["marque"] = {"produit_nom": "Cortex", "mentions_interdites": []}
    if poste:
        conf["poste"] = {"os": poste.get("os", ""),
                         "outils": [o for o, d in poste.get("outils", {}).items() if d.get("present")],
                         "mail_fournisseur": poste.get("mail", {}).get("fournisseur", ""),
                         "mail_boites": poste.get("mail", {}).get("boites", 0),
                         "mail_voie": poste.get("mail", {}).get("voie", "")}
    return conf


def _lire(racine, rel):
    f = Path(racine) / rel
    return f.read_text(encoding="utf-8").strip() if f.is_file() else "_Non renseigné : à compléter_"


def md_cadrage(conf, racine):
    d = conf["donnees"]["regime"]
    return f"""---
maillon: 1
produit_par: cortex-1-cadrage
statut: valide
controles:
  redacteur_unique_nomme: passe
  profil_pose: passe
  regime_fixe: passe
  racines_confirmees: passe
  substrats_declares: passe
  plafonds_acceptes: passe
  mail_optin_trace: passe
---

# Cadrage rejoué : {conf['organisation']['nom']}

Profil {conf['profil']}, conduite solo, régime {d}. Bornes récapitulées et confirmées le {date.today()} (rejeu de recette, sans personne).

## Racines confirmées

- {conf['collecte']['racines'][0]}

## Parties prenantes déclarées

{_lire(racine, 'Projets/PARTIES-PRENANTES.md')}

## Projets portés

{_lire(racine, 'Projets/PROJETS.md')}

## Projets subis

_Non renseigné : à compléter_

## Rituels déclarés

_Non renseigné : à compléter_

## Domaines de départ (hypothèses du profil)

{chr(10).join(f"- `{x['code']}` {x['nom']}" for x in conf['domaines'])}
"""


def md_ontologie(conf, racine):
    ecarts_f = Path(racine) / "ECARTS.json"
    ecarts = json.loads(ecarts_f.read_text(encoding="utf-8")) if ecarts_f.is_file() else []
    blocs = [f"[?] {e['question']}\n    indice : {e['indice']} ({e['type']})" for e in ecarts] \
        or ["Aucun écart candidat dans l'inventaire."]
    dossiers = sorted(p for p in Path(racine).iterdir() if p.is_dir())
    corpus = [f"| {p.name} | {sum(1 for f in p.rglob('*') if f.is_file())} |" for p in dossiers]
    return f"""---
maillon: 3
produit_par: cortex-3-ontologie
statut: brouillon
controles:
  entretien_mene: arbitre             # {len(ecarts)} écart(s) sans réponse : rejeu sans personne
  domaines_sous_plafond: passe
  chaque_domaine_a_une_preuve: arbitre
  distribution_equilibree: arbitre
  aucun_domaine_vide: arbitre
  matrice_ownership_remplie: arbitre
  lien_interdit_declare: arbitre
  ontologie_signee_client: arbitre
---

# Ontologie rejouée : {conf['organisation']['nom']}

## Ce que l'inventaire a révélé

{chr(10).join(b + chr(10) for b in blocs)}
## Corpus vu sous la racine

| Dossier | Fichiers |
|---|---|
{chr(10).join(corpus)}

## Domaines

{chr(10).join(f"- `{x['code']}` {x['nom']} : [déduction] domaine de départ du profil, preuve à établir sur l'inventaire" for x in conf['domaines'])}

## Points incertains à challenger

{len(ecarts)} écart(s) en [?] ci-dessus, sans réponse.
"""


def rejouer(profil, racine, atelier, slug="recette", nom="Organisation de recette", base_projets=""):
    atelier = Path(atelier)
    atelier.mkdir(parents=True, exist_ok=True)
    poste_f = atelier / "poste.json"
    poste = json.loads(poste_f.read_text(encoding="utf-8")) if poste_f.is_file() else None
    config_f = atelier / "config.yaml"
    existant = cortex_config.charger(config_f) if config_f.is_file() else None
    conf = cadrage(profil, racine, slug, nom, base_projets, poste, existant)
    (atelier / "config.yaml").write_text(emettre(conf), encoding="utf-8")
    (atelier / "00-cadrage.md").write_text(md_cadrage(conf, racine), encoding="utf-8")
    (atelier / "02-ontologie.md").write_text(md_ontologie(conf, racine), encoding="utf-8")
    relu = cortex_config.charger(atelier / "config.yaml")
    return cortex_config.valider_installable(relu)


# ── Auto-test ───────────────────────────────────────────────────────────────

def _autotest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp) / "racine"
        (racine / "Projets/X").mkdir(parents=True)
        (racine / "Projets/X/a.md").write_text("# a\n", encoding="utf-8")
        (racine / "ECARTS.json").write_text(json.dumps([
            {"id": 1, "type": "dossier_sans_domaine", "indice": "Divers/", "question": "Q1 ?"},
            {"id": 2, "type": "projet_non_declare", "indice": "Projets/X/", "question": "Q2 ?"},
        ]), encoding="utf-8")
        for profil in cortex_config.PROFILS:
            at = Path(tmp) / profil / "_cortex"
            erreurs = rejouer(profil, racine, at, slug=profil)
            assert not erreurs, (profil, erreurs)
            conf = cortex_config.charger(at / "config.yaml")
            assert conf["profil"] == profil and conf["conduite"] == "solo"
            assert conf["collecte"]["racines"] == [forme_tilde(racine)]
            assert conf["donnees"]["regime"] == "copie"
            onto = (at / "02-ontologie.md").read_text(encoding="utf-8")
            assert onto.count("\n[?] ") == 2, onto
            assert "## Ce que l'inventaire a révélé" in onto
        assert cortex_config.charger(Path(tmp) / "societe/_cortex/config.yaml")["mode"] == "federe"
        # Un config.yaml laissé par le maillon 0 est fusionné, jamais recréé.
        at = Path(tmp) / "fusion"
        at.mkdir()
        (at / "config.yaml").write_text('version: 1\nposte:\n  os: "linux"\n  outils: [git]\n  mail_fournisseur: "gmail"\n  mail_boites: 1\n  mail_voie: "connecteur"\n', encoding="utf-8")
        assert not rejouer("employe", racine, at)
        conf = cortex_config.charger(at / "config.yaml")
        assert conf["poste"]["os"] == "linux" and conf["poste"]["mail_voie"] == "connecteur" and conf["profil"] == "employe", conf["poste"]
        # Base déportée déclarée => pointeur ; aller-retour de l'émetteur.
        at = Path(tmp) / "ptr"
        assert not rejouer("dirigeant", racine, at, base_projets="https://base.exemple.test")
        conf = cortex_config.charger(at / "config.yaml")
        assert conf["donnees"]["regime"] == "pointeur"
        assert cortex_config.charger_texte(emettre(conf)) == conf, "aller-retour YAML"
    print("OK : rejeu des trois profils, écarts en [?], régime pointeur sur base déportée")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--profil", choices=cortex_config.PROFILS)
    p.add_argument("--racine", help="dossier parcouru (fixture)")
    p.add_argument("--atelier", help="dossier _cortex/ à écrire")
    p.add_argument("--slug", default="recette")
    p.add_argument("--nom", default="Organisation de recette")
    p.add_argument("--base-projets", default="", help="adresse d'une base déportée ; fixe le régime pointeur")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not (a.profil and a.racine and a.atelier):
        p.error("--profil, --racine et --atelier sont requis (ou --autotest)")
    erreurs = rejouer(a.profil, a.racine, a.atelier, a.slug, a.nom, a.base_projets)
    for e in erreurs:
        print("[refus]", e)
    print(f"{a.profil} : config.yaml, 00-cadrage.md, 02-ontologie.md écrits dans {a.atelier} ; "
          f"valider_installable : {'accepte' if not erreurs else str(len(erreurs)) + ' refus'}")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
