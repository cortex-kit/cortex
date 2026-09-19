# Audit à froid d'une lane

Tu audites la lane `<LANE>` du chantier Cortex v2 dans une session neuve, sans mémoire de son exécution. Le worktree est `~/Dev/cortex--<LANE>`, branche `lane/<LANE>`. Tu ne modifies rien : tu lis, tu rejoues, tu rends un verdict.

→ Fable 5 : effort `high`. Remonte tout, y compris l'incertain et le mineur ; couverture, pas filtrage. Chaque verdict s'appuie sur une sortie de commande ou un extrait de diff, jamais sur une impression. Ne transcris pas de raisonnement : des preuves.

## Lire d'abord

`chantiers/cortex-v2/README.md`, `01-cadrage.md`, `02-arbo.md`, `03-backlog.md` (ligne `<LANE>`), `04-contrat.md` en entier, `05-prompt-execution-<LANE>.md`, puis le rapport final de la lane tel que le chef d'orchestre te le transmet.

## Rejouer

1. `git -C ~/Dev/cortex--<LANE> diff main --stat` : la liste des fichiers touchés. Chaque fichier hors de la colonne « Possède » de `04-contrat.md` §1 est un défaut bloquant.
2. Chaque commande d'acceptation de `03-backlog.md` ligne `<LANE>`, telle quelle, dans le worktree. Colle la sortie.
3. `grep -rwiE "<liste de 01-cadrage.md §Marques interdites>" skills/ chantiers/ notice/ outils/ README.md` : zéro ligne attendue hors les quatre annexes internes connues.
4. `grep -rnE "/Users/|/home/|[A-Z]:\\\\" skills/ notice/ outils/ README.md` : zéro ligne attendue.
5. Chaque script Python de la lane : `python3 <script> --help` sort 0 ; l'auto-test annoncé tourne et sort 0 ; `grep -nE "^import|^from" <script>` ne montre que la stdlib.
6. Chaque SKILL.md de la lane : frontmatter `name` et `description` présents, moins de 300 lignes, section « Notice » conforme à `04-contrat.md` §10 pour un maillon.
7. Le contrat : chaque clé, chemin ou schéma que la lane produit ou consomme correspond à `04-contrat.md` (nom exact, forme `~`, enums). Un écart est un défaut bloquant.
8. Les invariants de `01-cadrage.md` : cherche activement ce qui les casserait (un sous-agent avec `Write`, un maillon qui lance le suivant, une note qui recopie plus de dix lignes, un plugin Obsidian requis).

## Rendre

Un tableau : critère, commande, sortie (extrait), verdict `passe` / `échoue` / `non mesurable`, confiance. Puis la liste des défauts par sévérité (bloquant, à corriger avant merge, mineur), chacun avec le fichier et la ligne. Puis une phrase : mergeable ou non. Ne propose pas de correctif dans le code ; nomme le défaut, la lane corrige.
