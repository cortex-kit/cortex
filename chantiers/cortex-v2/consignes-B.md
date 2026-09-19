# Consignes du chef d orchestre, lane B (2026-09-19)

Session en mode bypass : aucune commande hors de ton worktree, aucun `git push`, aucun `git merge`, aucun `rm` hors des fichiers que tu possedes. La sonde Cowork web du 2026-09-19 a montre que Cowork sur claude.ai tourne dans un conteneur distant sans acces au disque : le vault vit sur le poste, seule l app Cowork bureau peut le servir. Orchestrateur : session Claude `cortex-orchestre`, qui lit ton rapport final dans cet onglet.

- Kit d annexes tranche par la personne : **stop-slop seul**. humanizer, prompt-architect, presentation, compte-rendu et email-auditor ont ete retirees de `skills/` sur main (commit 2e0ee29) : ne les reintroduis pas. `fabricant/kit.txt` contient deja `stop-slop`.
- `PROVENANCE.md` : ne garder que stop-slop (MIT, notice jointe) et les lignes des annexes Anthropic hors kit ; les outils installes par le maillon 0 (Obsidian, uv, markitdown, git, gh, GitHub Desktop, Buzz, Softeria, mcp-email) ne sont pas redistribues, leur licence et leur URL vont dans `outils/OUTILS.md`.
- `stop-slop/SKILL.md` porte une occurrence de prenom a retirer : c est dans ton perimetre (annexe du kit), remplace par un terme generique.
- `fabrique.py` : le zip compte les maillons presents par glob `cortex-*` plus les annexes de kit.txt ; ne code aucun nombre en dur.
- La notice et OUTILS.md disent, en une ligne, que Cowork web ne convient pas (vault sur le poste) et que l app Cowork bureau reste a recetter.
