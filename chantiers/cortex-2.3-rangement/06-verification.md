# 06 : Vérification

Toutes les commandes se lancent depuis `~/Dev/cortex--rangement`.

## Critères d'acceptation (cochables)

Script et gardes
- [ ] `python3 skills/cortex-3b-rangement/scripts/range.py --autotest; echo $?` rend `0`.
- [ ] L'auto-test prouve chaque garde G1 à G9 dans les deux sens : le cas qui doit passer passe, le cas qui doit lever rend le code 3 et laisse l'arbre identique (liste des chemins, tailles, dates comparées avant et après).
- [ ] I-R1 : nombre de fichiers sous l'arbre de test identique avant `--appliquer`, après, et après `--annuler`.
- [ ] I-R2 : appliquer puis annuler rend un arbre identique (chemins, tailles, `mtime`).
- [ ] Déterminisme : deux `--proposer` sur la même fixture rendent un `03-rangement.json` identique hors `genere_le` (`diff` des deux fichiers sans cette ligne).
- [ ] Grep : aucun `os.remove`, `os.unlink`, `shutil.rmtree`, `shutil.copy`, `shutil.move`, `os.replace`, `os.chdir` dans `range.py` hors des deux exceptions d'annulation du contrat §5, chacune commentée.

```bash
grep -nE "os\.(remove|unlink|replace|chdir)|shutil\.(rmtree|copy|move)" skills/cortex-3b-rangement/scripts/range.py
```

Config, état, maillons
- [ ] `cortex_config.py` accepte `process` dans `donnees.structurants` avec l'avertissement « type 'process' retiré en 2.3.0, ignoré » et l'exclut de la liste effective (A6) ; une config 2.2 qui le porte passe le lint à 0. Il refuse un `referentiel.chemin` hors racine, une `partagees` qui n'est pas sous-ensemble de `racines` ; il accepte `config.example.yaml`.
- [ ] `copie_structurant.py --type process` sort en erreur avec un message qui nomme la règle ; `--type contrat` sur la même source réussit.
- [ ] `etat.py --autotest` rend `0` et couvre les quatre lignes du tableau du contrat §8 ; `etat.json` d'un atelier de recette compte dix étapes.
- [ ] Le maillon 4 refuse quand 3b vaut `en_cours` : contrôle de recette sur un atelier dont le journal porte une ligne `fait` et une ligne acceptée non faite.
- [ ] `scaffold.py` : aucun `{{` dans le vault généré, avec et sans référentiel ; le chemin du référentiel apparaît en forme `~` dans `CLAUDE.md` du vault.
- [ ] `federe.py` : avec `referentiel` dans `federation.yaml`, le commun porte `50 - Ressources/Référentiel commun.md` et une ligne dans `Centre.md` ; sans la clé, ni l'un ni l'autre ; deux générations ne diffèrent que sur `genere_le`.
- [ ] La section « Notice » de `cortex-3b-rangement/SKILL.md` est identique octet pour octet à celle de `cortex-3-ontologie/SKILL.md`.
- [ ] Doctrine : `grep -n "^## 12" skills/cortex-1-cadrage/references/doctrine.md` rend une ligne ; le §5 porte un amendement daté 2026-10-04.

Recette
- [ ] `python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?` rend `0`, avec plus de contrôles qu'avant la lane (compte avant et après dans `rapport.md`).
- [ ] Les contrôles white-label et « zéro chemin absolu » de la recette couvrent `skills/cortex-3b-rangement/`.
- [ ] Aucun `cd ` vers un dossier hors de l'atelier dans les SKILL.md touchés : `grep -nE '(^|[ ;&])cd [^.]' skills/cortex-3b-rangement/SKILL.md` ne rend que des lignes qui l'interdisent.

## Tests

```bash
python3 skills/cortex-3b-rangement/scripts/range.py --autotest
python3 skills/cortex-4-installation/scripts/etat.py --autotest
python3 skills/cortex-4-installation/scripts/cortex_config.py --autotest
python3 skills/cortex-4-installation/scripts/scaffold.py --autotest
python3 skills/cortex-5-ingest/scripts/copie_structurant.py --autotest
python3 skills/cortex-8-federation/scripts/federe.py --autotest
python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo "exit=$?"
```

## Contrôles sécurité
- [ ] Aucun secret, aucun nom réel de personne ou d'organisation dans les fixtures et le pack.
- [ ] `range.py` résout les liens symboliques avant de comparer un chemin aux racines (G4) : un lien sous une racine qui pointe hors d'elle lève le code 3 (cas dans l'auto-test).

## Contrôles silent-failure
- [ ] Aucun `except` vide sans trace, aucun repli qui agrège plusieurs causes en un seul message, aucun geste en échec qui continue le lot en silence : vérifié par l'agent `silent-failure-hunter` sur `range.py`, `etat.py`, `cortex_config.py`, `scaffold.py`, `federe.py`, `copie_structurant.py`.

## Comment on saura que ces contrôles ne mentent pas

Méthode : skill `verifier-avant-de-croire`.

- [ ] Chaque garde est prouvée mordante : l'auto-test contient le cas qui la fait lever ; en plus, une perturbation manuelle (désactiver G1 dans une copie jetable de `range.py`) fait rougir l'auto-test, sortie consignée dans `rapport.md`.
- [ ] Le grep des appels interdits a son témoin : la même commande sur un fichier jetable qui contient `os.remove(` rend une ligne.
- [ ] Le contrôle « aucun `{{` » a son témoin : un gabarit jetable qui garde `{{REFERENTIEL}}` le fait rougir.
- [ ] La comparaison d'arbre d'I-R2 a son témoin : un `touch` sur un fichier entre appliquer et annuler la fait échouer.
- [ ] Chaque assertion négative de la recette (pas de note par procédure d'entreprise, pas de procédure copiée) porte une positive sur le même objet (la note `Référentiel commun` existe, un contrat copié existe).

## Contrôle manuel consigné
- [ ] Dans une session Claude Code ouverte sur un atelier de recette (fixture dirigeant, après le maillon 3), « rangeons mes dossiers » déclenche `cortex-3b-rangement`, affiche un premier lot de quatre lignes en entier, et un refus total écrit `statut: refuse`. Sortie d'écran résumée dans `rapport.md`.

## Definition of Done
Tous les items cochés, la recette sort `0`, `rapport.md` écrit, la ligne **Statut** du `README.md` du pack dit « livrée, à auditer » avec le dernier hash.
