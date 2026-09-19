# PROVENANCE : emprunts du paquet Cortex

Établi le 2026-08-23, réduit le 2026-09-19 sur décision du chef d'orchestre : le kit d'annexes ne compte plus que `stop-slop`. Les annexes internes du fabricant (prompt-architect, presentation, compte-rendu, email-auditor) et humanizer sont retirées du kit et du dépôt.

Ce fichier est embarqué à la racine du zip. Il porte, pour chaque skill annexe qui part avec le paquet, son origine, son auteur, sa licence et le verdict de redistribution. La notice MIT de la skill empruntée est reproduite en fin de fichier : sa présence dans le zip est une condition de la licence.

Les outils installés par le maillon 0 (lecteur de notes, uv, markitdown, git, gh, GitHub Desktop, Buzz, Softeria, mcp-email) ne sont pas redistribués : chacun s'installe depuis son éditeur. Leur licence et leur adresse sont dans `outils/OUTILS.md`.

## Verdicts

| Skill | Origine | Auteur | Licence | Redistribution |
|---|---|---|---|---|
| stop-slop | github.com/hardikpandya/stop-slop | Hardik Pandya | MIT | **Oui**, notice MIT jointe |
| docx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non**, hors kit |
| pdf | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non**, hors kit |
| pptx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non**, hors kit |
| xlsx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non**, hors kit |

`fabricant/kit.txt` porte une seule ligne : `stop-slop`.

## Détail

### stop-slop : MIT, redistribuable

Copiée depuis `hardikpandya/stop-slop`. Le dossier `skills/stop-slop/` contient la licence d'origine (`LICENSE`, MIT, copyright 2025 Hardik Pandya) : elle voyage avec la skill dans le zip. La MIT autorise copie, distribution et sous-licence à condition de conserver la notice de copyright. Une adaptation locale : la ligne de déclenchement du `SKILL.md` a été rendue générique le 2026-09-19.

### docx, pdf, pptx, xlsx : Anthropic, non redistribuables

Les quatre skills documents officielles d'Anthropic portent un `LICENSE.txt` identique : « © 2025 Anthropic, PBC. All rights reserved. », régi par les conditions d'utilisation des services Anthropic, avec des restrictions explicites, dont :

> - Distribute, sublicense, or transfer these materials to any third party

La version publiée sur `github.com/anthropics/skills` porte la même restriction ; le README du dépôt la qualifie de « source-available, not open source ».

Verdict : ces quatre skills sortent du kit. Elles accompagnent Claude nativement dans la plupart des offres, et le dépôt public `anthropics/skills` reste consultable par la personne, sous les conditions d'Anthropic, sans que le paquet n'en distribue de copie.

## Notice de licence reproduite

Condition MIT : « The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. »

### stop-slop

```
MIT License

Copyright (c) 2025 Hardik Pandya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
