# Consignes du chef d orchestre, lane G (2026-09-19)

Session en mode bypass : aucune commande hors de ton worktree, aucun `git push`, aucun `git merge`, aucun `rm` hors des fichiers que tu possedes. La sonde Cowork web du 2026-09-19 a montre que Cowork sur claude.ai tourne dans un conteneur distant sans acces au disque : le vault vit sur le poste, seule l app Cowork bureau peut le servir. Orchestrateur : session Claude `cortex-orchestre`, qui lit ton rapport final dans cet onglet.

- Le kit d annexes est reduit a `stop-slop` : le zip compte les maillons presents (7 aujourd hui, 9 apres merge) plus une annexe. Aucune assertion a 13 ne survit ; compte par glob.
- Travaille en preparatoire : la recette etendue est rouge jusqu au merge des lanes B a F, c est voulu. Chaque nouveau controle cite la section du contrat qu il verifie.
- Le grep white-label couvre `skills/` en entier, annexes comprises, plus `notice/`, `outils/`, `README.md`.
- Les controles manuels (install plugin vivante, Cowork bureau, Windows) vont dans `06-verification.md` avec une ligne vide a remplir par le chef d orchestre.
