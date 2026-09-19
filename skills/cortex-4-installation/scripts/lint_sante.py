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

  3. LE RÉGIME DE LA DONNÉE EST LU. En régime copie, `50 - Ressources/Structurants/`
     porte des copies validées : le plafond de lignes ne s'y applique pas, et
     `structurant_perime` se lève quand le sha256 de la source diffère de celui
     de la copie. La péremption se calcule à chaque lint, elle n'est jamais
     stockée : un drapeau écrit vieillit, un hash recalculé ne ment pas.

Usage :
  python3 lint_sante.py --vault <chemin>
  python3 lint_sante.py --vault <chemin> --config <chemin>   # défaut : <vault>/config.yaml
  python3 lint_sante.py --vault <chemin> --json
  python3 lint_sante.py --vault <chemin> --bref              # une ligne, pour le hook
  python3 lint_sante.py --autotest

Code retour : 0 = sain, 1 = au moins un contrôle dur en échec, 2 = erreur d'appel.
"""

import argparse
import hashlib
import json
import re
import subprocess
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
    "_export",      # copies générées par la clôture pour le commun
    "_cortex",      # l'atelier d'installation, quand il vit dans le vault
}
IGNORE_BASENAMES = {"_README.md", "README.md", "CLAUDE.md", "Configuration.md"}

# Régime copie : les structurants copiés, contrat 04 §2.
STRUCTURANTS = Path("50 - Ressources/Structurants")
VISIBILITES = ("prive", "commun")

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
    "visibilite_hors_enum",
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


def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 16), b""):
            h.update(bloc)
    return h.hexdigest()


def peremption_structurant(fm):
    """None si la copie est à jour, sinon la raison. Calculée, jamais stockée."""
    src = str(fm.get("source_path") or "").strip()
    if not src and fm.get("structurant") == "fil_structurant":
        return None    # un fil de messagerie en résumé n'a pas de fichier qui change
    if not src or not fm.get("hash"):
        return "frontmatter incomplet (source_path ou hash absent)"
    chemin = Path(src).expanduser()
    if not chemin.is_file():
        return "source absente"
    if sha256_fichier(chemin) != str(fm.get("hash")).strip():
        return "source modifiee depuis la copie"
    return None


def derniere_cloture(vault):
    """Date du dernier commit du vault, ou None sans git."""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ci"], cwd=vault,
                           capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout.strip()[:10] if r.returncode == 0 and r.stdout.strip() else None


# ── Le lint ────────────────────────────────────────────────────────────────


def lint(vault, conf):
    sante = conf.get("sante", {})
    seuil_entree = sante.get("max_lignes_entree_journal", 10)
    seuil_total = sante.get("max_lignes_journal", 60)
    seuil_perime = sante.get("journal_perime_jours", 14)
    exige_pointeur = sante.get("pointeur_canonique_obligatoire", True)
    revue_mois = sante.get("agent_metier_revue_mois", 6)
    jours_cloture = sante.get("jours_sans_cloture_alerte", 7)
    codes = set(cortex_config.codes_domaines(conf))
    cles_scaffold = cortex_config.CLES_SCAFFOLD

    f = {k: [] for k in (
        "orphelins", "pointeur_canonique_absent", "tags_anti_pattern",
        "tags_hors_domaines", "phase_hors_enum", "progression_absente",
        "journal_entree_obese", "moustaches_residuelles", "chemins_absolus",
        "commun_edite_main", "visibilite_hors_enum", "journal_total_long",
        "dernier_journal_perime", "structurant_perime", "cloture_ancienne",
        "agents_perimes", "notes_sans_frontmatter", "contrat_config_invalide",
        "liens_casses",
    )}
    f["stats"] = {"total_md": 0, "audites": 0, "ignores": 0,
                  "regime": (conf.get("donnees") or {}).get("regime", "pointeur")}

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
        # Une lettre de lecteur s'ecrit avec UN antislash dans le texte lu. La v1
        # en exigeait deux (`\\\\` en chaine brute) et ne voyait donc aucun
        # chemin Windows. L'auto-test en porte le temoin.
        for m in re.finditer(r"(/Users/[\w.-]+|/home/[\w.-]+|[A-Za-z]:\\)", text):
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
        structurant = rel.parts[: len(STRUCTURANTS.parts)] == STRUCTURANTS.parts

        vis = fm.get("visibilite")
        if vis and vis not in VISIBILITES:
            f["visibilite_hors_enum"].append({"file": str(rel), "visibilite": vis})

        if structurant:
            raison = peremption_structurant(fm)
            if raison:
                f["structurant_perime"].append({
                    "file": str(rel), "source_path": fm.get("source_path", ""), "raison": raison})

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

        # Une copie de structurant est longue par nature : le plafond de lignes
        # protège les fiches qui pointent, pas les copies validées une par une.
        total_j, entree_max = (0, 0) if structurant else metriques_journal(body)
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

    # La dernière clôture, lue dans git : un vault qu'on ne clôture plus est
    # un vault qui meurt sans bruit. Le hook SessionStart relaie cette ligne.
    dc = derniere_cloture(vault)
    if dc:
        a = age_jours(dc)
        if a is not None and a > jours_cloture:
            f["cloture_ancienne"].append({"derniere_cloture": dc, "age_jours": a,
                                          "seuil": jours_cloture})

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
    "visibilite_hors_enum": "note(s) avec visibilite hors de prive | commun",
    "journal_total_long": "fiche(s) au journal long",
    "dernier_journal_perime": "projet(s) actif(s) au dernier_journal perime",
    "structurant_perime": "structurant(s) dont la source a change depuis la copie",
    "cloture_ancienne": "derniere cloture plus ancienne que le seuil",
    "agents_perimes": "agent(s) metier a revoir",
    "notes_sans_frontmatter": "note(s) sans frontmatter (tolere)",
}


def ligne_constat(it):
    """Un constat en une ligne lisible : le fichier, puis la raison.

    Les constats sont des dicts. Rendus en JSON brut, ils donnaient
    `{"file": "...", "source_path": "...", "raison": "..."}` a quelqu'un qui
    veut savoir quel fichier reprendre et pourquoi.
    """
    if not isinstance(it, dict):
        return str(it)
    tete = it.get("file") or it.get("chemin") or ""
    raison = (it.get("raison") or it.get("cle") or it.get("extrait")
              or it.get("visibilite") or "")
    if not raison:
        raison = ", ".join(f"{k} : {v}" for k, v in it.items()
                           if k not in ("file", "chemin"))
    return f"{tete} : {raison}" if tete and raison else (tete or raison)


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
            print(f"    - {ligne_constat(it)}")
        if len(items) > 12:
            print(f"    ... et {len(items) - 12} autre(s)")
        print()
    print("[OK] Vault sain." if sain
          else "[X] Au moins un controle DUR en echec. Code retour 1.")
    return sain


def bref(f):
    """Une ligne pour le hook SessionStart, en langage ordinaire."""
    durs = sum(len(f.get(k) or []) for k in DURS)
    dette = sum(len(f.get(k) or []) for k in LIBELLES if k not in DURS)
    # `structurant_perime` est deja dans `dette` : l'annoncer a part le comptait
    # deux fois dans la meme phrase (« 1 point a surveiller, 1 structurant perime »).
    ligne = f"Contrôle de santé : {durs} problème(s) bloquant(s), {dette} point(s) à surveiller."
    if f.get("cloture_ancienne"):
        c = f["cloture_ancienne"][0]
        ligne += (f" Dernière clôture il y a {c['age_jours']} jours (seuil {c['seuil']}) : "
                  "dites « clôture » en fin de bloc de travail.")
    return ligne


def main():
    p = argparse.ArgumentParser(description="Audit sante d'un vault Cortex.")
    p.add_argument("--vault")
    p.add_argument("--config", default=None, help="defaut : <vault>/config.yaml")
    p.add_argument("--json", action="store_true")
    p.add_argument("--bref", action="store_true", help="une ligne, pour le hook SessionStart")
    p.add_argument("--autotest", action="store_true")
    a = p.parse_args()
    if a.autotest:
        return _autotest()
    if not a.vault:
        p.error("--vault est requis")

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
    elif a.bref:
        print(bref(f))
    else:
        rendre(f, conf)
    return 1 if any(f.get(k) for k in DURS) else 0


CONFIG_TEST = """version: 1
organisation:
  nom: "Test"
  code: test
  redacteur: "T"
mode: solo
chemins:
  dossiers_projets: "~/Documents/Test"
donnees:
  regime: copie
domaines:
  - { code: ops, nom: "Ops", couleur: "#1c42da" }
cycles:
  - { cycle: mission, phase: "Cadrage", progression: 20 }
sante:
  max_lignes_entree_journal: 10
  jours_sans_cloture_alerte: 7
"""


def _autotest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp) / "vault"
        (v / STRUCTURANTS / "process").mkdir(parents=True)
        (v / "10 - Domaines").mkdir()
        (v / "config.yaml").write_text(CONFIG_TEST, encoding="utf-8")
        conf = cortex_config.charger(v / "config.yaml")
        (v / "10 - Domaines" / "Ops.md").write_text(
            "---\ntype: domaine\nvisibilite: commun\ntags:\n  - d/ops\n---\n# Ops\n\n[[Ops]]\n", encoding="utf-8")
        source = Path(tmp) / "PROCESS.md"
        source.write_text("# Process\n\nversion 1\n", encoding="utf-8")
        long_journal = "## Journal\n\n### 2026-09-19\n\n" + "ligne\n" * 30
        copie = v / STRUCTURANTS / "process" / "PROCESS.md"
        copie.write_text(f"---\ntype: structurant\nstructurant: process\ndomaine: \"[[Ops]]\"\n"
                         f"source_path: \"{source}\"\nhash: {sha256_fichier(source)}\ncopie_le: 2026-09-19\n---\n"
                         f"# Process\n\n{long_journal}", encoding="utf-8")

        f = lint(v, conf)
        assert not any(f[k] for k in DURS), {k: f[k] for k in DURS if f[k]}
        assert not f["journal_entree_obese"], "le plafond de lignes doit etre suspendu sur Structurants/"
        assert not f["structurant_perime"], f["structurant_perime"]
        assert f["stats"]["regime"] == "copie"

        source.write_text("# Process\n\nversion 2\n", encoding="utf-8")
        f = lint(v, conf)
        assert f["structurant_perime"] and f["structurant_perime"][0]["raison"] == "source modifiee depuis la copie"
        assert not any(f[k] for k in DURS), "structurant_perime est une dette, pas un controle dur"
        source.unlink()
        assert lint(v, conf)["structurant_perime"][0]["raison"] == "source absente"

        (v / "10 - Domaines" / "Ops.md").write_text(
            "---\ntype: domaine\nvisibilite: public\ntags:\n  - d/ops\n---\n# Ops\n\n[[Ops]]\n", encoding="utf-8")
        f = lint(v, conf)
        assert f["visibilite_hors_enum"] == [{"file": "10 - Domaines/Ops.md", "visibilite": "public"}], f["visibilite_hors_enum"]
        assert "visibilite_hors_enum" in DURS

        assert f["cloture_ancienne"] == [], "sans git, aucun rappel"
        assert "bloquant" in bref(f)
        f["cloture_ancienne"] = [{"derniere_cloture": "2026-09-01", "age_jours": 18, "seuil": 7}]
        assert "18 jours" in bref(f)
        # Un constat perime est deja compte dans la dette : jamais annonce deux fois.
        f["structurant_perime"] = [{"file": "50 - Ressources/Structurants/process/P.md",
                                    "source_path": "~/x/P.docx",
                                    "raison": "source modifiee depuis la copie"}]
        assert "structurant" not in bref(f), bref(f)
        assert (ligne_constat(f["structurant_perime"][0])
                == "50 - Ressources/Structurants/process/P.md : source modifiee depuis la copie")
        assert ligne_constat({"derniere_cloture": "2026-09-01", "age_jours": 18, "seuil": 7}) \
            == "derniere_cloture : 2026-09-01, age_jours : 18, seuil : 7"
        # Le seuil est lu dans la config, pas codé en dur.
        assert conf["sante"]["jours_sans_cloture_alerte"] == 7
        assert peremption_structurant({"source_path": "", "hash": ""}).startswith("frontmatter incomplet")

        # Temoin : une lettre de lecteur telle qu'elle s'ecrit, un seul antislash.
        temoin = v / "10 - Domaines" / "Windows.md"
        temoin.write_text("---\ntype: domaine\ntags:\n  - d/ops\n---\n"
                          "# Windows\n\nLe dossier est C:\\Users\\Nom\\Documents.\n", encoding="utf-8")
        vus = lint(v, conf)["chemins_absolus"]
        assert [c for c in vus if c["file"] == "10 - Domaines/Windows.md"
                and c["extrait"] == "C:\\"], vus
        temoin.unlink()
    print("OK lint_sante.py : structurant_perime, plafond suspendu, visibilite, cloture_ancienne, --bref, lettre de lecteur")
    return 0


if __name__ == "__main__":
    sys.exit(main())
