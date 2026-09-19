#!/usr/bin/env python3
"""retour.py — ce que le deck projeté porte, et que la source n'a pas.

Le maillon qui manquait à la chaîne. Un deck part en PPTX vers Canva, quelqu'un
l'y retouche, et plus rien ne compare jamais ce qui revient. Sur LAESSA, 41 pages
sur 48 avaient divergé de la source sans que personne le voie : 192 segments de
texte, dont 28 réécritures qui touchaient le propos. Une relance des scripts les
aurait tous effacés.

Ce script constate. **Il n'écrit rien et ne bloque rien** : un garde-fou qui
immobilise une production un jour de rush finit contourné, et c'est un rush qui
produit les retouches. Ce qu'on lui demande, c'est que personne ne puisse dire
qu'il ne savait pas.

    python3 retour.py <projete.pptx> <source.pptx>

Le PPTX projeté s'obtient de deux façons :

  - depuis une session Claude Code, par le MCP Canva : `get-export-formats`
    puis `export-design` en `pptx`, et on télécharge l'URL rendue ;
  - à la main, depuis Canva : Partager, Télécharger, PowerPoint.

Le script ne parle pas à Canva lui-même : l'export passe par un jeton de session
qu'un script isolé n'a pas. La frontière est là, et elle est nette. L'agent
exporte, le script mesure.

## Ce qu'il mesure, et comment

Les pages ne se comparent pas par leur rang : un deck retouché gagne et perd des
pages, et tout comparer rang à rang produirait 48 divergences là où il y en a 41.
Chaque page projetée est donc appariée à la page source dont le texte lui
ressemble le plus, une seule fois, au-dessus d'un seuil. Ce qui ne s'apparie pas
est signalé à part : ce sont les pages ajoutées dans l'outil de présentation, et
les pages de la source qui n'y sont pas arrivées.

Les segments modifiés sont classés en quatre familles, parce que leur gravité
n'est pas la même. Une conversion de nombre est une décision de style. Une
réécriture change ce que le client lit. Le total seul ne dit rien ; la
répartition dit où regarder.

## Ce qu'il ne voit pas

Le texte, et le texte seul. Une image déplacée, une couleur changée, une police
substituée, un bloc masqué derrière un autre : rien de tout cela n'apparaît ici.
Pour ça, il y a le rendu réel — `soffice --convert-to pdf`, puis on regarde.
"""

import collections
import difflib
import re
import sys
import unicodedata
from pathlib import Path

try:
    from pptx import Presentation
except ImportError:
    sys.exit("python-pptx manquant : pip install python-pptx")

# Au-dessus, deux pages sont la même page retouchée. En dessous, ce sont deux
# pages différentes. Relevé sur le deck LAESSA : les pages de tête refaites à la
# main (photos, logos) tombent à 0,17-0,53, les pages simplement retouchées
# remontent à 0,79 et plus. Le creux entre les deux populations est net.
SEUIL = 0.45

# Les nombres écrits en toutes lettres qu'une relecture convertit en chiffres.
# C'est la retouche la plus fréquente et la moins grave : elle ne change pas ce
# qui est dit. La distinguer évite de noyer les réécritures qui, elles, comptent.
NOMBRES = {
    "un", "une", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
    "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept",
    "dix-huit", "dix-neuf", "vingt", "trente", "quarante", "cinquante", "soixante",
    "cent", "cents", "mille", "million", "millions",
}


def normaliser(texte):
    """Le texte tel qu'il se lit, débarrassé de ce qui n'est pas du sens.

    Un export d'outil de présentation ne rend ni les mêmes apostrophes, ni les
    mêmes espaces que python-pptx. Sans cette passe, chaque apostrophe compterait
    pour une divergence et le rapport serait illisible.
    """
    t = unicodedata.normalize("NFKC", texte).replace("’", "'").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def pages(chemin):
    """Une chaîne de texte par page, dans l'ordre du document."""
    return [
        normaliser(" ".join(f.text_frame.text for f in p.shapes if f.has_text_frame))
        for p in Presentation(str(chemin)).slides
    ]


def apparier(projete, source):
    """Chaque page projetée vers la page source qui lui ressemble le plus.

    Une page source ne sert qu'une fois : sans ça, deux pages projetées proches
    se rattacheraient à la même source et l'une des deux passerait pour un ajout.
    """
    libres = list(range(len(source)))
    paires, orphelines = [], []
    for i, texte in enumerate(projete):
        meilleur = (0.0, None)
        for j in libres:
            r = difflib.SequenceMatcher(None, texte, source[j]).ratio()
            if r > meilleur[0]:
                meilleur = (r, j)
        score, j = meilleur
        if texte and score >= SEUIL:
            paires.append((i, j, score))
            libres.remove(j)
        else:
            orphelines.append(i)
    return paires, orphelines, libres


def classer(avant, apres):
    """Les segments qui séparent deux pages, par famille."""
    a, b = avant.split(), apres.split()
    familles = collections.Counter()
    exemples = collections.defaultdict(list)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "equal":
            continue
        av, ap = " ".join(a[i1:i2]), " ".join(b[j1:j2])
        if av.lower().strip(",.:;·") in NOMBRES and re.fullmatch(r"[\d\s]+", ap.strip()):
            famille = "nombres en lettres vers chiffres"
        elif tag == "delete":
            famille = "texte supprimé"
        elif tag == "insert":
            famille = "texte ajouté"
        else:
            famille = "texte réécrit"
        familles[famille] += 1
        exemples[famille].append((av, ap))
    return familles, exemples


def rapport(chemin_projete, chemin_source, detail=False):
    projete, source = pages(chemin_projete), pages(chemin_source)
    paires, ajoutees, absentes = apparier(projete, source)

    print(f"  projeté   {Path(chemin_projete).name:<28} {len(projete)} pages")
    print(f"  source    {Path(chemin_source).name:<28} {len(source)} pages")
    print()

    familles = collections.Counter()
    exemples = collections.defaultdict(list)
    retouchees = []
    for i, j, score in paires:
        if score >= 0.995:
            continue
        retouchees.append((i + 1, j + 1))
        f, e = classer(source[j], projete[i])
        familles.update(f)
        for cle, items in e.items():
            exemples[cle].extend((j + 1, av, ap) for av, ap in items)

    identiques = len(paires) - len(retouchees)
    total = sum(familles.values())

    if not total and not ajoutees and not absentes:
        print(f"  ✅ les {identiques} pages appariées sont identiques au caractère près")
        return 0

    print(f"  {identiques} page(s) identique(s) au caractère près")
    if retouchees:
        print(f"  {len(retouchees)} page(s) retouchée(s) · {total} segments divergent")
        for cle, n in familles.most_common():
            print(f"       {n:4d}  {cle}")
    print()

    # Les réécritures et les suppressions changent ce que le client lit. On les
    # montre toujours : c'est le seul endroit du rapport où un total ne suffit pas.
    for cle in ("texte réécrit", "texte supprimé", "texte ajouté"):
        items = exemples.get(cle)
        if not items:
            continue
        montres = items if detail else items[:6]
        print(f"  {cle} :")
        for page, av, ap in montres:
            print(f"       p{page:02d}  « {av[:64]} »")
            print(f"             vers  « {ap[:64] or '(rien)'} »")
        if len(items) > len(montres):
            print(f"       … et {len(items) - len(montres)} autre(s), --detail pour tout voir")
        print()

    if ajoutees:
        print(f"  {len(ajoutees)} page(s) ajoutée(s) dans le projeté, sans équivalent source :")
        for i in ajoutees:
            apercu = projete[i][:70] or "(aucun texte, sans doute une image posée à la main)"
            print(f"       p{i + 1:02d}  {apercu}")
        print()

    if absentes:
        print(f"  {len(absentes)} page(s) de la source absente(s) du projeté :")
        for j in absentes:
            print(f"       p{j + 1:02d}  {source[j][:70]}")
        print()

    print("  Ces écarts seraient perdus à la prochaine relance suivie d'un réimport.")
    print("  Les remonter à la source, ou décider de les écraser en le sachant.")
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__.split("\n\n")[3].strip())
    for chemin in args:
        if not Path(chemin).exists():
            sys.exit(f"introuvable : {chemin}")
    return rapport(args[0], args[1], detail="--detail" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
