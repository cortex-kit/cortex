# Rapport final de la lane G (capture d'écran de la session cortex-G, 2026-09-19)

  notice; a one-line status detail is included only if that address is registered to the same process in the session registry (a same-user process
  can register itself).
  Ran 1 shell command 
⏺ Rapport final lane G (après décisions du chef)
  Décisions appliquées
  - Marques : douze empreintes sha256 dans parcours_blanc.py (les dix formes plus kockpit et evrardmarcon) ; aucun mot en clair dans la recette ni
    dans 06. 
  - C1 à C10 : découpage inchangé.
  - Lettre C: : recette stricte, C9 reste rouge sur scripts/notice.md:51,53 jusqu'au %USERPROFILE% de la lane B.
  - Deck : import rend_deck et contrôle ignoré retirés ; la recette n'a plus de bucket « ignoré ».
  - markitdown : le contrôle poste.py --dry-run accepte toute commande après absent →, uvx --from "markitdown[all]" markitdown compris ; aucun autre
    contrôle ne contraint la forme de l'appel.
  fixtures.py : date fixée sur Projets/PARTIES-PRENANTES.md comme demandé. La double génération à 2 s divergeait encore sur employe/ECARTS.json (même
  défaut, fichier ajouté sans date) : corrigé de la même façon, dans mon fichier. Vérification : génération, attente 2 s, régénération, empreintes
  identiques ; auto-test « déterminisme vérifié » ; employé passe de 148 à 149 fichiers, dans la plage assertée.
  Commits sur lane/G, sans push : 6b509d2, c75b76b, 212e008.
  Sorties d'acceptation (2026-09-19)
  python3 skills/cortex-4-installation/recette/parcours_blanc.py; echo $?
  → 51 contrôle(s) passé(s), 31 en échec. exit 1 (rouge attendu avant merge)
    C1 6/16  C2 5/11  C3 0/1  C4 3/9  C5 2/4  C6 0/1  C7 4/4 VERT  C8 0/1  C9 1/2  C10 7/10 ; v1 23/23
  python3 skills/cortex-4-installation/recette/fixtures.py → 149 / 374 / 104 fichiers, déterminisme vérifié
  grep white-label <liste>  → skills/stop-slop/SKILL.md:8
  grep chemins absolus      → scripts/notice.md:51, :53
  Écarts hors lane (table finale de 06-verification.md) : stop-slop:8 (prénom, annexe), auditeur-ontologie.md avec Bash dans tools (E, §9), etat.py /7 en
  dur (B), fabricant/SKILL.md:72-77 marques en clair (B), notice.md lettre C: (B, décidé).
  Aucun point en attente. Prêt à rejouer la recette après chaque merge.
  ✓ Fait : quatre décisions appliquées, fixtures déterministes (deux fichiers datés), recette et 06 régénérés
  ✎ Modifié : recette/parcours_blanc.py, recette/fixtures.py, chantiers/cortex-v2/06-verification.md
  ↻ Lancé : parcours_blanc.py (51 ok / 31 XX, exit 1 attendu), fixtures.py double génération à 2 s identique, py_compile ok
  → Suite : en attente du merge B, relance de la recette à chaque merge
✻ Brewed for 1m 22s · done 12:32
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── cortex-G ─
❯ Lane B mergée sur lane/G, relance la recette et rapporte
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Fable 5.1 · high │ cortex--G │ « cortex-G » │ ⎇ lane/G │ ctx 27% │ $9.98 │ +841/-242                                                               /rc
  ⏵⏵ bypass permissions on (shift+tab to cycle) · ← for agents

## Commits
212e008 Lane G : decisions du chef (marques +2 empreintes, deck retire), fixtures deterministes (dates fixees sur PARTIES-PRENANTES et ECARTS), 06 regenere
c75b76b Lane G : 06-verification, tableau C1 a C10 avec sorties, controles manuels M1 a M3, ecarts hors lane
6b509d2 Lane G : recette v2, neuf etapes, trois profils, federation, manifestes, white-label, C1 a C10 (rouge avant merge, cible)
6a96212 Lane G : consignes du chef d orchestre
