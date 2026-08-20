---
type: meta
tags:
  - memo
  - claude-code
cree: 2026-06-27
maj: 2026-06-25
---
# Mémo - Commandes Claude Code

Remonte vers [[Centre]]. Aide-mémoire des commandes utilisées au quotidien dans Claude Code. À enrichir au fil de l'usage.

## Session

| Commande | Effet |
|---|---|
| `/add-dir <chemin>` | Ajout d'un nouveau dossier de travail dans la session courante. |

## Permissions

| Commande | Effet |
|---|---|
| `claude --dangerously-skip-permissions` | Désactive tous les prompts d'autorisation. Réservé environnement isolé (VPS, sandbox). |
| `/permissions` | Gestion fine de l'allowlist (Bash, Read, Edit, …) au sein d'une session. |
| `/fewer-permission-prompts` | Scanne l'historique et propose une allowlist optimisée sur l'usage réel. |
