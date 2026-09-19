# Consignes du chef d'orchestre, reprise de la lane F après merge (2026-09-19)

Tu reprends la lane F sur `main` de `~/Dev/cortex` (lanes B à G mergées). Tu possèdes `skills/cortex-8-federation/` et rien d'autre. Lis `04-contrat.md` en entier, amendements compris, puis `chantiers/cortex-v2/audit-F.md` (audit à froid, 14 points).

1. Défaut 2 (bloquant après merge) : `config_commun` dans `federe.py` écrit `mode: federe`, `commun.racine: ""`, et un bloc `donnees` (`regime: pointeur`, `structurants: []`). Vérifie avec `cortex_config.valider_installable` de `main` (celui de la lane C) que le commun généré rend une liste vide, puis `lint_sante.py --vault <commun>` à 0 et `--autotest` à 0.
2. Défaut 1 : l'import de `lint_sante` reste ; le contrat le rend public. Rien à changer, dis-le dans ton rapport.
3. Mineurs 3 à 10 de l'audit, tous dans ton fichier : corrige-les si chacun tient en moins de dix lignes (README au libellé du contrat, `empreinte()` qui ne saute que la clé `genere_le:` en début de ligne, unités homogènes dans la ligne de sortie, lecture et refus d'une `version` inconnue de `federation.yaml` et d'`index.json`, note privée hors index signalée, cohérence `index.json.slug`). Pour la rétrogradation des titres à la fusion d'acteurs, garde `## Journal` au niveau 2. Pour `fixtures()` qui importe la recette, laisse tel quel.
4. Rejoue tes quatre critères d'acceptation sur l'arbre fusionné et colle les sorties.

Commits sur `main` préfixés « Lane F : », aucun push. Rapport final : sorties, hash des commits, points en attente.
