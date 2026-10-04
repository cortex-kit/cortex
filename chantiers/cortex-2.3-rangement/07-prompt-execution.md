Tu exécutes la lane « rangement » de Cortex 2.3.0, un chantier déjà cadré. Ton seul contexte est le dossier `chantiers/cortex-2.3-rangement/` de ce dépôt. Tu travailles dans le worktree `~/Dev/cortex--rangement`, branche `lane/rangement`, et nulle part ailleurs.

Avant toute action :
1. Lis `chantiers/cortex-2.3-rangement/README.md`.
2. Lis `01-cadrage.md`, `02-backlog-produit.md`, `03-backlog-technique.md`, `04-contrat.md`, `05-execution.md`, `06-verification.md`, dans cet ordre.
3. Lis les sections de la doctrine et du contrat v2 que `05-execution.md` cite au préalable.

Ensuite, exécute `05-execution.md` dans l'ordre. Respecte strictement les non-objectifs de `01-cadrage.md` et la liste « Ne pas toucher » de `03-backlog-technique.md`. Les décisions D1 à D10 et T1 à T5 sont actées : ne les rediscute pas. Si une information nécessaire manque, arrête-toi et signale le trou au chef d'orchestre plutôt que de deviner.

À la fin, vérifie ton travail contre `06-verification.md` par un sous-agent à contexte frais, corrige, puis clôture :
1. Coche `05-execution.md` avec les hashes réels.
2. Écris `rapport.md` comme le décrit `05-execution.md`.
3. Mets à jour la ligne **Statut** du `README.md` du pack.
4. Rends compte au chef d'orchestre et arrête-toi : pas de fusion, pas de push, pas de tag, pas de `.claude-plugin/`. Le vault et la fiche de suivi sont tenus par le chef d'orchestre ; ne lance pas de clôture de vault.

Le chef d'orchestre est la session qui t'a envoyé ce prompt. Pour lui répondre, recopie l'attribut `from` du message reçu comme destinataire de ton `SendMessage`. Si l'envoi échoue, écris ton compte rendu en clair dans le terminal : il le lit à l'écran.

--- exécutant = Opus 5.5 (effort : high) ---
Applique les non-objectifs de 01-cadrage à TOUT le périmètre, pas seulement au premier cas rencontré : ne généralise ni ne restreins une consigne d'un item à l'autre. Tout le contexte utile est déjà dans 01-06 ; traite la phase en entier, sans multiplier les allers-retours.
Le temps compte : parallélise ce qui est indépendant (par exemple fixtures et doctrine pendant que `range.py` se teste).
Consigne permanente sur la fin de tes tours. Un message sans tool call termine ton tour, et le travail s'arrête jusqu'à ce qu'on te relance. Quatre façons de finir un tour sont exclues tant que la phase n'est pas terminée. Un : un long résumé de ce qui est fait qui se conclut en annonçant l'étape suivante, sans tool call. Deux : une offre de continuer sauf avis contraire, qui attend une réponse qui ne viendra pas. Trois : une liste de décisions pour l'humain alors qu'aucune, de ton propre aveu, ne bloque le reste. Quatre : juger que c'est un bon moment pour rendre compte parce que le tour a été long ou qu'un jalon est franchi. Les points d'étape et tes recommandations sur les décisions ouvertes sont bienvenus, mais mets-les dans le même message que ton prochain tool call et continue sur tout ce qui ne dépend pas de la réponse. Si tu te surprends à inviter l'humain à te réorienter ou à proposer d'attendre, supprime cette phrase et fais la chose suivante. Les seuls arrêts voulus : rien ne peut avancer sans le chef d'orchestre, ou ce qui te bloque est délibérément protégé. Cela ne lève pas la confirmation requise pour une action risquée ou destructrice.
