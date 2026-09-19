# Consignes du chef d orchestre, lane F (2026-09-19)

Session en mode bypass : aucune commande hors de ton worktree, aucun `git push`, aucun `git merge`, aucun `rm` hors des fichiers que tu possedes. La sonde Cowork web du 2026-09-19 a montre que Cowork sur claude.ai tourne dans un conteneur distant sans acces au disque : le vault vit sur le poste, seule l app Cowork bureau peut le servir. Orchestrateur : session Claude `cortex-orchestre`, qui lit ton rapport final dans cet onglet.

- Les exports fictifs pour tes tests : fabrique-les toi-meme dans un dossier temporaire au format `04-contrat.md` §6 (la lane E ecrit le vrai export en parallele, tu ne l attends pas).
- Le vault commun genere doit passer `lint_sante.py` v1 tel qu il existe sur main.
