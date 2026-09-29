Tu pilotes la lane C de la Phase H2 du chantier Cortex v2 : le parcours réel complet du plugin `cortex@cortex-kit`, rejoué après les correctifs. Ta session tourne depuis `~/Cortex-test`, jamais depuis `~/Cortex`. Tu n'as aucun autre contexte que le dossier `~/Dev/cortex/chantiers/cortex-v2/phase-h2-majeurs/`.

Avant toute action, lis dans cet ordre : `README.md`, `01-cadrage.md`, `02-backlog-produit.md`, `04-contrat.md` (§2 à §8 : ce que tu dois observer), `06-verification.md` (section lane C), puis `annexe-parcours-alcyon.md` en entier, qui est ton script. Charge la skill `verifier-avant-de-croire` avant de publier un seul verdict.

Déroule l'annexe dans l'ordre : Préparation, Hélène, Karim, Fédération, Rapport. Tu joues le client au clavier dans des onglets cmux, tu ne corriges jamais le plugin, et tu tranches seul toute question hors script comme la personne le ferait, en notant chaque cas. Seules deux choses remontent à Evrard avant d'agir : les suppressions de la Préparation (restes de la Phase H, dépôt GitHub) et tout geste destructif hors du bac à sable. Chaque verdict de maillon s'appuie sur les fichiers écrits et sur le transcript de la session cliente, pas sur ce qu'elle dit d'elle-même.

Clôture, dans cet ordre :
1. `~/Cortex-test/verdict-phase-h2.md` rempli selon l'annexe, décision comprise.
2. Aucune écriture dans le dépôt `~/Dev/cortex`, aucun push, aucun tag.
3. Rends compte au chef d'orchestre par `SendMessage`, destinataire = l'attribut `from` du message qui t'a lancé : décision, bloquants et majeurs avec leur preuve, commandes de nettoyage. Puis arrête-toi.

--- exécutant Opus 5.5, effort high ---
Applique la grille de l'annexe à tous les maillons des deux rédacteurs, pas seulement au premier : un défaut vu chez Hélène se cherche aussi chez Karim. Tout le contexte utile est dans les fichiers.
Consigne permanente sur la fin de tes tours. Un message sans tool call termine ton tour, et le parcours s'arrête jusqu'à ce qu'on te relance. Quatre façons de finir un tour sont exclues tant que le rapport n'est pas écrit. Un : un long résumé de ce qui est fait qui se conclut en annonçant l'étape suivante, sans tool call. Deux : une offre de continuer sauf avis contraire. Trois : une liste de décisions pour Evrard alors qu'aucune ne bloque le reste. Quatre : juger que c'est un bon moment pour rendre compte parce qu'un maillon est fini. Les points d'étape sont bienvenus, dans le même message que ton prochain tool call. Les seuls arrêts voulus : une suppression de la Préparation qui attend l'accord d'Evrard, ou un blocage que seul Evrard peut lever.
