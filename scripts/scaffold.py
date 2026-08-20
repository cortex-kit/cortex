#!/usr/bin/env python3
"""scaffold.py — instancie un vault Cortex depuis template/vault/. stdlib pure.

Zéro jugement, 100 % déterministe. C'est le point de reprise à coût nul de
toute la chaîne : `rm -rf` puis relance est un geste normal ici, pas un
incident. C'est précisément pourquoi ce maillon est isolé des maillons de
jugement (cadrage, ontologie).

Ce qu'il fait :
  1. charge config.yaml
  2. copie template/vault/ vers la destination en substituant les {{ }}
  3. génère .obsidian/graph.json depuis les domaines (Graph View est un plugin
     CORE : coloration sans aucune installation communautaire)
  4. génère 90 - Meta/Configuration.md, miroir LECTURE SEULE de la config
  5. git init + premier commit si git est demandé
  6. ÉCHOUE si une moustache subsiste

Usage :
  python3 scaffold.py --config <config.yaml> --out <dossier vault>
  python3 scaffold.py --config <config.yaml> --out <dossier> --force
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cortex_config  # noqa: E402

RACINE_SKILL = Path(__file__).resolve().parent.parent
GABARIT = RACINE_SKILL / "template" / "vault"


def blocs_generes(conf):
    """Les fragments Markdown dérivés de la config. Ils remplacent ce qui, chez
    Cosmos, était écrit en dur : les 4 domaines nommés apparaissaient dans 6
    notes et 3 templates, dont un dictionnaire JavaScript."""
    domaines = conf.get("domaines", [])
    cycles = cortex_config.cycles_par_nom(conf)

    liste = "\n".join(
        f"- [[{d['nom']}]] — tag `#d/{d['code']}`, prefixe de fiche `{d['code'].upper()}`"
        for d in domaines
    ) or "- _Non renseigné — à compléter avant transmission._"

    tags = "\n".join(f"- `#d/{d['code']}` {d['nom']}" for d in domaines)

    lignes = ["| `cycle` | `phase` autorisées | `progression` |", "|---|---|---|"]
    for nom, etapes in cycles.items():
        phases = " · ".join(f"`{e['phase']}`" for e in etapes)
        progs = " / ".join(str(e["progression"]) for e in etapes)
        lignes.append(f"| `{nom}` | {phases or '_(vide)_'} | {progs} |")
    lignes.append("| `aucun` | _(aucune : `phase` doit rester vide)_ | — |")
    table_cycles = "\n".join(lignes)

    return liste, tags, table_cycles


def substitutions(conf):
    """La table de substitution. Ses cles doivent correspondre EXACTEMENT a
    cortex_config.CLES_SCAFFOLD, que le lint utilise cote client ou scaffold.py
    n'est pas livre. L'assertion en fin de fonction rend l'oubli impossible :
    ajouter une moustache ici sans la declarer la-bas ferait passer un vault
    avec une moustache non substituee."""
    org = conf.get("organisation", {})
    liste, tags, table_cycles = blocs_generes(conf)
    table = {
        "{{ORGANISATION}}": org.get("nom", ""),
        "{{CODE}}": org.get("code", ""),
        "{{REDACTEUR}}": org.get("redacteur", ""),
        "{{COURRIEL}}": org.get("courriel", ""),
        "{{PRODUIT}}": (conf.get("marque") or {}).get("produit_nom", "Cortex"),
        "{{DOSSIERS_PROJETS}}": (conf.get("chemins") or {}).get("dossiers_projets", ""),
        "{{MODE}}": conf.get("mode", "solo"),
        "{{DATE}}": date.today().isoformat(),
        "{{DOMAINES_LISTE}}": liste,
        "{{DOMAINES_TAGS}}": tags,
        "{{CYCLES_TABLE}}": table_cycles,
        "{{SEUIL_JOURNAL}}": str((conf.get("sante") or {}).get("max_lignes_entree_journal", 10)),
    }
    ecart = set(table) ^ set(cortex_config.CLES_SCAFFOLD)
    assert not ecart, f"table de substitution desynchronisee de CLES_SCAFFOLD : {ecart}"
    return table


def substituer(texte, table):
    for cle, val in table.items():
        texte = texte.replace(cle, str(val))
    return texte


def graph_json(conf):
    """Groupes de couleur du Graph View, dérivés des domaines. Dans le système d'origine,
    `graph.json` portait `colorGroups: []` : les groupes documentés dans
    la doctrine n'avaient jamais été configurés."""
    groupes = []
    for d in conf.get("domaines", []):
        h = str(d.get("couleur", "#888888")).lstrip("#")
        try:
            rgb = int(h, 16)
        except ValueError:
            rgb = 0x888888
        groupes.append({"query": f"tag:#d/{d['code']}", "color": {"a": 1, "rgb": rgb}})
    groupes.append({"query": 'path:"00 - Centre"', "color": {"a": 1, "rgb": 0xFFFFFF}})
    return {
        "colorGroups": groupes,
        "showTags": True,
        "hideUnresolved": True,
        "showAttachments": False,
    }


def miroir_config(conf, chemin_config):
    liste, tags, table_cycles = blocs_generes(conf)
    org = conf.get("organisation", {})
    return f"""---
type: meta
tags:
  - doctrine
---
<!-- généré depuis {chemin_config.name} par scaffold.py — ne pas éditer -->
# Configuration

Miroir **lecture seule** de `{chemin_config.name}`, régénéré à chaque scaffold.
Sens unique : éditer ce fichier n'a aucun effet. Le canon est le YAML.

## Organisation

| Clé | Valeur |
|---|---|
| nom | {org.get('nom', '')} |
| code | `{org.get('code', '')}` |
| rédacteur | {org.get('redacteur', '')} |
| mode | `{conf.get('mode', 'solo')}` |

Un vault, un rédacteur. Toujours. Plusieurs personnes se traitent par plusieurs
vaults et un commun généré, jamais par plusieurs mains dans le même vault.

## Domaines

{tags}

## Cycles et phases

Source **unique** du mapping `phase` vers `progression`. Toute autre copie de
cette table est une divergence en attente.

{table_cycles}

## Seuils de santé

| Seuil | Valeur | Effet |
|---|---|---|
| entrée de journal | {(conf.get('sante') or {}).get('max_lignes_entree_journal', 10)} lignes | **bloquant** |
| journal total | {(conf.get('sante') or {}).get('max_lignes_journal', 60)} lignes | avertissement |
| journal périmé | {(conf.get('sante') or {}).get('journal_perime_jours', 14)} jours | avertissement |
| pointeur canonique | {'obligatoire' if (conf.get('sante') or {}).get('pointeur_canonique_obligatoire', True) else 'optionnel'} | **bloquant** |
"""


def config_sans_mentions(texte):
    """Vide `mentions_interdites` de la copie qui part chez le client.

    Substitution textuelle et non re-serialisation : la config du client reste
    ainsi lisible telle qu'elle a ete ecrite, commentaires compris.
    """
    sortie, saute_items_de = [], None
    for ligne in texte.splitlines():
        indent = len(ligne) - len(ligne.lstrip())
        # Forme multi-lignes : sauter les `- item` plus indentes que la cle,
        # sans quoi ils resteraient orphelins et casseraient le chargement.
        if saute_items_de is not None:
            if ligne.strip().startswith("-") and indent > saute_items_de:
                continue
            saute_items_de = None
        if ligne.strip().startswith("mentions_interdites:"):
            sortie.append(" " * indent + "mentions_interdites: []"
                          "   # videe a l'installation : la liste reste dans l'atelier")
            saute_items_de = indent
            continue
        sortie.append(ligne)
    return "\n".join(sortie) + "\n"


def notes_domaines(conf, dest):
    """Instancie `10 - Domaines/<nom>.md` depuis _Template Domaine.md.

    `{{title}}` est une moustache Obsidian, laissee intacte dans Templates/ ;
    ici elle est resolue, parce que ces notes-ci sont generees et non inserees
    a la main. La description reste un trou marque : la remplir supposerait
    d'inventer ce que le domaine recouvre.
    """
    gabarit = GABARIT / "90 - Meta" / "Templates" / "_Template Domaine.md"
    if not gabarit.is_file():
        return 0
    brut = gabarit.read_text(encoding="utf-8")
    dossier = dest / "10 - Domaines"
    dossier.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in conf.get("domaines", []):
        nom, code = d.get("nom", ""), d.get("code", "")
        if not nom or not code:
            continue
        texte = (brut.replace("d/CODE", f"d/{code}")
                     .replace("{{title}}", nom)
                     .replace("Description courte du domaine, deux lignes maximum.",
                              "_Non renseigné — à compléter._"))
        (dossier / f"{nom}.md").write_text(texte, encoding="utf-8")
        n += 1
    return n


def fichiers_du_gabarit():
    return {p.relative_to(GABARIT) for p in GABARIT.rglob("*") if p.is_file()}


def notes_du_client(dest, conf):
    """Les .md presents dans le vault qui ne viennent pas du gabarit.

    C'est la seule question qui compte avant un rmtree : ce dossier porte-t-il
    du travail humain ? Tout ce que l'installation genere -- Configuration.md,
    les notes de domaine -- se regenere et ne compte donc pas.
    """
    connus = fichiers_du_gabarit() | {Path("90 - Meta/Configuration.md")}
    connus |= {Path("10 - Domaines") / f"{d['nom']}.md"
               for d in conf.get("domaines", []) if d.get("nom")}
    return sorted(
        str(p.relative_to(dest))
        for p in dest.rglob("*.md")
        if p.is_file() and ".git" not in p.parts
        and p.relative_to(dest) not in connus
    )


def outillage_seul(dest, table_vide):
    """Rafraichit la couche d'agents sans toucher au contenu.

    Sans ce mode, corriger le lint n'atteignait aucun vault deja livre : les
    scripts de maintenance sont copies a l'installation, et le seul geste qui
    les remplacait etait un --force destructeur.
    """
    if not dest.is_dir():
        print(f"[X] {dest} n'existe pas : rien a rafraichir.", file=sys.stderr)
        return 2
    n = 0
    for src in sorted((GABARIT / ".claude").rglob("*")):
        if not src.is_file():
            continue
        cible = dest / src.relative_to(GABARIT)
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(substituer(src.read_text(encoding="utf-8"), table_vide),
                         encoding="utf-8")
        n += 1
    skill_lint = dest / ".claude" / "skills" / "lint"
    skill_lint.mkdir(parents=True, exist_ok=True)
    for nom in ("cortex_config.py", "lint_sante.py"):
        shutil.copy2(Path(__file__).resolve().parent / nom, skill_lint / nom)
        n += 1
    print(f"✓ Outillage rafraichi : {n} fichier(s) sous .claude/. Contenu intact.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Instancie un vault Cortex.")
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--force", action="store_true", help="ecrase la destination")
    p.add_argument("--ecraser-vault-peuple", action="store_true",
                   help="autorise --force a detruire un vault qui contient des notes")
    p.add_argument("--outillage-seul", action="store_true",
                   help="rafraichit .claude/ (skills, agents, scripts de lint) "
                        "sans toucher au contenu du vault")
    a = p.parse_args()

    chemin_config = Path(a.config).expanduser().resolve()
    dest = Path(a.out).expanduser().resolve()
    conf = cortex_config.charger(chemin_config)

    # Charger ne verifie que la syntaxe. Installer exige un contrat complet :
    # un vault sans domaine se scaffoldait et passait le lint en vert.
    manques = cortex_config.valider_installable(conf)
    if manques:
        print(f"[X] Config incomplete : {chemin_config}", file=sys.stderr)
        for m in manques:
            print(f"    - {m}", file=sys.stderr)
        print("    Le maillon 3 (cortex-3-ontologie) produit ces valeurs.",
              file=sys.stderr)
        return 2

    if not GABARIT.is_dir():
        print(f"[X] Gabarit introuvable : {GABARIT}", file=sys.stderr)
        return 2

    if a.outillage_seul:
        return outillage_seul(dest, table_vide=substitutions(conf))

    if dest.exists():
        if not a.force:
            print(f"[X] {dest} existe deja. --force pour ecraser.", file=sys.stderr)
            return 2
        # `--force` fait un rmtree. C'est anodin au maillon 4, ou le vault ne
        # contient encore que le gabarit -- et c'est une perte totale des le
        # maillon 5, ou il porte les notes du client. Le SKILL.md invite a
        # l'utiliser "sans hesiter" : cette invitation n'est vraie qu'avant
        # l'ingest, et rien dans le script ne faisait la difference.
        notes = notes_du_client(dest, conf)
        if notes and not a.ecraser_vault_peuple:
            print(f"[X] {dest} contient {len(notes)} note(s) qui ne viennent pas du "
                  "gabarit.", file=sys.stderr)
            for n in notes[:8]:
                print(f"    - {n}", file=sys.stderr)
            if len(notes) > 8:
                print(f"    ... et {len(notes) - 8} autre(s)", file=sys.stderr)
            print("    --force les detruirait sans sauvegarde. Si c'est voulu, "
                  "ajoute --ecraser-vault-peuple.", file=sys.stderr)
            print("    Pour ne rafraichir que la couche d'agents : --outillage-seul.",
                  file=sys.stderr)
            return 2
        shutil.rmtree(dest)

    table = substitutions(conf)
    ecrits = 0
    for src in sorted(GABARIT.rglob("*")):
        rel = src.relative_to(GABARIT)
        cible = dest / rel
        if src.is_dir():
            cible.mkdir(parents=True, exist_ok=True)
            continue
        cible.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in (".md", ".yaml", ".json", ".txt"):
            cible.write_text(substituer(src.read_text(encoding="utf-8"), table),
                             encoding="utf-8")
        else:
            shutil.copy2(src, cible)
        ecrits += 1

    # La config du client vit DANS son vault : c'est ce qui rend le vault
    # autonome et le lint exécutable sans argument supplementaire.
    # Mais PAS `mentions_interdites` : cette liste porte les autres clients du
    # consultant, et la copier ici ferait voyager leurs noms chez celui-ci —
    # le fichier qui existe pour interdire ces mentions serait celui qui les
    # transporte. Le lint ne s'en sert pas ; la recette de remise la lit dans
    # l'atelier, cote consultant.
    (dest / "config.yaml").write_text(
        config_sans_mentions(chemin_config.read_text(encoding="utf-8")),
        encoding="utf-8")

    # Le vault client embarque les scripts dont il a besoin EN MAINTENANCE.
    # Ils sont copies depuis scripts/ a l'installation plutot que stockes en
    # double dans le gabarit : deux copies dans git divergent, et c'est celle
    # que personne ne regarde qui finit par tourner chez le client.
    # scaffold.py n'est PAS copie : c'est un outil d'installation, pas de
    # maintenance, et le client n'a aucune raison de reinstancier son vault.
    skill_lint = dest / ".claude" / "skills" / "lint"
    skill_lint.mkdir(parents=True, exist_ok=True)
    for nom in ("cortex_config.py", "lint_sante.py"):
        shutil.copy2(Path(__file__).resolve().parent / nom, skill_lint / nom)

    # Les notes de domaine, une par entree de config. Sans elles, `Centre.md`
    # listait les domaines en wikilinks vers des notes inexistantes : le point
    # d'entree du vault, celui que la doctrine annonce comme le plus connecte,
    # etait livre avec autant de liens morts que le client a de domaines.
    ecrits += notes_domaines(conf, dest)

    (dest / ".obsidian").mkdir(parents=True, exist_ok=True)
    (dest / ".obsidian" / "graph.json").write_text(
        json.dumps(graph_json(conf), indent=2, ensure_ascii=False), encoding="utf-8")

    meta = dest / "90 - Meta"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "Configuration.md").write_text(
        miroir_config(conf, chemin_config), encoding="utf-8")

    # Une moustache de scaffold qui survit est un defaut de livraison : le
    # client lirait `{{ORGANISATION}}` dans sa propre doctrine.
    #
    # On ne controle QUE les cles de `table`. Trois familles de placeholders
    # cohabitent dans le gabarit et deux sont legitimes ici :
    #   - scaffold      {{ORGANISATION}}, {{DOMAINES_LISTE}}  -> doivent disparaitre
    #   - projet        {{NOM_PROJET}}, {{PREFIX}}            -> remplis par `nouveau-projet`
    #   - Obsidian core {{title}}, {{date:YYYY-MM-DD}}        -> remplis par Obsidian
    # Un controle sur `\{\{[A-Z_]+\}\}` echouerait sur la deuxieme famille.
    restes = []
    for f in sorted(dest.rglob("*")):
        if not (f.is_file() and f.suffix in (".md", ".yaml", ".json", ".txt")):
            continue
        contenu = f.read_text(encoding="utf-8", errors="replace")
        for cle in table:
            if cle in contenu:
                restes.append(f"{f.relative_to(dest)} : {cle}")
    if restes:
        print(f"[X] {len(restes)} moustache(s) non substituee(s) :", file=sys.stderr)
        for r in restes[:15]:
            print(f"    - {r}", file=sys.stderr)
        return 1

    # git init toujours, même sans remote : un vault versionné localement donne
    # l'annulation et l'historique, qui sont la moitié de la valeur d'un second
    # cerveau. `substrats.git_remote` ne gouverne que le push, pas le dépôt.
    try:
        subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
        subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Cortex", "-c", "user.email=cortex@localhost",
             "commit", "-q", "-m", "Vault initial (scaffold Cortex)"],
            cwd=dest, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[i] git non initialise ({e}) — le vault reste utilisable.")

    print(f"✓ Vault instancie : {dest}")
    print(f"✎ {ecrits} fichier(s) du gabarit + config.yaml + graph.json + Configuration.md")
    print(f"✎ {len(cortex_config.codes_domaines(conf))} domaine(s), "
          f"mode {conf.get('mode')}, 0 moustache residuelle")
    print(f"→ Suite : python3 lint_sante.py --vault \"{dest}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
