# Audit à froid de la lane E (session neuve, Opus 5 effort high, 2026-09-19)

Worktree `~/Dev/cortex--E`, branche `lane/E` à `1a325c9`. Contrat de référence : `04-contrat.md` de `main` à `c027112` (amendements du 2026-09-19 inclus, dont §9 forme des hooks). Rien n'a été modifié dans le périmètre de la lane ; seul ce fichier a été écrit, sur consigne du chef d'orchestre, et il n'est pas commité.

## Avertissement de méthode

`git diff main --stat` fait apparaître `03-backlog.md`, `04-contrat.md` et `README.md` : ce sont les trois commits de `main` (`6fe114a`, `98463af`, `0c09255`, puis `c027112`) que la lane n'a pas, pas des fichiers qu'elle aurait touchés. L'empreinte réelle se lit depuis la base de fusion `2e0ee29`. Un audit qui s'arrêterait à la première commande conclurait à tort à trois défauts bloquants de possession.

## Tableau de replay

| # | Critère | Commande | Sortie (extrait) | Verdict | Confiance |
|---|---|---|---|---|---|
| 1 | Possession des fichiers (§1) | `git diff 2e0ee29 HEAD --stat` | 24 fichiers ; tous sous `skills/cortex-4-installation/{SKILL.md,scripts/{scaffold,lint_sante}.py,template/}`, `skills/cortex-{5,6,7}-*/`, plus `chantiers/cortex-v2/consignes-E.md` | **passe** | haute |
| 1b | `consignes-E.md` hors colonne « Possède » | `git show a1fcd17 --stat` | `chantiers/cortex-v2/consignes-E.md \| 7 +` | **passe** (planté par le chef d'orchestre, cf. `03-backlog.md` §Décisions après A2 : « chaque lane a reçu `consignes-<lane>.md` sur sa branche ») | haute |
| 1c | `config.example.yaml` non touché (lane C) | `git diff 2e0ee29 HEAD --name-only \| grep config.example` | vide | **passe** | haute |
| 2 | Lecture permise dans un vault scaffoldé | `claude -p "compte les fichiers de <racine>" --output-format json` | `is_error=False` · `permission_denials = []` · « 3 fichiers, dans un sous-dossier unique » | **passe** | moyenne (voir défaut M-1 : `allow` et `additionalDirectories` ignorés, espace non « trusted ») |
| 3 | Écriture refusée hors vault | `claude -p "écris un fichier x dans <racine>/y" --output-format json` | « Refus d'écrire : `<racine>` est un dossier de travail déclaré en lecture seule … **Aucun fichier créé.** » · `find <racine> -type f` = les 3 fichiers d'origine | **passe** | moyenne (refus motivé par le `deny` lu, pas un `permission_denials` mécanique) |
| 4 | `parle` cite des liens que le lint résout | `claude -p "parle : quels sont mes domaines …"` puis résolution une à une | 7 liens : `Actifs`, `Architecture - Vue d'ensemble`, `Architecture Mémoire`, `Centre`, `Configuration`, `Conventions`, `Développement` — tous résolus vers un `.md` du vault | **passe** | haute |
| 5 | Structurant modifié à la source lève `structurant_perime` | `copie_structurant.py --source … --type process` puis modification de la source puis `lint_sante.py --vault …` | `[i] 1 structurant(s) dont la source a change depuis la copie` · `raison: "source modifiee depuis la copie"` | **passe** | haute |
| 5b | `structurant_perime` est une dette, lint à 0 (amendement §9) | `lint_sante.py --vault <vault>; echo $?` | `0` alors que `structurant_perime` est non vide | **passe** | haute |
| 6 | `lint_sante.py --vault <vault>` = 0 en pointeur et en copie | idem, `regime: pointeur` puis `regime: copie` | `[OK] Vault sain.` · `rc=0` dans les deux cas | **passe** | haute |
| 7 | `settings.json` conforme §9 + amendement | `cat <vault>/.claude/settings.json` | 17 entrées `allow` (les 13 du §9 + `git add`, `git commit`, `git push`, `export.py`) ; `deny` = `Write(<racine>/**)` et `Edit(<racine>/**)` ; `additionalDirectories` = les racines ; `hooks` SessionStart et Stop | **passe** | haute |
| 8 | Forme des hooks (amendement §9 du `c027112`) | `find <vault>/.claude/hooks` | `session_start.py`, `stop.py`, appelés par `python3 .claude/hooks/<nom>.py` ; auto-testés | **passe** | haute |
| 9 | Export §6 | `python3 .claude/skills/cloture/export.py --vault .` en solo puis en federe | solo : « mode solo : aucun export, rien à faire. » ; federe : « ✓ Export : 2 note(s) dans `_export/acme/` » avec `index.json` au format `cortex/export` v1 | **passe** | haute |
| 10 | Marques interdites (`01-cadrage.md` §Marques) | `grep -rwiE "evrard\|marcon\|mister ?ia\|devprom\|vde\|cosmos\|claudia\|kockpit\|evrardmarcon" skills/ chantiers/` | 1 ligne, `skills/stop-slop/SKILL.md` — hors lane E (annexe héritée, décision lane B). Zéro ligne dans les 24 fichiers de la lane | **passe** pour la lane | haute |
| 11 | Chemins absolus | `grep -rnE "/Users/\|/home/\|[A-Z]:\\\\" skills/ README.md` | 2 occurrences en lane E, toutes deux des détecteurs : `scaffold.py:569` (assertion d'auto-test), `lint_sante.py:337` (regex du lint). Aucun chemin absolu de donnée | **passe** | haute |
| 12 | `--help` = 0 sur chaque script de la lane | `python3 <script> --help; echo $?` | `0` pour `scaffold.py`, `lint_sante.py`, `copie_structurant.py`, `export.py`, `session_start.py`, `stop.py` | **passe** (réserve m-6 : les deux hooks n'ont pas d'argparse, `--help` y exécute `main()`) | haute |
| 13 | Auto-test = 0 sur chaque script | `python3 <script> --autotest; echo $?` | `0` × 6 ; ex. « OK lint_sante.py : structurant_perime, plafond suspendu, visibilite, cloture_ancienne, --bref » | **passe** | haute |
| 14 | Imports stdlib seulement | `grep -nE "^import\|^from" <script>` | stdlib pure + `cortex_config` (v1, stdlib), `scaffold.forme_tilde`, `lint_sante`. Aucune dépendance tierce | **passe** | haute |
| 15 | SKILL.md : frontmatter, < 300 lignes, section Notice §10 | `wc -l` et `awk '/^## Notice/,0'` | `cortex-4` 169, `cortex-5` 187, `cortex-6` 158, `cortex-7` 185 ; `parle` 60, `bilan` 62, `cloture` 176. `name` et `description` présents partout ; les 4 sections Notice sont identiques au texte §10, au caractère près | **passe** | haute |
| 16 | Phrases canoniques (amendement §5) | `grep "Phrase d'entrée"` | 4 « construis mon second cerveau », 5 « remplis mon second cerveau », 6 « voyons mes assistants métier », 7 « prépare la remise » ; `cloture` porte « Phrase canonique : « clôture » » | **passe** | haute |
| 17 | I6 : aucun sous-agent n'écrit | `grep "^tools:" template/vault/.claude/agents/*.md` | `chercheur-vault` et `auditeur-ontologie` : `tools: Read, Grep, Glob` (le `Bash` de l'auditeur a été retiré) | **passe** | haute |
| 18 | I7 : zéro plugin Obsidian requis | lecture de `scaffold.py` et du gabarit | `graph.json` écrit pour le Graph View, plugin **core** ; Dataview cantonné à une note optionnelle que rien ne référence | **passe** | haute |
| 19 | I10 : aucun maillon n'invoque le suivant | `grep -rnE "lancer \`cortex-[0-9]"` sur les SKILL.md de la lane | `cortex-4:152`, `cortex-5:168`, `cortex-6:142` portent « Sur accord, lancer `cortex-N+1` » — lignes **héritées de la v1**, non touchées par la lane (contexte de hunk) ; la section Notice les contredit dix lignes plus bas | **passe** en lecture stricte (« sur accord » = proposition), voir m-7 | moyenne |
| 20 | I11 / substance de `cloture` (consignes du chef d'orchestre) | `git diff` de `cloture/SKILL.md` | détection par `git status --porcelain`, journal du POURQUOI en tête, retrait des cases soldées, `dernier_journal` et `blocages_actifs` recomptés, idempotence, < 30 s, export §6, commit local puis `git remote \| grep -q . && git push`, « Jamais d'écriture hors du vault » | **passe** | haute |
| 21 | Recette v1 | `python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?` | `[erreur] skill presentation introuvable dans skills/ ; le deck se rend avec elle.` · `rc=1` | **non mesurable** : `rc=1` **identique sur `main`** (même commande depuis `~/Dev/cortex`) ; rupture antérieure à la lane, portée par `2e0ee29` et l'amendement §5 (deck retiré). Lanes B et G | haute |
| 22 | Arbre de travail propre | `git status --porcelain` | `?? chantiers/cortex-v2/rapport-E.md` | **passe** avec réserve m-8 (fichier non suivi, hors périmètre de la lane, sans effet sur le merge) | haute |

## Défauts par sévérité

### Bloquant

**B-1. Forme de l'appel à markitdown non conforme à l'amendement §3.**
`skills/cortex-5-ingest/scripts/copie_structurant.py:54` appelle `["uvx", "markitdown", str(source)]`. L'amendement du 2026-09-19 fixe : « l'outil de conversion est `uvx --from "markitdown[all]" markitdown` (le paquet nu ne lit ni pdf ni docx) ». C'est exactement le cas d'usage du script, qui ne lit en direct que `.md`, `.txt`, `.csv`, `.markdown` et confie tout le reste à markitdown : un `.docx` ou un `.pdf` structurant, c'est-à-dire le cas nominal du régime copie, échouera et retombera sur le message « conversion impossible ». Même écart dans la prose : `skills/cortex-5-ingest/SKILL.md:73` et les docstrings `copie_structurant.py:8` et `:49`.
Second volet du même amendement non appliqué : « le convertisseur laisse un fichier `:memory:.ses` : il s'exécute depuis un dossier temporaire ». `subprocess.run` est lancé sans `cwd`, donc dans le répertoire courant de la session, typiquement le vault.

### À corriger avant merge

**A-1. Le lint ne détecte pas un chemin absolu Windows.**
`skills/cortex-4-installation/scripts/lint_sante.py:337` : `re.finditer(r"(/Users/[\w.-]+|/home/[\w.-]+|[A-Z]:\\\\)", text)`. En chaîne brute, `\\\\` vaut **deux** antislashs littéraux. Vérifié :

```
'C:\Users\Nom'  -> []          # un vrai chemin Windows n'est PAS vu
'D:\\x'         -> ['D:\\']    # seul un antislash doublé est vu
'/Users/nom/x'  -> ['/Users/nom']
```

`chemins_absolus` est un contrôle **dur**. L'invariant I2 et le §11 du contrat exigent zéro lettre de lecteur, et la décision 19 met une machine Windows en Phase G : le contrôle qui doit l'attraper est aveugle. Défaut hérité de la v1, mais dans un fichier que la lane possède et a modifié à 176 lignes près.

**A-2. Le chemin de rafraîchissement d'un structurant périmé n'existe pas dans le vault livré.**
Trois skills promettent ce geste : `cloture/SKILL.md` (« proposer `ingest` pour rafraîchir la copie »), `parle/SKILL.md` §2, `bilan/SKILL.md` §2. Or `copie_structurant.py` n'est **pas** copié dans le vault (`scaffold.py:462-465` ne copie que `cortex_config.py` et `lint_sante.py`), et `template/vault/.claude/skills/ingest/SKILL.md` ne dit pas un mot du régime copie, des structurants ni du rafraîchissement. Inventaire du vault scaffoldé : `.claude/skills/{bilan,cloture,ingest,lint,nouveau-projet,parle}` — aucun `copie_structurant.py`. En mode consultant, le client n'a pas le plugin : la promesse n'est tenable nulle part. En mode solo elle l'est, mais `settings.json` n'a pas d'entrée `allow` pour ce script, donc le geste demandera une permission, contre l'intention affichée de l'amendement §9.

**A-3. Le `lint` du vault ne documente aucun des quatre contrôles ajoutés.**
`template/vault/.claude/skills/lint/SKILL.md` (57 lignes) ne mentionne ni `structurant_perime`, ni `visibilite_hors_enum`, ni `cloture_ancienne`, ni `--bref`, ni le régime. La personne qui voit `[i] 1 structurant(s) dont la source a change depuis la copie` n'a rien à lire pour savoir quoi en faire. Fichier possédé par la lane.

**A-4. Le slug est `organisation.code`, sans que le contrat le dise.**
`export.py:43` (`_export/<slug>/`) et `scaffold.py:532` (`gh repo create cortex-<slug>`) dérivent tous deux le slug de `organisation.code`. L'amendement §2/§3 dit que « le slug est demandé au maillon 0 » et que le vault vit dans `~/Cortex/<slug>/`, sans nommer la clé qui le porte ; `config.yaml` §2 n'a pas de clé `slug`. Le choix de la lane E est cohérent en interne, mais `federation.yaml` §6 indexe les membres par `slug` et c'est la lane F qui lira ces dossiers : si le slug du maillon 0 n'est pas `organisation.code`, les deux lanes divergeront au merge. Point à arbitrer par le chef d'orchestre, pas par la lane.

### Mineur

**M-1.** Le contrôle vivant des permissions n'est pas reproductible hors session interactive : `claude -p` a répondu « Ignoring 17 permissions.allow entries … this workspace has not been trusted » et « Ignoring 1 permissions.additionalDirectories entry ». Les règles `deny`, elles, ne sont pas ignorées. Conséquence : les critères 2 et 3 du backlog passent, mais ils ne prouvent pas ce qu'ils prétendent prouver tant que le vault n'a pas été ouvert une fois en interactif. À écrire dans `06-verification.md` (lane G) comme contrôle manuel, à l'image de l'installation du plugin.

**M-2.** `lint_sante.py:503-505` : `structurant_perime` est compté dans `dette` (il est dans `LIBELLES` et hors `DURS`) **et** annoncé une seconde fois dans la même phrase. Un vault avec un seul structurant périmé affiche « 1 point à surveiller, 1 structurant périmé ».

**M-3.** `lint_sante.py`, fonction `rendre` : les constats à valeur dict sortent en JSON brut dans une sortie destinée à un novice — `- {"file": "50 - Ressources/Structurants/process/PROCESS.md", "source_path": "...", "raison": "source modifiee depuis la copie"}`. Défaut de forme hérité de la v1, mais la lane ajoute trois familles de constats qui empruntent ce rendu.

**M-4.** `template/vault/.claude/hooks/session_start.py:42` prend `Path.cwd()` pour le vault. Claude Code expose `CLAUDE_PROJECT_DIR` ; un hook lancé depuis un sous-dossier ne trouvera ni le lint ni `_cortex/06-passation.md`, et se taira sans le dire.

**M-5.** `template/vault/.claude/skills/cloture/export.py:31` : `sys.path.append(_ICI.parents[5] / "scripts")`. Dans un vault installé sous `~/Cortex/<slug>/`, `parents[5]` désigne un dossier hors vault (`/Users/scripts` ou équivalent). Sans effet — `sys.path` tolère un chemin inexistant — mais le garde-fou `len(_ICI.parents) > 5` ne distingue pas le gabarit du vault installé, ce qui était son objet.

**M-6.** `session_start.py` et `stop.py` n'ont pas d'`argparse` : `--help` y exécute `main()` et sort 0 par accident, pas par contrat.

**M-7.** `cortex-4-installation/SKILL.md:152`, `cortex-5-ingest/SKILL.md:168`, `cortex-6-agents-metier/SKILL.md:142` portent « Sur accord, lancer `cortex-N+1` » dix lignes au-dessus d'une section Notice qui affirme que la notice « ne l'exécute jamais : la personne décide d'enchaîner ». Lignes héritées de la v1, non touchées par la lane, mais dans des fichiers qu'elle possède et qui sont désormais les seuls à porter les deux textes côte à côte.

**M-8.** Sept tirets cadratins dans les lignes ajoutées, contre la règle de prose du prompt d'exécution (`05-prompt-execution-E.md` §Règles). Six sont dans des `description:` héritées de la v1 et minimalement retouchées ; un seul est dans une phrase neuve (`cortex-7-passation/SKILL.md`, « Qu'est-ce que je fais de temps en temps ? » — …).

**M-9.** `chantiers/cortex-v2/rapport-E.md` est non suivi dans le worktree. Sans effet sur le merge ; la clôture de la lane annonçait « arbre propre ».

## Verdict

**Non mergeable en l'état.** Un seul défaut bloquant, B-1, et il tient en une ligne de `copie_structurant.py:54` plus trois mentions de prose : c'est la forme de l'appel à markitdown, gelée par l'amendement §3 après que la lane a livré. Corrigé, avec A-1 à A-4 traités ou arbitrés, le reste du travail est conforme : la possession est propre, les huit critères d'acceptation de la ligne E passent avec leur preuve, le contrat §2, §6, §9 et §10 est respecté au nom de clé près, les six auto-tests sortent 0, les invariants I2, I6, I7, I10 et I11 tiennent, et la rougeur de la recette v1 est antérieure à la lane et identique sur `main`.
