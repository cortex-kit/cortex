"""Chartes de marque — source unique de vérité pour tout deck de présentation.

Ces valeurs ne sont pas inventées : elles sont relevées sur les templates réels
et déjà en production ailleurs. Si une charte change, elle change ICI, et tous
les decks suivants en héritent. Ne recopie jamais un hexadécimal dans un
fichier de deck : importe la charte.

Provenance
  mia      claudia-bis-4-deck/SKILL.md §« La charte, relevée sur le template
           Mister IA » — relevée au pixel sur le template de référence.
  devprom  formation-devprom/references/pptx-design-spec.md §2 et §3.
  vde      contrat-vde/SKILL.md §palette + scripts/generate_contract.py.
  neutre   Aucune marque. Pour un deck perso ou un support qui ne doit engager
           aucune entité — voir le sanity check anti-fuite de /publier.

L'échelle typographique
  bis-4 travaille en points sur un canevas de 20 pouces ; bento travaille en
  pixels sur 1280×720. Le facteur est 1280 / (20 × 72) = 0,889 px/pt. L'échelle
  ci-dessous est cette conversion, arrondie à des valeurs rondes.

  Le plancher de 16 px n'est pas cosmétique : bis-4 l'a fixé après avoir constaté
  que du corps trop petit est illisible au fond d'une salle, et qu'il est la
  cause première des slides à moitié vides — on écrit plus parce que ça rentre.
  Descendre sous 16 px pour faire tenir du texte, c'est traiter le symptôme :
  c'est le contenu qu'il faut couper.
"""

# Échelle commune à toutes les marques (px sur un canevas 1280×720).
ECHELLE = {
    "geant": 176,     # un chiffre qui EST la slide — relevé à 195 pt sur le
                      # template Mister IA, où il porte 20 occurrences
    "hero": 112,      # titre de couverture, un seul par deck
    "titre": 50,      # titre de slide
    "sous_titre": 34, # accroche, chiffre mis en avant
    "corps": 21,      # texte courant
    "secondaire": 17, # légende de carte, colonne dense
    "note": 14,       # mention de bas de slide, folio
}
PLANCHER = 16

# Grille — voir references/format-bento.md. Marges latérales 96 px, bande utile
# 1088 px. Ces valeurs évitent de recalculer une gouttière à chaque deck.
COLS = {
    2: {"w": 528, "x": [96, 656]},
    3: {"w": 340, "x": [96, 470, 844]},
    4: {"w": 254, "x": [96, 374, 652, 930]},
}
BANDE = {"x": 96, "w": 1088, "droite": 1184}

_CHARTES = {
    "mia": {
        "nom": "Mister IA",
        "fond": "#FFFFFF",
        "fond_sombre": "#1E2A5E",   # couvertures et intercalaires
        "encre": "#1E293B",
        "attenue": "#64748B",
        "accent": "#1C42DA",
        "accent_doux": "#8EA0C4",
        "panneau": "#DCE5F5",       # fond de carte, encart
        "filet": "#E2E8F0",
        "titre_couleur": "#1E2A5E",
        "titre_variante": "#1B2E77",   # intercalaires de partie, grands titres
        "annotation": "#475569",       # commentaire : entre le corps et la légende
        "chapitre": "#3D8A6A",         # vert de section, pour un chapitre distinct
        "chapitre_doux": "#8DD3B5",
        # Gradation du plus soutenu au plus pâle. Pour une série comparée
        # (plusieurs barres, plusieurs jauges), on descend cette échelle plutôt
        # que d'inventer des teintes : elle vient du template, elle s'accorde.
        "gradation": ["#1C42DA", "#6B7FC7", "#8EA0C4", "#DDE3EE", "#E5EAF2"],
        "police": "'Inter', -apple-system, system-ui, sans-serif",
        "police_citation": "Georgia, 'Times New Roman', serif",
        "embarquer": ["Inter:400,600,700"],
        "esprit": "Institutionnel, bleu marine et bleu franc, fond clair. "
                  "Sobriété de cabinet : l'accent se mérite.",
    },
    "devprom": {
        "nom": "Devprom",
        "fond": "#F9F9F9",
        "fond_sombre": "#1A2B3C",
        "encre": "#333333",
        "attenue": "#707070",
        "accent": "#A68942",
        "accent_doux": "#C9B37A",
        "panneau": "#FFFFFF",
        "filet": "#E4E4E4",
        "titre_couleur": "#1A2B3C",
        "police": "'Montserrat', -apple-system, system-ui, sans-serif",
        "police_corps": "'Inter', -apple-system, system-ui, sans-serif",
        "police_citation": "Georgia, 'Times New Roman', serif",
        "embarquer": ["Montserrat:600,700", "Inter:400,600"],
        "esprit": "Bleu Prusse et Or Bronze. Titres en Montserrat, corps en "
                  "Inter — la bascule de police porte la hiérarchie.",
    },
    "vde": {
        "nom": "Voies d'Égypte",
        "fond": "#FAF6EE",
        "fond_sombre": "#0E2A47",
        "encre": "#1C1C1C",
        "attenue": "#7A7A7A",
        "accent": "#C9A961",
        "accent_doux": "#E8D9B0",
        "panneau": "#FFFFFF",
        "filet": "#E5DDCB",
        "titre_couleur": "#0E2A47",
        "police": "'Montserrat', -apple-system, system-ui, sans-serif",
        "police_titre": "'Cormorant Garamond', Georgia, serif",
        # Cormorant compose ses chiffres en style ancien : le 2, le 8 et le 9
        # descendent sous la ligne de base. Superbe dans un paragraphe, bancal
        # pour un chiffre-clé de 76 px qu'on veut voir lu d'un coup. Les chiffres
        # mis en avant repassent donc au sans-serif.
        "police_chiffres": "'Montserrat', -apple-system, system-ui, sans-serif",
        "police_citation": "'Cormorant Garamond', Georgia, serif",
        "embarquer": ["Montserrat:400,600", "Cormorant Garamond:600,700"],
        "esprit": "Bleu nuit, or et sable. Titres en Cormorant : le serif "
                  "porte le haut de gamme, le sable réchauffe le fond.",
    },
    "neutre": {
        "nom": "",
        "fond": "#FBFAF8",
        "fond_sombre": "#20262E",
        "encre": "#1C1C1C",
        "attenue": "#6B7280",
        "accent": "#2F4858",
        "accent_doux": "#94A7B3",
        "panneau": "#FFFFFF",
        "filet": "#E5E5E3",
        "titre_couleur": "#1C1C1C",
        "police": "-apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif",
        "police_citation": "Georgia, 'Times New Roman', serif",
        "embarquer": [],  # stack système : rien à embarquer, rien à casser
        "esprit": "Aucune marque, aucun logo. Pour un support qui ne doit "
                  "engager aucune entité.",
    },
}

MARQUES = tuple(_CHARTES)


def charte(marque):
    """Rend la charte d'une marque. `marque` ∈ mia | devprom | vde | neutre.

    Les clés absentes retombent sur des valeurs sûres : `police_titre` vaut
    `police` si la marque n'en distingue pas une, idem `police_corps`. Ça évite
    un KeyError sur une marque qui n'a qu'une famille.

    `police_chiffres` sert aux nombres mis en avant. Elle suit `police_titre`
    par défaut — sauf pour une famille à chiffres de style ancien, qui les fait
    danser sous la ligne de base et rend un chiffre-clé bancal à grande taille.
    """
    if marque not in _CHARTES:
        raise ValueError(
            f"Marque inconnue : {marque!r}. Attendu l'une de {MARQUES}. "
            "Une marque nouvelle s'ajoute dans chartes.py, jamais en dur "
            "dans un fichier de deck."
        )
    c = dict(_CHARTES[marque])
    c.setdefault("police_titre", c["police"])
    c.setdefault("police_corps", c["police"])
    c.setdefault("police_chiffres", c["police_titre"])
    # Rôles fins relevés sur le template Mister IA. Les autres marques n'ont pas
    # de template audité : plutôt que d'inventer des teintes pour elles, on
    # dérive de ce qu'elles ont déjà. Une valeur dérivée s'accorde toujours ;
    # une valeur inventée finit par jurer.
    c.setdefault("titre_variante", c["titre_couleur"])
    c.setdefault("annotation", c["attenue"])
    c.setdefault("chapitre", c["accent"])
    c.setdefault("chapitre_doux", c["accent_doux"])
    c.setdefault("gradation",
                 [c["accent"], c["accent_doux"], c["panneau"], c["filet"]])
    c["marque"] = marque
    c["echelle"] = dict(ECHELLE)
    return c


def famille(pile_css):
    """Première famille nommée d'une pile CSS, sans ses guillemets.

    Une charte écrit ses polices en pile CSS (`"'Inter', system-ui, sans-serif"`)
    parce que c'est ce dont le rendu web a besoin. PowerPoint, lui, veut un nom
    de famille seul. Une pile purement système ne nomme rien d'embarquable et
    rend None : il n'y a alors ni police à charger ni police à déclarer.
    """
    for part in (pile_css or "").split(","):
        p = part.strip().strip("'\"")
        if p and not p.startswith("-") and p not in (
                "system-ui", "sans-serif", "serif", "monospace", "ui-sans-serif"):
            return p
    return None


def theme(c):
    """Le bloc `theme` du document bento, dérivé d'une charte.

    bento exige `size` et `theme` (dont `fontFamily`) : sans eux l'app ne
    démarre pas du tout.
    """
    return {
        "background": c["fond"],
        "color": c["encre"],
        "accent": c["accent"],
        "fontFamily": c["police_corps"],
    }
