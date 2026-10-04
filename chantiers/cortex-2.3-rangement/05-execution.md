# 05 : Exécution

Cocher chaque ligne avec le hash du commit qui la porte. Un commit par bloc cohérent, sur `lane/rangement`, identité git du dépôt inchangée.

## Préalable
- [ ] Vérifier le worktree : `git -C ~/Dev/cortex--rangement status` propre, branche `lane/rangement`, base `2c1f289` (2.2.1 plus le pack).
- [ ] Lire `skills/cortex-1-cadrage/references/doctrine.md` §5, §8 à §11, puis `chantiers/cortex-v2/04-contrat.md` §1, §2, §5, §6, §9, §10 et ses amendements.
- [ ] Lancer la recette avant tout changement et noter le compte de contrôles et le code de sortie dans `rapport.md`.

## Tâches
1. [ ] `range.py` : `--proposer`, `--appliquer`, `--verifier`, `--annuler`, `--publier`, gardes G1 à G9, `--autotest` qui couvre chaque garde dans les deux sens (contrat §5) et les invariants I-R1 à I-R3 sur un arbre temporaire.
2. [ ] `references/nomenclature.md` et gabarit `AGENTS.md` (contrat §6, §7).
3. [ ] `SKILL.md` de `cortex-3b-rangement` : déclencheurs, conduite du `02-backlog-produit.md`, mots de la doctrine §8, contenu visible avant chaque accord (doctrine §10), section « Notice » identique aux maillons.
4. [ ] Maillon 1 et profils : les deux questions ; `cortex_config.py` et `config.example.yaml` (contrat §1).
5. [ ] `etat.py` : entrée « 3b », phrases, états (contrat §8) ; notice si nécessaire ; fin du maillon 3 ; garde du maillon 4.
6. [ ] Maillon 5 et `copie_structurant.py` : procédure hors copie, note `Référentiel commun`, notes-pointeurs des procédures personnelles.
7. [ ] Gabarit du vault et `scaffold.py` : `{{REFERENTIEL}}`, règle dans `CLAUDE.md`, `parle`, `ingest`.
8. [ ] Maillon 6 : classement personnel ou entreprise, publication par `range.py --publier`, ligne dans `AGENTS.md`.
9. [ ] Maillon 8 et `federe.py` : clé `referentiel`, note du commun, ligne du Centre, idempotence conservée.
10. [ ] Maillon 7 : le guide d'usage cite le dossier commun.
11. [ ] Doctrine : §12, amendement daté du §5, §9.
12. [ ] Fixtures et `parcours_blanc.py` : contrôles de `06-verification.md`.
13. [ ] `README.md` et notice si leur source cite les phrases.

## Clôture de la lane
- [ ] Passer `06-verification.md` par un sous-agent à contexte frais ; corriger ; repasser.
- [ ] Écrire `chantiers/cortex-2.3-rangement/rapport.md` : fait (avec hashes), écarts au contrat et leur motif, valeurs attendues dans des fichiers hors possession (dont la version 2.3.0 de `plugin.json`), suivis notés et non traités, compte de contrôles avant et après.
- [ ] Mettre à jour la ligne **Statut** de `README.md` de ce pack.

## Points d'arrêt
- Contrat muet ou contradictoire sur un point qui change le comportement vu par la personne : s'arrêter, le dire au chef d'orchestre.
- Fin de la tâche 13 et clôture faites : rendre compte au chef d'orchestre et s'arrêter. Pas de fusion, pas de push, pas de tag, pas de `plugin.json`.
