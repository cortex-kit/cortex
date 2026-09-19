# Consignes du chef d orchestre, lane E (2026-09-19)

Session en mode bypass : aucune commande hors de ton worktree, aucun `git push`, aucun `git merge`, aucun `rm` hors des fichiers que tu possedes. La sonde Cowork web du 2026-09-19 a montre que Cowork sur claude.ai tourne dans un conteneur distant sans acces au disque : le vault vit sur le poste, seule l app Cowork bureau peut le servir. Orchestrateur : session Claude `cortex-orchestre`, qui lit ton rapport final dans cet onglet.

- La personne veut que la skill `cloture` du vault porte la substance complete du rituel, sans aucune marque ni infrastructure tierce : detection des notes touchees, journal du POURQUOI en tete de `## Journal`, retrait des cases soldees (la trace vit dans git), frontmatter `dernier_journal` et `blocages_actifs`, idempotence, moins de trente secondes, export `_export/<slug>/` (`04-contrat.md` §6), regime copie respecte, commit git local puis `git push` seulement si un remote existe. Aucune ecriture vers une base externe.
- `scaffold.py` : `gh repo create <slug> --private --source . --push` propose apres `git init`, jamais impose ; la personne peut refuser et rester locale.
- Lis `AgriciDaniel/claude-obsidian` (ledger de provenance par hash) avant d ecrire `structurant_perime`, sans en copier une ligne.
