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
  5. génère .claude/settings.json : lecture seule sur les racines de collecte,
     refus d'écriture hors vault, hooks SessionStart et Stop
  6. git init + premier commit ; propose un dépôt privé (jamais imposé)
  7. ÉCHOUE si une moustache subsiste

Usage :
  python3 scaffold.py --config <config.yaml> --out <dossier vault>
  python3 scaffold.py --config <config.yaml> --out <dossier> --force
  python3 scaffold.py --config <config.yaml> --out <dossier> --depot-prive
  python3 scaffold.py --autotest
"""

import argparse
import json
import re
import shutil
import subprocess
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cortex_config  # noqa: E402

RACINE_SKILL = Path(__file__).resolve().parent.parent
GABARIT = RACINE_SKILL / "template" / "vault"

# Seuls ces suffixes passent par la substitution, donc par une lecture UTF-8.
SUFFIXES_TEXTE = (".md", ".yaml", ".json", ".txt")


def ignorable(src):
    """Un artefact d'execution du depot, qui n'a rien a faire chez le client.

    `__pycache__` apparait des qu'un script du gabarit a ete importe une fois.
    Le lire en UTF-8 fait sortir `--outillage-seul` en 1, et le copier tel quel
    livrerait un `.pyc` perime dans le vault.
    """
    return "__pycache__" in src.parts or src.suffix in (".pyc", ".pyo")

# Contrat 04 §9, amende le 2026-09-19 par le chef d'orchestre : lecture seule
# sur les racines, les deux scripts de la cloture (export, puis cloture.py qui
# fait add, commit et push) pour qu'une cloture de novice ne demande aucune
# permission, et le rafraichissement d'un structurant perime, qui est du meme
# registre : un geste de routine propose par le lint, `cloture`, `parle` et `bilan`.
ALLOW = [
    "Read", "Glob", "Grep",
    "Bash(python3 .claude/skills/lint/lint_sante.py:*)",
    "Bash(python3 .claude/skills/cloture/export.py:*)",
    "Bash(python3 .claude/skills/cloture/cloture.py:*)",
    "Bash(python3 .claude/skills/ingest/copie_structurant.py:*)",
    "Bash(python3 .claude/skills/agenda/agenda.py:*)",
    "Bash(python3 .claude/skills/miroir/miroir.py:*)",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
    "Bash(find:*)", "Bash(wc:*)", "Bash(ls:*)", "Bash(head:*)",
    "Bash(file:*)", "Bash(du:*)",
]
# Chemin ancré sur le vault : une commande relative cassait après un `cd` de la session.
HOOKS = {
    "SessionStart": [{"hooks": [{"type": "command",
                                 "command": 'python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start.py"'}]}],
    "Stop": [{"hooks": [{"type": "command",
                         "command": 'python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/stop.py"'}]}],
}


def forme_tilde(chemin):
    """Ramène un chemin du dossier personnel à la forme `~`.

    Défaut n°7 de la v1 : un `dossiers_projets` saisi en absolu traversait la
    substitution tel quel et le lint refusait le vault pour chemin absolu.
    Corrigé à la source, le lint reste inchangé.
    """
    s = str(chemin or "").strip().replace("\\", "/")
    if not s or s.startswith("~"):
        return s
    home = str(Path.home()).replace("\\", "/")
    if s == home or s.startswith(home + "/"):
        return "~" + s[len(home):]
    return s


def racines_collecte(conf):
    """`collecte.racines` en forme `~`. Une config v1 sans cette clé retombe
    sur `chemins.dossiers_projets` : c'est la seule racine qu'elle connaît."""
    rac = (conf.get("collecte") or {}).get("racines") or []
    if isinstance(rac, str):
        rac = [rac]
    if not rac:
        dp = (conf.get("chemins") or {}).get("dossiers_projets", "")
        rac = [dp] if dp else []
    return [forme_tilde(r) for r in rac if r]


def settings_json(conf, plateforme=None):
    """Les racines en lecture, jamais en écriture, et Bash confiné au vault.

    Une règle deny `Edit(<racine>/**)` par racine : elle couvre Write, Edit,
    MultiEdit et NotebookEdit. Une règle `Write(...)` n'est jamais consultée par
    Claude Code, qui le signale à chaque ouverture (Phase H).

    Les règles de permission ne voient pas un script Python ni un `echo >`
    lancés par Bash. Hors Windows, un sandbox sans échappatoire confine donc
    Bash au vault : racines en `denyWrite`, commun seul autorisé en plus,
    réseau limité au push. Sans lui, une session du vault a écrit dans un
    dossier du poste qui n'était ni le vault ni l'atelier (Phase H)."""
    racines = racines_collecte(conf)
    # Une racine qui passe par un lien symbolique (macOS : /var -> /private/var)
    # n'est pas reconnue par la règle écrite sous sa forme donnée : on écrit aussi
    # la forme réelle quand elle diffère (constat M4 du 2026-09-19).
    formes = []
    for r in racines:
        formes.append(r)
        reel = os.path.realpath(os.path.expanduser(r))
        if reel != os.path.abspath(os.path.expanduser(r)):
            formes.append(forme_tilde(reel))
    s = {
        # H2 lane C : un `git commit` tapé par l'assistant porte les lignes
        # d'attribution de la session du consultant ; le vault commite par
        # cloture.py, qui les retire.
        "permissions": {"allow": list(ALLOW), "deny": [f"Edit({r}/**)" for r in formes] + ["Bash(git commit:*)"],
                        "additionalDirectories": formes},
        "hooks": HOOKS,
    }
    # ponytail: pas de sandbox sous Windows natif (non pris en charge par Claude
    # Code) ; Bash y reste couvert par les seules règles, à revoir avec WSL2.
    if (plateforme or sys.platform) != "win32":
        commun = ((conf.get("commun") or {}).get("racine", "")
                  if conf.get("mode") == "federe" else "")
        s["sandbox"] = {
            "enabled": True,
            "allowUnsandboxedCommands": False,
            "autoAllowBashIfSandboxed": False,
            "filesystem": {"denyWrite": formes,
                           "allowWrite": [forme_tilde(commun)] if commun else []},
            # Le miroir lit la base de projets : son domaine seul s'ajoute, et seulement s'il est configuré.
            "network": {"allowedDomains": ["github.com"] + (
                ["api.notion.com"] if (conf.get("miroir") or {}).get("outil") == "notion" else [])},
        }
    return s


def ecrire_settings(dest, conf):
    cible = dest / ".claude" / "settings.json"
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(json.dumps(settings_json(conf), indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    return cible


def blocs_generes(conf):
    """Les fragments Markdown dérivés de la config. Ils remplacent ce qui, chez
    le système d'origine, était écrit en dur : les 4 domaines nommés apparaissaient dans 6
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
        "{{DOSSIERS_PROJETS}}": forme_tilde((conf.get("chemins") or {}).get("dossiers_projets", "")),
        "{{MODE}}": conf.get("mode", "solo"),
        "{{DATE}}": date.today().isoformat(),
        "{{DOMAINES_LISTE}}": liste,
        "{{DOMAINES_TAGS}}": tags,
        "{{CYCLES_TABLE}}": table_cycles,
        "{{SEUIL_JOURNAL}}": str((conf.get("sante") or {}).get("max_lignes_entree_journal", 10)),
        "{{REFERENTIEL}}": regle_referentiel(conf),
    }
    ecart = set(table) ^ set(cortex_config.CLES_SCAFFOLD)
    assert not ecart, f"table de substitution desynchronisee de CLES_SCAFFOLD : {ecart}"
    return table


def regle_referentiel(conf):
    """La règle du dossier commun pour le CLAUDE.md du vault (contrat 2.3 §7).

    Le chemin n'y entre que si le dossier existe : un `a_creer` ou un `inconnu`
    nommerait un dossier que l'assistant chercherait sans le trouver."""
    ref = conf.get("referentiel") or {}
    chemin = forme_tilde(ref.get("chemin", "")) if isinstance(ref, dict) else ""
    if not chemin or ref.get("etat") != "existant":
        return "Aucun dossier commun déclaré."
    if not sommaire_present(chemin):
        # Sommaire refusé au rangement (N12) : renvoyer au dossier lui-même, jamais à un fichier absent.
        return ("Pour une procédure, la charte graphique, une signature, un modèle ou un assistant "
                f"établi pour toute l'organisation, chercher d'abord dans le dossier commun `{chemin}`, "
                "puis lire le document lui-même. Ne jamais en recopier un dans ce vault.")
    return ("Pour une procédure, la charte graphique, une signature, un modèle ou un assistant "
            "établi pour toute l'organisation, lire d'abord le sommaire `AGENTS.md` du dossier "
            f"commun `{chemin}`, puis le document lui-même. Ne jamais en recopier un dans ce vault.")


def sommaire_present(chemin):
    """Le dossier commun porte-t-il son sommaire ? Seule sa présence se teste, il ne s'ouvre pas."""
    return (Path(os.path.expanduser(chemin)) / "AGENTS.md").is_file()


def rangement_inacheve(dossier_atelier):
    """Vrai quand l'étape 3b du rangement vaut `en_cours` dans l'atelier : des
    changements acceptés sont faits, d'autres non (contrat 2.3 §8). Construire
    là-dessus ferait naître des liens sur des chemins appelés à changer. Un journal
    illisible bloque aussi : on ne sait plus ce qui a bougé."""
    import etat
    pivot = etat.generer(dossier_atelier)
    return any(e.get("numero") == "3b" and e.get("etat") in ("en_cours", "illisible") for e in pivot["etapes"])


def note_referentiel(conf, dest):
    """`50 - Ressources/Référentiel commun.md` (contrat 2.3 §7) quand le dossier commun existe :
    le vault y renvoie, il ne porte aucune note par procédure d'entreprise. Écrite ici, à la
    construction, parce qu'elle ne dépend que de la config ; le remplissage la trouve faite."""
    ref = conf.get("referentiel") or {}
    if not isinstance(ref, dict) or ref.get("etat") != "existant" or not ref.get("chemin"):
        return 0
    chemin = forme_tilde(ref["chemin"])
    domaines = [d.get("nom", "") for d in conf.get("domaines") or [] if isinstance(d, dict) and d.get("nom")]
    note = dest / "50 - Ressources" / "Référentiel commun.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    sommaire = sommaire_present(chemin)
    index = "AGENTS.md" if sommaire else ""
    note.write_text(
        "---\ntype: ressource\nressource: referentiel\n"
        f'chemin: "{chemin}"\nindex: "{index}"\nvisibilite: commun\n---\n'
        "# Référentiel commun\n\n"
        "Le dossier commun de l'organisation porte ses documents de référence : procédures, charte "
        "graphique, signatures, modèles et assistants. Une procédure n'y existe qu'en un exemplaire.\n\n"
        + (f"Il vit hors de ce vault, à `{chemin}`. Lire d'abord son sommaire `AGENTS.md`, puis le document "
           "qu'il désigne ; rien ne s'en recopie ici.\n\n" if sommaire else
           f"Il vit hors de ce vault, à `{chemin}`, sans sommaire : y chercher le document, puis le lire ; "
           "rien ne s'en recopie ici.\n\n")
        + "Remonte vers [[Centre]]." + (" Domaines concernés : " + ", ".join(f"[[{d}]]" for d in domaines) + "."
                                       if domaines else "") + "\n", encoding="utf-8")
    return 1


def marquer_construction(dossier_atelier):
    """Inscrit dans `03-rangement.md` que le second cerveau est construit (`construit_le`) :
    `range.py` refuse ensuite de proposer ou d'appliquer, ses liens ne doivent plus bouger
    (D3). Un rangement jamais conclu passe `statut: passee`, arbitré « passée sans
    rangement ». Rien n'est écrit hors d'un atelier (sans `02-ontologie.md`)."""
    atelier = Path(dossier_atelier)
    if not (atelier / "02-ontologie.md").is_file():
        return
    md = atelier / "03-rangement.md"
    # Un geste fait au journal : le rangement a eu lieu, il ne devient jamais « passé sans rangement ».
    journal = atelier / "03-rangement-journal.jsonl"
    fait = journal.is_file() and '"resultat": "fait"' in journal.read_text(encoding="utf-8")
    jour = date.today().isoformat()
    if not md.is_file():
        md.write_text("---\nmaillon: 3b\nproduit_par: cortex-4-installation\nstatut: passee\nacceptees: []\n"
                      f'raison: "passée sans rangement"\nconstruit_le: {jour}\n---\n# Rangement des dossiers de travail\n\n'
                      "Le second cerveau a été construit sans rangement : les dossiers gardent leurs noms.\n",
                      encoding="utf-8")
        return
    texte = md.read_text(encoding="utf-8")
    if not texte.startswith("---\n") or "\nconstruit_le:" in texte.split("\n---", 2)[0]:
        return
    if not fait and re.search(r"^statut: (propose|)$", texte, re.M):
        texte = re.sub(r"^statut: .*$", 'statut: passee\nraison: "passée sans rangement"', texte, count=1, flags=re.M)
    md.write_text(texte.replace("---\n", f"---\nconstruit_le: {jour}\n", 1), encoding="utf-8")


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
| profil | `{conf.get('profil', '')}` |
| régime de la donnée | `{(conf.get('donnees') or {}).get('regime', 'pointeur')}` |
| racines lues, jamais écrites | {', '.join(f'`{r}`' for r in racines_collecte(conf)) or '_aucune_'} |

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


def outillage_seul(dest, conf, table_vide):
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
        if not src.is_file() or ignorable(src):
            continue
        cible = dest / src.relative_to(GABARIT)
        cible.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in SUFFIXES_TEXTE:
            cible.write_text(substituer(src.read_text(encoding="utf-8"), table_vide),
                             encoding="utf-8")
        else:
            shutil.copy2(src, cible)
        n += 1
    skill_lint = dest / ".claude" / "skills" / "lint"
    skill_lint.mkdir(parents=True, exist_ok=True)
    for nom in ("cortex_config.py", "lint_sante.py"):
        shutil.copy2(Path(__file__).resolve().parent / nom, skill_lint / nom)
        n += 1
    copier_ingest(dest)
    n += 1
    ecrire_settings(dest, conf)
    n += 1
    if (dest / ".git").is_dir() and not subprocess.run(
            ["git", "config", "--local", "user.name"], cwd=dest, capture_output=True).stdout.strip():
        poser_identite(dest, conf)
        print("✎ Identité git locale posée : les prochains commits ne portent plus celle du poste.")
    print(f"✓ Outillage rafraichi : {n} fichier(s) sous .claude/. Contenu intact.")
    return 0


def poser_identite(dest, conf):
    """Identité git locale au vault, le rédacteur à défaut « Cortex ».

    Sans elle, chaque commit porte l'identité globale du poste, celle du
    consultant, et son nom part chez le client par l'historique (Phase H)."""
    org = conf.get("organisation") or {}
    nom = str(org.get("redacteur") or "").strip() or "Cortex"
    courriel = str(org.get("courriel") or "").strip() or "cortex@localhost"
    subprocess.run(["git", "config", "user.name", nom], cwd=dest, check=True)
    subprocess.run(["git", "config", "user.email", courriel], cwd=dest, check=True)


def copier_ingest(dest):
    """Depose `copie_structurant.py` dans `<vault>/.claude/skills/ingest/`.

    En regime copie, `cloture`, `parle` et `bilan` proposent de rafraichir un
    structurant perime. Sans ce script dans le vault, la promesse ne tient
    qu'en mode solo, la ou le plugin est installe : en mode consultant, le
    client n'a que son vault. Le script y trouve `cortex_config.py` dans le
    dossier voisin `lint/`.
    """
    cible = dest / ".claude" / "skills" / "ingest"
    cible.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RACINE_SKILL.parent / "cortex-5-ingest" / "scripts" / "copie_structurant.py",
                 cible / "copie_structurant.py")
    return cible / "copie_structurant.py"


def depot_prive(dest, slug, executer):
    """Propose `gh repo create`, ne l'exécute que sur demande explicite.

    La personne peut refuser et rester locale : un vault versionné localement
    a déjà l'annulation et l'historique, le dépôt distant n'ajoute que la
    sauvegarde hors poste.
    """
    # Le chemin du vault en entier, jamais `cd` : le harnais de Claude Code laisse
    # `.claude/.cc-writes` dans tout dossier où une commande entre par `cd` (H2).
    cmd = ["gh", "repo", "create", slug, "--private", "--source", str(dest), "--push"]
    if not executer:
        print(f"→ Dépôt privé (sur accord, jamais imposé) : gh repo create {slug} --private "
              f"--source \"{dest}\" --push")
        return
    try:
        subprocess.run(cmd, cwd=dest, check=True)
        print(f"✓ Dépôt privé créé et poussé : {slug}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[i] Dépôt privé non créé ({e}). Le vault reste local, rien n'est perdu.")


def main():
    p = argparse.ArgumentParser(description="Instancie un vault Cortex.")
    p.add_argument("--config")
    p.add_argument("--out")
    p.add_argument("--force", action="store_true", help="ecrase la destination")
    p.add_argument("--ecraser-vault-peuple", action="store_true",
                   help="autorise --force a detruire un vault qui contient des notes")
    p.add_argument("--outillage-seul", action="store_true",
                   help="rafraichit .claude/ (skills, agents, scripts de lint) "
                        "sans toucher au contenu du vault")
    p.add_argument("--depot-prive", action="store_true",
                   help="cree et pousse un depot GitHub prive (gh repo create), "
                        "sur accord de la personne seulement")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.config or not a.out:
        p.error("--config et --out sont requis")

    chemin_config = Path(a.config).expanduser().resolve()
    dest = Path(a.out).expanduser().resolve()
    conf = cortex_config.charger(chemin_config)

    # Charger ne verifie que la syntaxe. Installer exige un contrat complet :
    # un vault sans domaine se scaffoldait et passait le lint en vert.
    manques = cortex_config.valider_installable(conf)
    for avert in cortex_config.avertissements(conf):
        print(f"[i] {avert}")
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
        return outillage_seul(dest, conf, table_vide=substitutions(conf))

    # Garde du maillon 4, en code et pas seulement dans la prose du SKILL.md.
    # L'atelier est le dossier de `config.yaml` quand il porte la carte des domaines.
    atelier = chemin_config.parent if (chemin_config.name == "config.yaml"
                                       and (chemin_config.parent / "02-ontologie.md").is_file()) else None
    if atelier is None:
        print(f"[i] Aucun atelier à côté de {chemin_config} (config.yaml et 02-ontologie.md) : "
              "l'état du rangement n'est pas vérifié, et rien n'y est inscrit.")
    if atelier is not None and rangement_inacheve(atelier):
        print("[X] Le rangement de vos dossiers n'est pas conclu (appliqué en partie, pas encore clos, ou sa "
              "trace est illisible) : terminez-le ou défaites-le avant de construire. Dites « rangeons mes "
              "dossiers ».", file=sys.stderr)
        return 2

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
        if ignorable(src):
            continue
        if src.suffix in SUFFIXES_TEXTE:
            cible.write_text(substituer(src.read_text(encoding="utf-8"), table),
                             encoding="utf-8")
        else:
            shutil.copy2(src, cible)
        ecrits += 1

    # La config du client vit DANS son vault : c'est ce qui rend le vault
    # autonome et le lint exécutable sans argument supplementaire.
    # Mais PAS `mentions_interdites` : cette liste porte les marques et les
    # outils du consultant, qu'il saisit lui-meme (decision 6, aucun nom de
    # client), et la copier ici ferait voyager ces marques chez le client —
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

    copier_ingest(dest)

    # Les permissions : les racines de collecte en lecture, jamais en écriture.
    # Générées et non copiées : elles dépendent de `collecte.racines`.
    ecrire_settings(dest, conf)

    # Les notes de domaine, une par entree de config. Sans elles, `Centre.md`
    # listait les domaines en wikilinks vers des notes inexistantes : le point
    # d'entree du vault, celui que la doctrine annonce comme le plus connecte,
    # etait livre avec autant de liens morts que le client a de domaines.
    ecrits += notes_domaines(conf, dest)
    ecrits += note_referentiel(conf, dest)

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
        if not (f.is_file() and f.suffix in SUFFIXES_TEXTE):
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
        poser_identite(dest, conf)
        subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "Vault initial (scaffold Cortex)"],
                       cwd=dest, check=True)
        git_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        git_ok = False
        print(f"[i] git non initialise ({e}), le vault reste utilisable.")

    if atelier is not None:
        marquer_construction(atelier)
    print(f"✓ Vault instancie : {dest}")
    print(f"✎ {ecrits} fichier(s) du gabarit + config.yaml + graph.json + Configuration.md")
    print(f"✎ {len(cortex_config.codes_domaines(conf))} domaine(s), "
          f"mode {conf.get('mode')}, 0 moustache residuelle")
    racines = racines_collecte(conf)
    print(f"✎ settings.json : {len(racines)} racine(s) en lecture seule, "
          f"{len(racines) + 1} regle(s) deny (dont git commit), 2 hooks")
    if git_ok:
        depot_prive(dest, "cortex-" + (conf.get("organisation") or {}).get("code", "vault"), a.depot_prive)
    print(f"→ Suite : python3 lint_sante.py --vault \"{dest}\"")
    return 0


def _autotest():
    import tempfile
    home = str(Path.home())
    assert forme_tilde(home + "/Documents/X") == "~/Documents/X"
    assert forme_tilde("~/Documents") == "~/Documents"
    assert forme_tilde("/srv/partage") == "/srv/partage"
    assert forme_tilde("") == ""

    conf = {"collecte": {"racines": [home + "/Documents", "~/Desktop/Travail"]}}
    s = settings_json(conf)
    assert s["permissions"]["additionalDirectories"] == ["~/Documents", "~/Desktop/Travail"], s
    assert s["permissions"]["deny"] == ["Edit(~/Documents/**)", "Edit(~/Desktop/Travail/**)",
                                        "Bash(git commit:*)"], s
    assert s["permissions"]["allow"] == ALLOW
    assert set(s["hooks"]) == {"SessionStart", "Stop"}
    # Bash confiné : pas d'échappatoire, racines interdites, commun autorisé en fédéré.
    sb = settings_json(dict(conf, mode="federe", commun={"racine": home + "/Cortex/commun"}),
                       "darwin")["sandbox"]
    assert sb["enabled"] and sb["allowUnsandboxedCommands"] is False, sb
    assert sb["filesystem"] == {"denyWrite": ["~/Documents", "~/Desktop/Travail"],
                                "allowWrite": ["~/Cortex/commun"]}, sb
    assert settings_json(conf, "darwin")["sandbox"]["filesystem"]["allowWrite"] == []
    assert settings_json(conf, "darwin")["sandbox"]["network"]["allowedDomains"] == ["github.com"]
    assert "api.notion.com" in settings_json(dict(conf, miroir={"outil": "notion"}), "darwin")["sandbox"]["network"]["allowedDomains"]
    assert "sandbox" not in settings_json(conf, "win32")
    # Config v1 : sans `collecte.racines`, la racine est `chemins.dossiers_projets`.
    assert racines_collecte({"chemins": {"dossiers_projets": home + "/Affaires"}}) == ["~/Affaires"]
    assert racines_collecte({}) == []
    # Racine par lien symbolique : la forme réelle est écrite en plus (constat M4).
    _d = Path(tempfile.mkdtemp()); (_d / "reel").mkdir(); (_d / "lien").symlink_to(_d / "reel")
    _s = settings_json({"collecte": {"racines": [str(_d / "lien")]}})
    assert len(_s["permissions"]["additionalDirectories"]) == 2 and any(
        "reel" in x for x in _s["permissions"]["deny"]), _s

    # Un scaffold réel depuis l'exemple, dans un dossier temporaire.
    exemple = RACINE_SKILL / "template" / "config.example.yaml"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "vault"
        r = subprocess.run([sys.executable, __file__, "--config", str(exemple), "--out", str(out)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        s = json.loads((out / ".claude" / "settings.json").read_text(encoding="utf-8"))
        assert s["permissions"]["deny"], s
        assert (out / ".claude" / "hooks" / "session_start.py").is_file()
        assert (out / ".claude" / "skills" / "parle" / "SKILL.md").is_file()
        assert (out / ".claude" / "skills" / "bilan" / "SKILL.md").is_file()
        # Le rafraichissement d'un structurant perime doit etre executable
        # depuis le seul vault, plugin absent (mode consultant).
        assert (out / ".claude" / "skills" / "ingest" / "copie_structurant.py").is_file()
        assert "gh repo create cortex-acme --private" in r.stdout, r.stdout
        assert "/Users/" not in (out / "90 - Meta" / "Runbook - Nouveau Projet.md").read_text(encoding="utf-8")
        assert "Bash(python3 .claude/skills/ingest/copie_structurant.py:*)" in s["permissions"]["allow"]

        # Un `__pycache__` dans le gabarit ne doit ni faire sortir en 1 ni
        # voyager chez le client : il apparait des qu'un script du gabarit a ete
        # importe une fois, et `--outillage-seul` le lisait en UTF-8.
        intrus = GABARIT / ".claude" / "hooks" / "__pycache__" / "stop.cpython-99.pyc"
        intrus.parent.mkdir(parents=True, exist_ok=True)
        intrus.write_bytes(b"\xcb\x0d\x0d\x0a\x00\xff\xfe")
        try:
            r = subprocess.run([sys.executable, __file__, "--config", str(exemple),
                                "--out", str(out), "--outillage-seul"],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr[-400:]
            assert not (out / ".claude" / "hooks" / "__pycache__").exists(), "le .pyc a voyage"
        finally:
            shutil.rmtree(intrus.parent)
    # {{REFERENTIEL}} : la règle porte le chemin en forme ~ quand le dossier
    # commun existe, la phrase d'absence sinon ; aucune moustache ne survit.
    with tempfile.TemporaryDirectory() as tmp:
        base = exemple.read_text(encoding="utf-8")
        for nom, bloc, attendu in (
                ("avec", 'referentiel:\n  etat: existant\n  chemin: "~/Documents/Clients/Référentiel"\n',
                 "`~/Documents/Clients/Référentiel`"),
                ("sans", "", "Aucun dossier commun déclaré.")):
            atelier = Path(tmp) / nom / "_cortex"
            atelier.mkdir(parents=True)
            cfg = atelier / "config.yaml"
            texte = re.sub(r"(?m)^referentiel:\n(  .*\n)*", "", base) + "\n" + bloc
            if bloc:  # le dossier commun vit sous une racine que d'autres partagent (contrat 2.3 §1)
                texte = texte.replace("partagees: []", 'partagees: ["~/Documents/Clients"]')
            cfg.write_text(texte, encoding="utf-8")
            out = Path(tmp) / nom / "vault"
            r = subprocess.run([sys.executable, __file__, "--config", str(cfg), "--out", str(out)],
                               capture_output=True, text=True)
            assert r.returncode == 0, (nom, r.stderr[-400:])
            claude = (out / "CLAUDE.md").read_text(encoding="utf-8")
            assert attendu in claude, (nom, claude[-600:])
            restes = [f for f in out.rglob("*.md") if "Templates" not in f.parts
                      and re.search(r"\{\{[A-Z_]+\}\}", f.read_text(encoding="utf-8"))]
            assert not restes, (nom, restes[:3])
        # N5 : la construction n'écrit jamais « passée sans rangement » quand un geste est fait ;
        # témoin : sans geste fait, elle l'écrit.
        for journal, attendu_statut in (('{"id": "r001", "resultat": "fait"}\n', "statut: propose"),
                                        ("", "statut: passee")):
            at = Path(tmp) / f"n5-{bool(journal)}"
            at.mkdir()
            (at / "02-ontologie.md").write_text("---\nstatut: valide\n---\n", encoding="utf-8")
            (at / "03-rangement.md").write_text("---\nstatut: propose\nacceptees: []\n---\n", encoding="utf-8")
            (at / "03-rangement-journal.jsonl").write_text(journal, encoding="utf-8")
            marquer_construction(at)
            md = (at / "03-rangement.md").read_text(encoding="utf-8")
            assert attendu_statut in md and "construit_le:" in md, (journal, md)
        # La garde du maillon 4 : un 3b `en_cours` refuse, en code 2, sans rien écrire.
        import etat
        avant = etat.generer
        etat.generer = lambda _a: {"etapes": [{"numero": "3b", "etat": "en_cours"}]}
        try:
            assert rangement_inacheve(Path(tmp))
        finally:
            etat.generer = avant
        assert not rangement_inacheve(Path(tmp) / "avec" / "_cortex")

    print("OK scaffold.py : {{REFERENTIEL}} avec et sans dossier commun, garde du rangement, forme ~, settings.json, hooks, skills parle, bilan et ingest, .pyc ignore, depot prive propose")
    return 0


if __name__ == "__main__":
    sys.exit(main())
