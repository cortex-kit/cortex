Tu audites, à froid, la lane « rangement » de Cortex 2.3.0. Tu n'as pas exécuté ce travail et tu ne fais aucune hypothèse de bienveillance envers l'exécutant. Tu ne corriges rien : ton livrable est le verdict, écrit dans `chantiers/cortex-2.3-rangement/audit.md` du worktree `~/Dev/cortex--rangement`.

1. Lis `README.md`, puis `01-cadrage.md` à `06-verification.md` du dossier `chantiers/cortex-2.3-rangement/`, puis `rapport.md`.
2. Examine ce qui a été réellement produit, en lançant toi-même :
   - `git -C ~/Dev/cortex--rangement status` : rien d'inattendu en attente.
   - `git -C ~/Dev/cortex--rangement log --oneline b8df8bb..HEAD` et `git diff --stat b8df8bb..HEAD` : le changement correspond au périmètre de `01-cadrage.md`, rien hors de `03-backlog-technique.md`, rien dans la liste « Ne pas toucher ».
   - Chaque commande de `06-verification.md`, ré-exécutée par toi ; ne lis pas une sortie citée par le rapport.
   - L'agent `silent-failure-hunter` (Agent tool, subagent_type « silent-failure-hunter ») sur `range.py`, `etat.py`, `cortex_config.py`, `scaffold.py`, `federe.py`, `copie_structurant.py` ; confronte ses findings à l'item « Contrôles silent-failure ».
3. Reprends `06-verification.md` item par item et statue PASS ou FAIL sur chacun, avec la preuve : sortie de commande, extrait de diff, comportement observé.
3bis. Audite les contrôles eux-mêmes. Charge la skill `verifier-avant-de-croire` et applique-la à `06-verification.md` :
   - tout critère qui attend un zéro : fais rendre non-zéro à la même sonde sur un témoin ;
   - toute garde G1 à G9 : casse ce qu'elle surveille dans une copie jetable et exige le rouge, en prouvant que ta perturbation était posée ;
   - toute assertion négative : vérifie qu'une positive porte sur le même objet ;
   - tout chiffre du rapport (comptes de contrôles, gestes) : remesure-le, et vérifie sur quoi ta commande a répondu (le worktree, pas `~/Dev/cortex`).
   Signale nommément tout critère que tu n'as pas pu calibrer.
4. Vérifie les non-objectifs de `01-cadrage.md` sur tout le diff : suppression, copie, écriture dans une base, déplacement entre deux espaces, lecture d'un fichier en ligne seulement, `cd` vers une racine, fichiers hors possession. Signale toute dérive, même si le résultat fonctionne.
5. Vérifie que la conduite écrite dans `cortex-3b-rangement/SKILL.md` tient les décisions D2, D5, D6, D7 et les mots interdits de la doctrine §8.
6. Rends un verdict : lane acceptée, ou lane à reprendre avec la liste précise de ce qui bloque, classé bloquant, majeur, mineur.

--- auditeur = Opus 5.5 (effort : high) ---
Remonte TOUT ce que tu trouves, y compris les points incertains ou de faible sévérité : à cette étape ton objectif est la couverture, pas le tri. Joins à chaque finding un niveau de confiance et une sévérité estimée. Ne termine pas ton tour sur un point d'étape : le verdict final, écrit dans `audit.md` et rendu au chef d'orchestre (recopie l'attribut `from` du message reçu), est la seule fin de tour attendue.
