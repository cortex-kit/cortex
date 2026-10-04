# 01 : Cadrage

## Pourquoi cette phase existe

La chaîne 2.2.0 constate le désordre sans y toucher. Le vault pointe alors vers « Nouveau document (3).docx », « Scan_0042.pdf » ou un dossier « Divers » de trois cents fichiers : le pointeur est juste, mais ni la personne ni une IA ne s'y retrouvent. Deuxième défaut : en régime copie, chaque vault recopie les procédures de l'entreprise. Dans une société à trois rédacteurs, la même procédure existe alors en quatre versions qui divergent, et aucune IA ne sait laquelle fait foi.

Le commanditaire a tranché le 2026-10-04 : Cortex range l'existant avant de construire, sans rien créer en double ni rien supprimer, et les documents établis pour toute l'entreprise vivent à un seul endroit partagé que toutes les IA consultent.

## Inclus dans cette phase

1. **Étape 3 bis « Rangement »**, facultative, entre le maillon 3 et le maillon 4. Skill `skills/cortex-3b-rangement/`, phrase « rangeons mes dossiers ». Elle propose une liste de changements, la fait valider par lots, l'applique par `range.py`, la vérifie, et sait l'annuler.
2. **Cadrage** (maillon 1) : deux questions nouvelles en langage ordinaire. Pour chaque dossier de travail nommé, d'autres personnes y travaillent-elles ? Puis : l'entreprise a-t-elle un dossier commun où l'on range la charte graphique, les signatures de mail, les procédures ?
3. **Référentiel commun** : adopté tel quel s'il existe (on n'en change l'organisation que sur une liste validée), création proposée à tous les profils s'il manque, index `AGENTS.md` écrit à sa racine sur accord renforcé.
4. **Procédures** : classées personnelle ou d'entreprise par leur emplacement et leur nom, et par une question quand le doute subsiste. Personnelle : note-pointeur dans le vault. D'entreprise : rangée dans le référentiel ; le vault pointe vers le référentiel et son index. Aucune procédure copiée, régime copie compris.
5. **Assistants métier** (maillon 6) : même règle. Un assistant établi pour toute l'entreprise est publié au format `SKILL.md` dans `<référentiel>/assistants/<nom>/`, par `range.py` avec accord renforcé, et l'index le référence.
6. **Base en ligne** (Notion, tableur partagé) : une proposition de structure et de nommage écrite dans `03-rangement.md` ; la personne l'applique elle-même.
7. **Vault et commun** : `CLAUDE.md` du gabarit, skills `parle` et `ingest` du vault, `scaffold.py`, note `50 - Ressources/Référentiel commun.md`, clé `referentiel` de `federation.yaml` reprise par `federe.py`.
8. **Suivi** : `etat.py` à dix entrées, phrase de l'étape 3 bis, garde du maillon 4 sur un rangement appliqué à moitié.
9. **Doctrine** : `references/doctrine.md` gagne le §12 « Ce que la chaîne écrit hors du vault » et un amendement au §5 (une procédure ne se copie jamais).
10. **Recette** : fixtures avec un arbre en désordre et un référentiel partagé, contrôles nouveaux dans `parcours_blanc.py`, verte.

## Exclus de cette phase (non-objectifs)

- **Créer une base** (Notion, Google Drive, OneDrive, tableur, serveur). Décision du 2026-10-04 : le régime 2.2.0 reste tel quel.
- **Écrire dans une base en ligne**, même sur accord. La base reçoit une proposition écrite, rien d'autre.
- **Supprimer** un fichier ou un dossier de la personne, **écraser** une destination existante, **dupliquer** un fichier, même temporairement, **convertir** une procédure en markdown à côté de l'original.
- **Déplacer par script entre deux espaces différents** (deux racines déclarées distinctes, par exemple un OneDrive personnel et une bibliothèque SharePoint) : le système ferait une copie puis une suppression. Ce geste s'écrit `manuel` dans la liste, la personne le fait dans l'interface de l'outil, Cortex vérifie après coup.
- **Ouvrir un fichier présent seulement en ligne** (OneDrive, iCloud, Drive en mode à la demande) : le lire le téléchargerait. Son nouveau nom se déduit du dossier et des métadonnées, ou se demande.
- **Ranger après la remise** (bilan à J+7 et J+30) : hors périmètre.
- **Renuméroter** les maillons, **renommer** une skill ou un artefact existant.
- **Lire hors des cinq endroits** de la doctrine §9. Le référentiel est une racine déclarée, pas une exception.
- **Entrer par `cd`** dans une racine ou un dossier hors de l'atelier (limite du harnais, doctrine §9).
- **Toucher** à `lint_sante.py`, aux skills `miroir` et `agenda`, à `cortex-0-poste`, à `scan.py` : ils appartiennent à d'autres chantiers ou n'ont pas à bouger.
- **Toucher** à `.claude-plugin/` (version, manifestes), à `main`, aux tags : gestes du chef d'orchestre.
- **Corriger** un défaut préexistant rencontré en route : il se note dans le rapport.

## Décisions déjà prises (à ne pas requestionner)

Du commanditaire, le 2026-10-04 :
- D1. Régime de donnée 2.2.0 maintenu ; Cortex ne crée aucune base.
- D2. Cortex range sur accord : la personne valide la liste ligne par ligne (lots de quatre lignes affichées), Cortex déplace et renomme, chaque geste est journalisé et annulable. Jamais de suppression ni de doublon.
- D3. Le rangement se fait après la décision des domaines, avant la construction : les noms suivent le vocabulaire des domaines et les liens du vault naissent sur les chemins définitifs.
- D4. Périmètre : les dossiers de travail, synchronisés compris ; pour une base en ligne, une proposition seulement.
- D5. Dossier partagé avec des collègues : accord renforcé. Une confirmation à part, qui dit que leurs liens et raccourcis casseront et liste les gestes concernés.
- D6. Procédure personnelle : le pointeur vit dans le vault de la personne. Procédure établie par l'entreprise : elle vit dans un dossier partagé de référence, et le vault y pointe pour que toutes les IA s'y réfèrent. En cas de doute, une question.
- D7. Référentiel absent : création proposée à tous les profils, la personne voit avec qui de droit. Référentiel existant (charte graphique, signatures, procédures déjà établies) : adopté.
- D8. Format lisible par toute IA : une procédure par fichier, un nom parlant et daté, un `AGENTS.md` à la racine qui donne pour chaque document son objet, son propriétaire et sa date.
- D9. Assistants métier : même règle que les procédures.
- D10. Lane lancée maintenant ; fusion après l'audit de la convergence phase 1.

Du chef d'orchestre (techniques, même valeur) :
- T1. Skill `cortex-3b-rangement`, entrée « 3b » dans `etat.py`. Étape facultative : `arbitre` (rien à ranger, ou refus) ne bloque pas le maillon 4 ; un rangement appliqué en partie le bloque.
- T2. Un geste dont l'origine et la destination relèvent de deux racines déclarées différentes est `manuel`, jamais exécuté par le script.
- T3. Le contrôle d'identité d'un fichier déplacé se fait par taille et date de modification, jamais par lecture du contenu.
- T4. L'annulation rejoue le journal à l'envers et ne retire que ce que Cortex a créé : un dossier resté vide, un `AGENTS.md` inchangé depuis son écriture.
- T5. `process` sort de `donnees.structurants` ; `copie_structurant.py` refuse le type `process`. Amendé par A6 : une config existante qui le porte reste valide, avec un avertissement.

## Risques et hypothèses

- **Client de synchronisation** : OneDrive ou Drive peut renommer un fichier pendant le passage (conflit, « (1) »). `range.py` vérifie juste avant chaque geste et s'arrête sur tout écart, sans réessayer en silence.
- **Droits** : un employé n'a pas toujours le droit d'écrire dans le dossier partagé. Une `PermissionError` s'écrit au journal comme un échec, le lot s'arrête, la personne est prévenue.
- **Windows** : `os.rename` y refuse une destination existante, POSIX l'écrase. La garde « destination absente » se teste juste avant le geste sur les deux systèmes ; jamais `os.replace`, jamais `shutil.move`.
- **Volume** : au-delà de `sante.max_gestes_rangement` (120) gestes, la liste s'arrête et le reste se déclare écarté (invariant « ce qui est écarté se déclare »).
- **Conflit de fusion** avec la convergence : `cortex_config.py`, `scaffold.py` et le gabarit du vault peuvent bouger côté `main`. Le chef d'orchestre rebase au moment de fusionner.
- **Hypothèse** : un fichier « en ligne seulement » se reconnaît par ses attributs (`st_flags & 0x40000000` sous macOS, `st_file_attributes & 0x400000` ou `0x1000` sous Windows). Si la détection échoue sur un poste, le fichier est traité comme local ; le rapport le dit.

## Modèle cible et effort

Exécutant Opus 5.5, effort `high`, session visible dans un onglet cmux. Auditeur Opus 5.5, effort `high`, session neuve.
