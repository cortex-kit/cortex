---
name: fabricant
description: Atelier de fabrication du paquet distribuable Cortex (chantier plug and play). Produit le zip qui se déplie en dossiers frères dans ~/.claude/skills/ chez un installateur novice : les sept maillons cortex-1 à cortex-7, les six skills annexes du manifeste kit.txt, la notice LISEZ-MOI.html avec tableau de bord vierge, et PROVENANCE.md. Porte aussi les deux rendus de l'état d'une installation (etat.py, rend_notice.py, rend_deck.py) depuis le pivot _cortex/etat.json. Réservé au fabricant : ce dossier ne part jamais dans le zip. Vit dans fabricant/ à la racine du dépôt cortex, hors plugin. Déclencher quand le consultant dit "fabrique le paquet Cortex", "fabricant", "génère le zip Cortex", "cortex-paquet", "prépare le kit plug and play", "régénère le tableau de bord Cortex", "produis le deck d'installation Cortex". Ne PAS confondre avec les sept maillons cortex-1 à cortex-7, qui installent un second cerveau : ici on fabrique ce qui les distribue.
---

# cortex-paquet — l'atelier du fabricant

Ce dossier fabrique le produit ; il n'en fait pas partie. Le zip qu'il produit
se déplie en 13 dossiers frères (7 maillons + 6 annexes) plus `LISEZ-MOI.html`
et `PROVENANCE.md`, et s'installe sans terminal, sans git, sans réseau.

Le kit prévu à dix est arbitré à six le 2026-08-23 : docx, pdf, pptx et xlsx
(Anthropic) portent une licence qui interdit la redistribution. La notice
pointe vers leur obtention directe auprès d'Anthropic.

## Fabriquer un paquet

```bash
python3 scripts/fabrique.py --sortie ~/Desktop/cortex.zip
```

`py` vaut `python3` sous Windows. La version du paquet est la date du jour,
sauf `--version` explicite. La fabrication est hors ligne et s'arrête net sur
trois contrôles bloquants :

1. **Provenance.** Chaque entrée de `kit.txt` a sa ligne dans `PROVENANCE.md`
   avec un verdict de redistribution positif. Un zip distribué ne se rappelle
   pas : c'est la seule opération irréversible de la chaîne, le contrôle passe
   AVANT toute copie.
2. **Complétude.** Chaque dossier du zip existe et porte un `SKILL.md` avec
   `name` et `description` en frontmatter.
3. **Profondeur.** Aucun `SKILL.md` au-delà de `<dossier>/SKILL.md` : Claude
   Code ne lit que `skills/<nom>/SKILL.md`, un cran plus bas est invisible.
   Exemption unique et documentée : `cortex-4-installation/template/`, dont
   les SKILL.md sont un chargement de scaffold, invisibles à dessein.

## Ce qui n'existe que dans le zip

Deux familles de copies, jamais versionnées ici (invariant I1, pointeur
jamais copie) :

- les six skills annexes, copiées depuis `~/.claude/skills/` à la fabrication ;
- l'outillage du tableau de bord (`etat.py`, `rend_notice.py`, `notice.md`,
  `VERSION`), déposé dans `cortex-4-installation/scripts/` du zip pour que le
  novice régénère son suivi sans cet atelier. Les scripts sondent leur
  emplacement : même dossier d'abord (zip), dépôt ensuite.

## L'état et ses deux rendus

Le pivot est `_cortex/etat.json`, une projection des frontmatter `statut` et
`controles` des artefacts. Il ne s'édite jamais à la main et se régénère à
l'identique sur un atelier inchangé, à l'horodatage près. Il porte les sept
étapes, dont le trou en 03 avec sa raison : la sortie du maillon 4 est le
vault lui-même, sa preuve le lint à 0.

```bash
python3 scripts/etat.py --atelier <chemin de _cortex/>
python3 scripts/rend_notice.py --pivot <_cortex>/etat.json --sortie <_cortex>/notice.html
python3 scripts/rend_deck.py   --pivot <_cortex>/etat.json --sortie <_cortex>/deck.bento.html
```

Les deux rendus lisent le même pivot et partagent leurs libellés d'état
(importés de `etat.py`) : une divergence entre le tableau de bord et le deck
est impossible par construction. Le deck s'appuie sur la skill `presentation`
(dossier frère) et sur le runtime bento embarqué dans
`modeles/bento-runtime.html` : il se rend hors ligne.

## Les traces d'origine du gabarit

Le maillon 1 en mode solo pré-remplit `marque.mentions_interdites` avec les
traces d'origine du gabarit. Liste ferme, mesurée sur le gabarit le
2026-08-23 : **le gabarit est propre**, aucune occurrence de Cosmos, Evrard,
Marcon, Mister IA, Devprom ni voiesdegypte dans
`cortex-4-installation/template/`. Le pré-remplissage retombe donc sur les
identifiants du fabricant, qui restent les fuites plausibles d'une session
conduite depuis ses machines : `Cosmos`, `Evrard`, `Marcon`, `Mister IA`,
`Devprom`, `voiesdegypte`. Re-mesurer à chaque évolution du gabarit
(`grep -riE` sur le template) avant de figer un paquet.

## Recette

La non-régression du paquet vit dans la recette de la chaîne :

```bash
python3 ../cortex-4-installation/recette/parcours_blanc.py
```

Elle fabrique un zip témoin à chaque exécution et vérifie la profondeur, la
complétude, la provenance, l'idempotence du pivot, le trou en 03, les sept
lignes à faire du tableau vierge, l'absence d'URL distante et la cohérence
deck / tableau de bord. Sortie 0 ou rien.

## Interdits

- Versionner une copie d'une skill annexe dans ce dossier ou ailleurs.
- Éditer `_cortex/etat.json` ou un rendu à la main : régénérer, toujours.
- Distribuer un zip dont un contrôle bloquant a été contourné.
- Ajouter une dépendance hors stdlib ou un accès réseau à la fabrication.
