"""Embarquement des polices dans le document.

Pourquoi ce fichier existe
  Une `fontFamily` qui nomme une police que le document ne transporte pas
  retombe en silence sur la suivante de la pile. Il n'y a aucun avertissement,
  et — c'est le piège — **ça aura l'air correct chez toi**, puisque Inter et
  Montserrat sont installées sur ta machine. Le client, lui, verra du Helvetica.
  Sur un livrable à ton nom c'est le genre de détail qui décrédibilise sans
  qu'on sache dire pourquoi.

  Les polices appartiennent au DOCUMENT, pas à l'application. Un deck bento
  n'hérite d'aucune police : ce qu'il ne transporte pas, il ne l'a pas.

Usage

    from chartes import charte
    from fonts import embarquer
    C = charte("mia")
    assets, fonts = embarquer(C["embarquer"])   # ["Inter:400,600,700"]
    doc = document(..., assets=assets, fonts=fonts)

Les woff2 sont mis en cache sous ~/.cache/cosmos-presentation-fonts/ : hors git
(pas de binaire dans le repo des skills) et téléchargés une seule fois.

Vérification finale : dans le navigateur, `window.bento.validate()` signale
`font-not-embedded`. C'est le seul contrôle qui voie le problème, précisément
parce qu'il est invisible en local.
"""

import base64
import hashlib
import pathlib
import re
import urllib.parse
import urllib.request

CACHE = pathlib.Path.home() / ".cache" / "cosmos-presentation-fonts"
# Google sert du woff2 à un navigateur récent, du ttf à un ancien. Les deux nous
# servent : le woff2 s'embarque dans le document HTML (léger), le ttf se mesure
# avec PIL pour le rendu PPTX (PIL ne lit pas le woff2). Même source, deux
# formats — c'est ce qui garantit que les deux rendus mesurent la même police.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
UA_TTF = "Mozilla/4.0"
# Le sous-ensemble latin de base : U+0000-00FF couvre é è à ç ù ô — tout le
# français. Inutile d'embarquer le cyrillique ou le vietnamien.
LATIN = "U+0000-00FF"


def _get(url, binaire=False, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binaire else r.read().decode("utf-8")


def _cache(url, ext="woff2", ua=UA):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:16] + "." + ext)
    if not f.exists():
        f.write_bytes(_get(url, binaire=True, ua=ua))
    return f


def _css(famille, poids, ua=UA):
    q = urllib.parse.quote(famille)
    axes = ";".join(str(p) for p in sorted(poids))
    return _get(f"https://fonts.googleapis.com/css2?family={q}:wght@{axes}"
                "&display=swap", ua=ua)


def _blocs_latins(css, poids):
    """Rend {graisse: url} pour le seul sous-ensemble latin de base.

    Le woff2 est servi découpé par alphabet, un bloc par sous-ensemble, et il
    faut alors trier. Le ttf, lui, arrive entier et sans `unicode-range` : il n'y
    a rien à trier et filtrer sur le latin rejetterait tout.
    """
    decoupe = "unicode-range" in css
    trouve = {}
    for bloc in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        if decoupe and LATIN not in bloc:
            continue
        m_url = re.search(r"src:\s*url\((https://[^)]+)\)", bloc)
        m_wt = re.search(r"font-weight:\s*(\d+)", bloc)
        if not m_url or not m_wt:
            continue
        wt = int(m_wt.group(1))
        if wt in poids and wt not in trouve:
            trouve[wt] = m_url.group(1)
    return trouve


def fichier_mesurable(famille, graisse=400):
    """Chemin d'un .ttf local pour cette famille et cette graisse.

    PIL sait mesurer un ttf, pas un woff2 — d'où ce second téléchargement. Le
    rendu PPTX mesure ainsi exactement la police que le rendu HTML embarque,
    sans quoi les deux formats se découperaient différemment.

    Retombe sur la graisse la plus proche si l'exacte n'existe pas : une police
    absente ferait échouer la mesure, alors qu'une graisse voisine donne une
    largeur à un ou deux pour cent près — assez pour découper des lignes.
    """
    css = _css(famille, [graisse], ua=UA_TTF)
    urls = _blocs_latins(css, [graisse])
    if not urls:                        # graisse refusée : reprendre ce qui vient
        css = _css(famille, [400, 700], ua=UA_TTF)
        urls = _blocs_latins(css, [400, 700])
    if not urls:
        raise RuntimeError(
            f"{famille} : aucun fichier mesurable en latin. Famille absente de "
            "Google Fonts ? Une pile système n'a pas besoin d'être mesurée — "
            "utiliser une famille locale à la place."
        )
    wt = min(urls, key=lambda w: abs(w - graisse))
    return _cache(urls[wt], ext="ttf", ua=UA_TTF)


def embarquer(specs):
    """specs : ["Inter:400,700", "Montserrat:600"] → (assets, fonts).

    Rend deux blocs à poser tels quels dans le document : `assets` associe une
    clé à un data URI woff2, `fonts` déclare quelle famille et quelle graisse
    chaque clé porte. Une pile système (spec vide) ne rapporte rien : il n'y a
    rien à embarquer et rien qui puisse casser.
    """
    assets, fonts = {}, []
    for spec in specs or []:
        famille, _, brut = spec.partition(":")
        famille = famille.strip()
        poids = [int(p) for p in (brut or "400").replace(" ", "").split(",")]
        # Un bloc @font-face par graisse ET par sous-ensemble ; on ne garde que
        # le latin de base, sinon on embarque cinq alphabets pour rien.
        vus = _blocs_latins(_css(famille, poids), poids)
        for wt, url in sorted(vus.items()):
            cle = f"{famille.lower().replace(' ', '-')}-{wt}"
            b64 = base64.b64encode(_cache(url).read_bytes()).decode("ascii")
            assets[cle] = f"data:font/woff2;base64,{b64}"
            fonts.append({"family": famille, "asset": cle, "weight": wt})

        manquants = sorted(set(poids) - set(vus))
        if manquants:
            raise RuntimeError(
                f"{famille} : graisses introuvables en latin {manquants}. "
                "Vérifier que la famille existe sur Google Fonts avec ces "
                "graisses, ou retirer la graisse de la charte."
            )
    return assets, fonts


if __name__ == "__main__":                      # contrôle : ça tourne vraiment
    a, f = embarquer(["Inter:400,700"])
    assert set(f_["weight"] for f_ in f) == {400, 700}, f
    assert all(v.startswith("data:font/woff2;base64,") for v in a.values())
    assert all(len(v) > 5000 for v in a.values()), "woff2 suspectement petit"
    print(f"OK — {len(a)} fichiers embarqués, "
          f"{sum(len(v) for v in a.values()) // 1024} Ko de data URI")
