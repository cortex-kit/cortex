# passation — les dossiers de chantier

Un dossier par chantier interne, un sous-dossier par phase. Cycle et format : [[Runbook - Chantiers (phase packs)]].

Le principe : un pack transmet **tout** le contexte nécessaire à l'exécution d'une phase, de sorte que la session qui l'a rédigé puisse mourir sans perte. C'est le test à appliquer avant de le considérer terminé — si sa seule lecture ne suffit pas à exécuter, il est incomplet.

Ces dossiers sont **opératoires et périssables**. Ils ne sont pas de la doctrine et le lint les ignore : ne pas y chercher une source de vérité durable, elle est dans `90 - Meta/` à la racine.
