# Backlog technique : Phase H2

Chemins relatifs à la racine du dépôt `~/Dev/cortex`. Une lane ne touche que ses fichiers ; un besoin ailleurs s'écrit dans son rapport.

## Lane A : code

| Fichier | Défaut | Point d'accroche |
|---|---|---|
| `skills/cortex-0-poste/scripts/poste.py` | 7 détection | `detecter()` l. 119, `_uvx()` l. 87, `gh_connecte()` l. 135 : chercher aussi dans le dossier des outils de `uv` (`uv tool dir --bin`, repli `~/.local/bin`) ; distinguer absent et non mesurable (`present: null` avec `raison`) |
| idem | 6 softeria | `voie()` l. 192-196 déduit `softeria` ; `--ecrire` l'écrit sans accord. Ajouter `--voie`, n'écrire `softeria` ou `mcp-email` que si `--voie` les nomme (`04-contrat.md` §2) |
| idem | mineur options | l. 282 : `options_proposees` retombe sur `OPTIONS` sans `--options` ; doit valoir la liste passée, vide sinon |
| `skills/cortex-4-installation/scripts/etat.py` | 9 étape 8 | l. 141-159 : en `mode: federe`, étape 8 `arbitre` tant qu'un membre de `federation.yaml` n'a pas `remis_le` (`04-contrat.md` §3) ; `phrase_suivante` en conséquence |
| idem | mineur statut | l. 158 : accepter `statut: en_cours` (état « En cours ») |
| `skills/cortex-4-installation/scripts/lint_sante.py` | 10 commun | l. 443-449 : garder la marque « généré » et ajouter la comparaison à `.cortex-genere` ; l'empreinte devient une fonction de `lint_sante`, que `federe.py` appelle (une seule définition) |
| `skills/cortex-8-federation/scripts/federe.py` | 10 et 9 | `empreinte()` l. 184 remplacée par l'appel à `lint_sante` ; nouvelle commande `--inscrire` (`04-contrat.md` §4) |
| `skills/cortex-4-installation/scripts/scaffold.py` | mineur hooks | `HOOKS` l. 71-76 seulement : chemin ancré sur `${CLAUDE_PROJECT_DIR}`. Rien d'autre dans ce fichier |
| `skills/cortex-4-installation/template/vault/.claude/hooks/session_start.py`, `stop.py` | mineur hooks | résoudre le vault depuis `CLAUDE_PROJECT_DIR`, sinon depuis leur emplacement (`04-contrat.md` §10) |
| `skills/cortex-4-installation/scripts/rend_notice.py` | 7 | seulement si la notice lit `present` : `null` s'affiche « à vérifier » |
| `skills/cortex-2-inventaire/scripts/scan.py` | mineur photos | un dossier hors projets qui ne contient que des médias (images, vidéos) devient `dossier_sans_domaine`, quel que soit le nombre de fichiers |
| `skills/cortex-4-installation/recette/parcours_blanc.py` | contrôles | un contrôle par correctif ci-dessus (`06-verification.md`, lane A) ; mise à jour de l. 348 si `options_proposees` change de sens |
| `chantiers/cortex-v2/phase-h2-majeurs/rapport-A.md` | rapport | créé par la lane |

## Lane B : conduite

| Fichier | Défauts |
|---|---|
| `skills/cortex-1-cadrage/references/doctrine.md` | 1, 3, 5 : trois sections nouvelles (`04-contrat.md` §5, §6, §7), citées par chaque SKILL.md |
| `skills/cortex-0-poste/SKILL.md` | 9 (nom court toujours demandé quand un atelier existe), 6 (question softeria, `--voie`), mineur options (`--options` porte le choix), 7 (un outil « non mesurable » se dit « à vérifier ») |
| `skills/cortex-1-cadrage/SKILL.md` | 1, 2, 3, 4, 5 ; décision 2 : inscription du rédacteur par `federe.py --inscrire` à la fin du cadrage en groupe |
| `skills/cortex-1-cadrage/references/profils/*.md` | 1, 3 si un profil propose des racines par défaut ou un mot interdit |
| `skills/cortex-2-inventaire/SKILL.md` à `skills/cortex-7-passation/SKILL.md` | 1, 3, 5 : renvoi à la doctrine, et correction de chaque phrase fautive repérée |
| `skills/cortex-7-passation/SKILL.md` | 8 : la limite Windows dans le guide de remise |
| `skills/cortex-8-federation/SKILL.md` | décision 3 (lancement depuis l'atelier, commande notice depuis un vault) ; mineur contrôle 3 (exclure la ligne « Généré par ») ; statut `en_cours` gardé, `etat.py` l'accepte |
| `skills/cortex-4-installation/template/vault/.claude/skills/*/SKILL.md` (cloture, parle, bilan, ingest, lint, nouveau-projet) | 1, 5 : le vault livré n'embarque pas la doctrine ; chaque SKILL.md du vault porte en une ligne la règle des mots (§5) et de la validation visible (§7). « Accepter l'écart » est sorti de `cloture` |
| `README.md`, `outils/OUTILS.md` | 8 : la limite Windows |
| `chantiers/cortex-v2/phase-h2-majeurs/rapport-B.md` | rapport, créé par la lane |

Contraintes de la recette déjà en place et que la lane B doit tenir : chaque SKILL.md sous 300 lignes (C2), section Notice et I10 intactes (C1, C2), zéro marque tierce (C8), zéro chemin absolu (C9).

## Lane C : parcours

Aucun fichier du dépôt. Écrit sous `~/Cortex-test/` et `~/Cortex/` selon `annexe-parcours-alcyon.md`. Livrable : `~/Cortex-test/verdict-phase-h2.md`.

## Dépendances

- B cite les interfaces de A (`--voie`, `--options`, `--inscrire`, règle de l'étape 8) telles que `04-contrat.md` les fige. A et B n'ont pas à s'attendre.
- C dépend du merge de A et B dans `fix/phase-h`, checkout de `~/Dev/cortex` sur `fix/phase-h` : le plugin se charge depuis ce dossier.

## Commandes de référence

```bash
python3 skills/cortex-4-installation/recette/parcours_blanc.py          # recette, sortie 0 attendue
python3 skills/cortex-0-poste/scripts/poste.py --autotest
python3 skills/cortex-4-installation/scripts/etat.py --autotest
python3 skills/cortex-4-installation/scripts/lint_sante.py --autotest
python3 skills/cortex-8-federation/scripts/federe.py --autotest
python3 skills/cortex-4-installation/scripts/scaffold.py --autotest
python3 skills/cortex-2-inventaire/scripts/scan.py --autotest
```

Vérifier le nom exact de l'option d'auto-test de chaque script avant de s'y fier.
