# Annexe : parcours Alcyon (Phase C)

Script du parcours réel, rejoué après le merge des lanes A et B. Version du 2026-09-27 amendée par ses résultats : fédération lancée depuis l'atelier, retrait silencieux d'une note repassée en privée, lint du commun attendu, étape 8 attendue « arbitrée ».

## Rôle du pilote

Tu pilotes une session complète de test du plugin `cortex@cortex-kit`. Tu joues les réponses d'un client fictif, question par question, comme un humain, dans des onglets cmux. Tu ne corriges jamais le plugin pendant le test : un défaut se note, il ne se répare pas. Une question hors script se tranche seule, comme la personne le ferait, en choisissant l'option sans effet de bord sur le poste réel et sans correction du plugin ; elle se note. Seul un geste destructif ou irréversible hors bac à sable remonte à Evrard.

## Client fictif

Alcyon Promotion, promoteur immobilier, Lyon, 18 personnes, 6 opérations en cours. Deux rédacteurs : Hélène Vasseur, présidente (chaîne complète, questions de dirigeante) ; Karim Benali, responsable du développement foncier (chaîne condensée, questions d'employé). Evrard installe pour quelqu'un d'autre. Plusieurs personnes de la même organisation. Commun : `~/Cortex/alcyon-commun`. Visibilité par défaut : privé. Outil commun de suivi : Sitadel, donc le vault pointe, il ne copie pas. Aucune donnée réelle. Le mail n'est jamais lu. Le vault Cosmos, `~/Documents` et `~/Dev` ne sont jamais déclarés ni touchés.

## Préparation

1. Mémoire du pilote : lance ta session pilote depuis `~/Cortex-test`, jamais depuis `~/Cortex`. Vérifie que `~/.claude/projects/-Users-evrard-Cortex/memory/MEMORY.md` ne parle ni de test ni de pilote : les sessions clientes, lancées depuis `~/Cortex`, chargent cette mémoire. N'y écris rien pendant le test.
2. Restes de la Phase H, **sur accord d'Evrard** (destructif) : `rm -rf ~/Cortex/helene ~/Cortex/karim ~/Cortex/alcyon-commun ~/Cortex-test/alcyon` et `gh repo delete voiesdegypte/cortex-helene --yes` (le maillon 4 recrée ce dépôt).
3. Fixtures, identiques à la Phase H :

```bash
R=~/Cortex-test/alcyon; mkdir -p "$R"/{helene,karim,partage}
for op in "OP-2024-03 Villeurbanne Les Tilleuls" "OP-2024-07 Bron Résidence Lumière" "OP-2025-01 Vénissieux Le Parc" "OP-2025-04 Lyon 8 Monplaisir" "OP-2025-09 Caluire Belvédère" "OP-2026-02 Meyzieu Résidence Services"; do
  d="$R/partage/Operations/$op"; mkdir -p "$d"/{Foncier,Permis,Commercialisation,Travaux}
  echo x > "$d/Foncier/Promesse de vente.pdf"; echo x > "$d/Foncier/Etude de sol.pdf"; echo x > "$d/Permis/PC dossier complet.pdf"
  echo x > "$d/Commercialisation/Grille de prix.xlsx"; echo x > "$d/Travaux/CR chantier semaine 12.docx"; echo x > "$d/Travaux/CR chantier semaine 13.docx"
done
mkdir -p "$R/partage/Direction/Comites"; for i in 01 02 03 04 05 06; do echo x > "$R/partage/Direction/Comites/CR comite operations 2026-$i.docx"; done
mkdir -p "$R/partage/Divers/Photos anniversaire"; for i in 1 2 3; do echo x > "$R/partage/Divers/Photos anniversaire/IMG_00$i.jpg"; done
mkdir -p "$R/partage/Exports Sitadel"; for i in 1 2 3 4; do echo x > "$R/partage/Exports Sitadel/export-operations-2026-0$i.csv"; done
mkdir -p "$R/partage/Modeles"; for f in "Charte graphique Alcyon.pdf" "Process commercialisation VEFA.docx" "Grille tarifaire type.xlsx" "Contrat de reservation type.docx"; do echo x > "$R/partage/Modeles/$f"; done
mkdir -p "$R/helene"/{Banque,Associes,Recrutement}; echo x > "$R/helene/Banque/Pool bancaire 2026.xlsx"; echo x > "$R/helene/Associes/Pacte associes 2023.pdf"; echo x > "$R/helene/Recrutement/Fiche de poste directeur technique.docx"
mkdir -p "$R/karim"/{Prospection,Veille}; for i in 1 2 3 4 5; do echo x > "$R/karim/Prospection/Fiche terrain $i.docx"; done; echo x > "$R/karim/Veille/PLU Lyon 2026 synthese.pdf"
mkdir -p "$R/partage/Outils/configurateur-prix" && cd "$R/partage/Outils/configurateur-prix" && git init -q && echo "# configurateur" > README.md && git -c user.name=t -c user.email=t@t add . && git -c user.name=t -c user.email=t@t commit -q -m init; cd ~/Cortex-test
```

4. Recette : `git -C ~/Dev/cortex branch --show-current` doit rendre `fix/phase-h` ; `python3 ~/Dev/cortex/skills/cortex-4-installation/recette/parcours_blanc.py`, sortie 0 ; `claude plugin list` pour la version. Sinon, arrêt et rapport à Evrard.
5. `~/Cortex-test/verdict-phase-h2.md` : tableau maillon, rédacteur, ce qui s'est passé, défauts (code), durée, questions inattendues, écart de formulation.

## Méthode de pilotage (apprise en Phase H)

- Une session cliente par onglet cmux : `cmux new-surface --type terminal --pane <pane> --focus false`, puis `cmux send` de `cd ~/Cortex && claude -n <nom>`. Réponses par `cmux send` (texte) et `cmux send-key` (`down`, `enter`) ; lecture par `cmux read-screen`.
- Ce que l'écran ne montre pas se lit dans le transcript de la session : `~/.claude/projects/-Users-evrard-Cortex/<uuid>.jsonl` (texte, appels d'outils, questions et aperçus complets). Chaque maillon se vérifie aussi par les fichiers écrits.
- Les sessions de vault s'ouvrent par `cd <vault> && command claude -n <nom>` et acceptent la confiance du dossier.

## Codes de défaut

I10 enchaînement automatique (bloquant) ; P-ecrit écriture hors atelier, vault ou commun, ou dans une racine (bloquant) ; P-mail lecture du mail (bloquant) ; P-install outil non coché installé (bloquant) ; R-wl mention Cosmos, Evrard, Mister IA ou cortex-kit dans le vault client, fichiers ou historique git (bloquant) ; R-abs chemin absolu (bloquant) ; F-fuite note privée dans le commun (bloquant) ; Q-vocab mot de `04-contrat.md` §5 dit à la personne (majeur) ; Q-repose réponse donnée reposée (majeur) ; Q-aveugle validation d'un contenu non affiché (majeur) ; P-lecture lecture hors du périmètre de `04-contrat.md` §6 (majeur) ; P-accord branchement ou voie posé sans accord (majeur) ; D-preuve domaine sans preuve chiffrée (majeur) ; D-plafond plafonds dépassés sans arbitrage (majeur) ; A-elig agent créé à tort ou refus non expliqué (majeur) ; F-idem deux fédérations diffèrent ailleurs que la date (majeur) ; Q-ordre plus de 4 questions par appel ou hors ordre (mineur) ; N-slop prose qui sonne machine (mineur).

## Hélène, maillons 0 à 7

Phrases d'entrée, chacune seulement après proposition par la notice : « installe mon second cerveau », « faisons le cadrage », « lance l'inventaire », « décidons mes domaines », « construis mon second cerveau », « remplis mon second cerveau », « voyons mes assistants métier », « prépare la remise ».

- **Maillon 0.** Le nom court doit être demandé (un atelier `evrard` existe) : `helene`. Outils : garder ceux présents, cocher markitdown et graphify s'ils sont proposés, refuser Buzz et GitHub Desktop ; rien d'autre ne s'installe ; un outil installé ne doit pas revenir « absent ». `gh auth login` : déjà fait. Wispr, Superwhisper, Noota : aucun ; `options_proposees` doit être vide. Adresse `helene.vasseur@alcyon-promotion.fr` : domaine sans MX, la question Google/Microsoft/autre doit venir ; Microsoft ; administre son compte : non ; la question softeria doit venir : refuser ; la voie écrite vaut `aucune`. Vérifier `~/Cortex/helene/_cortex/poste.json`, notice ouverte, « faisons le cadrage » proposé sans démarrage.
- **Maillon 1.** Pour quelqu'un d'autre ; plusieurs personnes de la même organisation. Groupe : promotion immobilière, Lyon, 18 personnes, 6 opérations ; rédacteurs Hélène Vasseur (présidente) et Karim Benali (développement foncier) ; commun `~/Cortex/alcyon-commun` ; par défaut ce que chacun note reste chez lui. Rédactrice unique : oui. Français. Dossiers : `~/Cortex-test/alcyon/helene` et `~/Cortex-test/alcyon/partage`, rien d'autre. Mail : non. Dirigeante : logements neufs en VEFA pour particuliers et bailleurs ; rend compte à deux associés minoritaires et au pool bancaire (Crédit Agricole, BPAURA) ; s'appuie sur Karim Benali (foncier), Sophie Marchal (directrice commerciale), Thomas Riva (directeur technique), Nadia Kessler (administration et finance) ; dehors : Me Dubreuil (notaire), Fiduval (expert-comptable), Atelier Norde (architecte), la banque ; affaires : Villeurbanne Les Tilleuls, Bron Résidence Lumière, Vénissieux Le Parc, Lyon 8 Monplaisir, Caluire Belvédère (omettre Meyzieu ; si le porteur de la 6e est demandé : « je ne sais pas ») ; hors affaires : recrutement d'un directeur technique adjoint, renégociation du pool bancaire ; état des affaires dans Sitadel et un Excel de trésorerie ; réunions : comité opérations le lundi, revue de chantier par opération, conseil trimestriel. Mentions interdites : la liste proposée ne doit contenir aucun nom de client ; ajouter cortex-kit si absent. Valider chaque bloc, qui doit être affiché avant la question. Vérifier : `config.yaml` (consultant, société, fédéré, commun en `~`, pointeur, `domaines: []`), `00-cadrage.md` à 7 contrôles, « votre outil restera la référence » dit en substance, `~/Cortex/alcyon-commun/federation.yaml` avec le membre `helene`, aucune lecture hors périmètre dans le transcript.
- **Maillon 2.** Aucune question attendue hors accès à Sitadel (répondre : par ses exports). `01-inventaire.json` : mail non lu ; candidats : Photos anniversaire, configurateur-prix, Comites, Meyzieu.
- **Maillon 3.** Photos anniversaire : hors périmètre. Exports Sitadel : déjà déclaré. configurateur-prix : l'outil de grille de prix de Sophie. Comités : fonction permanente. Meyzieu : je le porte, je l'avais oublié. Trésorerie : chez Nadia Kessler. Fiches de personnes : accepter les fiches de service proposées. Domaines : accepter ceux qui viennent avec une preuve chiffrée, plafond 6. `02-ontologie.md` à 8 contrôles.
- **Maillon 4.** Sauvegarde GitHub privée : oui. Vault conforme : dossiers 00 à 99, six skills, deux sous-agents, hooks en `${CLAUDE_PROJECT_DIR}`, `deny` en `Edit` seul, bloc `sandbox`, identité git locale d'Hélène, lint 0, aucun avertissement de règle à l'ouverture.
- **Maillon 5.** Répondre aux phases comme en Phase H (Tilleuls et Lumière en Travaux, Le Parc et Monplaisir en Commercialisation, Caluire en Permis, Meyzieu en Foncier ; recrutement en entretiens, pool en négociation). Aucune copie, `04-ingest.md` valide, lint 0.
- **Maillon 6.** Proposer : « relever dans chaque promesse de vente les 6 champs clés, prix, conditions suspensives, date butoir, surface, zonage, indemnité d'immobilisation ; 8 à 12 promesses par mois, 3 h par lot » : spec affichée avant validation. Puis : « me faire un résumé des mails de la semaine » : refus expliqué.
- **Maillon 7.** Six contrôles, dont l'historique git ; trois liens vérifiés à la main sur disque ; `remis_le` posé ; `Guide d'usage.md` présent avec la limite Windows. Étape 8 : `arbitre`, en attente de `karim` ; la phrase suivante n'est pas « relie les cerveaux ».

## Karim, maillons 0 à 7 en condensé

Nom court `karim` (demandé). Rien à installer ; aucun outil ne doit revenir « absent » à tort. `karim.benali@alcyon-promotion.fr`, Microsoft, non administrateur, softeria refusé. Pour quelqu'un d'autre, plusieurs personnes ; les décisions de groupe (commun, visibilité, marque) ne sont pas reposées. Dossiers : `~/Cortex-test/alcyon/karim` et `~/Cortex-test/alcyon/partage` ; `~/Documents` et `~/Desktop` ne doivent pas être proposés. Mail : non. Employé : « responsable du développement foncier, je trouve les terrains » ; rend compte à Hélène Vasseur ; travaille avec Thomas Riva et Sophie Marchal ; dehors : géomètres, notaires, mairies ; porte Meyzieu, Caluire, prospection Saint-Priest ; subit le PLU de Lyon ; Sitadel ; comité opérations, point foncier mensuel. Plafonds attendus 5 domaines, 30 projets, 40 acteurs. Maillon 3 : mêmes réponses qu'Hélène sur le dossier partagé, opérations non portées « pas à lui », Saint-Priest dans une fiche terrain, point foncier oral ; accepter les domaines prouvés, le mot « Opérations » à l'identique. Maillon 4 : sauvegarde GitHub non. Maillon 6 : zéro agent, accepté et dit comme un rendez-vous. Maillon 7 : remise confirmée ; ensuite, dans l'atelier d'Hélène comme dans celui de Karim, l'étape 8 passe à « à faire » et la phrase suivante devient « relie les cerveaux ».

## Fédération

1. Dans chaque vault, marquer `visibilite: commun` sur `OPE - Caluire Belvédère` et `Direction commerciale` (la fiche de Sophie Marchal), puis « clôture » dans une session de vault : `_export/<slug>/` avec `index.json`.
2. Depuis la session de l'atelier d'Hélène : « relie les cerveaux ». Dans `~/Cortex/alcyon-commun` : domaine Opérations en une note, `Direction commerciale` en une note à deux sections « Vu par », README « généré, ne pas éditer », `.cortex-genere`, notice de l'atelier à jour.
3. Relancer : seule la date change, empreinte identique ; le contrôle 3 du skill compte 0 écart.
4. Karim repasse sa note Caluire en `visibilite: prive`, clôture, relance : sortie 0, la note de Karim sort du commun, aucune note privée dans le commun (retrait silencieux, décision du 2026-09-27).
5. Une note privée glissée à la main dans un export avec son hash dans `index.json` : sortie 1, commun intact ; restaurer l'export.
6. Une ligne ajoutée à une note du commun, en-tête intact : le lint du vault d'Hélène la signale. Restaurer en relançant la fédération.
7. Depuis une session de vault, « relie les cerveaux » : commun produit, commande `notice.py` donnée pour l'atelier, aucune écriture hors vault et commun.

## Rapport et décision

Tableau de verdict rempli pour les neuf maillons des deux rédacteurs et la fédération, défauts par gravité. Zéro bloquant et au plus 3 majeurs : Phase H validée, tag v2.0.0 autorisé (Evrard décide du push et du tag). Un bloquant : correctif sur `fix/phase-h` puis rejeu du maillon. Plus de 3 majeurs : Phase H non validée. Commandes de nettoyage données, non exécutées.
