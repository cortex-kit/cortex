# Reprise de la lane B après audit à froid (2026-10-02)

Worktree `~/Dev/cortex--h2b`, branche `lane/h2b`. Tu possèdes les mêmes fichiers `.md` que la lane B (`03-backlog-technique.md`), aucun `.py`. Lis `audit-B.md` en entier, puis applique :

1. D1 : `doctrine.md:27`, le white-label se définit par les marques et outils du consultant, sans « clients déjà servis » (décision 6 de la Phase H2).
2. D2 : `template/vault/.claude/skills/cloture/SKILL.md` (récap l. 162-163 et l. 120) : aucun « Lint », aucun « solo », aucun nom de skill ; les avertissements en phrases ordinaires (« 2 notes sans dossier », « sauvegarde en ligne absente »).
3. D3 : `cortex-1-cadrage/SKILL.md:61-74` et `:95`, `cortex-2-inventaire/SKILL.md:32` : la traduction en langage ordinaire vaut dans les deux modes, consultant compris.
4. D10 : `cortex-0-poste/SKILL.md:34` : le maillon 0 ne liste jamais les dossiers de `~/Cortex/` (sur le poste d'un consultant, ce sont d'autres clients) ; il demande le nom court, et ne reconnaît que l'atelier dont le nom est donné.
5. D4 à D9, D12, D13 : traités si chacun tient en une ligne (noms d'outils et clés hors des messages de clôture ; contrôle 1 du maillon 7 reformulé sur ce qu'il attrape ; lecture de `federation.yaml` au cadrage dite explicitement dans la doctrine §9 comme seule lecture du commun hors maillon 8 ; `--inscrire` après la validation par bloc ; reprendre le nom d'un attendu tel qu'il figure dans la liste ; commentaire du contrôle 3 du maillon 8 ; exemple sans `~/Documents` ; connexion `gh` proposée sans question ajoutée).
6. Rejoue la recette et les greps de `06-verification.md` (lane B), colle les sorties dans `rapport-B.md` (section « Reprise »), commits sur `lane/h2b` préfixés « Lane H2B : », aucun push, aucun merge. Rends compte par SendMessage à la session nommée cortex-v2-installable-plugin, puis arrête-toi.
