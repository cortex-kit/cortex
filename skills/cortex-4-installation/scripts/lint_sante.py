#!/usr/bin/env python3
"""lint_sante.py — audit santé d'un vault Cortex. stdlib pure, lecture seule.

Porté depuis le linter du système d'origine. Deux différences de fond :

  1. TOUT SEUIL VIENT DE config.yaml. L'original portait ses enums et ses
     seuils en constantes, dupliqués avec la doctrine et deux scripts.
     Ici la config est la source unique.

  2. LES CONTRÔLES QUI COMPTENT BLOQUENT. Dans l'original, le journal obèse et
     le pointeur manquant étaient des `[i]` informatifs : ils constataient
     depuis des mois sans rien empêcher, et 7 fiches ont dérivé jusqu'à 51
     lignes sur une seule entrée de journal. La détection sans blocage ne
     protège pas. Ici ces contrôles sont dans DURS et mettent le code à 1.

Usage :
  python3 lint_sante.py --vault <chemin>
  python3 lint_sante.py --vault <chemin> --config <chemin>   # défaut : <vault>/config.yaml
  python3 lint_sante.py --vault <chemin> --json

Code retour : 0 = sain, 1 = au moins un contrôle dur en échec, 2 = erreur d'appel.
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cortex_config  # noqa: E402

# Placeholders remplis par Obsidian lui-même à la création d'une note.
# Leur présence dans un gabarit est normale et permanente.
RE_OBSIDIAN = re.compile(r"\{\{(title|date|time)(:[^}]*)?\}\}")

# Dossiers hors périmètre de contrôle (gabarits, packs opératoires, technique).
IGNORE_DIRS = {
    "90 - Meta/Templates",
    "90 - Meta/passation",
    "60 - Journal",
    ".obsidian",
    ".claude",
    ".trash",
    ".git",
}
IGNORE_BASENAMES = {"_README.md", "README.md", "CLAUDE.md", "Configuration.md"}

# Préfixes de tag qui encodent une logique déjà portée par une propriété.
ANTI_PATTERN_TAGS_PREFIX = (
    "vehicule-", "vehicule/", "payeur-", "payeur/",
    "domaine-", "domaine/", "cycle-", "cycle/", "phase-", "phase/",
)

# Contrôles durs : leur présence met le code de retour à 1.
# `journal_entree_obese` et `pointeur_canonique_absent` sont ici alors qu'ils
# étaient informatifs dans l'original. C'est le changement le plus important
# de ce port.
DURS = (
    "contrat_config_invalide",
    "liens_casses",
    "orphelins",
    "pointeur_canonique_absent",
    "tags_anti_pattern",
    "tags_hors_domaines",
    "phase_hors_enum",
    "progression_absente",
    "journal_entree_obese",
    "moustaches_residuelles",
    "chemins_absolus",
    "commun_edite_main",
)


# ── Parsing (repris de l'original) ──────────────────────────────────────────


def _valeur(v):
    """Nettoie une valeur de frontmatter : retire un commentaire de fin de ligne
    puis les guillemets.

    Le commentaire de fin de ligne est indispensable. Les templates documentent
    leurs champs en ligne — `cycle: mission   # cle de config.cycles` — ce qui
    est la bonne pratique pour un fichier qu'un humain remplit. Sans ce
    nettoyage, la valeur lue est `mission   # cle de config.cycles`, et le
    contrôle d'enum échoue sur toute fiche créée depuis un template.

    Le parseur dont ce port est issu portait la même faille, latente : elle ne
    s'est révélée qu'en instanciant réellement une fiche depuis le gabarit.
    """
    v = v.strip()
    if not (v.startswith('"') or v.startswith("'")):
        # `#` non précédé d'un espace = probablement un tag ou une couleur
        m = re.search(r"\s+#", v)
        if m:
            v = v[: m.start()].strip()
    else:
        q = v[0]
        fin = v.find(q, 1)
        if fin != -1:
            v = v[: fin + 1]
    return v.strip('"').strip("'")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm, courant = {}, None
    for line in text[3:end].strip().splitlines():
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- "):
            v = _valeur(line.lstrip()[2:])
            if courant is not None:
                courant.append(v)
            continue
        m = re.match(r"^([\w_]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        k, brut = m.group(1).strip(), m.group(2).strip()
        if brut == "" or brut.startswith("#"):
            courant = []
            fm[k] = courant
        else:
            if brut.startswith("[") and brut.endswith("]"):
                fm[k] = [_valeur(x) for x in brut[1:-1].split(",") if x.strip()]
            else:
                fm[k] = _valeur(brut)
            courant = None
    return fm


def liens_sortants(body):
    """Wikilinks reels d'un corps de note.

    Le code est retire d'abord : un `[[Nom du domaine]]` entre backticks est de
    la syntaxe citee, pas un lien — Obsidian ne le rend pas non plus. Sans ce
    retrait, la doctrine livree avec le vault, qui cite le format des
    proprietes, produisait trois liens morts a chaque installation.
    """
    sans_code = re.sub(r"```.*?```", " ", body, flags=re.S)
    sans_code = re.sub(r"`[^`\n]*`", " ", sans_code)
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", sans_code)


def est_ignore(rel):
    parts = rel.parts
    for ign in IGNORE_DIRS:
        ip = Path(ign).parts
        if len(parts) >= len(ip) and parts[: len(ip)] == ip:
            return True
    return rel.name in IGNORE_BASENAMES


def en_liste(v):
    if not v:
        return []
    return [v] if isinstance(v, str) else list(v)


def age_jours(v):
    if not isinstance(v, str) or not v.strip():
        return None
    try:
        d = datetime.strptime(v.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    return (date.today() - d).days


def _est_commentaire(ligne):
    """Une ligne appartenant à un bloc de commentaire HTML, ou à elle seule un
    commentaire. Approximation volontaire : on ne suit pas l'état d'ouverture du
    bloc sur plusieurs lignes, on écarte les lignes qui n'ont visiblement pas de
    contenu utile. Suffisant pour un budget de lignes.

    ponytail: heuristique ligne par ligne ; si un commentaire multiligne sans
    marqueur devient un cas réel, suivre l'état d'ouverture.
    """
    l = ligne.strip()
    return (l.startswith("<!--") or l.endswith("-->")
            or (l.startswith("<") and l.endswith(">")))


def metriques_journal(body):
    """(total_lignes, max_lignes_entree) de la section ## Journal."""
    lines = body.splitlines()
    debut = None
    for i, l in enumerate(lines):
        if re.match(r"^##\s+Journal\s*$", l):
            debut = i + 1
            break
    if debut is None:
        return (0, 0)
    fin = len(lines)
    for j in range(debut, len(lines)):
        if re.match(r"^##\s+", lines[j]):
            fin = j
            break
    # Les lignes de commentaire HTML ne comptent pas : les templates portent
    # leur mode d'emploi dans un bloc <!-- --> sous le titre de section, et ces
    # lignes tomberaient dans le budget de la première entrée réelle. Une
    # consigne de rédaction n'est pas du contenu recopié.
    section = [l for l in lines[debut:fin] if not _est_commentaire(l)]
    maxi, cur, n = 0, None, 0
    for l in section:
        if re.match(r"^###\s+\d{4}-\d{2}-\d{2}", l):
            if cur is not None:
                maxi = max(maxi, n)
            cur, n = l, 0
        elif cur is not None:
            n += 1
    if cur is not None:
        maxi = max(maxi, n)
    return (len(section), maxi)


# ── Le lint ────────────────────────────────────────────────────────────────


def lint(vault, conf):
    sante = conf.get("sante", {})
    seuil_entree = sante.get("max_lignes_entree_journal", 10)
    seuil_total = sante.get("max_lignes_journal", 60)
    seuil_perime = sante.get("journal_perime_jours", 14)
    exige_pointeur = sante.get("pointeur_canonique_obligatoire", True)
    revue_mois = sante.get("agent_metier_revue_mois", 6)
    codes = set(cortex_config.codes_domaines(conf))
    cles_scaffold = cortex_config.CLES_SCAFFOLD

    f = {k: [] for k in (
        "orphelins", "pointeur_canonique_absent", "tags_anti_pattern",
        "tags_hors_domaines", "phase_hors_enum", "progression_absente",
        "journal_entree_obese", "moustaches_residuelles", "chemins_absolus",
        "commun_edite_main", "journal_total_long", "dernier_journal_perime",
        "agents_perimes", "notes_sans_frontmatter", "contrat_config_invalide",
        "liens_casses",
    )}
    f["stats"] = {"total_md": 0, "audites": 0, "ignores": 0}

    # Toutes les notes du vault, y compris celles qu'on n'audite pas : une note
    # ignoree reste une cible de lien parfaitement legitime.
    notes_existantes = {p.stem for p in vault.rglob("*.md")
                        if p.is_file() and ".git" not in p.parts}

    # Avant d'auditer les notes, auditer le contrat qui les regit : un vault
    # sans domaine declare n'a rien qui puisse etre sain.
    f["contrat_config_invalide"] = cortex_config.valider_installable(conf)

    for md in sorted(vault.rglob("*.md")):
        rel = md.relative_to(vault)
        f["stats"]["total_md"] += 1

        try:
            text = md.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        # Ces contrôles s'appliquent à TOUT fichier, y compris ceux qu'on ignore
        # par ailleurs : un chemin absolu dans un CLAUDE.md est un défaut de
        # livraison même si le CLAUDE.md n'est pas une note.
        #
        # Trois familles de placeholders cohabitent et deux sont LÉGITIMES :
        #   - scaffold      {{ORGANISATION}}   -> jamais admis, nulle part
        #   - projet        {{NOM_PROJET}}     -> admis dans Templates/ seulement
        #   - Obsidian core {{title}}          -> admis partout
        # Un contrôle sur `"{{" in text` rejette les deux dernières et rend le
        # lint inutilisable : c'est exactement ce qu'il a fait au premier essai.
        dans_templates = "Templates" in rel.parts
        for cle in cles_scaffold:
            if cle in text:
                f["moustaches_residuelles"].append({"file": str(rel), "cle": cle})
        if not dans_templates:
            for m in re.finditer(r"\{\{[^}\n]+\}\}", text):
                if not RE_OBSIDIAN.fullmatch(m.group(0)):
                    f["moustaches_residuelles"].append(
                        {"file": str(rel), "cle": m.group(0)})
                    break
        for m in re.finditer(r"(/Users/[\w.-]+|/home/[\w.-]+|[A-Z]:\\\\)", text):
            f["chemins_absolus"].append({"file": str(rel), "extrait": m.group(1)})
            break

        if est_ignore(rel):
            f["stats"]["ignores"] += 1
            continue
        f["stats"]["audites"] += 1

        fm = parse_frontmatter(text)
        if not fm:
            f["notes_sans_frontmatter"].append(str(rel))
            continue

        typ = fm.get("type", "")
        body = text[text.find("\n---", 3) + 4:] if text.startswith("---") else text

        if typ not in ("hub", "dashboard") and not fm.get("domaine") and not liens_sortants(body):
            f["orphelins"].append(str(rel))

        # Un lien interne qui ne mene nulle part. Le controle manuel de la
        # recette porte sur les pointeurs EXTERNES, dont la destination n'est
        # pas verifiable par une machine ; un wikilink, lui, l'est — et faute
        # de ce controle un vault fraichement installe pouvait etre livre avec
        # des liens morts depuis Centre.md sans que rien ne le signale.
        for cible in liens_sortants(body) + liens_sortants(str(fm.get("domaine") or "")):
            nom = cible.split("#")[0].strip()
            if nom and nom not in notes_existantes:
                f["liens_casses"].append({"file": str(rel), "vers": nom})

        tags = en_liste(fm.get("tags"))
        mauvais = [t for t in tags if any(t.startswith(p) for p in ANTI_PATTERN_TAGS_PREFIX)]
        if mauvais:
            f["tags_anti_pattern"].append({"file": str(rel), "tags": mauvais})
        # La casse ne se documente pas, elle se contraint : dans le système d'origine, deux casses
        # d'un même code coexistaient avec le canon.
        hors = [t for t in tags
                if t.startswith("d/") and t[2:] not in codes]
        if hors:
            f["tags_hors_domaines"].append({"file": str(rel), "tags": sorted(hors)})

        total_j, entree_max = metriques_journal(body)
        if entree_max > seuil_entree:
            f["journal_entree_obese"].append({
                "file": str(rel), "entree_max": entree_max, "seuil": seuil_entree})
        if total_j > seuil_total:
            f["journal_total_long"].append({
                "file": str(rel), "lignes": total_j, "seuil": seuil_total})

        if typ == "projet":
            statut = fm.get("statut")
            cycle = fm.get("cycle")
            phase = fm.get("phase")
            autorisees = cortex_config.phases_autorisees(conf, cycle)

            if phase and phase not in autorisees:
                f["phase_hors_enum"].append({
                    "file": str(rel), "phase": phase, "cycle": cycle})
            if statut == "actif" and not fm.get("progression"):
                f["progression_absente"].append(str(rel))
            if exige_pointeur and statut in ("actif", None) and not any(
                    fm.get(k) for k in ("url_canonique", "repo", "dossier_local")):
                f["pointeur_canonique_absent"].append(str(rel))
            if statut == "actif":
                a = age_jours(fm.get("dernier_journal"))
                if a is None or a > seuil_perime:
                    f["dernier_journal_perime"].append({"file": str(rel), "age_jours": a})

    # Agents métier périmés : un agent qui répond encore alors que ses règles
    # de gestion ont changé est plus dangereux qu'un agent absent.
    for agent in sorted((vault / ".claude" / "agents").glob("*.md")):
        fm = parse_frontmatter(agent.read_text(encoding="utf-8"))
        a = age_jours(fm.get("revoir_le"))
        if a is not None and a > 0:
            f["agents_perimes"].append({
                "file": agent.name, "revoir_le": fm.get("revoir_le"), "retard_jours": a})
        elif fm.get("metier") in (True, "true") and not fm.get("revoir_le"):
            f["agents_perimes"].append({
                "file": agent.name, "revoir_le": None,
                "retard_jours": f"aucune date de revue (defaut {revue_mois} mois)"})

    # Le vault commun est GÉNÉRÉ : y écrire à la main casse le modèle fédéré,
    # où chaque fait n'a qu'un propriétaire.
    racine = (conf.get("commun") or {}).get("racine", "")
    if conf.get("mode") == "federe" and racine:
        for md in Path(racine).expanduser().rglob("*.md"):
            if "<!-- généré" not in md.read_text(encoding="utf-8", errors="replace")[:400]:
                f["commun_edite_main"].append(str(md))

    return f


# ── Rendu ──────────────────────────────────────────────────────────────────

LIBELLES = {
    "contrat_config_invalide": "manque(s) dans config.yaml",
    "liens_casses": "lien(s) [[ ]] vers une note inexistante",
    "orphelins": "note(s) orpheline(s) (sans domaine ni lien sortant)",
    "pointeur_canonique_absent": "projet(s) actif(s) sans pointeur canonique",
    "tags_anti_pattern": "note(s) avec tag encodant une propriete",
    "tags_hors_domaines": "note(s) avec tag #d/ hors des domaines declares",
    "phase_hors_enum": "projet(s) avec phase hors de l'enum de son cycle",
    "progression_absente": "projet(s) actif(s) sans progression",
    "journal_entree_obese": "fiche(s) avec une entree de journal trop longue",
    "moustaches_residuelles": "fichier(s) avec une moustache {{ }} non substituee",
    "chemins_absolus": "fichier(s) avec un chemin absolu",
    "commun_edite_main": "note(s) du vault commun editee(s) a la main",
    "journal_total_long": "fiche(s) au journal long",
    "dernier_journal_perime": "projet(s) actif(s) au dernier_journal perime",
    "agents_perimes": "agent(s) metier a revoir",
    "notes_sans_frontmatter": "note(s) sans frontmatter (tolere)",
}


def rendre(f, conf):
    s = f["stats"]
    nom = (conf.get("organisation") or {}).get("nom", "?")
    print(f"\n== Lint {nom} == ({s['audites']}/{s['total_md']} notes auditees, "
          f"{s['ignores']} ignorees)\n")
    sain = True
    for cle, libelle in LIBELLES.items():
        items = f.get(cle) or []
        if not items:
            continue
        dur = cle in DURS
        if dur:
            sain = False
        print(f"[{'!' if dur else 'i'}] {len(items)} {libelle} :")
        for it in items[:12]:
            print(f"    - {it if isinstance(it, str) else json.dumps(it, ensure_ascii=False)}")
        if len(items) > 12:
            print(f"    ... et {len(items) - 12} autre(s)")
        print()
    print("[OK] Vault sain." if sain
          else "[X] Au moins un controle DUR en echec. Code retour 1.")
    return sain


def main():
    p = argparse.ArgumentParser(description="Audit sante d'un vault Cortex.")
    p.add_argument("--vault", required=True)
    p.add_argument("--config", default=None, help="defaut : <vault>/config.yaml")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    vault = Path(a.vault).expanduser().resolve()
    if not vault.is_dir():
        print(f"[X] Vault introuvable : {vault}", file=sys.stderr)
        return 2
    cfg = Path(a.config).expanduser() if a.config else vault / "config.yaml"
    if not cfg.is_file():
        print(f"[X] Config introuvable : {cfg}", file=sys.stderr)
        return 2

    conf = cortex_config.charger(cfg)
    f = lint(vault, conf)

    if a.json:
        print(json.dumps(f, indent=2, ensure_ascii=False))
    else:
        rendre(f, conf)
    return 1 if any(f.get(k) for k in DURS) else 0


if __name__ == "__main__":
    sys.exit(main())
