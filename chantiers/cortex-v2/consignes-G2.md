# Consignes du chef d'orchestre, relance de la lane G après merge (2026-09-19)

Tu reprends la lane G sur `main` de `~/Dev/cortex` (les lanes B à G sont mergées ; ton worktree `~/Dev/cortex--G` est retiré). Tu possèdes `skills/cortex-4-installation/recette/` et `chantiers/cortex-v2/06-verification.md`, rien d'autre. Lis `04-contrat.md` en entier, y compris les deux blocs d'amendements en fin de fichier : ils tranchent les sept échecs constatés à la simulation de merge (98/105).

1. C1 : en `mode: solo`, l'étape 8 est `arbitre` ; le contrôle « 9/9 » devient « 8 faites et 1 arbitrée » (ou utilise un atelier `mode: federe` pour mesurer 9/9, au choix, dis lequel). La page vierge et `LISEZ-MOI.html` comptent 8 pastilles « À faire ».
2. C3 : n'exige la forme `~` que si le dossier des fixtures est sous le dossier personnel ; sinon accepte l'absolu et dis-le dans la sortie.
3. C4 : les hooks sont des scripts `.claude/hooks/session_start.py` et `stop.py` ; vérifie leur présence, que `session_start.py` contient `lint_sante.py` et `--bref`, que `stop.py` contient « clôture », et lance chacun avec `--autotest` (sortie 0).
4. Rejoue la recette complète jusqu'à 0 ; la seule tolérance admise est un contrôle marqué `[--]` non mesurable avec sa raison. Mets à jour `06-verification.md` : tableau C1 à C10 avec sorties, et les contrôles manuels M1 à M3 avec une ligne vide à remplir.
5. Ajoute aux contrôles manuels M-4 : les règles `allow` et `additionalDirectories` d'un vault sont ignorées par `claude -p` tant que le dossier n'a pas été ouvert une fois en interactif (« workspace has not been trusted ») ; seules les règles `deny` s'appliquent. La preuve vivante des permissions se fait donc en session interactive, sortie collée.
6. `python3 -m py_compile` sur tous les scripts du dépôt ; `grep` white-label et chemins absolus sur `skills/ notice/ outils/ README.md` : zéro ligne.

Commits sur `main` préfixés « Lane G : », aucun push (le chef d'orchestre pousse). Rapport final : sorties d'acceptation collées, hash des commits, points en attente.
