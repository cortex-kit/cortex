# Consignes du chef d orchestre, lane D (2026-09-19)

Session en mode bypass : aucune commande hors de ton worktree, aucun `git push`, aucun `git merge`, aucun `rm` hors des fichiers que tu possedes. La sonde Cowork web du 2026-09-19 a montre que Cowork sur claude.ai tourne dans un conteneur distant sans acces au disque : le vault vit sur le poste, seule l app Cowork bureau peut le servir. Orchestrateur : session Claude `cortex-orchestre`, qui lit ton rapport final dans cet onglet.

- `scan.py` ne couvre que le disque ; le bloc `mail` est rempli par l agent selon `04-contrat.md` §7. Ecris dans SKILL.md la procedure exacte par voie (connecteur Gmail, connecteur M365, Softeria, mcp-email), y compris le plafond et la declaration de depassement.
- Fixtures disponibles : `python3 skills/cortex-4-installation/recette/fixtures.py` genere `recette/fixtures/{employe,dirigeant,societe}/` (ignore par git).
