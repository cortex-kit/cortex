# Contrat : Phase H2

Ce contrat fige ce que la lane A implémente et ce que la lane B cite. Une lane qui a besoin d'en changer une ligne s'arrête et le signale au chef d'orchestre. Le contrat v2 (`chantiers/cortex-v2/04-contrat.md`) reste en vigueur pour tout le reste.

## §1 Propriété des fichiers

Lane A : les fichiers de la section « Lane A » de `03-backlog-technique.md`, plus `skills/cortex-4-installation/scripts/rend_notice.py` si un lecteur du champ `present` doit accepter `null` (§2). Lane B : la section « Lane B ». Aucun fichier en commun.

## §2 `poste.py` : détection honnête, voie mail sur accord

**Détection.** Un outil du kit se cherche, dans l'ordre : `shutil.which`, puis le dossier des outils de `uv` (`uv tool dir --bin` quand `uv` répond, sinon `~/.local/bin`, sinon `%USERPROFILE%\.local\bin` sous Windows), puis la sonde propre à l'outil (`uvx` pour markitdown). Un outil trouvé par le binaire est présent, sans appel à `uvx`.

Quand une sonde échoue pour une raison qui n'est pas l'absence (permission refusée, cache inaccessible, délai dépassé, `gh auth status` illisible), l'outil n'est pas déclaré absent :

```json
"markitdown": {"present": null, "version": "", "installe_par_cortex": false,
               "raison": "sonde uvx refusée : cache ~/.cache/uv inaccessible"}
"gh": {"present": true, "version": "2.89.0", "installe_par_cortex": false,
       "connecte": null, "raison": "gh auth status illisible ici"}
```

`--dry-run` n'imprime une ligne d'installation que pour `present: false`. Pour `null`, il imprime `<outil> : à vérifier (<raison>)`.

**Voie mail.** Nouvelle option `--voie {connecteur,softeria,mcp-email,imap,aucune}`. `--ecrire` n'écrit `softeria` ou `mcp-email` que si `--voie` les nomme. Sans `--voie`, la voie calculée par `voie()` s'écrit seulement si elle vaut `connecteur` ou `imap` ; une voie qui installerait quelque chose (`softeria`, `mcp-email`) devient `aucune`. `mail.voie_proposee` garde la voie calculée, pour que le skill sache quoi proposer.

```json
"mail": {"fournisseur": "m365", "boites": 1, "voie": "aucune",
         "voie_proposee": "softeria", "domaine": "alcyon-promotion.fr", "mx": ""}
```

**Options.** `options_proposees` vaut exactement la liste passée par `--options` ; sans `--options`, ou avec `--options aucune`, la liste est vide.

## §3 `etat.py` : l'étape 8 d'un groupe

En `mode: federe` :

- lire `<commun.racine>/federation.yaml` ; pour chaque membre, le vault est le parent de son dossier d'export (`<vault>/_export/<slug>` donne `<vault>`), et la remise se lit dans `<vault>/_cortex/06-passation.md` (clé `remis_le`) ;
- `federation.yaml` absent : étape 8 `arbitre`, raison « groupe non inscrit » ;
- liste `attendus` non vide (rédacteurs annoncés au cadrage, pas encore cadrés, §4) : étape 8 `arbitre`, raison « en attente de <nom>, <nom> » ;
- au moins un membre sans `remis_le` : étape 8 `arbitre`, raison « en attente de <slug>, <slug> » ; `phrase_suivante` ne vaut jamais « relie les cerveaux » dans ce cas, elle vaut la phrase de l'étape suivante de l'atelier courant, ou la phrase de fin si l'atelier est remis ;
- tous les membres remis et `07-federation.md` absent ou `brouillon` : étape 8 `a_faire`, `phrase_suivante` « relie les cerveaux » ;
- `07-federation.md` `valide` : `faite`.

Tout statut de frontmatter `en_cours` se lit comme `brouillon` (état « En cours »).

Le compteur de la notice reste « 8 faites et 1 arbitrée » tant que l'étape 8 est arbitrée ; il passe à 9 sur 9 quand le commun est généré et validé.

## §4 `federe.py --inscrire`

```bash
python3 federe.py --inscrire <slug> --redacteur "<Prénom Nom>" \
                  --export "~/Cortex/<slug>/vault/_export/<slug>" \
                  --config "<commun.racine>/federation.yaml" [--nom "<organisation>"] \
                  [--attendu "<Prénom Nom>" ...]
```

Crée le dossier du commun et `federation.yaml` s'ils manquent (`version: 1`, `nom` depuis `--nom`), ajoute le membre s'il n'y est pas, remplace son chemin d'export s'il y est déjà. Chaque `--attendu` ajoute un nom à la liste `attendus` s'il n'y est pas ; l'inscription d'un membre retire de `attendus` le nom égal à son `--redacteur`. N'écrit aucun autre fichier. Idempotent. Sort en 1 sans rien écrire si le dossier existe, n'est pas vide, et ne porte ni `federation.yaml` ni `.cortex-genere`. Le chemin s'écrit en forme `~`.

```yaml
version: 1
nom: "Alcyon Promotion"
membres:
  - { slug: helene, redacteur: "Hélène Vasseur", export: "~/Cortex/helene/vault/_export/helene" }
attendus: ["Karim Benali"]
```

`federe.py --config` ignore `attendus` et `redacteur` pour générer le commun ; `cortex_config.charger` doit relire ce fichier sans erreur (contrôle de recette existant, C6).

Le cadrage d'un rédacteur en groupe l'appelle une fois l'atelier écrit, avec son `--redacteur`, le chemin d'export que son vault aura (`~/Cortex/<slug>/vault/_export/<slug>`, l'emplacement du vault retenu par la Phase H), et un `--attendu` par autre rédacteur nommé dans la liste du groupe.

## §5 Doctrine : les mots qui ne se disent pas

Nouvelle section de `doctrine.md`, citée par chaque SKILL.md. Ces mots désignent la mécanique de la chaîne ; devant la personne, qu'elle soit client ou consultant, ils se remplacent :

| Ne se dit pas | Se dit |
|---|---|
| consultant, conduite | « vous installez pour quelqu'un d'autre » |
| solo, fédéré, mode | « vous seul » ; « chacun le sien dans l'équipe » |
| profil, dirigeant, employé, société, parcours dirigeant ou employé | ce que la personne a répondu : « vous dirigez », « vous travaillez pour un responsable », « vous êtes plusieurs » |
| régime, pointeur, copie | « votre outil reste la référence, le second cerveau y renvoie » ; « les documents de fond sont recopiés » |
| écart, écart candidat | « un point à éclaircir », « une question sur ce dossier » |
| maillon N, `cortex-N-…`, nom de skill ou de script | la phrase d'entrée de l'étape (« faisons le cadrage ») ou son nom ordinaire (« le cadrage ») |
| valeur d'enum, clé de config (`mail_optin`, `visibilite_defaut`, `arbitre`) | sa traduction en une phrase |

Vaut pour le texte des messages, les questions, les options, les descriptions d'option, les aperçus et les récapitulatifs. Ne vaut pas pour les fichiers de l'atelier, qui restent écrits avec les clés du contrat.

## §6 Doctrine : ce que la chaîne lit

La chaîne lit : l'atelier `_cortex/` du rédacteur courant, son vault, les racines déclarées au cadrage, les fichiers du plugin sous `${CLAUDE_SKILL_DIR}`, et `<commun.racine>` au maillon 8. Pour le second rédacteur d'un groupe, elle lit aussi `00-cadrage.md` et `config.yaml` de l'atelier du premier, pour reprendre les décisions de groupe, et rien d'autre de ses notes.

Elle ne lit jamais : le reste du dossier personnel (`~/Documents`, `~/Desktop`, `~/OneDrive*`, `~/Library`, les dépôts de code, les dossiers de travail du consultant), la mémoire de Claude (`~/.claude/projects/*/memory`), l'historique des sessions, le dépôt source du plugin hors `${CLAUDE_SKILL_DIR}`. Elle n'y cherche ni nom, ni marque, ni indice. Une racine se demande à la personne, elle ne se propose pas depuis un parcours du disque ; `~/Documents` et `~/Desktop` ne sont jamais des racines par défaut.

## §7 Doctrine : ce qui se valide se voit

Une question qui demande de valider, signer ou confirmer un contenu (récapitulatif, bloc, cahier des charges, carte, liste) porte ce contenu dans le texte visible du message qui la précède, ou dans l'aperçu de l'option qui le valide. Jamais « ci-dessus » vers un texte qui n'a pas été écrit. Un raisonnement n'est pas un affichage.

## §8 Doctrine : accord et réponses acquises

- **Accord.** Rien ne s'installe ni ne se branche sans une question qui dit ce que cela pose sur le poste. La voie softeria se propose ainsi : un petit serveur local, l'outil node, l'accès à la boîte sans passer par l'administrateur. Un refus écrit `--voie aucune`.
- **Réponse acquise.** Une réponse donnée ne se repose pas, même pour recommander l'inverse. Une conséquence se signale une fois, dans le récapitulatif, sans question.
- **Marque.** La liste des mentions interdites proposée au consultant ne contient que ses marques ; il la complète lui-même. Aucun nom d'un autre client ne s'y propose, aucun ne se cherche sur le poste. En groupe, la liste est une décision de groupe : fixée au premier cadrage, reprise telle quelle et annoncée aux suivants.
- **Atelier existant.** Au maillon 0, dès qu'un atelier existe sur le poste, la première question demande le nom court ; les ateliers existants y figurent comme options, avec « nouveau nom ».

## §9 Lint : le commun et son empreinte

`lint_sante.empreinte_commun(racine)` : sha256 de tous les fichiers du commun, hors `.cortex-genere`, `.git`, `.obsidian`, et hors les lignes qui portent `genere_le` ou « Généré par ». `federe.py` l'appelle pour écrire `.cortex-genere` ; le lint l'appelle pour comparer. En `mode: federe`, `commun_edite_main` signale : toute note sans la marque « généré » (règle actuelle), et un commun dont l'empreinte diffère de `.cortex-genere`, avec le message « le commun ne correspond plus à son empreinte : une note a été éditée à la main ou le commun est périmé ; relancer la fédération depuis l'atelier ».

## §10 Hooks

```json
"SessionStart": [{"hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start.py\""}]}],
"Stop":         [{"hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/stop.py\""}]}]
```

Les deux scripts résolvent le vault depuis `CLAUDE_PROJECT_DIR` quand elle existe, sinon depuis leur propre emplacement ; jamais depuis le dossier courant.
