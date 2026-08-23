# PROVENANCE — kit de skills annexes du paquet Cortex

Établi le 2026-08-23. Méthode : lecture des fichiers de chaque skill (licence,
frontmatter, attributions), historique git du dépôt `voiesdegypte/cosmos-skills`,
et vérification du dépôt d'origine quand il est identifiable.

Ce fichier est embarqué à la racine du zip. Il porte, pour chaque skill du kit
prévu par D3, son origine, son auteur, sa licence et le verdict de
redistribution dans un paquet livré à un tiers. Les notices de licence MIT des
deux skills empruntées sont reproduites en fin de fichier : leur présence dans
le zip est une condition de la licence, pas une politesse.

## Verdicts

| Skill | Origine | Auteur | Licence | Redistribution |
|---|---|---|---|---|
| stop-slop | github.com/hardikpandya/stop-slop | Hardik Pandya | MIT | **Oui**, notice MIT jointe |
| humanizer | github.com/blader/humanizer (v2.2.0) | Siqi Chen (blader) | MIT | **Oui**, notice MIT jointe |
| prompt-architect | interne cosmos-skills | Evrard Marcon | propriétaire (auteur = distributeur) | **Oui** |
| presentation | interne cosmos-skills | Evrard Marcon | propriétaire (auteur = distributeur) | **Oui** |
| compte-rendu | interne cosmos-skills | Evrard Marcon | propriétaire (auteur = distributeur) | **Oui** |
| email-auditor | interne cosmos-skills | Evrard Marcon | propriétaire (auteur = distributeur) | **Oui** |
| docx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non — hors kit** |
| pdf | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non — hors kit** |
| pptx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non — hors kit** |
| xlsx | Anthropic (skills documents de Claude) | Anthropic, PBC | © 2025, source-available | **Non — hors kit** |

Le kit livré compte donc **six** skills annexes, pas dix. `kit.txt` est réduit
en conséquence.

## Détail par skill

### stop-slop — MIT, redistribuable

Copiée depuis `hardikpandya/stop-slop` (commit `75c0487` du dépôt
cosmos-skills, « Add stop-slop skill (from hardikpandya/stop-slop) »). Le
dossier local contient la licence d'origine (`stop-slop/LICENSE`, MIT,
copyright 2025 Hardik Pandya) : elle voyage avec la skill dans le zip. La MIT
autorise copie, distribution et sous-licence à condition de conserver la
notice de copyright.

### humanizer — MIT, redistribuable, notice à joindre

Copie de `blader/humanizer` en version 2.2.0 (frontmatter local
`version: 2.2.0` ; le dépôt d'origine, même nom, même base — le guide
Wikipedia « Signs of AI writing » de WikiProject AI Cleanup — est en 2.11.2
au 2026-08-23). Auteur : Siqi Chen, pseudonyme GitHub `blader`. Licence MIT,
copyright 2025 Siqi Chen.

Le dossier local ne contient **pas** le fichier LICENSE d'origine ; la copie
locale n'en est pas moins couverte par la MIT du dépôt source. Condition de
redistribution : la notice de copyright doit accompagner la copie. Elle est
reproduite en fin de ce fichier, qui est lui-même embarqué dans le zip — la
condition est donc tenue par construction. La fabrication (`fabrique.py`)
peut en plus déposer un LICENSE dans le dossier ; ce n'est pas exigé tant que
PROVENANCE.md est dans le paquet.

### prompt-architect, presentation, compte-rendu, email-auditor — internes

Écrites par Evrard Marcon dans le dépôt cosmos-skills (prompt-architect,
compte-rendu, email-auditor : présentes dès l'import initial `2c033d4` du
2026-07-21, rédaction française, sans marqueur d'origine tierce ;
email-auditor porte `author: Evrard` en frontmatter ; presentation :
développée dans le dépôt, historique de commits dédiés `bbc0fa4` → `a9e672b`).
Aucune licence tierce à honorer : l'auteur est le distributeur, la
redistribution est sa décision.

### docx, pdf, pptx, xlsx — Anthropic, NON redistribuables

Les quatre skills documents officielles d'Anthropic. Chaque dossier local
porte un `LICENSE.txt` identique : « © 2025 Anthropic, PBC. All rights
reserved. », régie par les conditions d'utilisation des services Anthropic,
avec des restrictions additionnelles explicites, dont :

> - Distribute, sublicense, or transfer these materials to any third party

La version publiée sur `github.com/anthropics/skills` porte la **même**
restriction ; le README du dépôt la qualifie de « source-available, not open
source ». Il n'existe donc pas de canal alternatif qui autoriserait la
redistribution.

Verdict : ces quatre skills **sortent du kit**. Les inclure dans un zip livré
à un tiers serait une violation directe de la licence. Voie de remplacement
(à arbitrer, hors de ce fichier) : la notice indique à l'installateur comment
obtenir ces capacités directement auprès d'Anthropic — elles accompagnent
Claude nativement dans la plupart des offres, et le dépôt public
`anthropics/skills` reste consultable par lui, sous les conditions
d'Anthropic, sans que le paquet n'en distribue de copie.

## Notices de licence reproduites

Condition MIT : « The above copyright notice and this permission notice shall
be included in all copies or substantial portions of the Software. »

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

### humanizer

```
MIT License

Copyright (c) 2025 Siqi Chen

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
