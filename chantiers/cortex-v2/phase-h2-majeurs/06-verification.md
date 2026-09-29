# Vérification : Phase H2

Méthode : skill `verifier-avant-de-croire`, lue avant de poser les contrôles. Chaque contre-épreuve se joue sur le code de `fix/phase-h` d'avant la lane (`git stash` ou `git show fix/phase-h:<fichier> > <fichier>`, puis restauration), et son rouge se consigne dans le rapport.

## Lane A : critères cochables

- [ ] Recette complète : `python3 skills/cortex-4-installation/recette/parcours_blanc.py`, sortie 0, nombre de contrôles supérieur à 117.
- [ ] Auto-tests : `poste.py`, `etat.py`, `lint_sante.py`, `federe.py`, `scaffold.py`, `scan.py` avec `--autotest`, sortie 0 chacun.
- [ ] A1 détection. Dans un dossier temporaire, `PATH` réduit à `/usr/bin:/bin` et un faux `graphify` exécutable dans `$HOME_TEMP/.local/bin` (avec `HOME` pointé dessus) : `poste.py --dry-run` ne liste pas graphify. **Témoin** : sans le faux binaire, graphify est listé. **Contre-épreuve** : ancien `poste.py`, le faux binaire présent, graphify listé.
- [ ] A1 non mesurable. Une sonde `uvx` qui échoue en permission (par exemple `UV_CACHE_DIR` pointé sur un dossier en lecture seule, markitdown absent du PATH) : `--dry-run` imprime « à vérifier », jamais une commande d'installation. **Contre-épreuve** : ancien code, même montage, commande d'installation imprimée.
- [ ] A2 voie. `poste.py --ecrire --fournisseur m365` sans `--voie` sur un atelier temporaire : `mail.voie == "aucune"` et `voie_proposee == "softeria"`. Avec `--voie softeria` : `voie == "softeria"`. **Contre-épreuve** : ancien code, `softeria` écrit sans `--voie`.
- [ ] A3 options. Sans `--options` : `options_proposees == []`. **Contre-épreuve** : ancien code, trois options.
- [ ] A4 lint du commun. Commun généré par `federe.py` sur deux exports écrits par `export.py`, une ligne ajoutée à une note sans toucher l'en-tête : le lint d'un vault membre signale `commun_edite_main`. **Témoin positif** : même commun non touché, rien signalé. **Contre-épreuve** : ancien `lint_sante.py`, édition non signalée.
- [ ] A4 une seule empreinte. `grep -n "def empreinte" skills/cortex-8-federation/scripts/federe.py` ne rend plus de définition locale, ou rend un simple renvoi à `lint_sante` ; deux générations successives gardent la même `.cortex-genere` (contrôle C6 existant, vert).
- [ ] A5 inscription. `federe.py --inscrire` deux fois sur le même slug : un seul membre ; sur un dossier étranger non vide : sortie 1, dossier inchangé (liste des fichiers et empreinte avant et après).
- [ ] A6 attendus. Un atelier remis, `federation.yaml` à un membre et un `attendus` : étape 8 `arbitre`, raison qui nomme l'attendu, `phrase_suivante` différente de « relie les cerveaux ». C'est le cas d'Hélène remise avant le cadrage de Karim.
- [ ] A6 étape 8. Deux ateliers temporaires en groupe, `federation.yaml` à deux membres, un seul `remis_le` : étape 8 `arbitre`, raison qui nomme le membre en attente, `phrase_suivante` différente de « relie les cerveaux ». Les deux remis : `phrase_suivante == "relie les cerveaux"`. **Contre-épreuve** : ancien `etat.py`, étape 8 `a_faire` et « relie les cerveaux » dès le premier remis.
- [ ] A6 statut. Un `07-federation.md` en `statut: en_cours` : état « En cours », pas « Illisible ».
- [ ] A7 hooks. `settings.json` généré contient `${CLAUDE_PROJECT_DIR}` dans les deux commandes. `cd /tmp && CLAUDE_PROJECT_DIR=<vault> python3 <vault>/.claude/hooks/stop.py --autotest` sort en 0. **Contre-épreuve** : ancien hook lancé par sa commande relative depuis `/tmp`, fichier introuvable.
- [ ] A8 médias. Trois `.jpg` dans `Divers/Photos` hors projets : un candidat `dossier_sans_domaine`. **Témoin** : un dossier de trois `.docx` hors projets garde le comportement actuel (rien sous le seuil).
- [ ] Périmètre. `git diff --stat fix/phase-h..lane/h2a` ne touche que les fichiers de la lane A (`03-backlog-technique.md`). `export.py`, le bloc `sandbox` et `poser_identite()` sont intacts : `git diff fix/phase-h..lane/h2a -- skills/cortex-4-installation/template/vault/.claude/skills/cloture/export.py` est vide, et le diff de `scaffold.py` ne porte que sur `HOOKS`.

## Contrôles silent-failure (lane A)

- [ ] Agent `silent-failure-hunter` sur `poste.py`, `etat.py`, `lint_sante.py`, `federe.py`, `scan.py`, `session_start.py`, `stop.py` : aucun `except` qui avale une erreur sans trace, aucune sonde dont l'échec se lit « absent », aucun repli qui agrège deux causes en un message.

## Lane B : critères cochables

- [ ] Recette complète sur `lane/h2b`, sortie 0 : tailles de SKILL.md sous 300 lignes, section Notice et I10, zéro marque, zéro chemin absolu.
- [ ] Doctrine. `grep -n "^## " skills/cortex-1-cadrage/references/doctrine.md` montre les sections des mots, de la lecture, de la validation visible et de l'accord. **Témoin** : même grep sur `fix/phase-h`, absentes.
- [ ] Renvois. Chaque `skills/cortex-[0-8]-*/SKILL.md` cite la doctrine pour ces règles : `grep -L "<motif retenu par la lane>" skills/cortex-[0-8]-*/SKILL.md` ne rend rien. **Témoin** : sur `fix/phase-h`, le même `grep -L` rend les neuf fichiers.
- [ ] Skills du vault. Chaque `template/vault/.claude/skills/*/SKILL.md` porte la ligne des mots et de la validation visible (même méthode `grep -L`, même témoin).
- [ ] Maillon 0. Le texte exige le nom court dès qu'un atelier existe, la question softeria avec ce qu'elle pose, `--voie` et `--options` selon les réponses ; il n'invite jamais à modifier un script ou la configuration du shell.
- [ ] Maillon 1. Aucune racine proposée depuis un parcours du disque ; `~/Documents` et `~/Desktop` jamais par défaut ; liste de marque sans nom de client ; décision de groupe reprise chez le second rédacteur ; `federe.py --inscrire` en fin de cadrage en groupe, avec la forme de chemin de `04-contrat.md` §4.
- [ ] Phrases fautives du parcours, chacune absente ou réécrite dans le skill qui l'a produite : « Mode consultant », « conduite consultant », « parcours dirigeant », « trancher quatre écarts », « Accepter l'écart », « Passe au maillon 1 (cortex-1-cadrage) », « Le bloc identité ci-dessus est-il juste ? » sans bloc. Pour chacune, le rapport cite le passage du skill qui l'encadre désormais.
- [ ] Maillon 8. Lancement depuis l'atelier écrit ; depuis un vault, commande notice donnée ; contrôle 3 qui ignore la ligne « Généré par » (le rapport montre la commande et sa sortie sur un commun généré deux fois : 0 écart).
- [ ] Windows. `grep -n -i "windows" README.md outils/OUTILS.md skills/cortex-7-passation/SKILL.md` montre la limite et WSL2.
- [ ] Périmètre. `git diff --stat fix/phase-h..lane/h2b` ne touche que des `.md` de la lane B ; aucun `.py`.
- [ ] Prose. Pas de tiret cadratin ajouté : `git diff fix/phase-h..lane/h2b | grep "^+" | grep -c "—"` vaut 0.

## Lane C : parcours

Critères, règle de décision et codes de défaut : `annexe-parcours-alcyon.md`.

## Comment on saura que ces contrôles ne mentent pas

- [ ] Chaque contrôle de recette ajouté est joué dans les deux sens : vert sur le nouveau code, rouge sur l'ancien, les deux consignés dans le rapport.
- [ ] Chaque critère qui attend zéro (grep vides, 0 écart au contrôle 3, aucun fichier hors périmètre) porte son témoin, la même sonde rendant non-zéro sur `fix/phase-h` ou sur un cas monté.
- [ ] Chaque montage de test (faux binaire, cache en lecture seule, atelier temporaire) est vérifié posé avant la lecture du résultat.
- [ ] Toute mesure reprise d'un rapport est remesurée par l'auditeur, sur la bonne branche.

## Definition of Done

Lanes A et B : tous les items cochés, audit à froid « phase acceptée », merge dans `fix/phase-h` avec recette verte. Phase H2 : le parcours C sort sans bloquant et avec au plus 3 majeurs.
