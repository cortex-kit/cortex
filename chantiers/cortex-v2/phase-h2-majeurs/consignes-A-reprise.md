# Reprise de la lane A après audit à froid (2026-10-02)

Worktree `~/Dev/cortex--h2a`, branche `lane/h2a`. Tu possèdes les fichiers de la lane A (`03-backlog-technique.md`), aucun `.md` de skill. Lis `audit-A.md` en entier, puis applique :

1. M1 (amendement §9 acté par le chef) : `lint_sante.py`, `empreinte_commun` ignore les fichiers cachés (nom commençant par `.`) et `Thumbs.db`, `desktop.ini` ; même règle dans `federe.py` au calcul du sceau, pour que les deux empreintes restent égales. Témoin : un `.DS_Store` planté dans un commun généré ne change ni l'empreinte ni le verdict du lint.
2. Mineur : `etat.py` ne plante jamais sur un `federation.yaml` mal formé ou illisible ; l'étape 8 passe « illisible » avec la raison, la notice se régénère. Témoin dans l'auto-test.
3. Mineur : `poste.py --ecrire` sans `--voie` ni `--options` conserve les valeurs déjà écrites dans `poste.json` au lieu de les remettre à « aucune » ou vide. Témoin : deux `--ecrire` successifs, le second sans `--voie`, gardent la voie.
4. Les autres mineurs de l'audit : traités si chacun tient en moins de dix lignes, sinon laissés et listés.
5. Rejoue la recette (0 attendu, compte des contrôles noté), les auto-tests des neuf scripts, `ast.parse` sous `/usr/bin/python3`. Colle les sorties dans `rapport-A.md` (section « Reprise »). Commits sur `lane/h2a` préfixés « Lane H2A : », aucun push, aucun merge. Rends compte par SendMessage à la session nommée cortex-v2-installable-plugin, puis arrête-toi.
