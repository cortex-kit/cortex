#!/usr/bin/env python3
"""cortex_config.py — chargeur de config.yaml pour Cortex. stdlib pure.

POURQUOI CE FICHIER EXISTE
    Le noyau Cortex est en stdlib pure, comme le runtime dont il dérive.
    Un `import yaml` ajouterait une dépendance à installer chez chaque client,
    pour lire un fichier de 60 lignes. Ce chargeur coûte moins cher.

LE SOUS-ENSEMBLE YAML SUPPORTÉ (contrat, pas approximation)
    Quatre formes, et rien d'autre :

      1. scalaire racine                cle: valeur
      2. mapping imbriqué (1 niveau)    cle:
                                          sous: valeur
                                          sous2: [a, b]
      3. liste racine de dicts plats    cle:
                                          - { k: v, k2: v2 }
      4. liste inline                   cle: [a, b]

    Ce qui n'est PAS supporté, délibérément : mapping à 2 niveaux, liste de
    listes, liste de mappings multi-lignes, ancres, multi-documents, blocs
    littéraux (| et >).

    C'est pourquoi `cycles` est une LISTE PLATE avec une colonne `cycle`
    plutôt qu'un mapping de listes : la forme `cycles: {mission: [{...}]}`
    demanderait trois niveaux, donc un parseur bien plus gros. Une ligne par
    couple (cycle, phase) tient dans la forme 3, et `cycles_par_nom()` la
    regroupe à la lecture. Changer la forme de la donnée coûte moins que
    grossir l'outil qui la lit.

Usage :
    python3 cortex_config.py                      # auto-test sur config.example.yaml
    python3 cortex_config.py <chemin config.yaml> # charge et résume
"""

import re
import sys
from pathlib import Path

# ── Coercition des scalaires ────────────────────────────────────────────────

_VRAI = {"true", "yes", "oui"}
_FAUX = {"false", "no", "non"}


def _scalaire(v):
    """Convertit un scalaire YAML en type Python. Les guillemets sont retirés."""
    v = v.strip()
    if v.startswith("#"):
        return ""
    # Retirer un commentaire de fin de ligne, sauf s'il est dans des guillemets
    # ou s'il s'agit d'une couleur hexadécimale (#1c42da).
    if not (v.startswith('"') or v.startswith("'")):
        m = re.search(r"\s+#(?!\w{3,8}\b)", v)
        if m:
            v = v[: m.start()].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    bas = v.lower()
    if bas in _VRAI:
        return True
    if bas in _FAUX:
        return False
    if bas in ("", "~", "null"):
        return ""
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def _liste_inline(v):
    """`[a, b, "c d"]` -> [a, b, c d]. Respecte les guillemets."""
    interieur = v.strip()[1:-1]
    if not interieur.strip():
        return []
    morceaux, courant, quote = [], "", None
    for ch in interieur:
        if quote:
            if ch == quote:
                quote = None
            else:
                courant += ch
        elif ch in "\"'":
            quote = ch
        elif ch == ",":
            morceaux.append(courant)
            courant = ""
        else:
            courant += ch
    morceaux.append(courant)
    return [_scalaire(m) for m in morceaux if m.strip() != ""]


def _dict_inline(v):
    """`{ k: v, k2: "v 2" }` -> {k: v, k2: v 2}."""
    interieur = v.strip()[1:-1]
    out = {}
    for paire in _decoupe_virgules(interieur):
        if ":" not in paire:
            continue
        k, _, val = paire.partition(":")
        out[k.strip()] = _scalaire(val)
    return out


def _decoupe_virgules(s):
    """Découpe sur les virgules hors guillemets."""
    morceaux, courant, quote = [], "", None
    for ch in s:
        if quote:
            courant += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            courant += ch
            quote = ch
        elif ch == ",":
            morceaux.append(courant)
            courant = ""
        else:
            courant += ch
    morceaux.append(courant)
    return [m for m in morceaux if m.strip()]


# ── Le parseur ──────────────────────────────────────────────────────────────


def charger_texte(texte):
    """Parse le sous-ensemble documenté. Renvoie un dict."""
    conf = {}
    cle_courante = None      # clé racine ouverte (mapping ou liste)
    conteneur = None         # le dict ou la list en cours de remplissage

    for numero, brute in enumerate(texte.splitlines(), 1):
        ligne = brute.rstrip()
        nue = ligne.strip()
        if not nue or nue.startswith("#"):
            continue

        indente = len(ligne) - len(ligne.lstrip())

        # ── Item de liste ──
        if nue.startswith("- "):
            if conteneur is None:
                raise ValueError(
                    f"ligne {numero} : item de liste sans clé parente ouverte -> {nue!r}"
                )
            val = nue[2:].strip()
            if val.startswith("{") and val.endswith("}"):
                conteneur.append(_dict_inline(val))
            else:
                conteneur.append(_scalaire(val))
            continue

        m = re.match(r"^([\w_]+)\s*:\s*(.*)$", nue)
        if not m:
            raise ValueError(f"ligne {numero} : forme non supportée -> {nue!r}")
        cle, valeur = m.group(1), m.group(2).strip()

        # ── Clé imbriquée (sous un mapping racine ouvert) ──
        if indente > 0:
            if conteneur is None:
                raise ValueError(
                    f"ligne {numero} : clé indentée sans mapping parent -> {nue!r}"
                )
            if valeur.startswith("[") and valeur.endswith("]"):
                conteneur[cle] = _liste_inline(valeur)
            elif valeur == "":
                # Un mapping à 2 niveaux serait ici : hors contrat, on refuse
                # explicitement plutôt que d'avaler silencieusement.
                raise ValueError(
                    f"ligne {numero} : mapping à 2 niveaux non supporté ({cle!r}). "
                    "Aplatir en liste de dicts inline, voir la docstring."
                )
            else:
                conteneur[cle] = _scalaire(valeur)
            continue

        # ── Clé racine ──
        cle_courante = cle
        if valeur.startswith("[") and valeur.endswith("]"):
            conf[cle] = _liste_inline(valeur)
            conteneur = None
        elif valeur.startswith("{") and valeur.endswith("}"):
            conf[cle] = _dict_inline(valeur)
            conteneur = None
        elif valeur == "":
            # Forme 2 ou 3 : on ne sait pas encore. On ouvre un conteneur
            # hybride, résolu à la première ligne fille.
            conf[cle] = _Indetermine()
            conteneur = conf[cle]
        else:
            conf[cle] = _scalaire(valeur)
            conteneur = None

    return {k: (v.resoudre() if isinstance(v, _Indetermine) else v)
            for k, v in conf.items()}


class _Indetermine:
    """Une clé racine suivie d'un saut de ligne peut ouvrir un mapping OU une
    liste : on ne le sait qu'à la ligne suivante. Ce conteneur accepte les deux
    et se résout à la fin. Pas d'héritage — `class X(dict, list)` lève un
    TypeError en CPython (conflit de layout), et une passe de lecture anticipée
    coûterait plus cher que ces quinze lignes."""

    def __init__(self):
        self._map = {}
        self._items = []

    def append(self, v):
        self._items.append(v)

    def __setitem__(self, k, v):
        self._map[k] = v

    def resoudre(self):
        if self._items:
            return list(self._items)
        return dict(self._map)


def charger(chemin):
    chemin = Path(chemin)
    if not chemin.is_file():
        raise FileNotFoundError(f"config introuvable : {chemin}")
    return charger_texte(chemin.read_text(encoding="utf-8"))


# ── Accès dérivés ───────────────────────────────────────────────────────────


def cycles_par_nom(conf):
    """`cycles` est une liste plate ; renvoie {cycle: [{phase, progression}]}.
    C'est LA source unique du mapping phase -> progression : dans le système d'origine il
    était dupliqué dans Conventions.md, sync_cockpit.py et sync_missions.py."""
    out = {}
    for ligne in conf.get("cycles", []):
        out.setdefault(ligne.get("cycle", ""), []).append(
            {"phase": ligne.get("phase", ""),
             "progression": ligne.get("progression", 0)}
        )
    return out


def phases_autorisees(conf, cycle):
    """Enum fermé de `phase` pour un cycle donné. Vide = phase doit être vide."""
    return {e["phase"] for e in cycles_par_nom(conf).get(cycle, [])}


def codes_domaines(conf):
    return [d["code"] for d in conf.get("domaines", []) if d.get("code")]


def conduite(conf):
    """Mode de conduite de la chaîne : qui la mène. `solo` (l'installateur est
    le bénéficiaire) ou `consultant` (un tiers conduit). Absente ⇒ consultant :
    aucune config antérieure à la phase 5 ne porte la clé, et toutes étaient
    conduites par un consultant — c'est ce qui rend l'ajout rétro-compatible.

    La clé ne s'appelle pas `mode` : ce nom est déjà pris par la fédération du
    vault (`solo` | `federe`), une sémantique sans rapport. Arbitré 2026-08-23."""
    return conf.get("conduite", "consultant")


def valider_installable(conf):
    """Complétude du contrat : la config est-elle prête à produire un vault ?

    Distincte du chargement, qui ne vérifie que la syntaxe. La distinction est
    nécessaire parce que le maillon 1 écrit légitimement une config incomplète —
    `domaines` et `cycles` ne sont décidés qu'au maillon 3 — et doit pouvoir
    la relire sans erreur.

    Ce qu'elle ferme : sans elle, une config à `domaines: []` traversait toute
    la couche mécanique en vert. Elle se chargeait, elle scaffoldait un vault
    complet, et le lint le déclarait sain — alors qu'un vault sans domaine est
    exactement le mode de défaillance que la chaîne prétend interdire, et que
    `domaines` est documenté OBLIGATOIRE, 1 à 6, dans le fichier lui-même.
    Le seul garde-fou restant était un humain lisant un `statut:`.

    Renvoie une liste de messages ; vide = installable.
    """
    erreurs = []
    domaines = conf.get("domaines") or []
    plafond = (conf.get("collecte") or {}).get("plafond_domaines", 6)

    if not domaines:
        erreurs.append(
            "domaines: aucun domaine declare. Ils se decident au maillon 3, sur "
            "preuve chiffree tiree de l'inventaire. Installer sans eux produit un "
            "vault ou rien ne se classe.")
    elif len(domaines) > plafond:
        erreurs.append(
            f"domaines: {len(domaines)} declares, plafond {plafond}. Au-dela, chaque "
            "note hesite entre deux rattachements. C'est un constat de "
            "sous-segmentation a remonter au client, pas une case a ajouter.")

    codes = []
    for i, d in enumerate(domaines):
        code, nom = d.get("code", ""), d.get("nom", "")
        if not code or not nom:
            erreurs.append(f"domaines[{i}]: `code` et `nom` sont tous deux requis.")
            continue
        if not code.islower() or not code.isalpha() or not 2 <= len(code) <= 4:
            erreurs.append(
                f"domaines[{i}].code = {code!r} : 2 a 4 lettres minuscules. Il pilote "
                "le tag #d/ et le prefixe de fiche, il ne se corrige plus apres coup.")
        codes.append(code)
    if len(codes) != len(set(codes)):
        erreurs.append("domaines: deux domaines partagent le meme `code`.")

    if not conf.get("cycles"):
        erreurs.append(
            "cycles: aucun cycle declare. `phase` n'aurait alors aucun vocabulaire "
            "ferme, et le controle qui la verifie ne pourrait plus rien refuser.")

    if conduite(conf) not in ("solo", "consultant"):
        erreurs.append(
            f"conduite: {conf.get('conduite')!r} n'est ni 'solo' ni 'consultant'. "
            "Absente, la cle vaut 'consultant'. Ne pas confondre avec `mode`, "
            "qui porte la federation du vault (solo/federe).")

    communs = set(conf.get("vehicules") or []) & set(conf.get("payeurs") or [])
    if communs:
        erreurs.append(f"vehicules et payeurs partagent : {sorted(communs)}. "
                       "Qui vend et qui encaisse sont deux axes, jamais la meme valeur.")
    return erreurs


# Les moustaches remplies UNE FOIS, à l'installation, par scaffold.py.
# Cette liste vit ici et non dans scaffold.py parce que le lint doit la
# connaître alors qu'il tourne dans le vault du CLIENT, où scaffold.py n'est
# pas livré (c'est un outil d'installation, pas de maintenance).
#
# À distinguer de deux autres familles de placeholders, toutes deux légitimes :
#   - projet        {{NOM_PROJET}}, {{PREFIX}}  -> remplis par `nouveau-projet`,
#                                                  admis dans Templates/
#   - Obsidian core {{title}}, {{date:...}}     -> remplis par Obsidian, partout
CLES_SCAFFOLD = (
    "{{ORGANISATION}}", "{{CODE}}", "{{REDACTEUR}}", "{{COURRIEL}}",
    "{{PRODUIT}}", "{{DOSSIERS_PROJETS}}", "{{MODE}}", "{{DATE}}",
    "{{DOMAINES_LISTE}}", "{{DOMAINES_TAGS}}", "{{CYCLES_TABLE}}",
    "{{SEUIL_JOURNAL}}",
)


# ── Auto-test ───────────────────────────────────────────────────────────────


def _autotest():
    exemple = Path(__file__).resolve().parent.parent / "template" / "config.example.yaml"
    conf = charger(exemple)

    assert conf["version"] == 1, conf.get("version")
    assert conf["organisation"]["nom"], "organisation.nom vide"
    assert conf["organisation"]["code"].islower(), "organisation.code doit être minuscule"
    assert conf["mode"] in ("solo", "federe"), conf["mode"]
    assert conf["chemins"]["dossiers_projets"], "chemins.dossiers_projets vide"

    codes = codes_domaines(conf)
    assert codes, "aucun domaine"
    assert len(codes) <= conf["collecte"]["plafond_domaines"], "plafond de domaines dépassé"
    assert all(c == c.lower() for c in codes), f"codes non minuscules : {codes}"
    assert len(codes) == len(set(codes)), f"codes de domaine en doublon : {codes}"

    cycles = cycles_par_nom(conf)
    assert "mission" in cycles, list(cycles)
    assert phases_autorisees(conf, "mission"), "enum de phase vide pour mission"
    assert phases_autorisees(conf, "inconnu") == set(), "un cycle inconnu doit rendre un enum vide"

    assert conf["sante"]["max_lignes_entree_journal"] == 10, "le seuil doit être à 10"
    # `mentions_interdites` est une liste, et elle est VIDE dans l'exemple :
    # y mettre de vraies marques les ferait voyager dans chaque config client,
    # c'est-à-dire dans le fichier même censé les interdire. Le remplissage est
    # un geste du maillon 1, pas un défaut du gabarit.
    assert isinstance(conf["marque"]["mentions_interdites"], list)
    assert conf["marque"]["mentions_interdites"] == [], \
        "l'exemple ne doit porter aucune marque réelle"
    assert isinstance(conf["agents"]["skills"], list)

    # Les deux axes ne partagent jamais une valeur (Conventions §8).
    assert not (set(conf.get("vehicules", [])) & set(conf.get("payeurs", []))), \
        "vehicules et payeurs partagent une valeur"

    # Clé `conduite` (phase 5) : absente ⇒ consultant ; valeur inconnue ⇒
    # erreur qui nomme la clé ; les deux valeurs attendues passent.
    assert conduite(conf) == "consultant", "l'exemple ne porte pas la clé, le défaut doit être consultant"
    assert not any("conduite" in e for e in valider_installable(dict(conf, conduite="solo")))
    assert not any("conduite" in e for e in valider_installable(dict(conf, conduite="consultant")))
    assert any(e.startswith("conduite") for e in valider_installable(dict(conf, conduite="duo"))), \
        "une valeur de conduite inconnue doit être refusée"

    # Le refus explicite du mapping à 2 niveaux fait partie du contrat.
    try:
        charger_texte("a:\n  b:\n    c: 1\n")
        raise AssertionError("un mapping à 2 niveaux aurait dû être refusé")
    except ValueError:
        pass

    # Une couleur hexadécimale ne doit pas être tronquée comme un commentaire.
    t = charger_texte('domaines:\n  - { code: ops, nom: "Ops", couleur: "#1c42da" }\n')
    assert t["domaines"][0]["couleur"] == "#1c42da", t["domaines"][0]

    print(f"OK — {exemple.name} : {len(codes)} domaine(s), "
          f"{len(cycles)} cycle(s), mode {conf['mode']}")
    return 0


def main():
    if len(sys.argv) > 1:
        conf = charger(sys.argv[1])
        for cle in sorted(conf):
            print(f"{cle}: {conf[cle]!r}")
        return 0
    return _autotest()


if __name__ == "__main__":
    sys.exit(main())
