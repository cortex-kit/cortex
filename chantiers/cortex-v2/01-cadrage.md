# 01 : Cadrage

## Pourquoi

Cortex v1 installe un second cerveau chez une organisation : sept maillons, un vault markdown qui pointe sans copier, une couche de quatre skills et deux sous-agents, un zip qui se déplie dans le dossier des skills. Recette verte à 38 contrôles. La chaîne suppose un consultant qui la conduit, un poste déjà équipé, une messagerie jamais branchée, et s'arrête à la remise.

La v2 vise une personne seule, sans compétence technique, qui suit une notice et obtient un vault vivant : son poste équipé, ses données inventoriées selon son profil, ses parties prenantes retrouvées par questionnement, un agent qui répond sur tout son travail, une clôture quotidienne qui alimente, et, pour une société, plusieurs vaults reliés à un commun.

## Périmètre

- Un maillon 0 qui équipe le poste (outils, mail) et ouvre une notice pas à pas.
- Trois profils (employé, dirigeant, société) qui pilotent questions, racines, plafonds, domaines de départ.
- Un régime de donnée hybride : pointeur si une base déportée existe, copie sélective des structurants sinon.
- Un scan outillé du disque, un bloc mail rempli par l'agent via le connecteur retenu.
- Un entretien de compréhension : les écarts entre déclaré et observé deviennent des questions.
- Une couche vault étendue : permissions lecture seule avec refus d'écriture hors vault, hooks, skills `parle` et `bilan`, dépôt git privé.
- Une fédération complète : contrat d'échange, agrégateur, vault commun généré.
- Une distribution par plugin Claude Code, un zip de repli, un dépôt public autoportant.
- Une recette à trois profils fictifs, puis un parcours réel sur le poste du fabricant.

## Non-objectifs

- Formation humaine, support, suivi contractuel après remise.
- Migration du vault du fabricant vers le contrat v2.
- Couche de visualisation (tableau de bord web, cockpit).
- Agents qui écrivent dans le vault.
- Plugins Obsidian communautaires requis.
- Anglais (réservé à une v2.1 par un dossier `i18n/`).
- Corps de mails copiés en régime pointeur.
- Toute dépendance à un terminal précis ou à un geste de la machine du fabricant.

## Les 19 décisions (2026-09-19)

| # | Point | Décision |
|---|---|---|
| 1 | Base | Faire évoluer la v1, diff additif, recette conservée |
| 2 | Donnée | Hybride par régime. `donnees.regime: pointeur` si une base déportée existe ou est choisie ; `copie` sinon : organigramme, process, fiches de poste, contrats, projets, acteurs, tenants et aboutissants, validés un par un |
| 3 | Profils | Employé, dirigeant, société, les trois d'emblée, tronc commun et variantes |
| 4 | Distribution | Plugin Claude Code, zip de repli, dépôt GitHub autoportant (notice, liens, rien à chercher ailleurs) |
| 5 | Outils maillon 0 | Obsidian, Wispr Flow (option), git et GitHub privé, Graphify (optionnel au maillon 2), et le kit issu de la veille (`02-arbo.md` §Outils) |
| 6 | Mail | Détection du fournisseur ; connecteur claude.ai par défaut (Gmail, Microsoft 365) ; `mcp-email` dès deux boîtes Google ; Softeria pour Outlook perso ou M365 sans admin |
| 7 | Permissions scan | Allowlist lecture seule et `deny` écriture sur les racines, dans `.claude/settings.json` du vault ; jamais de bypass |
| 8 | Agent dialogue | Skill `parle`, sous-agent `chercheur-vault`, notice HTML pas à pas ouverte à chaque étape |
| 9 | Dépôt | `~/Dev/cortex`, org GitHub neutre `cortex-kit`, public, MIT |
| 10 | Fédération | Tout en v2 : contrat d'échange, agrégateur, vault commun généré, recetté sur trois vaults fictifs |
| 11 | Premier réel | Le fabricant lui-même, vault neuf `~/Cortex/<slug>/` hors dossier synchronisé, profil dirigeant, après recette verte |
| 12 | Exécution | Autant de lanes visibles que nécessaire, ouvertes par la session chef d'orchestre, audit à froid par phase en session neuve |
| 13 | Migration | Historique conservé par `git subtree split` depuis le dépôt personnel de skills du fabricant, retrait commité, fichier de redirection laissé |
| 14 | Surface | Terminal et Cowork compatibles : aucun geste lié à un terminal précis, scripts via `uv`, recette Cowork après sonde |
| 15 | Graphify | Optionnel, proposé au maillon 2 si un dépôt de code ou un gros dossier de documents est détecté, jamais sur le vault |
| 16 | Outlook perso | Softeria embarqué, Node LTS installé dans ce seul cas |
| 17 | Corps de mail | Jamais copiés en régime pointeur. En régime copie, les fils structurants validés un par un entrent en résumé, expéditeurs anonymisés, règle écrite dans la notice |
| 18 | Langue | Français seul |
| 19 | Windows | Le fabricant dispose d'une machine Windows ; la Phase G y rejoue le maillon 0 et l'installation du plugin |

## Invariants conservés de la v1

I2 zéro chemin absolu · I3 zéro marque tierce (white-label) · I4 un vault, un rédacteur · I5 le commun est généré · I6 aucun sous-agent n'écrit · I7 zéro plugin communautaire requis · I8 `phase` dans l'enum de son cycle · I10 aucun maillon n'invoque le suivant (la notice propose la phrase suivante, ne l'exécute pas) · I11 un artefact `_cortex/` non validé arrête la chaîne. I1 « pointeur jamais copie » devient conditionnel au régime (`04-contrat.md` §2).

## Marques interdites dans `skills/`, `chantiers/`, `notice/`, `outils/`, `README.md`

Le nom du fabricant, ses prénom et nom, ses trois marques commerciales, le nom de son vault personnel, le nom de sa méthode d'audit. Le grep de recette porte la liste exacte (`03-backlog.md`, ligne G). Une lane qui rencontre l'une d'elles dans un fichier hérité de la v1 la remplace par un terme générique.

## Risques

- Une lane touche un fichier qu'elle ne possède pas : conflit au merge. Parade : `04-contrat.md` §1, audit à froid.
- La recette v1 passe au rouge dès que `etat.py` compte neuf étapes (lane B) et jusqu'au merge de G : attendu, documenté dans `04-contrat.md` §5.
- Le connecteur Gmail ne tient qu'un compte : règle de bascule vers `mcp-email` écrite dans `04-contrat.md` §7.
- Les quatre annexes internes (presentation, compte-rendu, email-auditor, stop-slop) portent des marques du fabricant héritées : lane B les traite ou les retire du kit, sur décision du chef d'orchestre.

## Cibles modèle

Exécutant : Fable 5, effort `high`. Auditeur : Fable 5, effort `high`. Les prompts 05 et 06 ne demandent jamais de raisonnement transcrit : des preuves, des sorties de commande, des extraits de diff.
